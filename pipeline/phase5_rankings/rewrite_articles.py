import json
import os
import requests
import re
from datetime import datetime
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

# --- Setup ---
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
WP_ACCESS_TOKEN = os.getenv("WP_ACCESS_TOKEN")
WP_API = "https://public-api.wordpress.com/wp/v2/sites/keyshowrtheprime.wordpress.com"

headers = {
    "Authorization": f"Bearer {WP_ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

# --- Paths ---
rankings_path = "outputs/rankings.json"
published_path = "outputs/published_articles.json"
rewrite_log_path = "outputs/rewrite_log.json"

# --- Load data ---
with open(rankings_path, "r") as f:
    rankings_data = json.load(f)

with open(published_path, "r") as f:
    published_data = json.load(f)

# Build lookup for published articles
published_lookup = {
    p["keyword"]: p for p in published_data["published"]
}

# --- Get rewrite queue ---
rewrite_queue = rankings_data["rewrite_queue"]
light_rewrites = rewrite_queue.get("light", [])
full_rewrites = rewrite_queue.get("full", [])

all_rewrites = [
    {"keyword": kw, "type": "light"} for kw in light_rewrites
] + [
    {"keyword": kw, "type": "full"} for kw in full_rewrites
]

print(f"\n🔄 Starting rewrite engine...")
print(f"   Light rewrites: {len(light_rewrites)}")
print(f"   Full rewrites:  {len(full_rewrites)}")
print(f"   Total:          {len(all_rewrites)}\n")

if not all_rewrites:
    print("✅ No rewrites needed — all articles performing well!")
    exit()


def build_rewrite_prompt(keyword, rewrite_type, original_content):
    """Build rewrite prompt based on rewrite type."""

    if rewrite_type == "light":
        instruction = f"""You are an expert SEO content writer. It is 2026.

The following article is ranking at position 11-20 on Google for the keyword "{keyword}".
It needs a LIGHT REWRITE to improve its ranking.

Focus on:
- Strengthening the introduction (first 100 words are critical)
- Making the title more compelling and click-worthy
- Adding more specific 2026 examples and data points
- Improving keyword placement in subheadings
- Making the FAQ section more comprehensive

ORIGINAL ARTICLE:
{original_content[:2000]}

Write the improved full article now. Keep the same structure but make it significantly better.
Start with # for the title. Include all original sections plus improvements.
Reference 2026 tools and trends throughout."""

    else:  # full rewrite
        instruction = f"""You are an expert SEO content writer. It is 2026.

The following article is ranking at position 21+ on Google for the keyword "{keyword}".
It needs a FULL REWRITE with a completely fresh angle to compete for page 1.

New approach:
- Take a completely different angle — be more specific and actionable
- Lead with a surprising statistic or insight about "{keyword}" in 2026
- Use a step-by-step format that readers can immediately apply
- Include real tool names, pricing, and comparisons relevant to 2026
- Make it the most comprehensive guide available on this topic
- Add a detailed FAQ with questions people actually ask in 2026

ORIGINAL ARTICLE (for reference only — do NOT copy):
{original_content[:1000]}

Write a completely fresh, superior article on "{keyword}" now.
Target: 2000 words minimum.
Start with # for the H1 title.
End with a ## FAQ section with 5 detailed questions and answers."""

    return instruction


def markdown_to_html(content):
    """Convert markdown to HTML."""
    lines = content.split("\n")
    html_lines = []
    for line in lines:
        if line.startswith("# "):
            html_lines.append(f"<h1>{line[2:].strip()}</h1>")
        elif line.startswith("## "):
            html_lines.append(f"<h2>{line[3:].strip()}</h2>")
        elif line.startswith("### "):
            html_lines.append(f"<h3>{line[4:].strip()}</h3>")
        elif line.strip() == "":
            html_lines.append("<br>")
        else:
            line = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', line)
            line = re.sub(r'\*(.*?)\*', r'<em>\1</em>', line)
            html_lines.append(f"<p>{line}</p>")
    return "\n".join(html_lines)


def rewrite_article(keyword, rewrite_type):
    """Rewrite article using Groq API."""
    print(f"  ✍️  Rewriting: '{keyword}' ({rewrite_type} rewrite)")

    # Get original content from published articles
    published = published_lookup.get(keyword, {})
    post_id = published.get("post_id")

    # Fetch original content from WordPress
    original_content = f"Article about {keyword} for 2026 marketing professionals."

    try:
        wp_response = requests.get(
            f"{WP_API}/posts/{post_id}",
            headers=headers
        )
        if wp_response.status_code == 200:
            original_content = wp_response.json().get("content", {}).get("rendered", original_content)
    except Exception:
        pass

    # Build prompt and call Groq
    prompt = build_rewrite_prompt(keyword, rewrite_type, original_content)

    print(f"     🤖 Calling LLaMA 3.3 70B for {rewrite_type} rewrite...")

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a world-class SEO content writer in 2026. "
                    "You write articles that rank on page 1 of Google. "
                    "Your writing is clear, authoritative, and packed with "
                    "actionable advice. You always write for humans first, "
                    "search engines second."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.8,
        max_tokens=3000
    )

    new_content = response.choices[0].message.content
    word_count = len(new_content.split())
    print(f"     ✅ Rewrite complete — {word_count} words")

    return new_content, post_id


def update_wordpress_post(post_id, keyword, new_content):
    """Update existing WordPress post with rewritten content."""
    html_content = markdown_to_html(new_content)

    # Extract title from first line
    first_line = new_content.split("\n")[0]
    new_title = first_line.replace("# ", "").strip()

    update_data = {
        "title": new_title,
        "content": html_content,
        "status": "publish"
    }

    response = requests.post(
        f"{WP_API}/posts/{post_id}",
        headers=headers,
        json=update_data
    )

    if response.status_code in [200, 201]:
        updated_url = response.json().get("link", "")
        print(f"     🔗 Updated: {updated_url}")
        return updated_url
    else:
        print(f"     ❌ Update failed: {response.text[:200]}")
        return None


# --- Main rewrite loop ---
rewrite_log = []

for item in all_rewrites:
    keyword = item["keyword"]
    rewrite_type = item["type"]

    new_content, post_id = rewrite_article(keyword, rewrite_type)

    if post_id:
        updated_url = update_wordpress_post(post_id, keyword, new_content)
    else:
        updated_url = None
        print(f"     ⚠️  No post ID found for '{keyword}'")

    log_entry = {
        "keyword": keyword,
        "rewrite_type": rewrite_type,
        "rewritten_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "post_id": post_id,
        "updated_url": updated_url,
        "word_count": len(new_content.split()),
        "status": "success" if updated_url else "failed"
    }

    rewrite_log.append(log_entry)
    print()

# --- Save rewrite log ---
output = {
    "rewrite_run_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "total_rewrites": len(rewrite_log),
    "successful": len([r for r in rewrite_log if r["status"] == "success"]),
    "failed": len([r for r in rewrite_log if r["status"] == "failed"]),
    "log": rewrite_log
}

with open(rewrite_log_path, "w") as f:
    json.dump(output, f, indent=2)

print(f"💾 Saved rewrite log to: {rewrite_log_path}")
print(f"\n✅ Phase 5B — Rewrite Engine complete!")
print(f"   Rewrites completed: {output['successful']}")
print(f"   Next: Phase 6 — Looker Studio Dashboard")