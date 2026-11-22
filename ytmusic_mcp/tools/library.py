import json
from mcp.server.fastmcp import FastMCP
from ytmusic_mcp.client import get_ytmusic
from ytmusic_mcp.models import LibraryActions

def register_library_tools(mcp: FastMCP):
    """Registers library management tools with the FastMCP server."""
    
    @mcp.tool()
    def manage_library(
        action: LibraryActions,
        video_id: str = "",
        playlist_id: str = "",
        artist_id: str = "",
        limit: int = 100
    ) -> str:
        """
        Manage your personal YouTube Music library (Likes, Saves, Follows).
        
        Args:
            action: Action to perform ('like', 'unlike', 'save_album', 'remove_album', 'follow_artist', 'unfollow_artist', 'list_liked_songs').
            video_id: The video ID of the song (Required for 'like', 'unlike').
            playlist_id: The playlist ID of the album (Required for 'save_album', 'remove_album').
            artist_id: The channel ID of the artist (Required for 'follow_artist', 'unfollow_artist').
            limit: Maximum number of liked songs to return (default 100).
        """
        yt = get_ytmusic()
        
        # 1. LIKE Song
        if action == LibraryActions.LIKE:
            if not video_id: return "Error: video_id is required."
            response = yt.rate_song(video_id, rating="LIKE")
            return json.dumps({"success": True, "message": "Song liked.", "response": response})
            
        # 2. UNLIKE Song
        elif action == LibraryActions.UNLIKE:
            if not video_id: return "Error: video_id is required."
            response = yt.rate_song(video_id, rating="INDIFFERENT")
            return json.dumps({"success": True, "message": "Song unliked.", "response": response})
            
        # 3. SAVE Album
        elif action == LibraryActions.SAVE_ALBUM:
            if not playlist_id: return "Error: playlist_id is required."
            response = yt.rate_playlist(playlist_id, rating="LIKE")
            return json.dumps({"success": True, "message": "Album saved to library.", "response": response})
            
        # 4. REMOVE Album
        elif action == LibraryActions.REMOVE_ALBUM:
            if not playlist_id: return "Error: playlist_id is required."
            response = yt.rate_playlist(playlist_id, rating="INDIFFERENT")
            return json.dumps({"success": True, "message": "Album removed from library.", "response": response})
            
        # 5. FOLLOW Artist
        elif action == LibraryActions.FOLLOW_ARTIST:
            if not artist_id: return "Error: artist_id is required."
            response = yt.subscribe_artists([artist_id])
            return json.dumps({"success": True, "message": "Artist followed.", "response": response})
            
        # 6. UNFOLLOW Artist
        elif action == LibraryActions.UNFOLLOW_ARTIST:
            if not artist_id: return "Error: artist_id is required."
            response = yt.unsubscribe_artists([artist_id])
            return json.dumps({"success": True, "message": "Artist unfollowed.", "response": response})
            
        # 7. LIST Liked Songs
        elif action == LibraryActions.LIST_LIKED_SONGS:
            liked_playlist = yt.get_liked_songs(limit=limit)
            tracks = liked_playlist.get("tracks", [])
            
            formatted_tracks = []
            for t in tracks:
                artists_str = ", ".join([a.get("name", "Unknown") for a in t.get("artists", [])])
                formatted_tracks.append({
                    "title": t.get("title", "Unknown"),
                    "artists": artists_str,
                    "album": t.get("album", {}).get("name", "Unknown") if t.get("album") else "Unknown",
                    "videoId": t.get("videoId")
                })
                
            return json.dumps({
                "success": True,
                "playlist_title": liked_playlist.get("title", "Liked Songs"),
                "total_tracks": len(formatted_tracks),
                "tracks": formatted_tracks
            }, indent=2)
