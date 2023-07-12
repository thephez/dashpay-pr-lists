# Dash Pull Requests Info Fetcher

This project allows you to fetch the information related to pull requests for a
particular milestone from a specific repository on GitHub.

Configured for [dashpay/dash](https://github.com/dashpay/dash) and
[dashpay/platform](https://github.com/dashpay/platform) in this repository.

## Features

- Fetch all pull requests for a specified milestone in a GitHub repository
- Fetch details like title, number, state, and labels of pull requests
- Handles pagination to retrieve all available pull requests
- Error handling for API response codes

## Requirements

- Python 3.7 or later
- `requests` library (install via pip: `pip install requests`)

## Usage

The script uses several constants to operate:

- `ORG`: The GitHub organization (or user) name
- `REPO`: The GitHub repository name
- `MILESTONE`: The milestone number
- `STATE`: The state of issues to fetch ('all', 'open', 'closed')

You should set these constants to match your target repository and milestone
before running the script.

```python
ORG = 'dashpay'
REPO = 'dash'
MILESTONE = '34' # 34 = v20.0; find on https://github.com/dashpay/dash/milestones
STATE = 'all'
```

To run the script, use a Python interpreter:

```shell
python fetch_pull_requests.py
```

The script will make an API request to GitHub, fetch the relevant pull requests,
and print out their details. Please note that due to API rate limits, you may
encounter errors if you run the script many times in a short period.

## Output

The script outputs the pull request details in tab-separated format:

```text
<title> <number> <state> <labels>
```

At the end of the output, it will also provide a summary of the number of pull
requests retrieved for the given milestone.

## CI

This repository uses a GitHub Action to periodically run scripts for the Dash
Core and Dash Platform repositories as defined in
[pr-checks.yml](.github/workflows/pr-checks.yml).

## License

[MIT](LICENSE.md)
