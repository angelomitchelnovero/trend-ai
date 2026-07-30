"""Technology-only question answering with current-news sources."""

import re
from urllib.parse import quote_plus

import feedparser
import requests
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.ai.digest import _get_model
from app.ingestion.rss import strip_html

router = APIRouter(prefix="/ask", tags=["ask trend.ai"])
GOOGLE_NEWS_RSS = "https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
TECHNOLOGY_TERMS = re.compile(r"\b(ai|artificial intelligence|machine learning|openai|chatgpt|anthropic|gemini|apple|macbook|iphone|ipad|android|google|microsoft|windows|linux|software|hardware|technology|tech|computer|laptop|phone|chip|semiconductor|nvidia|amd|intel|robot|cyber|security|cloud|internet|app|startup|tesla|electric vehicle|ev)\b", re.IGNORECASE)


class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=500)


def _current_technology_sources(question: str) -> list[dict[str, str]]:
    response = requests.get(GOOGLE_NEWS_RSS.format(query=quote_plus(question)), headers={"User-Agent": "trendai-by-aloe/0.1"}, timeout=12)
    response.raise_for_status()
    sources = []
    for entry in feedparser.parse(response.content).entries[:6]:
        title, url = strip_html(entry.get("title", "")), entry.get("link", "")
        if title and url:
            sources.append({"title": title, "url": url, "summary": strip_html(entry.get("summary", ""))})
    return sources


@router.post("")
def ask_trend_ai(payload: AskRequest):
    question = payload.question.strip()
    if not TECHNOLOGY_TERMS.search(question):
        return {"answer": "Trend.ai focuses on AI and technology. I can help with current tech products, companies, software, chips, cybersecurity, and AI—but not general politics or news.", "sources": []}
    try:
        sources = _current_technology_sources(question)
    except requests.RequestException as exc:
        raise HTTPException(status_code=503, detail="Trend.ai could not reach current technology news. Please try again shortly.") from exc
    if not sources:
        return {"answer": "I could not find recent technology reporting for that question. Try naming the product, company, or technology you mean.", "sources": []}

    briefs = "\n\n".join(f"SOURCE {index}: {source['title']}\nBRIEF: {source['summary'] or 'No summary provided.'}\nURL: {source['url']}" for index, source in enumerate(sources, 1))
    prompt = f"""You are Trend.ai, an assistant exclusively for AI and technology.
Answer the user's technology question using only the recent reporting below. Be direct and concise. For questions using words such as 'latest' or 'today', explain that the answer reflects these current search results. Never add unsupported facts. Cite supporting source numbers in square brackets.

Question: {question}

Recent technology reporting:
{briefs}"""
    try:
        answer = _get_model().generate_content(prompt).text.strip()
    except Exception:
        # Current reporting remains useful even if the optional answer model is unavailable.
        answer = "Here is the latest technology reporting I found for that question:\n" + "\n".join(
            f"- {source['title']} [{index}]" for index, source in enumerate(sources[:3], 1)
        )
    return {"answer": answer, "sources": [{"number": index, "title": source["title"], "url": source["url"]} for index, source in enumerate(sources, 1)]}
