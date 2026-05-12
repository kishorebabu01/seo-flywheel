import json
import os
from datetime import datetime

# --- Load raw keywords ---
input_path = "outputs/raw_keywords.json"
output_path = "outputs/classified_keywords.json"

with open(input_path, "r") as f:
    keywords = json.load(f)

print(f"\n🔍 Classifying {len(keywords)} keywords...\n")

# --- Classification buckets ---
quick_wins = []
ctr_fixes = []
content_gaps = []
others = []

for kw in keywords:
    query = kw["query"]
    clicks = kw["clicks"]
    impressions = kw["impressions"]
    ctr = kw["ctr"]
    position = kw["position"]

    # Already tagged as content gap
    if kw.get("type") == "content_gap":
        kw["classification"] = "content_gap"
        kw["reason"] = "Not ranking — fresh article needed"
        content_gaps.append(kw)

    # Quick Win: position 8-15
    elif 8 <= position <= 15:
        kw["classification"] = "quick_win"
        kw["reason"] = f"Ranking at {position} — needs content boost to reach page 1"
        quick_wins.append(kw)

    # CTR Fix: impressions > 500, CTR < 2%
    elif impressions >= 500 and ctr < 2.0:
        kw["classification"] = "ctr_fix"
        kw["reason"] = f"{impressions} impressions but only {ctr}% CTR — title/meta needs fixing"
        ctr_fixes.append(kw)

    # Everything else
    else:
        kw["classification"] = "other"
        kw["reason"] = "Already performing well or insufficient data"
        others.append(kw)

# --- Summary ---
print(f"✅ Classification complete!\n")
print(f"  🚀 Quick Wins:    {len(quick_wins)} keywords")
for kw in quick_wins:
    print(f"     → {kw['query']} (position {kw['position']})")

print(f"\n  👁️  CTR Fixes:     {len(ctr_fixes)} keywords")
for kw in ctr_fixes:
    print(f"     → {kw['query']} (CTR: {kw['ctr']}%, impressions: {kw['impressions']})")

print(f"\n  📝 Content Gaps:  {len(content_gaps)} keywords")
for kw in content_gaps:
    print(f"     → {kw['query']}")

print(f"\n  ✔️  Others:        {len(others)} keywords (performing well)")

# --- Build final output ---
classified = {
    "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "summary": {
        "total": len(keywords),
        "quick_wins": len(quick_wins),
        "ctr_fixes": len(ctr_fixes),
        "content_gaps": len(content_gaps),
        "others": len(others)
    },
    "quick_wins": quick_wins,
    "ctr_fixes": ctr_fixes,
    "content_gaps": content_gaps,
    "others": others
}

# --- Save output ---
with open(output_path, "w") as f:
    json.dump(classified, f, indent=2)

print(f"\n💾 Saved classified keywords to: {output_path}")
print(f"\n✅ Phase 1 — Keyword Classification complete!")
print(f"   Next: Phase 2 — Competitor Research on Content Gaps")