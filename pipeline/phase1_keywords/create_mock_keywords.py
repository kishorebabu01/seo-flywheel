import json
import os

# Mock keyword data simulating real GSC output
# These represent 3 types your classifier will detect:
# - Quick Wins: position 8-15
# - CTR Fixes: impressions > 500, CTR < 2%
# - Content Gaps: not ranking (we add these manually)

mock_keywords = [
    # QUICK WINS — ranking 8-15, just need a push
    {
        "query": "best ai tools for marketing",
        "clicks": 12,
        "impressions": 320,
        "ctr": 3.75,
        "position": 9.2
    },
    {
        "query": "how to use chatgpt for seo",
        "clicks": 8,
        "impressions": 210,
        "ctr": 3.81,
        "position": 11.5
    },
    {
        "query": "ai content marketing strategy",
        "clicks": 5,
        "impressions": 180,
        "ctr": 2.78,
        "position": 14.3
    },
    {
        "query": "growth marketing tools 2025",
        "clicks": 9,
        "impressions": 275,
        "ctr": 3.27,
        "position": 10.1
    },

    # CTR FIXES — high impressions, very low CTR
    # People see us but don't click — title/meta needs fixing
    {
        "query": "saas marketing automation",
        "clicks": 6,
        "impressions": 890,
        "ctr": 0.67,
        "position": 4.2
    },
    {
        "query": "digital marketing for startups",
        "clicks": 11,
        "impressions": 1200,
        "ctr": 0.92,
        "position": 3.8
    },
    {
        "query": "b2b lead generation strategies",
        "clicks": 4,
        "impressions": 760,
        "ctr": 0.53,
        "position": 5.1
    },

    # BORDERLINE — will be classified by the classifier
    {
        "query": "marketing analytics dashboard",
        "clicks": 22,
        "impressions": 430,
        "ctr": 5.12,
        "position": 6.3
    },
    {
        "query": "email marketing best practices",
        "clicks": 31,
        "impressions": 520,
        "ctr": 5.96,
        "position": 7.8
    },
    {
        "query": "seo strategy for new website",
        "clicks": 3,
        "impressions": 95,
        "ctr": 3.16,
        "position": 18.4
    }
]

# Content Gap keywords — not in GSC at all
# These are opportunities competitors rank for but we don't
content_gaps = [
    {
        "query": "ai seo tools comparison",
        "clicks": 0,
        "impressions": 0,
        "ctr": 0.0,
        "position": 0,
        "type": "content_gap"
    },
    {
        "query": "how to automate content marketing",
        "clicks": 0,
        "impressions": 0,
        "ctr": 0.0,
        "position": 0,
        "type": "content_gap"
    },
    {
        "query": "llm for seo content writing",
        "clicks": 0,
        "impressions": 0,
        "ctr": 0.0,
        "position": 0,
        "type": "content_gap"
    }
]

# Combine all keywords
all_keywords = mock_keywords + content_gaps

# Save to outputs folder
output_path = "outputs/raw_keywords.json"
os.makedirs("outputs", exist_ok=True)

with open(output_path, "w") as f:
    json.dump(all_keywords, f, indent=2)

print("✅ Mock keyword data created!")
print(f"   Total keywords: {len(all_keywords)}")
print(f"   Quick Win candidates: 4")
print(f"   CTR Fix candidates: 3")
print(f"   Content Gaps: 3")
print(f"   Borderline: {len(mock_keywords) - 7}")
print(f"\n💾 Saved to: {output_path}")