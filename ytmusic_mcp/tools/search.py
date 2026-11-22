from mcp.server.fastmcp import FastMCP
from ytmusic_mcp.client import get_ytmusic
from ytmusic_mcp.models import SearchFilter
from ytmusic_mcp.format_output import format_search_results

def register_search_tools(mcp: FastMCP):
    """Registers all search-related tools with the FastMCP server instance."""
    
    @mcp.tool()
    def search_music(query: str, filter_type: SearchFilter = SearchFilter.SONGS, limit: int = 10) -> str:
        """
        Search YouTube Music for songs, albums, artists, playlists, or videos.
        
        Args:
            query: The search text (e.g. 'Dua Lipa Levitating' or 'Jazz Relax'). REQUIRED.
            filter_type: Type of results to filter by. Options: 'songs', 'albums', 'artists', 'playlists', 'videos'. Default is 'songs'.
            limit: Maximum number of results to return (default 10).
        """
        if not query:
            return "Error: A search query is required."

        yt = get_ytmusic()
        result = yt.search(query=query, filter=filter_type.value, limit=limit)
        
        return format_search_results(result, query)
