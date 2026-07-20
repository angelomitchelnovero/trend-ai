"""
Experiment 1 — RSS data quality check
======================================

Goal: figure out whether Philippine news RSS feeds are clean and
consistent enough to build a real ingestion pipeline on top of.

This is a throwaway script. No DB, no API, no UI — just pull raw RSS
from a few outlets, print what we get, and flag anything that looks
broken so we can decide keep / tweak / cut before building Phase 1.

Usage:
    pip install feedparser requests
    python experiments/01_rss_quality_check.py
"""

import re
import sys
from dataclasses import dataclass, field
from html import unescape

import feedparser
import requests

# ---------------------------------------------------------------------------
# Feeds to check. Add/remove outlets here as you find working feed URLs —
# these are common candidates but outlets sometimes change/retire feed paths,
# so verify each one still resolves before trusting the results.
# ---------------------------------------------------------------------------
FEEDS = {
    "Rappler": "https://www.rappler.com/feed/",
    "Inquirer": "https://newsinfo.inquirer.net/feed",
    "GMA News": "https://data.gmanetwork.com/gno/rss/news/feed.xml",
}

REQUEST_TIMEOUT = 15
USER_AGENT = "trendai-by-aloe/0.1 (RSS quality experiment)"

# Fields we actually need downstream: title, summary, timestamp, source.
REQUIRED_FIELDS = ["title", "summary", "published"]


@dataclass
class FeedIssues:
    source: str
    fetch_error: str | None = None
    entry_count: int = 0
    missing_fields: dict = field(default_factory=dict)   # field -> count
    encoding_flags: list = field(default_factory=list)   # entries w/ odd chars
    empty_summaries: int = 0
    duplicate_titles: int = 0


HTML_TAG_RE = re.compile(r"<[^>]+>")
# Common signs of a mangled/undecoded encoding (mojibake, leftover entities)
SUSPICIOUS_CHARS_RE = re.compile(r"(â€|Ã©|Ã¢|&#\d+;|&amp;amp;|\uFFFD)")


def fetch_feed(name: str, url: str):
    """Fetch and parse a single RSS feed, returning (feedparser result, error)."""
    try:
        resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
    except requests.RequestException as e:
        return None, f"HTTP fetch failed: {e}"

    parsed = feedparser.parse(resp.content)

    # feedparser sets `bozo` when it hit a parse error but still tried its best
    if parsed.bozo and not parsed.entries:
        return None, f"Feed parse failed: {parsed.bozo_exception}"

    return parsed, None


def check_entry_field(entry, field_name: str) -> bool:
    """Return True if the field is present and non-empty."""
    value = entry.get(field_name)
    return bool(value and str(value).strip())


def strip_html(text: str) -> str:
    return unescape(HTML_TAG_RE.sub("", text or "")).strip()


def analyze_feed(name: str, parsed) -> FeedIssues:
    issues = FeedIssues(source=name)
    issues.entry_count = len(parsed.entries)

    seen_titles = set()

    for entry in parsed.entries:
        for f in REQUIRED_FIELDS:
            if not check_entry_field(entry, f):
                issues.missing_fields[f] = issues.missing_fields.get(f, 0) + 1

        title = entry.get("title", "")
        summary_raw = entry.get("summary", "")
        summary_clean = strip_html(summary_raw)

        if not summary_clean:
            issues.empty_summaries += 1

        combined = f"{title} {summary_raw}"
        if SUSPICIOUS_CHARS_RE.search(combined):
            issues.encoding_flags.append(title[:80])

        if title in seen_titles:
            issues.duplicate_titles += 1
        seen_titles.add(title)

    return issues


def print_sample_entries(name: str, parsed, n: int = 5):
    print(f"\n--- {name}: sample of {min(n, len(parsed.entries))} entries ---")
    for entry in parsed.entries[:n]:
        title = entry.get("title", "<MISSING TITLE>")
        summary = strip_html(entry.get("summary", ""))
        summary_preview = (summary[:140] + "...") if len(summary) > 140 else summary
        published = entry.get("published", "<MISSING TIMESTAMP>")

        print(f"  Title:     {title}")
        print(f"  Published: {published}")
        print(f"  Summary:   {summary_preview or '<EMPTY>'}")
        print()


def print_issue_report(issues: FeedIssues):
    print(f"\n=== {issues.source}: quality report ===")

    if issues.fetch_error:
        print(f"  FAILED TO FETCH: {issues.fetch_error}")
        return

    print(f"  Entries fetched:     {issues.entry_count}")

    if issues.missing_fields:
        for f, count in issues.missing_fields.items():
            print(f"  Missing '{f}':        {count} / {issues.entry_count}")
    else:
        print("  Missing fields:      none")

    print(f"  Empty summaries:     {issues.empty_summaries}")
    print(f"  Duplicate titles:    {issues.duplicate_titles}")

    if issues.encoding_flags:
        print(f"  Possible encoding issues in {len(issues.encoding_flags)} entries, e.g.:")
        for t in issues.encoding_flags[:3]:
            print(f"    - {t}")
    else:
        print("  Encoding issues:     none detected")


def main():
    all_issues = []

    for name, url in FEEDS.items():
        print(f"Fetching {name} ({url}) ...")
        parsed, error = fetch_feed(name, url)

        if error:
            issues = FeedIssues(source=name, fetch_error=error)
            all_issues.append(issues)
            print(f"  -> ERROR: {error}")
            continue

        print_sample_entries(name, parsed)
        issues = analyze_feed(name, parsed)
        all_issues.append(issues)

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for issues in all_issues:
        print_issue_report(issues)

    # ------------------------------------------------------------------
    # Exit-criteria hint for Phase 0: this experiment "passes" if every
    # feed fetched successfully, missing-field counts are near zero, and
    # no meaningful encoding corruption was found. That's a judgment
    # call for you to make from the report above — this script just
    # surfaces the evidence.
    # ------------------------------------------------------------------
    failed = [i for i in all_issues if i.fetch_error]
    if failed:
        print(f"\n{len(failed)} feed(s) failed to fetch — check URLs/network before judging quality.")
        sys.exit(1)


if __name__ == "__main__":
    main()
