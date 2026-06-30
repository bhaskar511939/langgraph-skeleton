import httpx
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

from config import settings

# Cache HTTP clients — reuse connection pool across requests.
# Headers (including auth tokens) are rebuilt on each make_llm() call
# so tokens stay fresh without recreating the connection pool.
_http_client:       httpx.Client | None       = None
_async_http_client: httpx.AsyncClient | None  = None


def _get_http_clients() -> tuple[httpx.Client, httpx.AsyncClient]:
    global _http_client, _async_http_client
    if _http_client is None:
        _http_client       = httpx.Client()
        _async_http_client = httpx.AsyncClient()
    return _http_client, _async_http_client


def make_llm(model: str | None = None) -> ChatOpenAI:
    """
    Build an LLM instance per request.

    Uses any OpenAI-compatible provider via OPENAI_BASE_URL.
    Supports: OpenAI, Azure OpenAI, Anthropic (via proxy),
    Google Gemini (via proxy), local models (Ollama), etc.

    HTTP clients are cached for connection pool reuse.
    Auth headers are rebuilt each call so tokens stay fresh.
    """
    sync_c, async_c = _get_http_clients()
    return ChatOpenAI(
        api_key=SecretStr(settings.OPENAI_API_KEY),
        base_url=settings.OPENAI_BASE_URL,
        model=model or settings.DEFAULT_MODEL,
        http_client=sync_c,
        http_async_client=async_c,
    )
