import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # App
    APP_ENV:    str = os.getenv("APP_ENV", "local")
    APP_NAME:   str = "LangGraph Production Skeleton"
    HOST:       str = os.getenv("HOST", "localhost")
    PORT:       int = int(os.getenv("PORT", "8000"))
    DEBUG:      bool = os.getenv("DEBUG", "false").lower() == "true"
    LOG_LEVEL:  str = os.getenv("LOG_LEVEL", "INFO")

    # LLM — works with any OpenAI-compatible provider
    OPENAI_API_KEY:  str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    DEFAULT_MODEL:   str = os.getenv("DEFAULT_MODEL", "gpt-4o")

    # Memory
    MEMORY_BACKEND:  str = os.getenv("MEMORY_BACKEND", "memory")
    MONGODB_URI:     str = os.getenv("MONGODB_URI", "")
    MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME", "langgraph_db")

    # Agent behaviour
    SUMMARIZE_AFTER: int = int(os.getenv("SUMMARIZE_AFTER", "10"))

    # MCP (optional)
    MCP_SERVER_URL:   str = os.getenv("MCP_SERVER_URL", "")
    MCP_SERVER_TOKEN: str = os.getenv("MCP_SERVER_TOKEN", "")


settings = Settings()
