import logging
import time
import uuid
from typing import AsyncGenerator

from fastapi import Request

from config import settings
from agent.events import emit_error, emit_done, emit_info
from agent.stream_events import stream_graph
from api.sse import sse, keepalive
from utils.security import validate_query

logger = logging.getLogger(__name__)


class ChatService:

    async def stream(
        self,
        query:   str,
        user_id: str            = "default",
        model:   str | None     = None,
        request: Request | None = None,
    ) -> AsyncGenerator[str, None]:
        try:
            query = validate_query(query)
        except ValueError as e:
            yield sse(emit_error(str(e)))
            return

        request_id = uuid.uuid4().hex[:8]
        start      = time.time()

        logger.info("Request received", extra={
            "request_id": request_id,
            "user_id":    user_id,
            "query_len":  len(query),
            "model":      model or settings.DEFAULT_MODEL,
        })

        config = {
            "configurable": {
                "thread_id": user_id,
                **({"model_override": model} if model else {}),
            }
        }

        try:
            yield sse(emit_info("thinking", "Thinking..."))

            async for event in stream_graph(query, config, request):
                if event.get("__keepalive__"):
                    yield keepalive()
                else:
                    yield sse(event)

            elapsed = time.time() - start
            logger.info(f"[{request_id}] completed in {elapsed:.2f}s")
            yield sse(emit_done(f"Response complete ({elapsed:.1f}s)"))

        except Exception as e:
            logger.error(f"[{request_id}] stream error: {e}", exc_info=True)
            yield sse(emit_error("An error occurred. Please try again.", request_id=request_id))
