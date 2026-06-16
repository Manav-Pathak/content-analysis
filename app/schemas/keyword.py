from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from app.models.enums import SourceType


def normalize_keyword(keyword: str) -> str:
    return " ".join(keyword.strip().lower().split())


class KeywordCreate(BaseModel):
    keyword: str = Field(min_length=2, max_length=255)
    description: str | None = Field(default=None, max_length=2000)

    @field_validator("keyword")
    @classmethod
    def keyword_must_have_text(cls, value: str) -> str:
        normalized = normalize_keyword(value)
        if len(normalized) < 2:
            raise ValueError("Keyword must contain at least 2 non-space characters")
        return value.strip()


class KeywordSourceConfigResponse(BaseModel):
    id: str
    source_type: SourceType
    is_enabled: bool
    query_override: str | None
    fetch_interval_minutes: int
    last_checked_at: datetime | None
    last_cursor: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class KeywordResponse(BaseModel):
    id: str
    keyword: str
    normalized_keyword: str
    description: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    source_configs: list[KeywordSourceConfigResponse] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class KeywordListResponse(BaseModel):
    keywords: list[KeywordResponse]
