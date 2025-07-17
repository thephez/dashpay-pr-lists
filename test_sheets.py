#!/usr/bin/env python3
"""
Test script to verify Google Sheets API setup
"""
import os
import sys

def test_environment():
    """Test environment variables and files"""
    print("=== Testing Environment Setup ===")
    
    # Check SPREADSHEET_ID
    spreadsheet_id = os.environ.get('SPREADSHEET_ID')
    if not spreadsheet_id:
        print("❌ SPREADSHEET_ID environment variable not set")
        print("   Set it with: export SPREADSHEET_ID='your_spreadsheet_id_here'")
        return False
    else:
        print(f"✅ SPREADSHEET_ID: {spreadsheet_id}")
    
    # Check service-account.json
    if not os.path.exists('service-account.json'):
        print("❌ service-account.json not found")
        print("   Download from Google Cloud Console")
        return False
    else:
        print("✅ service-account.json found")
    
    return True

def test_imports():
    """Test if required packages are installed"""
    print("\n=== Testing Package Imports ===")
    
    try:
        import requests
        print("✅ requests imported successfully")
    except ImportError:
        print("❌ requests not installed")
        return False
    
    try:
        import google.auth
        print("✅ google-auth imported successfully")
    except ImportError:
        print("❌ google-auth not installed")
        print("   Install with: pip install google-auth")
        return False
    
    
    try:
        import googleapiclient
        print("✅ google-api-python-client imported successfully")
    except ImportError:
        print("❌ google-api-python-client not installed")
        print("   Install with: pip install google-api-python-client")
        return False
    
    return True

def test_sheets_connection():
    """Test Google Sheets API connection"""
    print("\n=== Testing Google Sheets Connection ===")
    
    try:
        from sheets_utils import get_sheets_service
        service = get_sheets_service()
        print("✅ Google Sheets service created successfully")
        
        # Test basic API call
        spreadsheet_id = os.environ.get('SPREADSHEET_ID')
        if spreadsheet_id:
            try:
                result = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
                print(f"✅ Successfully accessed spreadsheet: {result.get('properties', {}).get('title', 'Unknown')}")
                return True
            except Exception as e:
                print(f"❌ Failed to access spreadsheet: {e}")
                return False
        
    except Exception as e:
        print(f"❌ Failed to create Google Sheets service: {e}")
        return False
    
    return True

def main():
    print("Google Sheets API Setup Test")
    print("=" * 40)
    
    success = True
    
    # Test environment
    if not test_environment():
        success = False
    
    # Test imports
    if not test_imports():
        success = False
    
    # Test connection (only if previous tests passed)
    if success and not test_sheets_connection():
        success = False
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 All tests passed! Google Sheets integration is ready.")
        print("\nYou can now run:")
        print("  python3 core-prs.py --sheets")
        print("  python3 platform-prs.py --sheets")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()