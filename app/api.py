from datetime import datetime
from math import ceil
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Request, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Article, ArticleStatus
from app.schemas import ArticleCreate, ArticleListResponse, ArticleResponse, ErrorResponse, Pagination
from app.services.processor import process_article

router = APIRouter(prefix="/articles", tags=["Articles"])


def get_db(request: Request):
    yield from request.app.state.database.session()


DbSession = Annotated[Session, Depends(get_db)]


def conflict(message: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail={"code": "ARTICLE_URL_ALREADY_EXISTS", "message": message},
    )


@router.post(
    "",
    response_model=ArticleResponse,
    status_code=status.HTTP_202_ACCEPTED,
    responses={409: {"model": ErrorResponse, "description": "Article URL already exists"}},
    summary="Store and asynchronously process a news article",
)
def create_article(
    payload: ArticleCreate,
    background_tasks: BackgroundTasks,
    request: Request,
    db: DbSession,
) -> Article:
    normalized_url = str(payload.url)
    if db.scalar(select(Article.id).where(Article.url == normalized_url)) is not None:
        raise conflict("An article with this URL already exists.")

    article = Article(
        company_name=payload.company_name,
        title=payload.title,
        url=normalized_url,
        content=payload.content,
        status=ArticleStatus.PENDING.value,
    )
    db.add(article)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise conflict("An article with this URL already exists.") from exc
    db.refresh(article)
    background_tasks.add_task(
        process_article, article.id, request.app.state.database.session_factory
    )
    return article


@router.get("/{article_id}", response_model=ArticleResponse, summary="Get an article by ID")
def get_article(article_id: int, db: DbSession) -> Article:
    article = db.get(Article, article_id)
    if article is None:
        raise HTTPException(status_code=404, detail={"code": "ARTICLE_NOT_FOUND", "message": "Article not found."})
    return article


@router.get("", response_model=ArticleListResponse, summary="List and filter articles")
def list_articles(
    db: DbSession,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    article_status: Annotated[ArticleStatus | None, Query(alias="status")] = None,
    category: str | None = None,
    company_name: str | None = None,
    created_from: datetime | None = None,
    created_to: datetime | None = None,
) -> ArticleListResponse:
    filters = []
    if article_status is not None:
        filters.append(Article.status == article_status.value)
    if category:
        filters.append(Article.category == category.lower().strip())
    if company_name:
        filters.append(Article.company_name.ilike(f"%{company_name.strip()}%"))
    if created_from:
        filters.append(Article.created_at >= created_from)
    if created_to:
        filters.append(Article.created_at <= created_to)

    total = db.scalar(select(func.count(Article.id)).where(*filters)) or 0
    articles = db.scalars(
        select(Article)
        .where(*filters)
        .order_by(Article.created_at.desc(), Article.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return ArticleListResponse(
        items=[ArticleResponse.model_validate(article) for article in articles],
        pagination=Pagination(
            page=page,
            page_size=page_size,
            total_items=total,
            total_pages=ceil(total / page_size),
        ),
    )
