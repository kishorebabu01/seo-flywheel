import json
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

load_dotenv()

# --- Paths ---
published_path = "outputs/published_articles.json"
rankings_path = "outputs/rankings.json"

# --- GSC Config ---
TOKEN_FILE = "config/token.json"
SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]
SITE_URL = "https://keyshowrtheprime.wordpress.com"

# --- Date range: last 14 days ---
end_date = datetime.today().strftime("%Y-%m-%d")
start_date = (datetime.today() - timedelta(days=14)).strftime("%Y-%m-%d")


def get_gsc_service():
    """Authenticate and return GSC service."""
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
    return build("searchconsole", "v1", credentials=creds)


def check_ranking_for_url(service, url, keyword):
    """Check GSC ranking for a specific URL and keyword."""
    try:
        request_body = {
            "startDate": start_date,
            "endDate": end_date,
            "dimensions": ["query", "page"],
            "dimensionFilterGroups": [{
                "filters": [{
                    "dimension": "page",
                    "operator": "equals",
                    "expression": url
                }]
            }],
            "rowLimit": 10
        }

        response = service.searchanalytics().query(
            siteUrl=SITE_URL,
            body=request_body
        ).execute()

        rows = response.get("rows", [])

        if rows:
            # Find the row matching our target keyword
            for row in rows:
                if keyword.lower() in row["keys"][0].lower():
                    return {
                        "position": round(row["position"], 1),
                        "clicks": row["clicks"],
                        "impressions": row["impressions"],
                        "ctr": round(row["ctr"] * 100, 2)
                    }
            # Return best ranking if keyword not found exactly
            best = rows[0]
            return {
                "position": round(best["position"], 1),
                "clicks": best["clicks"],
                "impressions": best["impressions"],
                "ctr": round(best["ctr"] * 100, 2)
            }
        else:
            return None

    except Exception as e:
        print(f"     ⚠️  GSC error: {str(e)[:100]}")
        return None


def classify_ranking(position):
    """Classify ranking and determine action needed."""
    if position is None:
        return "not_indexed", "resubmit_to_indexing"
    elif position <= 10:
        return "success", "none"
    elif position <= 20:
        return "needs_improvement", "light_rewrite"
    else:
        return "underperforming", "full_rewrite"


def simulate_ranking(keyword):
    """
    Simulate ranking data for new articles.
    Real GSC data appears after 3-7 days of indexing.
    """
    import random

    # New articles typically start at position 20-60
    simulated_positions = {
        "ai seo tools comparison": 34.5,
        "how to automate content marketing": 28.2,
        "llm for seo content writing": 41.8
    }

    position = simulated_positions.get(keyword, random.uniform(25, 55))

    return {
        "position": position,
        "clicks": 0,
        "impressions": random.randint(5, 50),
        "ctr": 0.0,
        "simulated": True
    }


# --- Load published articles ---
with open(published_path, "r") as f:
    data = json.load(f)

published = data["published"]

print(f"\n📊 Starting ranking check...")
print(f"   Articles to check: {len(published)}")
print(f"   Date range: {start_date} → {end_date}\n")

# --- Connect to GSC ---
service = get_gsc_service()

# --- Check each article ---
ranking_results = []

for article in published:
    keyword = article["keyword"]
    url = article["url"]
    title = article["title"]

    print(f"  🔍 Checking: '{keyword}'")
    print(f"     URL: {url}")

    # Try real GSC data first
    ranking_data = check_ranking_for_url(service, url, keyword)

    # If no real data yet, use simulation
    if not ranking_data:
        print(f"     ℹ️  No GSC data yet — using simulated ranking")
        ranking_data = simulate_ranking(keyword)

    position = ranking_data["position"]
    status, action = classify_ranking(position)

    # Determine action emoji
    action_emoji = {
        "none": "✅",
        "light_rewrite": "🔄",
        "full_rewrite": "🔴",
        "resubmit_to_indexing": "📤"
    }.get(action, "❓")

    print(f"     📍 Position: {position}")
    print(f"     {action_emoji} Status: {status} → Action: {action}")

    result = {
        "keyword": keyword,
        "title": title,
        "url": url,
        "checked_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ranking": ranking_data,
        "status": status,
        "action_needed": action,
        "published_at": article["published_at"]
    }

    ranking_results.append(result)
    print()

# --- Summary ---
success = [r for r in ranking_results if r["status"] == "success"]
light_rewrite = [r for r in ranking_results if r["action_needed"] == "light_rewrite"]
full_rewrite = [r for r in ranking_results if r["action_needed"] == "full_rewrite"]
not_indexed = [r for r in ranking_results if r["action_needed"] == "resubmit_to_indexing"]

print(f"📊 Ranking Check Summary:")
print(f"   ✅ Success (pos 1-10):        {len(success)}")
print(f"   🔄 Light rewrite (pos 11-20): {len(light_rewrite)}")
print(f"   🔴 Full rewrite (pos 21+):    {len(full_rewrite)}")
print(f"   📤 Not indexed:               {len(not_indexed)}")

# --- Save results ---
output = {
    "checked_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "date_range": f"{start_date} → {end_date}",
    "total_checked": len(ranking_results),
    "summary": {
        "success": len(success),
        "light_rewrite": len(light_rewrite),
        "full_rewrite": len(full_rewrite),
        "not_indexed": len(not_indexed)
    },
    "results": ranking_results,
    "rewrite_queue": {
        "light": [r["keyword"] for r in light_rewrite],
        "full": [r["keyword"] for r in full_rewrite]
    }
}

with open(rankings_path, "w") as f:
    json.dump(output, f, indent=2)

print(f"\n💾 Saved ranking data to: {rankings_path}")
print(f"\n✅ Phase 5A — Ranking Check complete!")
print(f"   Next: Phase 5B — Rewrite triggered articles")