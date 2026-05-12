# 🚀 AI Content Marketing Intelligence & SEO Flywheel

> A fully automated SEO content pipeline that identifies keyword 
> opportunities, researches competitors, generates AI-written articles, 
> publishes to WordPress, monitors rankings, and rewrites underperforming 
> content — all automatically.

## 🔴 Live Demo
- **Published Articles:** https://keyshowrtheprime.wordpress.com
- **Looker Studio Dashboard:** [https://datastudio.google.com/reporting/dc4ac046-339f-4050-adae-e3285aecb3fb]

## 🏗️ Architecture

PHASE 1 — KEYWORD INTELLIGENCE
GitHub Actions (Monday 9am)
→ fetch_keywords.py — pulls 90 days GSC data
→ classify_keywords.py — sorts into Quick Wins, CTR Fixes, Content Gaps

PHASE 2 — COMPETITOR RESEARCH
→ research_competitors.py — SerpAPI fetches top 5 results per gap keyword
→ Builds structured content brief per keyword

PHASE 3 — AI ARTICLE GENERATION
→ generate_articles.py — Groq API (LLaMA 3.3 70B) writes full articles
→ enrich_article.py — adds JSON-LD schema, internal links, readability score

PHASE 4 — PUBLISHING
→ publish_to_wordpress.py — WordPress REST API publishes articles
→ Google Indexing API submits URLs

PHASE 5 — RANKING MONITOR & REWRITE LOOP
→ check_rankings.py — GSC checks position every 14 days
→ rewrite_articles.py — triggers light/full rewrite via Groq API

PHASE 6 — DASHBOARD
→ push_to_supabase.py — syncs all data to Supabase
→ export_to_csv.py — exports to Google Sheets
→ Looker Studio — live performance dashboard

## 🛠️ Tech Stack 

| Component | Tool |
|-----------|------|
| AI Writer | Groq API — LLaMA 3.3 70B |
| Keyword Data | Google Search Console API |
| Competitor Research | SerpAPI |
| Publishing | WordPress REST API |
| Database | Supabase |
| Automation | GitHub Actions |
| Dashboard | Looker Studio |
| Language | Python 3.11+ |

## 📁 Project Structure

seo-flywheel/
├── pipeline/
│   ├── phase1_keywords/
│   │   ├── fetch_keywords.py
│   │   ├── create_mock_keywords.py
│   │   └── classify_keywords.py
│   ├── phase2_research/
│   │   └── research_competitors.py
│   ├── phase3_articles/
│   │   ├── generate_articles.py
│   │   └── enrich_article.py
│   ├── phase4_publish/
│   │   └── publish_to_wordpress.py
│   ├── phase5_rankings/
│   │   ├── check_rankings.py
│   │   └── rewrite_articles.py
│   └── phase6_dashboard/
│       ├── push_to_supabase.py
│       └── export_to_csv.py
├── config/
│   └── google_credentials.json
├── outputs/
│   ├── raw_keywords.json
│   ├── classified_keywords.json
│   ├── content_briefs.json
│   ├── generated_articles.json
│   ├── enriched_articles.json
│   ├── published_articles.json
│   ├── rankings.json
│   └── rewrite_log.json
├── .env
├── .gitignore
└── README.md

## ⚙️ Setup

1. Cloneing the repo
2. Createing virtual environment: `python -m venv venv`
3. Activate: `venv\Scripts\activate`
4. Installing dependencies: `pip install -r requirements.txt`
5. Copying `.env.example` to `.env` and adding the API keys
6. Running Phase 1: `python pipeline/phase1_keywords/fetch_keywords.py`

## 🔑 Required API Keys

- `GROQ_API_KEY` — [console.groq.com](https://console.groq.com)
- `SERP_API_KEY` — [serpapi.com](https://serpapi.com)
- `SUPABASE_URL` + `SUPABASE_KEY` — [supabase.com](https://supabase.com)
- `WP_ACCESS_TOKEN` — WordPress.com OAuth
- Google Cloud OAuth credentials — Google Search Console API

## 📊 Results
- 3 AI-written SEO articles published automatically
- Full keyword classification pipeline operational
- Ranking monitor with automatic rewrite triggers
- Live Looker Studio dashboard

## 👨‍💻 Author
**Kishore Babu** — Growth Marketing Portfolio Project 3/10