from app.services.classifier import classify_article
from app.services.summarizer import summarize_article


def test_classifies_ev_article_as_automotive() -> None:
    category = classify_article(
        "Company announces investment in the new EV plan",
        "The company will spend 2 billion dollars in this sector.",
    )
    assert category == "automotive"


def test_title_has_more_classification_weight_than_content() -> None:
    assert classify_article("New cloud software launched", "The bank offers a loan.") == "technology"


def test_unknown_article_uses_other_category() -> None:
    assert classify_article("Quarterly announcement", "Leadership met on Tuesday.") == "other"


def test_summary_is_shorter_and_preserves_original_sentences() -> None:
    content = (
        "Example Motors announced a large electric vehicle investment. "
        "The business will spend two billion dollars on battery production. "
        "Construction starts next year. Thousands of jobs may be created. "
        "The first vehicles are expected in 2029. Local officials welcomed the plan."
    )
    summary = summarize_article(content, max_sentences=2)
    assert len(summary) < len(content)
    assert summary.count(".") <= 2
    assert all(sentence in content for sentence in summary.split(". "))


def test_short_content_is_returned_unchanged() -> None:
    content = "The company opened a new store. It will employ 50 people."
    assert summarize_article(content) == content
