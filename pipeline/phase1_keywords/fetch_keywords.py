import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Load environment variables
load_dotenv()

# --- CONFIG ---
SITE_URL = "https://keyshowrtheprime.wordpress.com"
CREDENTIALS_FILE = "config/google_credentials.json"
TOKEN_FILE = "config/token.json"
SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]

# --- DATE RANGE: last 90 days ---
end_date = datetime.today().strftime("%Y-%m-%d")
start_date = (datetime.today() - timedelta(days=90)).strftime("%Y-%m-%d")


def get_gsc_service():
    """Authenticate and return GSC service object."""
    creds = None

    # Load existing token if available
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    # If no valid token, do the OAuth login flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Save token for next time
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    return build("searchconsole", "v1", credentials=creds)


def fetch_keywords(service):
    """Pull 90 days of keyword data from GSC."""
    print(f"\n📡 Fetching keywords from GSC...")
    print(f"   Site: {SITE_URL}")
    print(f"   Date range: {start_date} → {end_date}\n")

    request_body = {
        "startDate": start_date,
        "endDate": end_date,
        "dimensions": ["query"],
        "rowLimit": 500
    }

    response = service.searchanalytics().query(
        siteUrl=SITE_URL,
        body=request_body
    ).execute()

    rows = response.get("rows", [])

    if not rows:
        print("⚠️  No keyword data yet — your site is new.")
        print("   This is normal. GSC takes 2-3 days to show data.")
        print("   We will proceed with mock data for now.")
        return []

    print(f"✅ Found {len(rows)} keywords\n")

    keywords = []
    for row in rows:
        keyword = {
            "query": row["keys"][0],
            "clicks": row["clicks"],
            "impressions": row["impressions"],
            "ctr": round(row["ctr"] * 100, 2),
            "position": round(row["position"], 1)
        }
        keywords.append(keyword)
        print(f"  🔑 {keyword['query']}")
        print(f"     Clicks: {keyword['clicks']} | "
              f"Impressions: {keyword['impressions']} | "
              f"CTR: {keyword['ctr']}% | "
              f"Position: {keyword['position']}")

    return keywords


def main():
    service = get_gsc_service()
    keywords = fetch_keywords(service)

    # Save to output file
    output_path = "outputs/raw_keywords.json"
    with open(output_path, "w") as f:
        json.dump(keywords, f, indent=2)

    print(f"\n💾 Saved {len(keywords)} keywords to {output_path}")
    print("\n✅ Phase 1 — Keyword fetch complete!")


if __name__ == "__main__":
    main()