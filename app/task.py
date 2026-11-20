import os

from celery import Celery

from app.database import Database
from app.services.processor import process_article

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./articles.db")

celery_app = Celery("company_news", broker=REDIS_URL, backend=REDIS_URL)
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    broker_connection_retry_on_startup=True,
    timezone="UTC",
)

# Support both `app.task:app` and the more explicit `app.task:celery_app`.
app = celery_app


@celery_app.task(
    bind=True,
    name="articles.process_article",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def process_article_task(self, article_id: int) -> None:
    """Run processing in the worker; only the article ID crosses Redis."""
    database = Database(DATABASE_URL)
    try:
        process_article(article_id, database.session_factory)
    finally:
        database.dispose()
