import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import settings
from utils.logging import setup_logging

logger = logging.getLogger(__name__)
_start_time = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.APP_NAME} — env={settings.APP_ENV} model={settings.DEFAULT_MODEL}")
    from agent.tools.mcp import init_mcp_tools
    from agent.graph import get_graph
    await init_mcp_tools()
    get_graph()
    logger.info(f"Ready in {time.time() - _start_time:.2f}s")
    yield
    logger.info(f"{settings.APP_NAME} stopped")


def create_app() -> FastAPI:
    setup_logging()

    app = FastAPI(
        title=settings.APP_NAME,
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs" if settings.DEBUG else None,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    from api.routes import router
    app.include_router(router, prefix="/api")

    @app.exception_handler(Exception)
    async def _500(request: Request, exc: Exception):
        logger.error(f"Unhandled error {request.url}: {exc}", exc_info=True)
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "detail": str(exc)})

    @app.exception_handler(ValueError)
    async def _400(request: Request, exc: ValueError):
        return JSONResponse(status_code=400, content={"error": "Bad Request", "detail": str(exc)})

    return app


app = create_app()
