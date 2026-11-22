import json
from mcp.server.fastmcp import FastMCP
from ytmusic_mcp.client import get_ytmusic
from ytmusic_mcp.models import BrowseActions
from ytmusic_mcp.format_output import (
    format_track_list, format_playlist_list, format_artist, format_album,
    format_history
)

def register_browse_tools(mcp: FastMCP):
    """Registers all browsing and information tools with the FastMCP server."""
    
    @mcp.tool()
    def browse_music(
        action: BrowseActions,
        playlist_id: str = "",
        video_id: str = "",
        artist_id: str = "",
        album_id: str = "",
        limit: int = 25
    ) -> str:
        """
        Browse, list, and fetch detailed information from YouTube Music.
        
        Args:
            action: What to browse. REQUIRED.
            playlist_id: ID of a playlist (Required for GET_PLAYLIST_TRACKS, GET_MOOD_PLAYLISTS).
            video_id: ID of a song/video (Required for GET_SONG_DETAILS, GET_LYRICS, GET_SONG_CREDITS, GET_RELATED_SONGS, GET_WATCH_PLAYLIST).
            artist_id: ID of an artist (Required for GET_ARTIST, GET_ARTIST_ALBUMS).
            album_id: ID of an album (Required for GET_ALBUM).
            limit: Maximum items to return (default 25).
        """
        yt = get_ytmusic()
        
        if not action:
            return "Error: action is required."
            
        # 1. PLAYLISTS
        if action == BrowseActions.LIST_PLAYLISTS:
            playlists = yt.get_library_playlists(limit=limit)
            return format_playlist_list(playlists, title="Your Playlists")
            
        elif action == BrowseActions.GET_PLAYLIST_TRACKS:
            if not playlist_id: return "Error: playlist_id is required."
            playlist = yt.get_playlist(playlist_id, limit=limit)
            title = playlist.get("title", "Playlist")
            tracks = playlist.get("tracks", [])
            return format_track_list(tracks, title=f"Tracks in '{title}'")
            
        # 2. SONGS
        elif action == BrowseActions.GET_SONG_DETAILS:
            if not video_id: return "Error: video_id is required."
            song = yt.get_song(video_id)
            return json.dumps(song, indent=2) # Often complex, keep as JSON or write custom
            
        elif action == BrowseActions.GET_LYRICS:
            if not video_id: return "Error: video_id is required."
            # We first need the browseId for lyrics
            song = yt.get_song(video_id)
            try:
                watch_playlist = yt.get_watch_playlist(videoId=video_id)
                lyrics_id = watch_playlist.get("lyrics")
                if not lyrics_id:
                    return "No lyrics available for this song."
                lyrics = yt.get_lyrics(lyrics_id)
                return lyrics.get("lyrics", "No lyrics text found.") if isinstance(lyrics, dict) else str(lyrics)
            except Exception as e:
                return f"Failed to get lyrics: {str(e)}"
                
        elif action == BrowseActions.GET_SONG_CREDITS:
            if not video_id: return "Error: video_id is required."
            try:
                watch_playlist = yt.get_watch_playlist(videoId=video_id)
                related_id = watch_playlist.get("related")
                if not related_id:
                    return "No credits available for this song."
                credits = yt.get_song_credits(related_id)
                return json.dumps(credits, indent=2)
            except Exception as e:
                return f"Failed to get credits: {str(e)}"
                
        elif action == BrowseActions.GET_RELATED_SONGS:
            if not video_id: return "Error: video_id is required."
            try:
                watch_playlist = yt.get_watch_playlist(videoId=video_id)
                related_id = watch_playlist.get("related")
                if not related_id:
                    return "No related songs available."
                related = yt.get_song_related(related_id)
                return json.dumps(related, indent=2)
            except Exception as e:
                return f"Failed to get related songs: {str(e)}"
                
        # 3. ARTISTS & ALBUMS
        elif action == BrowseActions.GET_ARTIST:
            if not artist_id: return "Error: artist_id is required."
            artist = yt.get_artist(artist_id)
            return format_artist(artist)
            
        elif action == BrowseActions.GET_ARTIST_ALBUMS:
            if not artist_id: return "Error: artist_id is required."
            albums = yt.get_artist_albums(artist_id, params="")
            return json.dumps(albums, indent=2)
            
        elif action == BrowseActions.GET_ALBUM:
            if not album_id: return "Error: album_id is required."
            album = yt.get_album(album_id)
            return format_album(album)
            
        # 4. EXPLORE
        elif action == BrowseActions.GET_CHARTS:
            charts = yt.get_charts()
            return json.dumps(charts, indent=2)
            
        elif action == BrowseActions.GET_MOOD_CATEGORIES:
            categories = yt.get_mood_categories()
            return json.dumps(categories, indent=2)
            
        elif action == BrowseActions.GET_MOOD_PLAYLISTS:
            if not playlist_id: return "Error: playlist_id (params) is required for mood playlists."
            playlists = yt.get_mood_playlists(playlist_id)
            return format_playlist_list(playlists, title="Mood Playlists")
            
        elif action == BrowseActions.GET_HOME_FEED:
            home = yt.get_home(limit=3)
            return json.dumps(home, indent=2)
            
        # 5. HISTORY & LIBRARY
        elif action == BrowseActions.GET_HISTORY:
            history = yt.get_history()
            return format_history(history[:limit])
            
        elif action == BrowseActions.GET_LIBRARY_ALBUMS:
            albums = yt.get_library_albums(limit=limit)
            return json.dumps(albums, indent=2)
            
        elif action == BrowseActions.GET_LIBRARY_ARTISTS:
            artists = yt.get_library_artists(limit=limit)
            return json.dumps(artists, indent=2)
            
        elif action == BrowseActions.GET_LIBRARY_SONGS:
            songs = yt.get_library_songs(limit=limit)
            return format_track_list(songs, title="Library Songs")
            
        elif action == BrowseActions.GET_LIBRARY_SUBSCRIPTIONS:
            subs = yt.get_library_subscriptions(limit=limit)
            return json.dumps(subs, indent=2)
            
        elif action == BrowseActions.GET_ACCOUNT_INFO:
            info = yt.get_account_info()
            return json.dumps(info, indent=2)
            
        elif action == BrowseActions.GET_WATCH_PLAYLIST:
            if not video_id and not playlist_id: return "Error: video_id or playlist_id is required."
            watch = yt.get_watch_playlist(videoId=video_id, playlistId=playlist_id, limit=limit)
            tracks = watch.get("tracks", []) if isinstance(watch, dict) else []
            return format_track_list(tracks, title="Radio / Up Next")
            
        elif action == BrowseActions.GET_SEARCH_SUGGESTIONS:
            # Reusing video_id arg as query for simplicity to avoid adding another arg
            query = video_id or playlist_id
            if not query: return "Error: query (pass in video_id) is required."
            suggestions = yt.get_search_suggestions(query)
            return json.dumps(suggestions, indent=2)
            
        elif action == BrowseActions.GET_LIBRARY_PODCASTS:
            podcasts = yt.get_library_podcasts(limit=limit)
            return json.dumps(podcasts, indent=2)
            
        elif action == BrowseActions.GET_PODCAST_EPISODES:
            if not playlist_id: return "Error: playlist_id is required."
            episodes = yt.get_podcast(playlist_id, limit=limit)
            return json.dumps(episodes, indent=2)
            
        return "Error: Unknown browse action."
