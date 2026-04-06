from datetime import datetime
from pydantic import BaseModel, EmailStr, field_validator


# ── Request Schemas (what the API accepts) ──────────────────────────────────

class UserCreate(BaseModel):
    """Used for POST /auth/register"""
    email: EmailStr          # Pydantic validates email format automatically
    password: str

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class UserLogin(BaseModel):
    """Used for POST /auth/login"""
    email: EmailStr
    password: str


# ── Response Schemas (what the API returns) ─────────────────────────────────

class UserResponse(BaseModel):
    """Returned after register and in /me — never includes the password"""
    id: str
    email: str
    created_at: datetime

    # Tells Pydantic to read data from ORM attributes (not just dicts)
    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """Returned after successful login"""
    access_token: str
    token_type: str = "bearer"
