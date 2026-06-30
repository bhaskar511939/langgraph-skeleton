"""
MCP (Model Context Protocol) server configuration.

MCP enables AI agents to connect to external tool servers using a
standardized protocol. This allows tools to be developed independently
of the agent and discovered at runtime.

Transport types:
  streamable_http — remote HTTP MCP server (most common)
  stdio           — local subprocess MCP server

Auth types:
  bearer          — Authorization: Bearer <token>
  none            — no authentication

To add an MCP server:
  1. Add an entry to MCP_SERVERS below
  2. Set transport, url, and auth configuration
  3. The agent will discover and load all tools automatically on startup

Example:
  MCP_SERVERS = {
      "my_server": {
          "url":       "https://my-mcp-server.com/mcp",
          "transport": "streamable_http",
          "auth_type": "bearer",
          "token":     "your-bearer-token",
      }
  }
"""

MCP_SERVERS: dict = {
    # Add your MCP servers here.
    # Leave empty to run without MCP tools.
    #
    # "example": {
    #     "url":       "https://example-mcp-server.com/mcp",
    #     "transport": "streamable_http",
    #     "auth_type": "bearer",
    #     "token":     "your-token",
    # },
}
