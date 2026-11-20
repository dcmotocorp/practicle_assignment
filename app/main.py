import os
from collections.abc import Callable
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI

from app.api import router
from app.database import Database
from app.task import process_article_task


def create_app(
    database_url: str | None = None,
    task_dispatcher: Callable[[int, Any], Any] | None = None,
) -> FastAPI:
    database = Database(database_url or os.getenv("DATABASE_URL", "sqlite:///./articles.db"))

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        database.create_tables()
        yield
        database.dispose()

    application = FastAPI(
        title="Company News Article API",
        description=(
            "Store company news and process classification and summarization "
            "asynchronously using deterministic Python rules."
        ),
        version="1.0.0",
        lifespan=lifespan,
    )
    application.state.database = database
    application.state.dispatch_article = task_dispatcher or (
        lambda article_id, _session_factory: process_article_task.delay(article_id)
    )
    application.include_router(router)

    @application.get("/health", tags=["System"], summary="Service health check")
    def health() -> dict[str, str]:
        return {"status": "healthy"}

    return application


app = create_app()
