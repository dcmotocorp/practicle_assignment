import re
from collections import Counter

STOP_WORDS = frozenset(
    "a an and are as at be been by for from has have he in is it its of on or that "
    "the their they this to was were will with company".split()
)


def _sentences(content: str) -> list[str]:
    normalized = re.sub(r"\s+", " ", content).strip()
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+", normalized) if part.strip()]


def _words(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def summarize_article(content: str, max_sentences: int = 3, max_characters: int = 400) -> str:
    """Create a deterministic extractive summary from the original sentences."""
    sentences = _sentences(content)
    if not sentences:
        return ""
    if len(sentences) <= max_sentences and len(" ".join(sentences)) <= max_characters:
        return " ".join(sentences)

    meaningful_words = [word for word in _words(content) if word not in STOP_WORDS]
    frequencies = Counter(meaningful_words)
    ranked: list[tuple[float, int]] = []
    for index, sentence in enumerate(sentences):
        words = [word for word in _words(sentence) if word not in STOP_WORDS]
        score = sum(frequencies[word] for word in words) / max(len(words), 1)
        if index == 0:
            score += 1.0
        ranked.append((score, index))

    target_count = min(max_sentences, max(1, round(len(sentences) * 0.35)))
    chosen = sorted(index for _, index in sorted(ranked, reverse=True)[:target_count])

    result: list[str] = []
    for index in chosen:
        candidate = " ".join([*result, sentences[index]])
        if len(candidate) <= max_characters:
            result.append(sentences[index])
    if result:
        return " ".join(result)
    return sentences[chosen[0]][:max_characters].rstrip()
