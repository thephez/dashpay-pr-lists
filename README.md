# Dash PR Lists to Google Sheets

This project fetches pull request data from Dash Core and Platform repositories and can output to
either console or Google Sheets.

Configured for [dashpay/dash](https://github.com/dashpay/dash) and
[dashpay/platform](https://github.com/dashpay/platform) in this repository.

## Setup

1. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

2. **Set up Google Sheets API (Service Account - Secure):**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one
   - Enable the Google Sheets API
   - Go to "Credentials" > "Create Credentials" > "Service Account"
   - Create a service account with a descriptive name (e.g., "dashpay-pr-sheets")
   - Download the JSON key file and save as `service-account.json` in this directory
   - **Important**: Share your Google Sheet with the service account email address (found in the
     JSON file as `client_email`)

3. **Set environment variables:**

   Bash
  
   ```bash
   export SPREADSHEET_ID="your_google_sheets_id_here"
   ```

   Fish

   ```fish
   set -x SPREADSHEET_ID your_google_sheets_id_here
   ```

   You can find the spreadsheet ID in the URL:
   `https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit`

## Features

- Fetch all pull requests for a specified milestone in a GitHub repository
- Fetch details like title, number, state, and labels of pull requests
- Handles pagination to retrieve all available pull requests
- Error handling for API response codes
- **Smart Updates**: When writing to Google Sheets, the script intelligently updates existing rows
  and adds new ones without breaking existing content
- **Fallback**: If Google Sheets integration fails, it falls back to console output
- **Separate Sheets**: Core and Platform PRs are written to separate sheet tabs
- **Headers**: Automatically adds column headers when writing to sheets

## Usage

### Console Output (Original Behavior)

```bash
python core-prs.py
python platform-prs.py
```

### Google Sheets Output

```bash
python core-prs.py --sheets
python platform-prs.py --sheets
```

## Output Formats

### Console Output

The script outputs the pull request details in tab-separated format:

**Core PRs:**

```text
<title> <number> <state> <labels>
```

**Platform PRs:**

```text
<org/repo> <milestone> <title> <number> <state> <labels>
```

### Google Sheets Structure

**Core PRs Sheet:** | Title | Number | State | Labels | Milestone |

**Platform PRs Sheet:**  
| Org/Repo | Milestone | Title | Number | State | Labels |

## Configuration

Edit the milestone numbers in the scripts:

- `core-prs.py`: Update `MILESTONE` variable
- `platform-prs.py`: Update `MILESTONE` variable

## Security Features

This implementation uses **Google Service Account** authentication, which is much more secure than
OAuth:

- ✅ **No broad Drive access** - Only accesses sheets you explicitly share
- ✅ **No user interaction** - Fully automated, no browser popups
- ✅ **Principle of least privilege** - Service account only has access to what you grant
- ✅ **Revokable** - You can revoke access by unsharing the sheet
- ✅ **Auditable** - All access is logged under the service account identity

## First Run

The script will automatically authenticate using the service account. No browser authentication
required!

## Troubleshooting

### Test Your Setup

Run the test script to verify everything is configured correctly:

```bash
python3 test_sheets.py
```

### Creating a Test Spreadsheet

1. Go to [Google Sheets](https://sheets.google.com)
2. Create a new spreadsheet
3. Copy the spreadsheet ID from the URL
4. Set the SPREADSHEET_ID environment variable
5. **Note**: The "Core PRs" and "Platform PRs" sheets will be created automatically when you first run the scripts

## CI

This repository uses a GitHub Action to periodically run scripts for the Dash Core and Dash Platform
repositories as defined in [pr-checks.yml](.github/workflows/pr-checks.yml).

## License

[MIT](LICENSE.md)
