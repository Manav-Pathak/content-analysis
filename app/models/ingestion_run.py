import uuid
from datetime import datetime, timezone
from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.enums import IngestionStatus, SourceType


class IngestionRun(Base):
    __tablename__ = "ingestion_runs"

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
    source_type: Mapped[SourceType] = mapped_column(
        Enum(SourceType, name="source_type_enum"),
        nullable=False,
        index=True,
    )
    status: Mapped[IngestionStatus] = mapped_column(
        Enum(IngestionStatus, name="ingestion_status_enum"),
        default=IngestionStatus.PENDING,
        nullable=False,
        index=True,
    )
    scheduled_for: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cursor_before: Mapped[str | None] = mapped_column(String(255), nullable=True)
    cursor_after: Mapped[str | None] = mapped_column(String(255), nullable=True)
    request_count: Mapped[int] = mapped_column(Integer, default=0)
    items_seen: Mapped[int] = mapped_column(Integer, default=0)
    items_inserted: Mapped[int] = mapped_column(Integer, default=0)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    response_meta: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True
    )

    tracked_keyword: Mapped["TrackedKeyword"] = relationship(back_populates="ingestion_runs")
    source_config: Mapped["KeywordSourceConfig | None"] = relationship(back_populates="ingestion_runs")
    mentions: Mapped[list["Mention"]] = relationship(back_populates="ingestion_run")

    def __repr__(self):
        return (
            f"<IngestionRun id={self.id} source_type={self.source_type} "
            f"status={self.status}>"
        )
