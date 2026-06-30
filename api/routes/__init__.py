from fastapi import APIRouter
from api.routes.chat   import router as chat_router
from api.routes.health import router as health_router

router = APIRouter(prefix="/v1/chat", tags=["Chat"])
router.include_router(chat_router)
router.include_router(health_router)
