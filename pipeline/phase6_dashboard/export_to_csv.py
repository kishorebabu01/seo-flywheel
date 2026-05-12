import json
import csv
import os
from datetime import datetime

print("\n📊 Exporting pipeline data to CSV...")

os.makedirs("outputs/csv", exist_ok=True)


def export_keywords():
    with open("outputs/classified_keywords.json", "r") as f:
        classified = json.load(f)

    all_keywords = (
        classified["quick_wins"] +
        classified["ctr_fixes"] +
        classified["content_gaps"] +
        classified["others"]
    )

    filepath = "outputs/csv/keywords.csv"
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "query", "clicks", "impressions",
            "ctr", "position", "classification", "reason"
        ])
        writer.writeheader()
        for kw in all_keywords:
            writer.writerow({
                "query": kw["query"],
                "clicks": kw.get("clicks", 0),
                "impressions": kw.get("impressions", 0),
                "ctr": kw.get("ctr", 0),
                "position": kw.get("position", 0),
                "classification": kw.get("classification", ""),
                "reason": kw.get("reason", "")
            })

    print(f"  ✅ keywords.csv — {len(all_keywords)} rows")


def export_articles():
    with open("outputs/published_articles.json", "r") as f:
        data = json.load(f)

    filepath = "outputs/csv/articles.csv"
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "keyword", "title", "url", "post_id",
            "word_count", "readability_score",
            "status", "published_at"
        ])
        writer.writeheader()
        for article in data["published"]:
            writer.writerow({
                "keyword": article["keyword"],
                "title": article["title"],
                "url": article["url"],
                "post_id": article["post_id"],
                "word_count": article.get("word_count", 0),
                "readability_score": article.get("readability_score", 0),
                "status": "published",
                "published_at": article["published_at"]
            })

    print(f"  ✅ articles.csv — {len(data['published'])} rows")


def export_rankings():
    with open("outputs/rankings.json", "r") as f:
        data = json.load(f)

    filepath = "outputs/csv/rankings.csv"
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "keyword", "url", "position", "clicks",
            "impressions", "ctr", "status",
            "action_needed", "checked_at"
        ])
        writer.writeheader()
        for result in data["results"]:
            ranking = result.get("ranking", {})
            writer.writerow({
                "keyword": result["keyword"],
                "url": result["url"],
                "position": ranking.get("position", 0),
                "clicks": ranking.get("clicks", 0),
                "impressions": ranking.get("impressions", 0),
                "ctr": ranking.get("ctr", 0),
                "status": result["status"],
                "action_needed": result["action_needed"],
                "checked_at": result["checked_at"]
            })

    print(f"  ✅ rankings.csv — {len(data['results'])} rows")


def export_rewrites():
    with open("outputs/rewrite_log.json", "r") as f:
        data = json.load(f)

    filepath = "outputs/csv/rewrites.csv"
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "keyword", "rewrite_type", "post_id",
            "updated_url", "word_count",
            "status", "rewritten_at"
        ])
        writer.writeheader()
        for entry in data["log"]:
            writer.writerow({
                "keyword": entry["keyword"],
                "rewrite_type": entry["rewrite_type"],
                "post_id": entry.get("post_id", ""),
                "updated_url": entry.get("updated_url", ""),
                "word_count": entry.get("word_count", 0),
                "status": entry["status"],
                "rewritten_at": entry["rewritten_at"]
            })

    print(f"  ✅ rewrites.csv — {len(data['log'])} rows")


# Run all exports
export_keywords()
export_articles()
export_rankings()
export_rewrites()

print(f"\n💾 All CSV files saved to: outputs/csv/")
print(f"✅ Export complete!")
print(f"\n   Next: Upload CSVs to Google Sheets")
print(f"   Then connect Google Sheets to Looker Studio")