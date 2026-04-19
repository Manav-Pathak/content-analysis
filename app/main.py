from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session
from app.database import engine, Base, get_db

# Application startup wiring lives in this module.
# Import models so SQLAlchemy knows about them before create_all
import app.models.user  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Runs on startup: creates all tables if they don't exist.
    In production you'd use Alembic migrations instead.
    """
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="BrandTrack API",
    description="Backend for ingesting and analysing brand mentions from external sources.",
    version="0.1.0",
    lifespan=lifespan,
)

# Register routers
from app.routes import auth  # noqa: E402
app.include_router(auth.router)


@app.get("/health", tags=["health"])
def health_check():
    """Quick sanity check  no auth needed."""
    return {"status": "ok"}


@app.get("/health/db", tags=["health"])
def database_health_check(db: Session = Depends(get_db)):
    """
    Verifies that the API can talk to Postgres and that startup created
    the current ORM tables.
    """
    db.execute(text("SELECT 1"))
    inspector = inspect(db.bind)
    return {
        "status": "ok",
        "database": "connected",
        "users_table_present": inspector.has_table("users"),
    }
