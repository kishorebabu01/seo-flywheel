import json
import os
from datetime import datetime
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()

# --- Setup ---
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

input_path = "outputs/content_briefs.json"
output_path = "outputs/generated_articles.json"

# --- Load content briefs ---
with open(input_path, "r") as f:
    data = json.load(f)

briefs = data["briefs"]

print(f"\n✍️  Starting AI article generation...")
print(f"   Articles to write: {len(briefs)}\n")


def build_prompt(brief):
    """Build a detailed prompt from the content brief."""
    cb = brief["content_brief"]
    keyword = cb["target_keyword"]
    sections = "\n".join([f"- {s}" for s in cb["must_include_sections"]])
    competitor_titles = "\n".join(
        [f"- {t}" for t in cb["competitor_titles"][:3]]
    )

    prompt = f"""You are an expert SEO content writer specialising in digital marketing and growth marketing topics. It is currently 2026 so dont give 2025 stuffs, give only for 2026 by putting in headline as 2026.

Write a comprehensive, SEO-optimised article based on the following brief:

TARGET KEYWORD: {keyword}
RECOMMENDED TITLE: {cb['recommended_title']}
TARGET WORD COUNT: {cb['recommended_word_count']} words
TARGET AUDIENCE: {cb['target_audience']}
CONTENT ANGLE: {cb['content_angle']}

REQUIRED SECTIONS:
{sections}

COMPETITOR TITLES TO BEAT:
{competitor_titles}

SEO REQUIREMENTS:
- Use the primary keyword "{keyword}" naturally throughout
- Include keyword in H1 title, first paragraph, and at least 2 subheadings
- Write in a clear, engaging, professional tone
- Include actionable advice and real examples relevant to 2026
- Reference current AI tools and trends as of 2026
- Add a FAQ section at the end with 5 questions and answers
- Use H2 and H3 subheadings throughout
- Aim for {cb['recommended_word_count']} words
- All statistics, tools, and references must be relevant to 2026

FORMAT:
- Start with the H1 title using # 
- Use ## for H2 subheadings
- Use ### for H3 subheadings
- End with a ## FAQ section
- Do not include any preamble or explanation — just write the article

Write the full article now: only for the year 2026"""

    return prompt


def generate_article(brief):
    """Call Groq API to generate a full article."""
    keyword = brief["keyword"]
    print(f"  🤖 Writing article for: '{keyword}'")
    print(f"     Calling LLaMA 3.3 70B via Groq...")

    prompt = build_prompt(brief)

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert SEO content writer with 10 years "
                    "of experience writing high-ranking articles for "
                    "digital marketing, SaaS, and growth marketing topics. "
                    "You write in a clear, authoritative, and engaging style "
                    "that both Google and human readers love."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.7,
        max_tokens=3000
    )

    article_content = response.choices[0].message.content
    word_count = len(article_content.split())

    print(f"     ✅ Article written — {word_count} words")

    return {
        "keyword": keyword,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "word_count": word_count,
        "model_used": "llama-3.3-70b-versatile",
        "content": article_content,
        "brief": brief["content_brief"]
    }


# --- Main loop ---
all_articles = []

for brief in briefs:
    article = generate_article(brief)
    all_articles.append(article)
    print(f"     💾 Saved: {article['keyword']}\n")

# --- Save output ---
output = {
    "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "total_articles": len(all_articles),
    "articles": all_articles
}

with open(output_path, "w") as f:
    json.dump(output, f, indent=2)

print(f"💾 Saved {len(all_articles)} articles to: {output_path}")
print(f"\n✅ Phase 3 — Article Generation complete!")
print(f"   Next: Phase 3B — Article Enrichment")
print(f"   (Schema markup + internal links + readability score)")