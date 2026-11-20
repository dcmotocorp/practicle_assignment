import re

CATEGORY_KEYWORDS: dict[str, tuple[str, ...]] = {
    "automotive": (
        "automotive", "automobile", "electric vehicle", "vehicle", "vehicles",
        "car", "cars", "ev", "battery", "charging",
    ),
    "finance": (
        "bank", "banking", "loan", "investment", "interest rate", "insurance",
        "financial",
    ),
    "technology": (
        "software", "cloud", "cybersecurity", "chip", "semiconductor",
        "data center", "technology",
    ),
    "energy": ("solar", "wind", "oil", "gas", "renewable", "power", "energy"),
    "healthcare": (
        "hospital", "medicine", "pharmaceutical", "drug", "healthcare",
    ),
    "retail": ("store", "ecommerce", "consumer", "shopping", "retail"),
}


def _normalize(text: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", text.lower()))


def _contains_phrase(text: str, phrase: str) -> bool:
    return re.search(rf"\b{re.escape(phrase)}\b", text) is not None


def classify_article(title: str, content: str) -> str:
    """Return the highest-scoring category using fixed keyword rules."""
    normalized_title = _normalize(title)
    normalized_content = _normalize(content)
    scores = {
        category: sum(
            (3 if _contains_phrase(normalized_title, keyword) else 0)
            + (1 if _contains_phrase(normalized_content, keyword) else 0)
            for keyword in keywords
        )
        for category, keywords in CATEGORY_KEYWORDS.items()
    }
    best_category = max(scores, key=scores.get)
    return best_category if scores[best_category] > 0 else "other"
