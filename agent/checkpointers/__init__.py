import logging
from config import settings

logger = logging.getLogger(__name__)


def get_checkpointer():
    """
    Return the configured checkpointer based on MEMORY_BACKEND env var.

    memory  → MemorySaver  (default, no external deps)
    mongodb → MongoDBSaver (requires MONGODB_URI)

    Adding a new backend:
      1. Create agent/checkpointers/<name>.py
      2. Add case below
    """
    from agent.checkpointers.memory import get_memory_checkpointer

    backend = settings.MEMORY_BACKEND

    if backend == "mongodb":
        try:
            from agent.checkpointers.mongodb import get_mongodb_checkpointer
            return get_mongodb_checkpointer()
        except Exception as e:
            logger.warning(
                f"MongoDB checkpointer unavailable ({e.__class__.__name__}: {e})"
                " — falling back to MemorySaver"
            )

    return get_memory_checkpointer()
