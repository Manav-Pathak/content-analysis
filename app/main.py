from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import engine, Base

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
    title="Content Insight API",
    description="Backend for ingesting and analysing content from external sources.",
    version="0.1.0",
    lifespan=lifespan,
)

# Register routers
from app.routes import auth  # noqa: E402
app.include_router(auth.router)


@app.get("/health", tags=["health"])
def health_check():
    """Quick sanity check — no auth needed."""
    return {"status": "ok"}
