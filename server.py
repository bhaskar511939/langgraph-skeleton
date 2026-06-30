import sys
sys.dont_write_bytecode = True

from config import settings
from utils.logging import setup_logging

setup_logging()

import uvicorn

if __name__ == "__main__":
    print(f"""
===========================================================
 LangGraph Production Skeleton
===========================================================
 Environment : {settings.APP_ENV}
 URL         : http://{settings.HOST}:{settings.PORT}
 Model       : {settings.DEFAULT_MODEL}
 Memory      : {settings.MEMORY_BACKEND}
 Debug       : {settings.DEBUG}
===========================================================
""")
    uvicorn.run(
        "api.app:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        access_log=False,
        log_level="warning",
    )
