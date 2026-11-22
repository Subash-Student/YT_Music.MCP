import json
from mcp.server.fastmcp import FastMCP, Context
from ytmusic_mcp.client import get_ytmusic
from enum import Enum
from mcp.types import SamplingMessage, TextContent

class RecommendSource(str, Enum):
    RECENT_HISTORY = "recent_history"
    LIKED_SONGS = "liked_songs"
    SPECIFIC_PLAYLIST = "specific_playlist"

def register_recommend_tools(mcp: FastMCP):
    """Registers the recommendation engine tool with the FastMCP server."""
    
    @mcp.tool()
    async def recommend_music(
        ctx: Context,
        source: RecommendSource,
        playlist_id: str = "",
        count: int = 10
    ) -> str:
        """
        AI-Powered Music Recommendation Engine.
        Analyzes your listening history, liked songs, or a specific playlist to recommend new songs you might love.
        
        Args:
            source: The source to base recommendations on ('recent_history', 'liked_songs', 'specific_playlist'). REQUIRED.
            playlist_id: The ID of the playlist to use. REQUIRED if source is 'specific_playlist'.
            count: Number of recommendations to generate (default 10).
        """
        yt = get_ytmusic()
        
        tracks = []
        source_name = ""
        
        if source == RecommendSource.RECENT_HISTORY:
            history = yt.get_history()
            tracks = history[:50]
            source_name = "your recent listening history"
            
        elif source == RecommendSource.LIKED_SONGS:
            liked = yt.get_liked_songs(limit=50)
            tracks = liked.get("tracks", [])
            source_name = "your liked songs"
            
        elif source == RecommendSource.SPECIFIC_PLAYLIST:
            if not playlist_id:
                return "Error: playlist_id is required when source is 'specific_playlist'."
                
            playlist = yt.get_playlist(playlist_id, limit=None)
            tracks = playlist.get("tracks", [])
            source_name = f"the playlist '{playlist.get('title', playlist_id)}'"
            
        if not tracks:
            return "Error: Could not find any tracks in the selected source to base recommendations on."
            
        # Format tracks for the LLM
        simplified_tracks = []
        for i, t in enumerate(tracks[:50]):
            artists = ", ".join([a.get("name", "Unknown") for a in t.get("artists", []) if isinstance(a, dict)])
            simplified_tracks.append(f"- {t.get('title', 'Unknown')} by {artists}")
            
        tracks_text = "\n".join(simplified_tracks)
        
        prompt = f"""
You are an expert music curator and recommendation engine. 
I am providing you a list of songs from {source_name}.

Source Tracks:
{tracks_text}

Based on the musical style, genres, and vibe of these source tracks, please recommend {count} NEW songs that the user would likely enjoy.
Try to avoid recommending songs that are already in the source list.

Format your output as a clean, beautiful Markdown list, including:
- Song Title
- Artist
- A brief 1-sentence explanation of why this matches their taste based on the source tracks.

Your response:
"""
        
        result = await ctx.session.create_message(
            messages=[
                SamplingMessage(
                    role="user",
                    content=TextContent(type="text", text=prompt)
                )
            ],
            max_tokens=1500
        )
        
        if result.content.type == "text":
            return json.dumps({
                "success": True,
                "source": source.value,
                "recommendations": result.content.text
            })
            
        return "Error: Failed to receive text content from client LLM."
