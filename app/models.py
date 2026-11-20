from datetime import datetime, timezone
from enum import StrEnum

from sqlalchemy import CheckConstraint, DateTime, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ArticleStatus(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Article(Base):
    __tablename__ = "articles"
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'processing', 'completed', 'failed')",
            name="ck_articles_status",
        ),
        Index("ix_articles_created_at_id", "created_at", "id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    company_name: Mapped[str] = mapped_column(String(200), index=True)
    title: Mapped[str] = mapped_column(String(500))
    url: Mapped[str] = mapped_column(String(2048), unique=True, index=True)
    content: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(
        String(20), default=ArticleStatus.PENDING.value, index=True
    )
    category: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True
    )
