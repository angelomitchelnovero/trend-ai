"""
Experiment 5 — Daily digest generation
=========================================

Goal: feed Gemini 5-8 summarized stories from the day and see whether it
can generate a coherent, well-toned daily briefing worth showing on a
dashboard — before building scheduled digest generation into Phase 4.

This reuses the RSS fetch from Experiment 1 to get real headlines/
summaries for today, then asks Gemini to write a single digest.

Usage:
    pip install -r requirements.txt
    export GEMINI_API_KEY=your_key_here
    python experiments/05_digest_check.py
"""

import os
import re
import sys
from html import unescape

import feedparser
import requests

try:
    import google.generativeai as genai
except ImportError:
    print("Missing dependency: pip install google-generativeai")
    sys.exit(1)

REQUEST_TIMEOUT = 15
USER_AGENT = "trendai-by-aloe/0.1 (digest experiment)"
HTML_TAG_RE = re.compile(r"<[^>]+>")

FEEDS = {
    "Rappler": "https://www.rappler.com/feed/",
    "Inquirer": "https://newsinfo.inquirer.net/feed",
    "GMA News": "https://data.gmanetwork.com/gno/rss/news/feed.xml",
}
MAX_STORIES = 8

DIGEST_PROMPT = """You are writing a short daily "what's trending in the
Philippines" briefing for a news dashboard. Below are today's top story
headlines and summaries from multiple outlets. Write a single cohesive
briefing (150-250 words) that groups related stories, highlights what
matters most, and reads naturally rather than as a bullet dump. Keep a
neutral, informative tone — this is a news digest, not opinion content.

Stories:
{stories}

Daily briefing:"""


def strip_html(text: str) -> str:
    return unescape(HTML_TAG_RE.sub("", text or "")).strip()


def fetch_todays_stories(max_stories: int):
    stories = []
    for source, url in FEEDS.items():
        try:
            resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
        except requests.RequestException as e:
            print(f"  Skipping {source}: fetch failed ({e})")
            continue

        parsed = feedparser.parse(resp.content)
        for entry in parsed.entries[:3]:  # a few per outlet
            title = entry.get("title", "")
            summary = strip_html(entry.get("summary", ""))
            if title and summary:
                stories.append(f"[{source}] {title} — {summary[:200]}")
            if len(stories) >= max_stories:
                break
        if len(stories) >= max_stories:
            break
    return stories[:max_stories]


def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Set GEMINI_API_KEY in your environment first.")
        sys.exit(1)

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")

    print("Fetching today's stories across feeds...")
    stories = fetch_todays_stories(MAX_STORIES)

    if len(stories) < 3:
        print(f"Only found {len(stories)} usable stories — not enough for a")
        print("meaningful digest test. Check feed availability (see Experiment 1).")
        sys.exit(1)

    print(f"\nUsing {len(stories)} stories:")
    for s in stories:
        print(f"  - {s}")

    prompt = DIGEST_PROMPT.format(stories="\n".join(stories))

    print("\nGenerating digest...\n")
    try:
        response = model.generate_content(prompt)
    except Exception as e:
        print(f"Digest generation FAILED: {e}")
        sys.exit(1)

    print("=" * 60)
    print("DAILY DIGEST")
    print("=" * 60)
    print(response.text.strip())

    print("\n" + "=" * 60)
    print("Manually review: does this read like something worth putting on")
    print("a dashboard? Check tone, length, and whether it actually groups")
    print("related stories sensibly rather than just listing them.")


if __name__ == "__main__":
    main()
