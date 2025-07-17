import os
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def get_sheets_service():
    """Get authenticated Google Sheets service using Service Account."""
    print("Attempting to authenticate with Google Sheets API using Service Account...")
    
    # Check for service account credentials
    service_account_file = 'service-account.json'
    
    if not os.path.exists(service_account_file):
        raise FileNotFoundError(
            f"\nERROR: {service_account_file} not found!\n"
            "Please follow these steps for secure Service Account setup:\n"
            "1. Go to https://console.cloud.google.com/\n"
            "2. Create a new project or select existing one\n"
            "3. Enable Google Sheets API\n"
            "4. Go to 'Credentials' > 'Create Credentials' > 'Service Account'\n"
            "5. Create a service account with a descriptive name\n"
            "6. Download the JSON key file and save as 'service-account.json'\n"
            "7. Share your Google Sheet with the service account email address\n"
            "   (found in the service-account.json file as 'client_email')\n"
            "\nService Account benefits:\n"
            "- No broad Drive access required\n"
            "- Only accesses sheets you explicitly share\n"
            "- More secure for automation"
        )
    
    try:
        print(f"Loading service account credentials from {service_account_file}...")
        
        # Load and validate the service account file
        with open(service_account_file, 'r') as f:
            service_account_info = json.load(f)
        
        # Create credentials from service account info
        creds = Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
        
        print(f"Service account email: {service_account_info.get('client_email', 'Unknown')}")
        print("✅ Service account credentials loaded successfully")
        
        # Build the service
        service = build('sheets', 'v4', credentials=creds)
        print("✅ Google Sheets service initialized successfully")
        return service
        
    except json.JSONDecodeError as e:
        raise Exception(f"Invalid JSON in {service_account_file}: {e}")
    except KeyError as e:
        raise Exception(f"Missing required field in {service_account_file}: {e}")
    except Exception as e:
        raise Exception(f"Failed to build Google Sheets service: {e}")

def ensure_sheet_exists(spreadsheet_id, sheet_name):
    """Ensure a sheet exists, create if it doesn't."""
    service = get_sheets_service()
    
    try:
        # Get existing sheets
        spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        existing_sheets = [sheet['properties']['title'] for sheet in spreadsheet['sheets']]
        
        if sheet_name not in existing_sheets:
            print(f"Creating sheet: {sheet_name}")
            request_body = {
                'requests': [{
                    'addSheet': {
                        'properties': {
                            'title': sheet_name
                        }
                    }
                }]
            }
            
            service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body=request_body
            ).execute()
            print(f"✅ Sheet '{sheet_name}' created successfully")
        else:
            print(f"✅ Sheet '{sheet_name}' already exists")
            
    except Exception as e:
        raise Exception(f"Failed to ensure sheet exists: {e}")

def write_to_sheet(spreadsheet_id, sheet_name, data, start_row=1):
    """
    Write data to Google Sheets.
    
    Args:
        spreadsheet_id: Google Sheets ID
        sheet_name: Name of the sheet tab
        data: List of lists containing the data to write
        start_row: Starting row number (1-indexed)
    """
    service = get_sheets_service()
    
    # Ensure sheet exists first
    ensure_sheet_exists(spreadsheet_id, sheet_name)
    
    # Clear existing data first
    range_name = f"'{sheet_name}'!A{start_row}:Z"
    try:
        service.spreadsheets().values().clear(
            spreadsheetId=spreadsheet_id,
            range=range_name
        ).execute()
    except Exception as e:
        print(f"Warning: Could not clear existing data: {e}")
    
    # Write new data
    range_name = f"'{sheet_name}'!A{start_row}"
    body = {
        'values': data
    }
    
    result = service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=range_name,
        valueInputOption='RAW',
        body=body
    ).execute()
    
    return result

def append_to_sheet(spreadsheet_id, sheet_name, data):
    """
    Append data to Google Sheets without clearing existing content.
    
    Args:
        spreadsheet_id: Google Sheets ID
        sheet_name: Name of the sheet tab
        data: List of lists containing the data to append
    """
    service = get_sheets_service()
    
    # Ensure sheet exists first
    ensure_sheet_exists(spreadsheet_id, sheet_name)
    
    range_name = f"'{sheet_name}'!A:Z"
    body = {
        'values': data
    }
    
    result = service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range=range_name,
        valueInputOption='RAW',
        insertDataOption='INSERT_ROWS',
        body=body
    ).execute()
    
    return result

def get_existing_data(spreadsheet_id, sheet_name):
    """
    Get existing data from Google Sheets.
    
    Args:
        spreadsheet_id: Google Sheets ID
        sheet_name: Name of the sheet tab
    
    Returns:
        List of lists containing existing data
    """
    service = get_sheets_service()
    
    # Ensure sheet exists first
    ensure_sheet_exists(spreadsheet_id, sheet_name)
    
    range_name = f"'{sheet_name}'!A:Z"
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=range_name
    ).execute()
    
    return result.get('values', [])

def update_sheet_intelligently(spreadsheet_id, sheet_name, new_data, key_column=1):
    """
    Update sheet by comparing existing data with new data.
    Updates existing rows and adds new ones.
    
    Args:
        spreadsheet_id: Google Sheets ID
        sheet_name: Name of the sheet tab
        new_data: List of lists containing new data
        key_column: Column index (0-based) to use as unique key for comparison
    """
    existing_data = get_existing_data(spreadsheet_id, sheet_name)
    
    # If no existing data, just write all new data
    if not existing_data:
        return write_to_sheet(spreadsheet_id, sheet_name, new_data)
    
    # Create a map of existing data using the key column
    existing_map = {}
    for i, row in enumerate(existing_data):
        if len(row) > key_column:
            existing_map[row[key_column]] = i
    
    # Prepare updated data
    updated_data = existing_data[:]
    
    # Update existing rows and collect new rows
    new_rows = []
    for new_row in new_data:
        if len(new_row) > key_column:
            key = new_row[key_column]
            if key in existing_map:
                # Update existing row
                row_index = existing_map[key]
                updated_data[row_index] = new_row
            else:
                # New row to be added
                new_rows.append(new_row)
    
    # Add new rows
    updated_data.extend(new_rows)
    
    # Write back to sheet
    return write_to_sheet(spreadsheet_id, sheet_name, updated_data)
