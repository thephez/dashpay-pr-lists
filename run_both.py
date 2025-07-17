#!/usr/bin/env python3
"""
Combined script to run both core and platform PR fetchers
"""
import argparse
import os
import sys
from core_prs import get_pull_requests as get_core_prs
from platform_prs import get_pull_requests as get_platform_prs

def main():
    parser = argparse.ArgumentParser(description='Get both Dash Core and Platform PR lists')
    parser.add_argument('--sheets', action='store_true', 
                       help='Write data to Google Sheets instead of console')
    parser.add_argument('--core-only', action='store_true',
                       help='Only fetch Core PRs')
    parser.add_argument('--platform-only', action='store_true',
                       help='Only fetch Platform PRs')
    args = parser.parse_args()
    
    if args.sheets and not os.environ.get('SPREADSHEET_ID'):
        print("Error: SPREADSHEET_ID environment variable is required for Google Sheets output")
        print("Set it with: export SPREADSHEET_ID='your_spreadsheet_id_here'")
        sys.exit(1)
    
    success = True
    
    if not args.platform_only:
        try:
            print("Fetching Dash Core PRs...")
            from core_prs import ORG as CORE_ORG, MILESTONE as CORE_MILESTONE
            get_core_prs(CORE_ORG, 'dash', CORE_MILESTONE, write_to_sheets=args.sheets)
        except Exception as e:
            print(f"Error fetching Core PRs: {e}")
            success = False
    
    if not args.core_only:
        try:
            print("Fetching Dash Platform PRs...")
            from platform_prs import ORG as PLATFORM_ORG, MILESTONE as PLATFORM_MILESTONE
            get_platform_prs(PLATFORM_ORG, 'platform', PLATFORM_MILESTONE, write_to_sheets=args.sheets)
        except Exception as e:
            print(f"Error fetching Platform PRs: {e}")
            success = False
    
    if success:
        print("\nAll PR data fetched successfully!")
    else:
        print("\nSome errors occurred during execution.")
        sys.exit(1)

if __name__ == "__main__":
    main()
