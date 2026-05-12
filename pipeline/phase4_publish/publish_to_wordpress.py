import json
import os
import re
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- WordPress credentials ---
WP_SITE_URL = "https://public-api.wordpress.com/wp/v2/sites/keyshowrtheprime.wordpress.com"
WP_ACCESS_TOKEN = os.getenv("WP_ACCESS_TOKEN")

# --- Paths ---
input_path = "outputs/enriched_articles.json"
output_path = "outputs/published_articles.json"

# --- Auth header using OAuth token ---
headers = {
    "Authorization": f"Bearer {WP_ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

# --- Load enriched articles ---
with open(input_path, "r") as f:
    data = json.load(f)

articles = data["articles"]

print(f"\n📮 Starting WordPress publishing...")
print(f"   Site: keyshowrtheprime.wordpress.com")
print(f"   Articles to publish: {len(articles)}\n")


def markdown_to_html(content):
    """Convert markdown article to HTML for WordPress."""
    lines = content.split("\n")
    html_lines = []

    for line in lines:
        if line.startswith("# "):
            text = line[2:].strip()
            html_lines.append(f"<h1>{text}</h1>")
        elif line.startswith("## "):
            text = line[3:].strip()
            html_lines.append(f"<h2>{text}</h2>")
        elif line.startswith("### "):
            text = line[4:].strip()
            html_lines.append(f"<h3>{text}</h3>")
        elif line.strip() == "":
            html_lines.append("<br>")
        else:
            line = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', line)
            line = re.sub(r'\*(.*?)\*', r'<em>\1</em>', line)
            line = re.sub(
                r'\[([^\]]+)\]\(([^)]+)\)',
                r'<a href="\2">\1</a>',
                line
            )
            html_lines.append(f"<p>{line}</p>")

    return "\n".join(html_lines)


def build_schema_html(schema):
    """Wrap JSON-LD schema in script tag for WordPress."""
    if not schema:
        return ""

    article_schema = schema.get("article", {})
    faq_schema = schema.get("faq", {})
    schema_html = ""

    if article_schema:
        schema_html += f"""
<script type="application/ld+json">
{json.dumps(article_schema, indent=2)}
</script>
"""

    if faq_schema:
        schema_html += f"""
<script type="application/ld+json">
{json.dumps(faq_schema, indent=2)}
</script>
"""

    return schema_html


def create_excerpt(content, max_length=160):
    """Create meta description from first paragraph."""
    clean = re.sub(r'[#*\[\]()]', '', content)
    paragraphs = [p.strip() for p in clean.split('\n') if len(p.strip()) > 50]
    if paragraphs:
        excerpt = paragraphs[0][:max_length]
        return excerpt + "..." if len(paragraphs[0]) > max_length else excerpt
    return ""


def publish_article(article):
    """Publish a single article to WordPress via REST API."""
    keyword = article["keyword"]
    content = article["content"]
    brief = article["brief"]

    print(f"  📤 Publishing: '{keyword}'")

    # Convert markdown to HTML
    html_content = markdown_to_html(content)

    # Add schema markup
    schema_html = build_schema_html(article.get("schema", {}))
    full_content = html_content + "\n" + schema_html

    # Build WordPress post object
    post_data = {
        "title": brief["recommended_title"],
        "content": full_content,
        "status": "publish",
        "excerpt": create_excerpt(content)
    }

    # Call WordPress REST API
    api_url = f"{WP_SITE_URL}/posts"
    print(f"     🔗 Calling: {api_url}")

    response = requests.post(
        api_url,
        headers=headers,
        json=post_data
    )

    print(f"     📡 Status code: {response.status_code}")

    if response.status_code in [200, 201]:
        post = response.json()
        published_url = post.get("link", "")
        post_id = post.get("id", "")

        print(f"     ✅ Published successfully!")
        print(f"     🔗 URL: {published_url}")
        print(f"     📌 Post ID: {post_id}")

        return {
            "keyword": keyword,
            "title": brief["recommended_title"],
            "post_id": post_id,
            "url": published_url,
            "status": "published",
            "published_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "word_count": article["word_count"],
            "readability_score": article["readability"]["score"]
        }
    else:
        print(f"     ❌ Failed to publish")
        print(f"     Error: {response.text[:300]}")

        return {
            "keyword": keyword,
            "title": brief["recommended_title"],
            "status": "failed",
            "error": response.text[:300],
            "attempted_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }


# --- Main publishing loop ---
published = []
failed = []

for article in articles:
    result = publish_article(article)

    if result["status"] == "published":
        published.append(result)
    else:
        failed.append(result)

    print()

# --- Save output ---
output = {
    "published_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "total_attempted": len(articles),
    "total_published": len(published),
    "total_failed": len(failed),
    "published": published,
    "failed": failed
}

with open(output_path, "w") as f:
    json.dump(output, f, indent=2)

print(f"💾 Saved publishing results to: {output_path}")
print(f"\n✅ Phase 4 — Publishing complete!")
print(f"   Published: {len(published)}")
print(f"   Failed:    {len(failed)}")

if published:
    print(f"\n🌐 Live article URLs:")
    for p in published:
        print(f"   → {p['url']}")

print(f"\n   Next: Phase 5 — Ranking Monitor & Rewrite Loop")