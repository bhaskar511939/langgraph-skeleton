import logging
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from api.schemas import AskRequest, ALLOWED_MODELS
from api.services import ChatService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/ask")
async def chat_ask(body: AskRequest, request: Request):
    user_id = getattr(request.state, "user_id", None) or body.user_id
    model   = body.model if body.model in ALLOWED_MODELS else None

    return StreamingResponse(
        ChatService().stream(
            query=body.query,
            user_id=user_id,
            model=model,
            request=request,
        ),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "close", "X-Accel-Buffering": "no"},
    )
