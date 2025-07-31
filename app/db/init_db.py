import logging
from sqlalchemy.orm import Session

from app.db.session import SessionLocal, engine
from app.db.base import Base
from app.models.user import User
from app.models.employment import Employment
from app.models.verification_code import VerificationCode
from app.models.access_log import AccessLog

logger = logging.getLogger(__name__)


def init_db() -> None:
    """Initialize database tables"""
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
        # Create initial data if needed
        db = SessionLocal()
        try:
            create_initial_data(db)
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise


def create_initial_data(db: Session) -> None:
    """Create initial data for the application"""
    # This function can be used to create default users, settings, etc.
    # For now, we'll just log that it's ready
    logger.info("Database is ready for use")
    pass
