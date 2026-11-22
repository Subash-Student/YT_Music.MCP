import os
import json
from mcp.server.fastmcp import FastMCP
from ytmusic_mcp.client import get_ytmusic

def register_auth_tools(mcp: FastMCP):
    """Registers authentication tools with the FastMCP server."""
    
    @mcp.tool()
    def get_auth_status() -> str:
        """
        Check the current connection and login status of the YouTube Music client.
        Shows whether the client is authenticated and displays account details if logged in.
        """
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        project_dir = os.path.dirname(current_dir)
        auth_file = os.path.join(project_dir, "browser.json")
        
        status = {
            "browser_json_exists": os.path.exists(auth_file),
            "authenticated": False,
            "account_name": None,
            "error": None
        }
        
        try:
            yt = get_ytmusic()
            # ytmusicapi client returns auth status by checking if header exists
            is_auth = yt.headers.get("cookie") is not None
            status["authenticated"] = is_auth
            
            if is_auth:
                try:
                    info = yt.get_account_info()
                    status["account_name"] = info.get("accountName", "Unknown Account")
                except Exception as e:
                    status["error"] = f"Failed to fetch account info (cookie might be expired): {str(e)}"
                    status["authenticated"] = False
        except Exception as e:
            status["error"] = f"Failed to initialize client: {str(e)}"
            
        return json.dumps(status, indent=2)


