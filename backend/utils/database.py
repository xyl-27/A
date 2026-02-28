from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Generator
from utils.config import settings
from utils.logger import logger

# Create engine
db_available = False
engine = None
SessionLocal = None

try:
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=3600,
        echo=settings.DEBUG
    )
    # Test connection
    with engine.connect() as conn:
        pass
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db_available = True
    logger.info("Database connected successfully")
except Exception as e:
    logger.warning(f"Database not available: {e}")
    engine = None
    SessionLocal = None
    db_available = False

# Create base class for models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Get database session"""
    if not db_available:
        yield None
        return
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """Get database session context manager"""
    if not db_available:
        yield None
        return
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def init_db():
    """Initialize database tables"""
    if not db_available:
        logger.warning("Database not available, skipping initialization")
        return
    from models import market, industry, hot_topic
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized")
