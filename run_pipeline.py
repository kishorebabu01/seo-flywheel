import subprocess
import sys
import os

def run(script):
    print(f"\n{'='*50}")
    print(f"▶ Running: {script}")
    print(f"{'='*50}")
    result = subprocess.run(
        [sys.executable, script],
        capture_output=False
    )
    if result.returncode != 0:
        print(f"❌ Failed: {script}")
        print("Fix the error above before continuing.")
        sys.exit(1)
    print(f"✅ Done: {script}")

print("\n🚀 SEO FLYWHEEL — FULL PIPELINE RUN")
print("="*50)

# Phase 1 — Keyword Intelligence
print("\n📍 PHASE 1 — KEYWORD INTELLIGENCE")
run("pipeline/phase1_keywords/fetch_keywords.py")
run("pipeline/phase1_keywords/create_mock_keywords.py")
run("pipeline/phase1_keywords/classify_keywords.py")

# Phase 2 — Competitor Research
print("\n📍 PHASE 2 — COMPETITOR RESEARCH")
run("pipeline/phase2_research/research_competitors.py")

# Phase 3 — Article Generation
print("\n📍 PHASE 3 — AI ARTICLE GENERATION")
run("pipeline/phase3_articles/generate_articles.py")
run("pipeline/phase3_articles/enrich_article.py")

# Phase 4 — Publishing
print("\n📍 PHASE 4 — PUBLISHING TO WORDPRESS")
run("pipeline/phase4_publish/publish_to_wordpress.py")

# Phase 5 — Rankings + Rewrite
print("\n📍 PHASE 5 — RANKING MONITOR + REWRITE")
run("pipeline/phase5_rankings/check_rankings.py")
run("pipeline/phase5_rankings/rewrite_articles.py")

# Phase 6 — Dashboard
print("\n📍 PHASE 6 — DASHBOARD SYNC")
run("pipeline/phase6_dashboard/push_to_supabase.py")
run("pipeline/phase6_dashboard/export_to_csv.py")

print("\n" + "="*50)
print("🎉 FULL PIPELINE COMPLETE!")
print("="*50)
print("\n✅ Keywords classified")
print("✅ Competitor research done")
print("✅ Articles written by AI")
print("✅ Articles published to WordPress")
print("✅ Rankings checked")
print("✅ Rewrites triggered if needed")
print("✅ Data synced to Supabase")
print("✅ CSVs exported for Looker Studio")
print("\n🌐 Check your live articles:")
print("   https://keyshowrtheprime.wordpress.com")
print("\n📊 Check your dashboard:")
print("   https://lookerstudio.google.com")