"""
Database connection settings and factory.
"""

from typing import Optional

from pymongo import MongoClient
from pymongo.database import Database


# Module-level client (set by app on startup)
_mongo_client: Optional[MongoClient] = None
_db_name: str = "chatbot_db"


def set_db_config(uri: str, db_name: str) -> None:
    """Set MongoDB URI and database name (called from config)."""
    global _db_name
    _db_name = db_name
    init_client(uri)


def init_client(uri: str) -> MongoClient:
    """Initialize global MongoClient."""
    global _mongo_client
    _mongo_client = MongoClient(uri)
    return _mongo_client


def get_mongo_client() -> MongoClient:
    """Return configured MongoClient. Raises if not initialized."""
    if _mongo_client is None:
        raise RuntimeError("Database not initialized. Call set_db_config or init_client first.")
    return _mongo_client


def get_database() -> Database:
    """Return configured database instance."""
    return get_mongo_client()[_db_name]
