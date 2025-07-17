import requests
import os
from sheets_utils import update_sheet_intelligently

ORG = 'dashpay'
REPO = 'dash'
MILESTONE = '52' # 52 = v23.0; find on https://github.com/dashpay/dash/milestones
STATE = 'all'

# Google Sheets configuration
SPREADSHEET_ID = os.environ.get('SPREADSHEET_ID', '')
SHEET_NAME = 'Core PRs'


def get_pull_requests(org, repo, milestone, state='all', write_to_sheets=False):
    query_url = 'https://api.github.com/repos/{}/{}/issues?&state={}&milestone={}&sort=created&direction=asc'.format(org, repo, state, milestone)
    #print(query_url)
    results = requests.get(query_url)

    # Check for invalid response
    if results.status_code != requests.codes.ok:
        print('{} Error: {}'.format(results.status_code, results.json()['message']))
        raise
    
    prs = results.json()
    pr_name = None

    #print(results.links)
    # Get any remaining pages of data
    while 'next' in results.links.keys():
        results = requests.get(results.links['next']['url'])
        prs.extend(results.json())

    pull_request_count = sum(1 for p in prs if 'pull_request' in p)
    print('{} Milestone items retrieved\n\tPull requests: {}'.format(len(prs), pull_request_count))
    
    # Collect data for Google Sheets
    sheet_data = []
    if write_to_sheets:
        # Add header row
        sheet_data.append(['Title', 'Number', 'State', 'Labels', 'Milestone'])
    
    for pr in prs:
        # Get milestone
        m = 'Unassigned'
        if pr['milestone'] is not None:
            m = pr['milestone']['title']
            if pr_name is None:
                pr_name = m

        # Get labels
        labels = ""
        if pr['labels'] is not None:
            for label in pr['labels']:
                labels = '{}; {}'.format(label['name'], labels).strip()

        if 'pull_request' in pr:
            if write_to_sheets:
                sheet_data.append([pr['title'], pr['number'], pr['state'], labels, m])
            else:
                print('{}\t{}\t{}\t{}'.format(pr['title'], pr['number'], pr['state'], labels))
        else:
            #print('Issue: {} {} {}'.format(pr['number'], pr['title'], m))
            continue

    print('\n{} PRs retrieved for the {} milestone (GitHub milestone #{})"'.format(pull_request_count, pr_name, MILESTONE))
    
    # Write to Google Sheets if requested
    if write_to_sheets and SPREADSHEET_ID and len(sheet_data) > 1:
        try:
            print('Writing to Google Sheets...')
            update_sheet_intelligently(SPREADSHEET_ID, SHEET_NAME, sheet_data, key_column=1)
            print('Successfully updated Google Sheets!')
        except Exception as e:
            print(f'Error writing to Google Sheets: {e}')
            print('Falling back to console output...')
            for row in sheet_data[1:]:  # Skip header
                print('{}\t{}\t{}\t{}'.format(row[0], row[1], row[2], row[3]))
    
    return sheet_data if write_to_sheets else None

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Get Dash Core PR list')
    parser.add_argument('--sheets', action='store_true', 
                       help='Write data to Google Sheets instead of console')
    args = parser.parse_args()
    
    get_pull_requests(ORG, REPO, MILESTONE, write_to_sheets=args.sheets)

if __name__ == "__main__":
    main()
