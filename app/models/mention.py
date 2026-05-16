import uuid
from datetime import datetime, timezone
from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.enums import MentionContentType, SourceType


class Mention(Base):
    __tablename__ = "mentions"
    __table_args__ = (
        UniqueConstraint(
            "tracked_keyword_id",
            "source_type",
            "external_id",
            name="uq_mentions_keyword_source_external_id",
        ),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    tracked_keyword_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("tracked_keywords.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    source_config_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("keyword_source_configs.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    ingestion_run_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("ingestion_runs.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    source_type: Mapped[SourceType] = mapped_column(
        Enum(SourceType, name="source_type_enum"),
        nullable=False,
        index=True,
    )
    content_type: Mapped[MentionContentType] = mapped_column(
        Enum(MentionContentType, name="mention_content_type_enum"),
        nullable=False,
    )
    external_id: Mapped[str] = mapped_column(String(255), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    body_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    matched_text_snippet: Mapped[str | None] = mapped_column(Text, nullable=True)
    url: Mapped[str] = mapped_column(String(1000), nullable=False)
    author_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    author_external_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    community_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    language: Mapped[str | None] = mapped_column(String(16), nullable=True)
    score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    comment_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    view_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    like_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    discovered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True
    )
    raw_payload: Mapped[dict] = mapped_column(JSONB, nullable=False)

    tracked_keyword: Mapped["TrackedKeyword"] = relationship(back_populates="mentions")
    source_config: Mapped["KeywordSourceConfig | None"] = relationship(back_populates="mentions")
    ingestion_run: Mapped["IngestionRun | None"] = relationship(back_populates="mentions")

    def __repr__(self):
        return (
            f"<Mention id={self.id} source_type={self.source_type} "
            f"external_id={self.external_id}>"
        )
