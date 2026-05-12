import json
import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# --- Setup Supabase via REST API directly ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}

print("\n📤 Pushing all pipeline data to Supabase...")


def push_to_table(table_name, rows):
    """Push rows to a Supabase table via REST API."""
    url = f"{SUPABASE_URL}/rest/v1/{table_name}"
    success = 0
    failed = 0

    for row in rows:
        response = requests.post(url, headers=headers, json=row)
        if response.status_code in [200, 201]:
            success += 1
        else:
            failed += 1
            print(f"     ⚠️  Failed: {response.text[:100]}")

    return success, failed


# ─────────────────────────────────────────
# 1. PUSH KEYWORDS
# ─────────────────────────────────────────
print("\n  📊 Pushing keywords...")

with open("outputs/classified_keywords.json", "r") as f:
    classified = json.load(f)

all_keywords = (
    classified["quick_wins"] +
    classified["ctr_fixes"] +
    classified["content_gaps"] +
    classified["others"]
)

keyword_rows = []
for kw in all_keywords:
    keyword_rows.append({
        "query": kw["query"],
        "clicks": int(kw.get("clicks", 0)),
        "impressions": int(kw.get("impressions", 0)),
        "ctr": float(kw.get("ctr", 0)),
        "position": float(kw.get("position", 0)),
        "classification": kw.get("classification", "unknown"),
        "reason": kw.get("reason", "")
    })

success, failed = push_to_table("keywords", keyword_rows)
print(f"     ✅ Keywords pushed: {success} | Failed: {failed}")

# ─────────────────────────────────────────
# 2. PUSH ARTICLES
# ─────────────────────────────────────────
print("\n  📝 Pushing articles...")

with open("outputs/published_articles.json", "r") as f:
    published_data = json.load(f)

article_rows = []
for article in published_data["published"]:
    article_rows.append({
        "keyword": article["keyword"],
        "title": article["title"],
        "url": article["url"],
        "post_id": str(article["post_id"]),
        "word_count": int(article.get("word_count", 0)),
        "readability_score": float(article.get("readability_score", 0)),
        "status": "published",
        "published_at": article["published_at"]
    })

success, failed = push_to_table("articles", article_rows)
print(f"     ✅ Articles pushed: {success} | Failed: {failed}")

# ─────────────────────────────────────────
# 3. PUSH RANKINGS
# ─────────────────────────────────────────
print("\n  📈 Pushing rankings...")

with open("outputs/rankings.json", "r") as f:
    rankings_data = json.load(f)

ranking_rows = []
for result in rankings_data["results"]:
    ranking = result.get("ranking", {})
    ranking_rows.append({
        "keyword": result["keyword"],
        "url": result["url"],
        "position": float(ranking.get("position", 0)),
        "clicks": int(ranking.get("clicks", 0)),
        "impressions": int(ranking.get("impressions", 0)),
        "ctr": float(ranking.get("ctr", 0)),
        "status": result["status"],
        "action_needed": result["action_needed"],
        "checked_at": result["checked_at"]
    })

success, failed = push_to_table("rankings", ranking_rows)
print(f"     ✅ Rankings pushed: {success} | Failed: {failed}")

# ─────────────────────────────────────────
# 4. PUSH REWRITES
# ─────────────────────────────────────────
print("\n  🔄 Pushing rewrite log...")

with open("outputs/rewrite_log.json", "r") as f:
    rewrite_data = json.load(f)

rewrite_rows = []
for entry in rewrite_data["log"]:
    rewrite_rows.append({
        "keyword": entry["keyword"],
        "rewrite_type": entry["rewrite_type"],
        "post_id": str(entry.get("post_id", "")),
        "updated_url": entry.get("updated_url", ""),
        "word_count": int(entry.get("word_count", 0)),
        "status": entry["status"],
        "rewritten_at": entry["rewritten_at"]
    })

success, failed = push_to_table("rewrites", rewrite_rows)
print(f"     ✅ Rewrites pushed: {success} | Failed: {failed}")

# ─────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────
print(f"\n{'='*45}")
print(f"✅ Supabase sync complete!")
print(f"{'='*45}")
print(f"\n   Next: Connect Looker Studio to Supabase")