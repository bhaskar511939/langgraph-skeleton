import time
import logging
from fastapi import APIRouter, HTTPException
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

from config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health", tags=["Health"])
async def health():
    return {
        "status": "ok",
        "env":    settings.APP_ENV,
        "model":  settings.DEFAULT_MODEL,
        "memory": settings.MEMORY_BACKEND,
    }


@router.get("/test", tags=["Health"])
async def test_llm():
    from agent.llm import make_llm
    try:
        t   = time.time()
        llm = make_llm()
        r   = await llm.ainvoke([HumanMessage(content="Say hello in one sentence.")])
        return {"status": "ok", "model": settings.DEFAULT_MODEL, "response": r.content[:200], "latency_s": round(time.time() - t, 2)}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


@router.get("/debug/state/{user_id}", tags=["Health"])
async def debug_state(user_id: str):
    from agent.graph import get_graph
    graph  = get_graph()
    config = {"configurable": {"thread_id": user_id}}
    try:
        state = graph.get_state(config)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"No state for '{user_id}': {e}")
    if not state or not state.values:
        return {"user_id": user_id, "message_count": 0, "summary": "", "messages": []}
    messages = state.values.get("messages", [])
    preview  = []
    for m in messages:
        if isinstance(m, HumanMessage):   preview.append({"role": "user",      "content": str(m.content)[:120]})
        elif isinstance(m, AIMessage):    preview.append({"role": "assistant", "content": str(m.content)[:120]})
        elif isinstance(m, ToolMessage):  preview.append({"role": "tool",      "content": str(m.content)[:80]})
    return {"user_id": user_id, "message_count": len(messages), "summary": state.values.get("summary", ""), "messages": preview}
