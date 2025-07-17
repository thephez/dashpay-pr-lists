import requests
import os
from sheets_utils import update_sheet_intelligently

ORG = 'dashevo'
STATE = 'all'
MILESTONE='28' # 28 = v2.0.0; find on https://github.com/dashevo/platform/milestones

# Google Sheets configuration
SPREADSHEET_ID = os.environ.get('SPREADSHEET_ID', '')
SHEET_NAME = 'Platform PRs'

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
    print('{}\n{}: {} milestone items retrieved\n\tPull requests: {}\n'.format('-' * 40, repo, len(prs), pull_request_count))
    
    # Collect data for Google Sheets
    sheet_data = []
    if write_to_sheets:
        # Add header row
        sheet_data.append(['Org/Repo', 'Milestone', 'Title', 'Number', 'State', 'Labels'])
    
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

        # Check if merged/closed?
        
        if 'pull_request' in pr:
            org_repo = '{}/{}'.format(org, repo)
            if write_to_sheets:
                sheet_data.append([org_repo, pr_name, pr['title'], pr['number'], pr['state'], labels])
            else:
                print('{}\t{}\t{}\t{}\t{}\t{}'.format(org_repo, pr_name, pr['title'], pr['number'], pr['state'], labels))
        else:
            #print('Issue: {} {} {}'.format(pr['number'], pr['title'], m))
            continue

    print('\n{} PRs retrieved for the {} milestone of {}/{} (GitHub milestone #{})\n{}\n'.format(pull_request_count, pr_name, org, repo, milestone, '-' * 40))
    
    # Write to Google Sheets if requested
    if write_to_sheets and SPREADSHEET_ID and len(sheet_data) > 1:
        try:
            print('Writing to Google Sheets...')
            update_sheet_intelligently(SPREADSHEET_ID, SHEET_NAME, sheet_data, key_column=3)
            print('Successfully updated Google Sheets!')
        except Exception as e:
            print(f'Error writing to Google Sheets: {e}')
            print('Falling back to console output...')
            for row in sheet_data[1:]:  # Skip header
                print('{}\t{}\t{}\t{}\t{}\t{}'.format(row[0], row[1], row[2], row[3], row[4], row[5]))
    
    return sheet_data if write_to_sheets else None

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Get Dash Platform PR list')
    parser.add_argument('--sheets', action='store_true', 
                       help='Write data to Google Sheets instead of console')
    args = parser.parse_args()
    
    repo = 'platform'
    get_pull_requests(ORG, repo, MILESTONE, write_to_sheets=args.sheets)

if __name__ == "__main__":
    main()
