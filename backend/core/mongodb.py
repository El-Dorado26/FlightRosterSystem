import os
import logging
from typing import Optional
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE")

_mongo_client: Optional[MongoClient] = None
_mongo_db: Optional[Database] = None


def get_mongodb_client() -> MongoClient:
    global _mongo_client
    if _mongo_client is None:
        logger.info(f"Connecting to MongoDB: {MONGODB_URI[:20]}...")
        _mongo_client = MongoClient(MONGODB_URI)
        logger.info("MongoDB client created successfully!")
    return _mongo_client


def get_mongodb_database() -> Database:
    global _mongo_db
    if _mongo_db is None:
        client = get_mongodb_client()
        _mongo_db = client[MONGODB_DATABASE]
    return _mongo_db


def get_rosters_collection() -> Collection:
    db = get_mongodb_database()
    return db["rosters"]


def test_mongodb_connection() -> bool:
    """Test MongoDB connection and return True if successful."""
    try:
        client = get_mongodb_client()
        # Ping the database to verify connection
        client.admin.command('ping')
        logger.info(f"✓ MongoDB connection successful! Database: {MONGODB_DATABASE}")
        return True
    except Exception as e:
        logger.error(f"✗ MongoDB connection failed: {e}")
        return False


def close_mongodb_connection():
    global _mongo_client, _mongo_db
    if _mongo_client:
        logger.info("Closing MongoDB connection...")
        _mongo_client.close()
        _mongo_client = None
        _mongo_db = None
        logger.info("MongoDB connection closed.")


def save_roster_to_mongodb(roster_data: dict) -> str:
    collection = get_rosters_collection()
    result = collection.insert_one(roster_data)
    return str(result.inserted_id)


def get_roster_from_mongodb(roster_id: str) -> Optional[dict]:
    from bson import ObjectId
    collection = get_rosters_collection()
    
    try:
        roster = collection.find_one({"_id": ObjectId(roster_id)})
        if roster:
            roster["id"] = str(roster["_id"])
            del roster["_id"]
        return roster
    except Exception:
        return None


def list_rosters_from_mongodb(flight_id: Optional[int] = None, limit: int = 100) -> list:
    """
    List rosters from MongoDB with optional filtering
    
    Args:
        flight_id: Optional flight ID to filter by
        limit: Maximum number of rosters to return
        
    Returns:
        List of roster documents
    """
    collection = get_rosters_collection()
    
    query = {}
    if flight_id:
        query["flight_id"] = flight_id
    
    rosters = list(collection.find(query).sort("generated_at", -1).limit(limit))
    
    # Convert ObjectId to string
    for roster in rosters:
        roster["id"] = str(roster["_id"])
        del roster["_id"]
    
    return rosters


def delete_roster_from_mongodb(roster_id: str) -> bool:
    """
    Delete a roster from MongoDB
    
    Args:
        roster_id: MongoDB ObjectId as string
        
    Returns:
        True if deleted, False otherwise
    """
    from bson import ObjectId
    collection = get_rosters_collection()
    
    try:
        result = collection.delete_one({"_id": ObjectId(roster_id)})
        return result.deleted_count > 0
    except Exception:
        return False
