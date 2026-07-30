"""Lightweight, shared classifier for article and trend-card categories."""

import re

# Specific global product categories come first, followed by Philippine-news
# categories. Returning None is preferable to confidently guessing wrong.
CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "AI": [
        "artificial intelligence", "openai", "chatgpt", "gemini", "anthropic", "claude",
        "large language model", "generative ai", "machine learning", "deepmind", "copilot",
        "grok", "ai model", "model release",
    ],
    "Tech": [
        "technology", "tech", "software", "semiconductor", "chip", "nvidia", "amd",
        "microsoft", "google", "apple", "meta", "startup", "cybersecurity", "cloud",
        "robotics", "quantum", "iphone", "android", "data center",
    ],
    "Weather/Disaster": [
        "typhoon", "bagyo", "storm", "flood", "baha", "earthquake", "lindol", "landslide",
        "signal no", "pagasa", "evacuat", "eruption", "volcano", "rainfall", "habagat",
    ],
    "Politics": [
        "senate", "congress", "president", "duterte", "marcos", "impeachment", "election",
        "comelec", "malacanang", "senator", "vice president", "politic", "government", "dilg", "ombudsman",
    ],
    "Finance": [
        "peso", "stock", "inflation", "gdp", "bsp", "market", "economy", "bank", "fuel price",
        "gasoline", "oil price", "tax", "business", "trade", "investment", "interest rate",
    ],
    "Entertainment": [
        "actor", "actress", "celebrity", "concert", "album", "movie", "film", "kapamilya", "kapuso",
        "showbiz", "artista", "abs-cbn", "gma network", "singer", "netflix series",
    ],
    "Sports": [
        "pba", "uaap", "ncaa", "basketball", "volleyball", "boxing", "fifa", "world cup", "olympics",
        "sea games", "nba", "football", "sports", "athlete", "tournament",
    ],
    "Local": [
        "mmda", "traffic", "dpwh", "road", "lrt", "mrt", "manila", "quezon city", "cebu", "davao",
        "barangay", "local government", "lgu",
    ],
}

_COMPILED = {
    category: [re.compile(re.escape(keyword), re.IGNORECASE) for keyword in keywords]
    for category, keywords in CATEGORY_KEYWORDS.items()
}


def classify(text: str) -> str | None:
    """Return a product category, or None for an uncertain match."""
    if not text:
        return None
    for category, patterns in _COMPILED.items():
        if any(pattern.search(text) for pattern in patterns):
            return category
    return None
