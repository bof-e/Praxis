"""
Database setup and session management for Praxis v0.3
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from src.models import Base
from src.config import settings


def get_engine():
    """Create database engine"""
    return create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
    )


def init_db(engine=None):
    """Initialize database tables"""
    if engine is None:
        engine = get_engine()
    Base.metadata.create_all(bind=engine)


def get_session() -> Session:
    """Get database session"""
    engine = get_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()


# Create default readiness models on initialization
def seed_default_data(session: Session):
    """Seed database with default data"""
    from ..models import ReadinessModel, TaskType
    
    # Check if models already exist
    existing = session.query(ReadinessModel).count()
    if existing == 0:
        # Create default models - they'll be created on first use by ReadinessEngine
        pass
    
    session.commit()
