import sys
from mcp.server.fastmcp import FastMCP
from ytmusic_mcp.tools.search import register_search_tools
from ytmusic_mcp.tools.playlist import register_playlist_tools
from ytmusic_mcp.tools.import_export import register_import_export_tools
from ytmusic_mcp.tools.library import register_library_tools
from ytmusic_mcp.tools.recommend import register_recommend_tools
from ytmusic_mcp.tools.browse import register_browse_tools
from ytmusic_mcp.tools.auth import register_auth_tools
from ytmusic_mcp.client import get_ytmusic

# 1. Create the central FastMCP server instance
mcp = FastMCP("YouTube Music")

# 2. Register tool modules
register_search_tools(mcp)
register_playlist_tools(mcp)
register_import_export_tools(mcp)
register_library_tools(mcp)
register_recommend_tools(mcp)
register_browse_tools(mcp)
register_auth_tools(mcp)

# 3. Run server via STDIO
if __name__ == "__main__":
    print("Starting YouTube Music MCP Server via STDIO...", file=sys.stderr)
    # Pre-warm the client to verify and log authentication status immediately on startup
    get_ytmusic()
    mcp.run(transport="stdio")
