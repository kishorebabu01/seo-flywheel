import json
import os
import re
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# --- Paths ---
input_path = "outputs/generated_articles.json"
output_path = "outputs/enriched_articles.json"

# --- Load generated articles ---
with open(input_path, "r") as f:
    data = json.load(f)

articles = data["articles"]

print(f"\n🔧 Starting article enrichment...")
print(f"   Articles to enrich: {len(articles)}\n")


def calculate_readability_score(text):
    """
    Simple Flesch Reading Ease approximation.
    Higher score = easier to read.
    Target: 60-70 for general audience.
    """
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    words = text.split()
    
    if not sentences or not words:
        return 0

    avg_sentence_length = len(words) / len(sentences)
    
    # Count syllables (simple approximation)
    def count_syllables(word):
        word = word.lower()
        vowels = "aeiouy"
        count = 0
        prev_vowel = False
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_vowel:
                count += 1
            prev_vowel = is_vowel
        return max(1, count)
    
    total_syllables = sum(count_syllables(w) for w in words)
    avg_syllables = total_syllables / len(words)
    
    # Flesch Reading Ease formula
    score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables)
    score = round(max(0, min(100, score)), 1)
    
    return score


def get_readability_label(score):
    """Convert score to human readable label."""
    if score >= 70:
        return "Easy — Great for general audience"
    elif score >= 60:
        return "Standard — Good for most readers"
    elif score >= 50:
        return "Fairly Difficult — Consider simplifying"
    else:
        return "Difficult — Needs rewriting for clarity"


def build_json_ld_schema(article):
    """Build Article + FAQ JSON-LD schema for SEO."""
    keyword = article["keyword"]
    content = article["content"]
    
    # Extract FAQ questions from content
    faq_pairs = []
    lines = content.split("\n")
    
    current_question = None
    current_answer = []
    in_faq = False
    
    for line in lines:
        line = line.strip()
        if "FAQ" in line.upper():
            in_faq = True
            continue
        
        if in_faq:
            # Detect questions (lines ending with ?)
            if line.endswith("?") and len(line) > 10:
                if current_question and current_answer:
                    faq_pairs.append({
                        "question": current_question,
                        "answer": " ".join(current_answer).strip()
                    })
                current_question = line.lstrip("#").strip()
                current_answer = []
            elif current_question and line and not line.startswith("#"):
                current_answer.append(line)
    
    # Add last FAQ pair
    if current_question and current_answer:
        faq_pairs.append({
            "question": current_question,
            "answer": " ".join(current_answer).strip()
        })
    
    # Limit to 5 FAQ pairs
    faq_pairs = faq_pairs[:5]
    
    # Build Article schema
    article_schema = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": article["brief"]["recommended_title"],
        "description": f"Comprehensive guide to {keyword} for marketing professionals",
        "keywords": keyword,
        "author": {
            "@type": "Person",
            "name": "Kishore"
        },
        "publisher": {
            "@type": "Organization",
            "name": "Keyshowrtheprime",
            "url": "https://keyshowrtheprime.wordpress.com"
        },
        "datePublished": datetime.now().strftime("%Y-%m-%d"),
        "dateModified": datetime.now().strftime("%Y-%m-%d"),
        "mainEntityOfPage": {
            "@type": "WebPage",
            "@id": f"https://keyshowrtheprime.wordpress.com/{keyword.replace(' ', '-')}"
        }
    }
    
    # Build FAQ schema
    faq_schema = None
    if faq_pairs:
        faq_schema = {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": pair["question"],
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": pair["answer"]
                    }
                }
                for pair in faq_pairs
            ]
        }
    
    return article_schema, faq_schema, faq_pairs


def add_internal_links(content, all_keywords, current_keyword):
    """
    Add internal links to related articles.
    Simulates reading sitemap and finding related content.
    """
    # Other keywords become internal link targets
    other_keywords = [
        kw for kw in all_keywords 
        if kw != current_keyword
    ]
    
    links_added = 0
    max_links = 3
    
    for kw in other_keywords:
        if links_added >= max_links:
            break
            
        # Create URL slug
        slug = kw.lower().replace(" ", "-")
        url = f"https://keyshowrtheprime.wordpress.com/{slug}"
        
        # Find first occurrence of keyword in content
        # and wrap with markdown link
        if kw.lower() in content.lower() and links_added < max_links:
            # Case-insensitive replacement (first occurrence only)
            pattern = re.compile(re.escape(kw), re.IGNORECASE)
            replacement = f"[{kw}]({url})"
            new_content = pattern.sub(replacement, content, count=1)
            
            if new_content != content:
                content = new_content
                links_added += 1
    
    return content, links_added


# --- Get all keywords for internal linking ---
all_keywords = [a["keyword"] for a in articles]

# --- Main enrichment loop ---
enriched_articles = []

for article in articles:
    keyword = article["keyword"]
    content = article["content"]
    
    print(f"  📝 Enriching: '{keyword}'")
    
    # 1. Readability score
    score = calculate_readability_score(content)
    label = get_readability_label(score)
    needs_rewrite = score < 60
    
    print(f"     📊 Readability score: {score} — {label}")
    
    # 2. JSON-LD Schema
    article_schema, faq_schema, faq_pairs = build_json_ld_schema(article)
    print(f"     📋 Schema built — FAQ pairs found: {len(faq_pairs)}")
    
    # 3. Internal links
    enriched_content, links_added = add_internal_links(
        content, all_keywords, keyword
    )
    print(f"     🔗 Internal links added: {links_added}")
    
    # 4. Flag if needs rewrite
    if needs_rewrite:
        print(f"     ⚠️  Readability below 60 — flagged for rewrite")
    
    # Build enriched article object
    enriched = {
        "keyword": keyword,
        "generated_at": article["generated_at"],
        "enriched_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "word_count": article["word_count"],
        "model_used": article["model_used"],
        "status": "ready_to_publish",
        "readability": {
            "score": score,
            "label": label,
            "needs_rewrite": needs_rewrite
        },
        "seo": {
            "primary_keyword": keyword,
            "internal_links_added": links_added,
            "faq_pairs_found": len(faq_pairs),
            "schema_types": ["Article", "FAQPage"] if faq_schema else ["Article"]
        },
        "schema": {
            "article": article_schema,
            "faq": faq_schema
        },
        "content": enriched_content,
        "brief": article["brief"]
    }
    
    enriched_articles.append(enriched)
    print(f"     ✅ Enrichment complete\n")

# --- Save output ---
output = {
    "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "total_articles": len(enriched_articles),
    "ready_to_publish": len([a for a in enriched_articles if not a["readability"]["needs_rewrite"]]),
    "needs_rewrite": len([a for a in enriched_articles if a["readability"]["needs_rewrite"]]),
    "articles": enriched_articles
}

with open(output_path, "w") as f:
    json.dump(output, f, indent=2)

print(f"💾 Saved {len(enriched_articles)} enriched articles to: {output_path}")
print(f"\n✅ Phase 3B — Article Enrichment complete!")
print(f"   Ready to publish: {output['ready_to_publish']}")
print(f"   Needs rewrite:    {output['needs_rewrite']}")
print(f"\n   Next: Phase 4 — Publishing via WordPress REST API")