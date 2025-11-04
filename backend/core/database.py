import os
from collections.abc import Generator

from core.models import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")

engine = create_engine(DATABASE_URL, echo=False)

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
