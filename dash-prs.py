import requests
import json
import pprint

ORG = 'dashpay'
REPO = 'dash'
MILESTONE = '34' # 34 = v20.0; find on https://github.com/dashpay/dash/milestones
STATE = 'all'


def get_pull_requests(org, repo, milestone, state='all'):
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
            #print('{}\t{}\t{}\t{}\t{}'.format(pr['title'], pr['number'], pr['state'], labels, m))
            print('{}\t{}\t{}\t{}'.format(pr['title'], pr['number'], pr['state'], labels))
        else:
            #print('Issue: {} {} {}'.format(pr['number'], pr['title'], m))
            continue

    print('\n{} PRs retrieved for the {} milestone (GitHub milestone #{})"'.format(pull_request_count, pr_name, MILESTONE))

def main():
    get_pull_requests(ORG, REPO, MILESTONE)

if __name__ == "__main__":
    main()
