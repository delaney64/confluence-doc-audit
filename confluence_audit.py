import requests
import csv
from datetime import datetime, timezone

# ── CONFIG ────────────────────────────────────────────────────────────────────
EMAIL     = "your-email@.org"
API_TOKEN = "your-api-token-here"
BASE_URL  = "atlassian.net/wiki/rest/api/content"
OUTPUT    = "confluence_audit_results.csv"

# ── PAGES ─────────────────────────────────────────────────────────────────────
PAGES = [
    {"id": "126374959", "title": "Incident Response Runbooks",                "recorded_date": "5/2/23"},
    {"id": "126377168", "title": "CyberArk Runbooks",                         "recorded_date": "3/21/24"},
    {"id": "126400623", "title": "Defense Evasion Techniques",                "recorded_date": "3/21/23"},
    {"id": "126375694", "title": "Dell Encryption",                           "recorded_date": "6/29/21"},
    {"id": "126377253", "title": "Email Analysis",                            "recorded_date": "4/1/24"},
    {"id": "126376967", "title": "How to Handle Malware Requests More Effectively", "recorded_date": "5/2/23"},
    {"id": "126376271", "title": "InsightVM",                                 "recorded_date": "4/21/22"},
    {"id": "126374721", "title": "New Security System Builds",                "recorded_date": "2/16/21"},
    {"id": "126376605", "title": "Proofpoint",                                "recorded_date": "11/17/22"},
    {"id": "126375934", "title": "Security Backups",                          "recorded_date": "9/30/21"},
    {"id": "126376148", "title": "ServiceNow",                                "recorded_date": "1/31/24"},
    {"id": "126374659", "title": "Splunk Runbooks",                           "recorded_date": "8/11/20"},
    {"id": "126373926", "title": "Tenable",                                   "recorded_date": "6/29/21"},
    {"id": "126373923", "title": "VeraCode",                                  "recorded_date": "4/16/24"},
]

# ── THRESHOLDS ────────────────────────────────────────────────────────────────
STALE_DAYS = 365  # flag pages not updated in over a year

# ── MAIN ──────────────────────────────────────────────────────────────────────
def fetch_page(page_id):
    url = f"{BASE_URL}/{page_id}?expand=version,metadata.labels"
    resp = requests.get(url, auth=(EMAIL, API_TOKEN))
    resp.raise_for_status()
    return resp.json()

def days_since(date_str):
    dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    return (datetime.now(timezone.utc) - dt).days

def parse_recorded(date_str):
    """Parse the recorded date string (M/D/YY) into a comparable date."""
    try:
        return datetime.strptime(date_str, "%m/%d/%y").date()
    except ValueError:
        return None

def date_match(recorded_str, actual_dt_str):
    """Compare recorded date vs actual API date — returns MATCH, MISMATCH, or NEWER."""
    recorded = parse_recorded(recorded_str)
    if not recorded:
        return "UNKNOWN"
    actual = datetime.fromisoformat(actual_dt_str.replace("Z", "+00:00")).date()
    if actual == recorded:
        return "MATCH"
    elif actual > recorded:
        return "NEWER"
    else:
        return "MISMATCH"

def main():
    results = []
    print(f"\n{'Title':<50} {'Recorded':<12} {'Actual Update':<14} {'Updated By':<25} {'Days Ago':<10} {'Match':<10} {'Status'}")
    print("-" * 145)

    for page in PAGES:
        try:
            data = fetch_page(page["id"])
            version     = data["version"]
            updated_raw = version["when"]
            updated_by  = version["by"].get("displayName", "Unknown")
            days_ago    = days_since(updated_raw)
            actual_date = datetime.fromisoformat(updated_raw.replace("Z", "+00:00")).strftime("%m/%d/%Y")
            match       = date_match(page["recorded_date"], updated_raw)
            status      = "STALE" if days_ago > STALE_DAYS else "OK"

            print(f"{data['title']:<50} {page['recorded_date']:<12} {actual_date:<14} {updated_by:<25} {days_ago:<10} {match:<10} {status}")

            results.append({
                "Page ID":           page["id"],
                "Title":             data["title"],
                "Recorded Date":     page["recorded_date"],
                "Actual Last Updated": actual_date,
                "Date Match":        match,
                "Updated By":        updated_by,
                "Days Since Update": days_ago,
                "Status":            status,
                "URL":               f"https://atlassian.net/wiki/spaces/ITSEC/pages/{page['id']}"
            })

        except requests.HTTPError as e:
            print(f"{page['title']:<50} ERROR: {e.response.status_code} {e.response.reason}")
            results.append({
                "Page ID":           page["id"],
                "Title":             page["title"],
                "Recorded Date":     page["recorded_date"],
                "Actual Last Updated": "ERROR",
                "Date Match":        "ERROR",
                "Updated By":        "",
                "Days Since Update": "",
                "Status":            f"HTTP {e.response.status_code}",
                "URL":               f"https://.atlassian.net/wiki/spaces/ITSEC/pages/{page['id']}"
            })

    # Write CSV
    with open(OUTPUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    stale_count    = sum(1 for r in results if r["Status"] == "STALE")
    mismatch_count = sum(1 for r in results if r["Date Match"] == "MISMATCH")
    newer_count    = sum(1 for r in results if r["Date Match"] == "NEWER")
    print(f"\n{'─'*145}")
    print(f"Done. {len(results)} pages checked | {stale_count} STALE | {newer_count} updated since your list | {mismatch_count} MISMATCH | Report: {OUTPUT}\n")

if __name__ == "__main__":
    main()
