import logging
from collections.abc import Callable

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Article, ArticleStatus
from app.services.classifier import classify_article
from app.services.summarizer import summarize_article

logger = logging.getLogger(__name__)


def process_article(article_id: int, session_factory: Callable[[], Session]) -> None:
    """Classify and summarize an article using an independent database session."""
    with session_factory() as db:
        article = db.scalar(select(Article).where(Article.id == article_id))
        if article is None or article.status not in {
            ArticleStatus.PENDING.value,
            ArticleStatus.PROCESSING.value,
        }:
            return
        try:
            article.status = ArticleStatus.PROCESSING.value
            db.commit()
            article.category = classify_article(article.title, article.content)
            article.summary = summarize_article(article.content)
            article.status = ArticleStatus.COMPLETED.value
            db.commit()
        except Exception:
            db.rollback()
            failed_article = db.get(Article, article_id)
            if failed_article is not None:
                failed_article.status = ArticleStatus.FAILED.value
                db.commit()
            logger.exception("Article %s processing failed", article_id)
