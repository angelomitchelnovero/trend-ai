"""
Experiment 4 — Trending signal check
=======================================

Goal: pull Reddit r/Philippines hot posts + Google Trends PH side by
side and eyeball whether this is genuinely useful trending signal, or
just noise not worth building a pipeline stage for.

Both sources are OPTIONAL and skip gracefully if unconfigured:

- Reddit requires manual approval for new API access (Responsible
  Builder Policy). Request it here:
  https://support.reddithelp.com/hc/en-us/requests/new?ticket_form_id=14868593862164

- Google Trends uses SerpApi's Trending Now endpoint instead of the
  `pytrends` library — pytrends' GitHub repo was archived by its own
  maintainers in April 2025 and its calls now 404 (confirmed locally).
  Free tier: 100 searches/month at https://serpapi.com/users/sign_up

Usage:
    pip install -r requirements.txt

    # Google Trends only:
    export SERPAPI_KEY=...
    python experiments/04_trending_signal_check.py

    # With Reddit too, once you have approved credentials:
    export REDDIT_CLIENT_ID=...
    export REDDIT_CLIENT_SECRET=...
    export REDDIT_USER_AGENT=trendai-by-aloe/0.1
    python experiments/04_trending_signal_check.py
"""

import os
import sys

import requests

SUBREDDIT = "Philippines"
NUM_POSTS = 15

SERPAPI_TRENDING_URL = "https://serpapi.com/search.json"
SERPAPI_GEO = "PH"
REQUEST_TIMEOUT = 15

REDDIT_AVAILABLE = True
try:
    import praw
except ImportError:
    REDDIT_AVAILABLE = False


def reddit_configured() -> bool:
    return bool(os.environ.get("REDDIT_CLIENT_ID") and os.environ.get("REDDIT_CLIENT_SECRET"))


def serpapi_configured() -> bool:
    return bool(os.environ.get("SERPAPI_KEY"))


def fetch_reddit_hot():
    """Returns a list of posts, or None if Reddit isn't available/configured."""
    if not REDDIT_AVAILABLE:
        print("praw not installed — skipping Reddit (pip install praw to enable).")
        return None

    if not reddit_configured():
        print("REDDIT_CLIENT_ID / REDDIT_CLIENT_SECRET not set — skipping Reddit.")
        print("Reddit now requires manual approval for new API access (Responsible")
        print("Builder Policy). Request it here:")
        print("  https://support.reddithelp.com/hc/en-us/requests/new?ticket_form_id=14868593862164")
        print("Once approved, set the env vars and re-run — no code changes needed.")
        return None

    client_id = os.environ["REDDIT_CLIENT_ID"]
    client_secret = os.environ["REDDIT_CLIENT_SECRET"]
    user_agent = os.environ.get("REDDIT_USER_AGENT", "trendai-by-aloe/0.1")

    try:
        reddit = praw.Reddit(client_id=client_id, client_secret=client_secret, user_agent=user_agent)
        posts = []
        for submission in reddit.subreddit(SUBREDDIT).hot(limit=NUM_POSTS):
            if submission.stickied:
                continue
            posts.append({
                "title": submission.title,
                "score": submission.score,
                "num_comments": submission.num_comments,
                "flair": submission.link_flair_text,
                "url": submission.url,
            })
        return posts
    except Exception as e:
        print(f"Reddit fetch failed: {e}")
        print("If this is a 401/403, your app may still be pending Reddit's approval queue.")
        return None


def fetch_google_trends_ph():
    """Returns a list of trending search dicts, or None if unconfigured/failed."""
    if not serpapi_configured():
        print("SERPAPI_KEY not set — skipping Google Trends.")
        print("Free tier (100 searches/month): https://serpapi.com/users/sign_up")
        return None

    try:
        resp = requests.get(
            SERPAPI_TRENDING_URL,
            params={
                "engine": "google_trends_trending_now",
                "geo": SERPAPI_GEO,
                "api_key": os.environ["SERPAPI_KEY"],
            },
            timeout=REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        print(f"SerpApi Google Trends fetch failed: {e}")
        return None

    return data.get("trending_searches", [])


def main():
    print(f"=== Reddit r/{SUBREDDIT} — top {NUM_POSTS} hot posts ===\n")
    reddit_posts = fetch_reddit_hot()
    if reddit_posts is None:
        print("  (skipped)")
    else:
        for p in reddit_posts:
            flair = f" [{p['flair']}]" if p["flair"] else ""
            print(f"  ({p['score']:>5} pts, {p['num_comments']:>4} comments){flair} {p['title']}")

    print("\n=== Google Trends PH — trending searches right now (via SerpApi) ===\n")
    trends = fetch_google_trends_ph()
    if trends is None:
        print("  (skipped)")
    else:
        for i, item in enumerate(trends, 1):
            vol = item.get("search_volume")
            vol_str = f" (~{vol:,} searches)" if vol else ""
            print(f"  {i}. {item.get('query')}{vol_str}")

    print("\n" + "=" * 60)
    print("Manually assess:")
    if reddit_posts is not None:
        print("- Do Reddit hot posts overlap with real current events, or is it")
        print("  mostly memes/off-topic chatter for this subreddit?")
    if trends is not None:
        print("- Do Google Trends terms look like genuine news-adjacent signal,")
        print("  or mostly celebrity gossip / unrelated search spikes?")
    if reddit_posts is not None and trends is not None:
        print("- Is there overlap between the two sources, or are they telling")
        print("  completely different stories?")
    if reddit_posts is None and trends is None:
        print("- Both sources are unconfigured right now — set REDDIT_* and/or")
        print("  SERPAPI_KEY to get a real read on this experiment.")


if __name__ == "__main__":
    main()
