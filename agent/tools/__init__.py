from agent.tools.builtin import ALL_TOOLS
from agent.tools.mcp import get_mcp_tools


def get_all_tools():
    """Combine built-in tools with dynamically loaded MCP tools."""
    return ALL_TOOLS + get_mcp_tools()


__all__ = ["ALL_TOOLS", "get_all_tools"]
