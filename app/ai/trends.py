"""Fact-grounded English briefs for global AI and Tech trend cards."""

import os
import re
import time
from html import unescape

import google.generativeai as genai
import requests
from sqlalchemy.orm import Session

from app.ai.summarize import SECONDS_BETWEEN_CALLS
from app.models.schema import TrendingTerm

META_DESCRIPTION = re.compile(
    r'<meta[^>]+(?:name|property)=["\'](?:description|og:description)["\'][^>]+content=["\']([^"\']+)',
    re.IGNORECASE,
)
_model = None


def _get_model():
    global _model
    if _model is None:
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])
        _model = genai.GenerativeModel("gemini-2.5-flash")
    return _model


def _source_description(url: str | None) -> str:
    if not url:
        return ""
    try:
        response = requests.get(url, headers={"User-Agent": "trendai-by-aloe/0.1"}, timeout=15)
        match = META_DESCRIPTION.search(response.text)
        return unescape(match.group(1)).strip() if match else ""
    except requests.RequestException:
        return ""


def _brief(title: str, description: str) -> tuple[str, str]:
    prompt = f"""Turn this news metadata into an English trend card.
Use only facts present below. Do not speculate, add background facts, or make claims from general knowledge.
If the metadata does not establish a fact, say so plainly.

Return exactly two lines:
TITLE: an English headline of at most 16 words
SUMMARY: two short English sentences explaining what happened and why it may matter.

Original title: {title}
Publisher description: {description or 'No publisher description available.'}"""
    response = _get_model().generate_content(prompt).text.strip()
    title_line, _, summary_line = response.partition("\n")
    english_title = title_line.removeprefix("TITLE:").strip() or title
    summary = summary_line.removeprefix("SUMMARY:").strip()
    if not summary:
        summary = "The publisher is reporting this development. Open the source for verified details and updates."
    return english_title, summary


def enrich_global_trends(db: Session, limit: int = 4) -> int:
    """Translate and summarize unprocessed global trend records, paced for Gemini's free tier."""
    terms = (db.query(TrendingTerm)
        .filter(TrendingTerm.scope == "global", TrendingTerm.summary.is_(None))
        .order_by(TrendingTerm.captured_at.desc())
        .limit(limit).all())
    for index, term in enumerate(terms):
        term.title, term.summary = _brief(term.term, _source_description(term.url))
        db.commit()
        if index < len(terms) - 1:
            time.sleep(SECONDS_BETWEEN_CALLS)
    return len(terms)
