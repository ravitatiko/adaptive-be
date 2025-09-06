# MongoDB-compatible database module
# This module provides compatibility functions for existing SQLAlchemy imports
# while using MongoDB as the actual database

from .mongodb import get_database
import logging

logger = logging.getLogger(__name__)

# Create a dummy Base class for compatibility with existing models
class Base:
    """Dummy Base class for compatibility with SQLAlchemy models"""
    pass

# Dependency to get database (MongoDB)
def get_db():
    """Get MongoDB database instance"""
    try:
        db = get_database()
        if db is None:
            logger.error("Database not connected")
            return None
        yield db
    except Exception as e:
        logger.error(f"Error getting database: {e}")
        yield None
