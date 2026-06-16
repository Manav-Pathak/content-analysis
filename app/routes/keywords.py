from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.keyword import KeywordCreate, KeywordListResponse, KeywordResponse, normalize_keyword
from app.services.keywords import (
    create_keyword_for_user,
    deactivate_keyword,
    get_user_keyword,
    get_user_keyword_by_normalized,
    list_user_keywords,
)

router = APIRouter(prefix="/keywords", tags=["keywords"])


@router.post("", response_model=KeywordResponse, status_code=status.HTTP_201_CREATED)
def create_keyword(
    keyword_data: KeywordCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a tracked keyword for the current user.
    This only stores tracking intent; external API calls happen later in workers.
    """
    existing = get_user_keyword_by_normalized(
        db,
        current_user.id,
        normalize_keyword(keyword_data.keyword),
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Keyword is already being tracked",
        )

    return create_keyword_for_user(
        db=db,
        user=current_user,
        keyword=keyword_data.keyword,
        description=keyword_data.description,
    )


@router.get("", response_model=KeywordListResponse)
def list_keywords(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List active tracked keywords owned by the current user."""
    return KeywordListResponse(keywords=list_user_keywords(db, current_user.id))


@router.get("/{keyword_id}", response_model=KeywordResponse)
def get_keyword(
    keyword_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return one tracked keyword with its source configs."""
    tracked_keyword = get_user_keyword(db, current_user.id, keyword_id)
    if not tracked_keyword:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Keyword not found",
        )
    return tracked_keyword


@router.delete("/{keyword_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_keyword(
    keyword_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Soft-delete a tracked keyword by deactivating it and its source configs.
    Historical mentions remain available for future analytics decisions.
    """
    tracked_keyword = get_user_keyword(db, current_user.id, keyword_id)
    if not tracked_keyword:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Keyword not found",
        )
    deactivate_keyword(db, tracked_keyword)
    return None
