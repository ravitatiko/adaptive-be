from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from .config import settings
import logging

logger = logging.getLogger(__name__)

class MongoDB:
    client: AsyncIOMotorClient = None
    database = None

mongodb = MongoDB()

async def connect_to_mongo():
    """Create database connection"""
    try:
        mongodb.client = AsyncIOMotorClient(settings.database_url)
        # Test the connection
        await mongodb.client.admin.command('ping')
        logger.info("Connected to MongoDB successfully")
        
        # Get database (you can specify a database name here)
        mongodb.database = mongodb.client.adaptive_learning
        return mongodb.database
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise e

async def close_mongo_connection():
    """Close database connection"""
    if mongodb.client:
        mongodb.client.close()
        logger.info("Disconnected from MongoDB")

def get_database():
    """Get database instance"""
    return mongodb.database

# Synchronous client for testing
def get_sync_client():
    """Get synchronous MongoDB client for testing"""
    return MongoClient(settings.database_url)

def test_mongodb_connection():
    """Test MongoDB connection synchronously"""
    try:
        client = get_sync_client()
        # Test the connection
        client.admin.command('ping')
        logger.info("MongoDB connection test successful")
        client.close()
        return True
    except Exception as e:
        logger.error(f"MongoDB connection test failed: {e}")
        return False

