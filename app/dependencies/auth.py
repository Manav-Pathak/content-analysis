from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.services.auth import decode_access_token

# Tells FastAPI to look for "Authorization: Bearer <token>" in the request header
# Also makes a lock icon appear in Swagger /docs for protected routes
bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    FastAPI dependency — inject this into any route that requires auth.

    Flow:
      1. FastAPI extracts the token from the Authorization header
      2. We decode & validate the JWT
      3. We look up the user in the DB
      4. We return the User object (routes then know who is making the request)

    Usage in a route:
        @router.get("/protected")
        def protected(current_user: User = Depends(get_current_user)):
            return {"owner": current_user.id}
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user_id = decode_access_token(credentials.credentials)
    if user_id is None:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None or not user.is_active:
        raise credentials_exception

    return user
