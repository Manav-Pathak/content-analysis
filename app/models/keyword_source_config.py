import uuid
from datetime import datetime, timezone
from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.enums import SourceType


class KeywordSourceConfig(Base):
    __tablename__ = "keyword_source_configs"
    __table_args__ = (
        UniqueConstraint(
            "tracked_keyword_id",
            "source_type",
            name="uq_keyword_source_configs_keyword_source_type",
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
    source_type: Mapped[SourceType] = mapped_column(
        Enum(SourceType, name="source_type_enum"),
        nullable=False,
        index=True,
    )
    is_enabled: Mapped[bool] = mapped_column(default=True, index=True)
    query_override: Mapped[str | None] = mapped_column(String(255), nullable=True)
    fetch_interval_minutes: Mapped[int] = mapped_column(default=30)
    last_checked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_cursor: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    tracked_keyword: Mapped["TrackedKeyword"] = relationship(back_populates="source_configs")
    mentions: Mapped[list["Mention"]] = relationship(back_populates="source_config")
    ingestion_runs: Mapped[list["IngestionRun"]] = relationship(back_populates="source_config")

    def __repr__(self):
        return (
            f"<KeywordSourceConfig keyword_id={self.tracked_keyword_id} "
            f"source_type={self.source_type}>"
        )
