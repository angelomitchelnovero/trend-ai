"""
Experiment 2 — AI summarization quality
=========================================

Goal: check whether Gemini (free tier) can produce good summaries of
real Philippine news articles — including Taglish / local-context
headlines — before we build auto-summarization into the pipeline.

This script takes 5 real articles (reuses the RSS fetch logic from
Experiment 1) and asks Gemini to summarize each one. You read the
output and judge: accuracy, tone, length, handling of local terms.

Usage:
    pip install -r requirements.txt
    export GEMINI_API_KEY=your_key_here
    python experiments/02_summarization_check.py
"""

import os
import sys
from html import unescape
import re

import feedparser
import requests

try:
    import google.generativeai as genai
except ImportError:
    print("Missing dependency: pip install google-generativeai")
    sys.exit(1)

REQUEST_TIMEOUT = 15
USER_AGENT = "trendai-by-aloe/0.1 (summarization experiment)"
HTML_TAG_RE = re.compile(r"<[^>]+>")

# Reuse one feed known to carry Taglish/local-context headlines.
FEED_URL = "https://www.rappler.com/feed/"
NUM_ARTICLES = 5

SUMMARY_PROMPT = """You are summarizing a Philippine news article for a daily
trending briefing. Write a concise 2-3 sentence summary in English, but keep
any Taglish terms, local place names, or local context in the original
article intact rather than translating them away. Be accurate — do not add
facts that aren't in the source text.

Title: {title}

Article text:
{body}

Summary:"""


def strip_html(text: str) -> str:
    return unescape(HTML_TAG_RE.sub("", text or "")).strip()


def fetch_sample_articles(url: str, n: int):
    resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    parsed = feedparser.parse(resp.content)

    articles = []
    for entry in parsed.entries[:n]:
        title = entry.get("title", "")
        body = strip_html(entry.get("summary", "")) or strip_html(entry.get("description", ""))
        articles.append({"title": title, "body": body})
    return articles


def summarize(model, title: str, body: str) -> str:
    prompt = SUMMARY_PROMPT.format(title=title, body=body)
    response = model.generate_content(prompt)
    return response.text.strip()


def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Set GEMINI_API_KEY in your environment first.")
        sys.exit(1)

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")

    print(f"Fetching {NUM_ARTICLES} sample articles from {FEED_URL} ...")
    articles = fetch_sample_articles(FEED_URL, NUM_ARTICLES)

    if not articles:
        print("No articles fetched — check the feed URL / network.")
        sys.exit(1)

    for i, article in enumerate(articles, 1):
        print(f"\n=== Article {i} ===")
        print(f"Title:    {article['title']}")
        print(f"Original: {article['body'][:200]}{'...' if len(article['body']) > 200 else ''}")

        if not article["body"]:
            print("Summary:  SKIPPED (empty body — RSS summary field was empty)")
            continue

        try:
            summary = summarize(model, article["title"], article["body"])
        except Exception as e:
            print(f"Summary:  FAILED ({e})")
            continue

        print(f"Summary:  {summary}")

    print("\n" + "=" * 60)
    print("Manually review above for: accuracy, tone, length, and whether")
    print("Taglish/local terms were preserved sensibly rather than mistranslated.")


if __name__ == "__main__":
    main()
