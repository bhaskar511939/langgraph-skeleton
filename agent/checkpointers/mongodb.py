import logging
from config import settings

logger = logging.getLogger(__name__)


def get_mongodb_checkpointer():
    """
    Build a MongoDBSaver checkpointer.
    Raises on misconfiguration so the caller can fall back to memory.

    Why MongoDB over SQLite for production:
    - Survives server restarts and deployments
    - Supports horizontal scaling (multiple server instances)
    - TTL indexes for automatic conversation expiry
    - Native support for large message histories
    """
    from pymongo import MongoClient
    from langgraph.checkpoint.mongodb import MongoDBSaver

    if not settings.MONGODB_URI:
        raise ValueError("MONGODB_URI not set in environment")

    client       = MongoClient(settings.MONGODB_URI)
    checkpointer = MongoDBSaver(client, db_name=settings.MONGODB_DB_NAME)

    logger.info(f"Memory backend: MongoDB ({settings.MONGODB_DB_NAME})")
    return checkpointer
