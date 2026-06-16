from sqlalchemy.orm import Session, selectinload
from app.models.enums import SourceType
from app.models.keyword_source_config import KeywordSourceConfig
from app.models.tracked_keyword import TrackedKeyword
from app.models.user import User
from app.schemas.keyword import normalize_keyword


DEFAULT_SOURCE_TYPES = (SourceType.YOUTUBE, SourceType.REDDIT)


def get_user_keyword_by_normalized(
    db: Session,
    user_id: str,
    normalized_keyword: str,
) -> TrackedKeyword | None:
    return (
        db.query(TrackedKeyword)
        .filter(
            TrackedKeyword.user_id == user_id,
            TrackedKeyword.normalized_keyword == normalized_keyword,
            TrackedKeyword.is_active.is_(True),
        )
        .first()
    )


def get_user_keyword(
    db: Session,
    user_id: str,
    keyword_id: str,
) -> TrackedKeyword | None:
    return (
        db.query(TrackedKeyword)
        .options(selectinload(TrackedKeyword.source_configs))
        .filter(
            TrackedKeyword.id == keyword_id,
            TrackedKeyword.user_id == user_id,
            TrackedKeyword.is_active.is_(True),
        )
        .first()
    )


def list_user_keywords(db: Session, user_id: str) -> list[TrackedKeyword]:
    return (
        db.query(TrackedKeyword)
        .options(selectinload(TrackedKeyword.source_configs))
        .filter(
            TrackedKeyword.user_id == user_id,
            TrackedKeyword.is_active.is_(True),
        )
        .order_by(TrackedKeyword.created_at.desc())
        .all()
    )


def create_keyword_for_user(
    db: Session,
    user: User,
    keyword: str,
    description: str | None,
) -> TrackedKeyword:
    tracked_keyword = TrackedKeyword(
        user_id=user.id,
        keyword=keyword.strip(),
        normalized_keyword=normalize_keyword(keyword),
        description=description,
    )
    db.add(tracked_keyword)
    db.flush()

    for source_type in DEFAULT_SOURCE_TYPES:
        db.add(
            KeywordSourceConfig(
                tracked_keyword_id=tracked_keyword.id,
                source_type=source_type,
            )
        )

    db.commit()
    db.refresh(tracked_keyword)
    return get_user_keyword(db, user.id, tracked_keyword.id) or tracked_keyword


def deactivate_keyword(db: Session, tracked_keyword: TrackedKeyword) -> TrackedKeyword:
    tracked_keyword.is_active = False
    for source_config in tracked_keyword.source_configs:
        source_config.is_enabled = False
    db.commit()
    db.refresh(tracked_keyword)
    return tracked_keyword
