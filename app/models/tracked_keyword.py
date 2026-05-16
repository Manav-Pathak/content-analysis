import uuid
from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class TrackedKeyword(Base):
    __tablename__ = "tracked_keywords"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "normalized_keyword",
            name="uq_tracked_keywords_user_normalized_keyword",
        ),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    keyword: Mapped[str] = mapped_column(String(255), nullable=False)
    normalized_keyword: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user: Mapped["User"] = relationship(back_populates="tracked_keywords")
    source_configs: Mapped[list["KeywordSourceConfig"]] = relationship(
        back_populates="tracked_keyword",
        cascade="all, delete-orphan",
    )
    mentions: Mapped[list["Mention"]] = relationship(
        back_populates="tracked_keyword",
        cascade="all, delete-orphan",
    )
    ingestion_runs: Mapped[list["IngestionRun"]] = relationship(
        back_populates="tracked_keyword",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<TrackedKeyword id={self.id} keyword={self.keyword}>"
