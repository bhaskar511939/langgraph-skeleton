import logging
from langgraph.checkpoint.memory import MemorySaver

logger = logging.getLogger(__name__)


def get_memory_checkpointer() -> MemorySaver:
    logger.info("Memory backend: in-memory (MemorySaver)")
    return MemorySaver()
