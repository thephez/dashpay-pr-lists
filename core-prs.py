import os
import requests
from dotenv import load_dotenv

load_dotenv()

ORG = 'dashpay'
REPO = 'dash'
MILESTONE = '23.1'
EXCLUDE_UNMERGED = False

GRAPHQL_URL = 'https://api.github.com/graphql'

QUERY = '''
query($owner: String!, $repo: String!, $milestone: String!, $cursor: String) {
  repository(owner: $owner, name: $repo) {
    milestones(query: $milestone, first: 1) {
      nodes {
        title
        pullRequests(first: 100, after: $cursor) {
          pageInfo { hasNextPage endCursor }
          nodes {
            number
            title
            state
            merged
            createdAt
            labels(first: 10) { nodes { name } }
          }
        }
      }
    }
  }
}
'''

def get_pull_requests(org, repo, milestone):
    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        print('Error: GITHUB_TOKEN environment variable required')
        return

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    all_prs = []
    cursor = None
    milestone_title = None

    while True:
        variables = {
            'owner': org,
            'repo': repo,
            'milestone': milestone,
            'cursor': cursor
        }

        response = requests.post(GRAPHQL_URL, json={'query': QUERY, 'variables': variables}, headers=headers)

        if response.status_code != 200:
            print(f'{response.status_code} Error: {response.text}')
            return

        data = response.json()

        if 'errors' in data:
            print(f'GraphQL Error: {data["errors"]}')
            return

        milestones = data['data']['repository']['milestones']['nodes']
        if not milestones:
            print(f'Milestone "{milestone}" not found')
            return

        milestone_data = milestones[0]
        milestone_title = milestone_data['title']
        pr_data = milestone_data['pullRequests']

        all_prs.extend(pr_data['nodes'])

        if pr_data['pageInfo']['hasNextPage']:
            cursor = pr_data['pageInfo']['endCursor']
        else:
            break

    # Sort by creation date ascending
    all_prs.sort(key=lambda pr: pr['createdAt'])

    print('{}\n{}: {} PRs retrieved\n'.format('-' * 40, repo, len(all_prs)))

    for pr in all_prs:
        # Skip closed PRs that weren't merged
        if EXCLUDE_UNMERGED and pr['state'] == 'CLOSED' and not pr['merged']:
            continue

        label_names = [label['name'] for label in pr['labels']['nodes']]
        labels = '; '.join(label_names) + ';' if label_names else ''
        state = 'merged' if pr['merged'] else pr['state'].lower()

        print('{}\t{}\t{}\t{}'.format(
            pr['title'], pr['number'], state, labels
        ))

    print('\n{} PRs retrieved for the {} milestone of {}/{}\n{}\n'.format(
        len(all_prs), milestone_title, org, repo, '-' * 40
    ))

def main():
    get_pull_requests(ORG, REPO, MILESTONE)

if __name__ == "__main__":
    main()
