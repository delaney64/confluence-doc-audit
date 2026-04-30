# confluence-audit

A lightweight Python script to audit Confluence page update dates against a tracked list — built for the USAC IT Security team.

## What it does

- Fetches the actual `last updated` date for each page via the Confluence REST API
- Compares it against your recorded date list
- Flags pages as `MATCH`, `NEWER`, or `MISMATCH`
- Flags pages not updated in over a year as `STALE`
- Outputs a clean CSV report

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/<your-username>/confluence-audit.git
cd confluence-audit
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure credentials

Open `confluence_audit.py` and update the config block at the top:

```python
EMAIL     = "your-email@email.org"
API_TOKEN = "your-api-token-here"
```

Generate an API token at: https://id.atlassian.com/manage-profile/security/api-tokens

> **Never commit your API token.** Use environment variables or a `.env` file (excluded via `.gitignore`) for production use.

### 4. Run

```bash
python confluence_audit.py
```

## Output

Prints a summary table to the terminal and saves `confluence_audit_results.csv` with the following columns:

| Column | Description |
|---|---|
| Page ID | Confluence page ID |
| Title | Page title |
| Recorded Date | Date from your tracked list |
| Actual Last Updated | Date returned by the Confluence API |
| Date Match | `MATCH`, `NEWER`, or `MISMATCH` |
| Updated By | Display name of last editor |
| Days Since Update | Days elapsed since last update |
| Status | `OK` or `STALE` (configurable threshold) |
| URL | Direct link to the page |

## Configuration

| Variable | Default | Description |
|---|---|---|
| `STALE_DAYS` | `365` | Days before a page is flagged `STALE` |
| `OUTPUT` | `confluence_audit_results.csv` | Output file name |

## Date Match logic

- **MATCH** — Confluence date aligns with your recorded date
- **NEWER** — Page was updated after your recorded date (someone edited it since)
- **MISMATCH** — Recorded date is newer than Confluence (possible data entry error)

## Requirements

- Python 3.8+
- Atlassian Cloud account with API token access
- Read permission on the target Confluence space
