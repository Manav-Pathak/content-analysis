from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import settings

database_url = settings.sqlalchemy_database_url

# SQLite needs this special arg; harmless to remove when switching to Postgres
connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}

engine = create_engine(database_url, connect_args=connect_args, pool_pre_ping=True)

# SessionLocal is the factory that creates individual DB sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base class all ORM models inherit from."""
    pass


def get_db():
    """
    FastAPI dependency that yields a DB session per request,
    and ensures it's closed even if an error occurs.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
