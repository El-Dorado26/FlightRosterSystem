import os
from collections.abc import Generator

from core.models import Base
from core.user_models import User
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")

# Optimize connection pooling for better performance
engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_size=10,          # Number of persistent connections
    max_overflow=20,       # Additional connections when pool is full
    pool_pre_ping=True,    # Verify connections before using
    pool_recycle=3600,     # Recycle connections after 1 hour
    connect_args={
        "connect_timeout": 10,
        "options": "-c statement_timeout=30000"  # 30 second query timeout
    }
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    Base.metadata.create_all(bind=engine)

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_database():
    if os.getenv("SKIP_DB", "false").lower() == "true":
        return

    print("Creating database tables...")
    create_tables()
    print("Database initialized successfully!")


class DatabaseManager:
    @staticmethod
    def get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    @staticmethod
    def get_session() -> Session:
        return SessionLocal()

    @staticmethod
    def close_session(db: Session):
        db.close()

    @staticmethod
    def commit_and_refresh(db: Session, obj):
        """Commit transaction and refresh object."""
        db.commit()
        db.refresh(obj)
        return obj

    @staticmethod
    def safe_commit(db: Session) -> bool:
        """Safely commit transaction with error handling."""
        try:
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            print(f"Database commit failed: {e}")
            return False
