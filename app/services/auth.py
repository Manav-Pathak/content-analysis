from datetime import datetime, timedelta, timezone
import bcrypt
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.config import settings
from app.models.user import User

# ── Password Helpers ─────────────────────────────────────────────────────────

def hash_password(plain_password: str) -> str:
    """Never store plain text. bcrypt adds a salt automatically."""
    return bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """bcrypt.checkpw performs a safe hash comparison."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


# ── JWT Helpers ──────────────────────────────────────────────────────────────

def create_access_token(user_id: str) -> str:
    """
    Creates a signed JWT token.
    - sub (subject): who this token represents — the user's UUID
    - exp (expiry): when the token stops being valid
    """
    expiry = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expiration_minutes)
    payload = {
        "sub": user_id,
        "exp": expiry,
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> str | None:
    """
    Decodes and validates a JWT token.
    Returns the user_id (sub claim) if valid, None if expired/tampered.
    """
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        user_id: str = payload.get("sub")
        return user_id
    except JWTError:
        return None


# ── DB-level Auth Helpers ────────────────────────────────────────────────────

def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    """
    Returns the User if credentials are valid, None otherwise.
    Keeping this in the service layer means routes stay thin.
    """
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
