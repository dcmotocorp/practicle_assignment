from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator

from app.models import ArticleStatus


class ArticleCreate(BaseModel):
    company_name: str = Field(min_length=1, max_length=200)
    title: str = Field(min_length=1, max_length=500)
    url: HttpUrl
    content: str = Field(min_length=1)

    @field_validator("company_name", "title", "content")
    @classmethod
    def reject_blank_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be blank")
        return value


class ArticleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_name: str
    title: str
    url: str
    content: str
    status: ArticleStatus
    category: str | None
    summary: str | None
    created_at: datetime


class Pagination(BaseModel):
    page: int
    page_size: int
    total_items: int
    total_pages: int


class ArticleListResponse(BaseModel):
    items: list[ArticleResponse]
    pagination: Pagination


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    detail: ErrorDetail
