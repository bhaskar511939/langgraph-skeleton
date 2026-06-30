import logging
from typing import List
from langchain_core.tools import BaseTool

logger = logging.getLogger(__name__)

_mcp_tools:  List[BaseTool] = []
_initialized = False


async def init_mcp_tools() -> None:
    """
    Load tools from all configured MCP servers at startup.

    MCP (Model Context Protocol) is an open standard that allows
    AI agents to connect to external tool servers. This enables
    organizations to build and maintain tools independently of the
    agent, discovered and loaded at runtime.

    Tools are loaded once at startup and cached. The agent uses
    get_mcp_tools() to access them alongside built-in tools.
    """
    global _mcp_tools, _initialized
    if _initialized:
        return

    try:
        from langchain_mcp_adapters.client import MultiServerMCPClient
    except ImportError:
        logger.warning("langchain-mcp-adapters not installed — MCP tools disabled")
        _initialized = True
        return

    from agent.tools.mcp_config import MCP_SERVERS

    if not MCP_SERVERS:
        logger.info("No MCP servers configured")
        _initialized = True
        return

    tools: List[BaseTool] = []

    for name, cfg in MCP_SERVERS.items():
        try:
            transport  = cfg.get("transport", "streamable_http").replace("-", "_")
            auth_type  = cfg.get("auth_type", "none")
            headers    = {}

            if auth_type == "bearer" and cfg.get("token"):
                headers["Authorization"] = f"Bearer {cfg['token']}"

            server_cfg = {"url": cfg["url"], "transport": transport}
            if headers:
                server_cfg["headers"] = headers

            client       = MultiServerMCPClient({name: server_cfg})
            server_tools = await client.get_tools()
            tools.extend(server_tools)
            logger.info(f"MCP [{name}] loaded {len(server_tools)} tools")
        except Exception as e:
            logger.warning(f"MCP [{name}] failed — {e.__class__.__name__}: {e}")

    _mcp_tools   = tools
    _initialized = True
    logger.info(f"MCP ready — {len(_mcp_tools)} tools total")


def get_mcp_tools() -> List[BaseTool]:
    return _mcp_tools
