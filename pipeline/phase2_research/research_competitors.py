import json
import os
from datetime import datetime
from dotenv import load_dotenv
from serpapi import GoogleSearch

# Load environment variables
load_dotenv()

SERP_API_KEY = os.getenv("SERP_API_KEY")

# --- Load content gap keywords ---
input_path = "outputs/classified_keywords.json"
output_path = "outputs/content_briefs.json"

with open(input_path, "r") as f:
    classified = json.load(f)

content_gaps = classified["content_gaps"]

print(f"\n🔍 Starting competitor research...")
print(f"   Keywords to research: {len(content_gaps)}\n")


def research_keyword(keyword):
    """Fetch top 5 Google results for a keyword via SerpAPI."""
    query = keyword["query"]
    print(f"  🔎 Researching: '{query}'")

    params = {
        "engine": "google",
        "q": query,
        "api_key": SERP_API_KEY,
        "num": 5,
        "gl": "us",
        "hl": "en"
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    organic = results.get("organic_results", [])

    competitors = []
    for i, result in enumerate(organic[:5]):
        competitor = {
            "rank": i + 1,
            "title": result.get("title", ""),
            "url": result.get("link", ""),
            "meta_description": result.get("snippet", ""),
            "displayed_url": result.get("displayed_link", "")
        }
        competitors.append(competitor)
        print(f"     #{i+1} {competitor['title'][:60]}...")

    return competitors


def build_content_brief(keyword, competitors):
    """Build a structured content brief from competitor data."""
    query = keyword["query"]

    # Analyse competitor titles for patterns
    titles = [c["title"] for c in competitors]
    snippets = [c["meta_description"] for c in competitors]

    # Build the brief
    brief = {
        "keyword": query,
        "classification": "content_gap",
        "researched_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "competitor_count": len(competitors),
        "competitors": competitors,
        "content_brief": {
            "target_keyword": query,
            "recommended_title": f"Ultimate Guide to {query.title()}",
            "recommended_word_count": 2000,
            "target_audience": "Marketing professionals and growth teams",
            "content_angle": "Comprehensive, actionable guide with examples",
            "must_include_sections": [
                f"What is {query}?",
                f"Why {query} matters in 2025",
                f"Step-by-step guide to {query}",
                "Best tools and resources",
                "Common mistakes to avoid",
                "FAQ section"
            ],
            "competitor_titles": titles,
            "competitor_snippets": snippets,
            "seo_requirements": {
                "primary_keyword": query,
                "keyword_density": "1-2%",
                "meta_description_length": "150-160 characters",
                "recommended_headings": "H1, H2, H3 structure",
                "internal_links": 3,
                "schema_type": "Article + FAQ"
            }
        }
    }

    return brief


# --- Main loop ---
all_briefs = []

for keyword in content_gaps:
    competitors = research_keyword(keyword)
    brief = build_content_brief(keyword, competitors)
    all_briefs.append(brief)
    print(f"   ✅ Brief built for: {keyword['query']}\n")

# --- Save output ---
output = {
    "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "total_briefs": len(all_briefs),
    "briefs": all_briefs
}

with open(output_path, "w") as f:
    json.dump(output, f, indent=2)

print(f"💾 Saved {len(all_briefs)} content briefs to: {output_path}")
print(f"\n✅ Phase 2 — Competitor Research complete!")
print(f"   Next: Phase 3 — AI Article Generation with Groq")