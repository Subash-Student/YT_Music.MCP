import json
from mcp.server.fastmcp import FastMCP
from ytmusic_mcp.client import get_ytmusic
from ytmusic_mcp.models import PlaylistActions
from ytmusic_mcp.helper import process_and_add_tracks, calculate_match_score

def register_playlist_tools(mcp: FastMCP):
    """Registers playlist management tools with the FastMCP server."""
    
    @mcp.tool()
    def manage_playlist(
        action: PlaylistActions,
        playlist_id: str = "",
        playlist_name: str = "",
        description: str = "",
        song_query: str = "",
        dry_run: bool = False
    ) -> str:
        """
        Manage YouTube Music playlists. Create, delete, rename, duplicate, merge, or clean up playlists.
        Also handles adding or removing specific songs by searching.
        
        Args:
            action: Action to perform (e.g. 'create', 'delete', 'rename', 'add_song', 'remove_song', 'cleanup_all', etc.). REQUIRED.
            playlist_id: ID of the playlist. REQUIRED for most actions except 'create'.
            playlist_name: New name for the playlist. REQUIRED for 'create', 'rename', 'duplicate'.
            description: Description for the playlist. Optional.
            song_query: The name of the song to search for and add/remove. REQUIRED for 'add_song' and 'remove_song'.
            dry_run: If True for cleanup or remove_song, will only return what WOULD be done.
        """
        yt = get_ytmusic()
        
        if not action:
            return "Error: action is required."
            
        # 1. CREATE
        if action == PlaylistActions.CREATE:
            if not playlist_name: return "Error: playlist_name is required for creating."
            response = yt.create_playlist(playlist_name, description)
            return json.dumps({"success": True, "message": f"Playlist '{playlist_name}' created.", "playlist_id": response})
            
        # 2. DELETE
        elif action == PlaylistActions.DELETE:
            if not playlist_id: return "Error: playlist_id is required."
            response = yt.delete_playlist(playlist_id)
            return json.dumps({"success": True, "message": "Playlist deleted.", "response": response})
            
        # 3. RENAME
        elif action == PlaylistActions.RENAME:
            if not playlist_id or not playlist_name: return "Error: playlist_id and playlist_name are required."
            response = yt.edit_playlist(playlist_id, title=playlist_name)
            return json.dumps({"success": True, "message": f"Playlist renamed to '{playlist_name}'.", "response": response})
            
        # 4. UPDATE DESCRIPTION
        elif action == PlaylistActions.UPDATE_DESCRIPTION:
            if not playlist_id or not description: return "Error: playlist_id and description are required."
            response = yt.edit_playlist(playlist_id, description=description)
            return json.dumps({"success": True, "message": "Playlist description updated.", "response": response})
            
        # 5. CLEAR (Remove all tracks)
        elif action == PlaylistActions.CLEAR:
            if not playlist_id: return "Error: playlist_id is required."
            playlist = yt.get_playlist(playlist_id, limit=None)
            tracks = playlist.get("tracks", [])
            if not tracks:
                return json.dumps({"success": True, "message": "Playlist is already empty."})
            if dry_run:
                return json.dumps({"success": True, "message": f"Dry Run: Would remove {len(tracks)} tracks."})
            response = yt.remove_playlist_items(playlist_id, tracks)
            return json.dumps({"success": True, "message": f"Removed {len(tracks)} tracks.", "response": response})
            
        # 6. DUPLICATE
        elif action == PlaylistActions.DUPLICATE:
            if not playlist_id or not playlist_name: return "Error: playlist_id and playlist_name are required."
            new_id = yt.create_playlist(playlist_name, description, source_playlist=playlist_id)
            return json.dumps({"success": True, "message": f"Playlist duplicated to '{playlist_name}'.", "new_playlist_id": new_id})
            
        # 7. MERGE (Needs two playlist IDs, we'll use description as the source playlist ID to merge from for now)
        elif action == PlaylistActions.MERGE:
            source_id = description
            if not playlist_id or not source_id: return "Error: Target playlist_id and Source playlist_id (passed via description arg) are required."
            source_playlist = yt.get_playlist(source_id, limit=None)
            tracks = source_playlist.get("tracks", [])
            video_ids = [t["videoId"] for t in tracks if t.get("videoId")]
            if dry_run:
                return json.dumps({"success": True, "message": f"Dry Run: Would add {len(video_ids)} tracks to {playlist_id}."})
            if video_ids:
                response = yt.add_playlist_items(playlist_id, video_ids)
                return json.dumps({"success": True, "message": f"Merged {len(video_ids)} tracks.", "response": response})
            return json.dumps({"success": True, "message": "Source playlist has no tracks."})
            
        # 8. REMOVE DUPLICATES
        elif action == PlaylistActions.REMOVE_DUPLICATES:
            if not playlist_id: return "Error: playlist_id is required."
            playlist = yt.get_playlist(playlist_id, limit=None)
            tracks = playlist.get("tracks", [])
            seen_video_ids = set()
            duplicates = []
            for track in tracks:
                vid = track.get("videoId")
                if not vid: continue
                if vid in seen_video_ids:
                    duplicates.append(track)
                else:
                    seen_video_ids.add(vid)
            if not duplicates:
                return json.dumps({"success": True, "message": "No duplicates found."})
            if dry_run:
                return json.dumps({"success": True, "message": f"Dry Run: Would remove {len(duplicates)} duplicates."})
            response = yt.remove_playlist_items(playlist_id, duplicates)
            return json.dumps({"success": True, "message": f"Removed {len(duplicates)} duplicates.", "response": response})
            
        # 9. REMOVE UNAVAILABLE
        elif action == PlaylistActions.REMOVE_UNAVAILABLE:
            if not playlist_id: return "Error: playlist_id is required."
            playlist = yt.get_playlist(playlist_id, limit=None)
            tracks = playlist.get("tracks", [])
            unavailable = [t for t in tracks if not t.get("isAvailable", True) or not t.get("videoId")]
            if not unavailable:
                return json.dumps({"success": True, "message": "No unavailable tracks found."})
            if dry_run:
                return json.dumps({"success": True, "message": f"Dry Run: Would remove {len(unavailable)} unavailable tracks."})
            response = yt.remove_playlist_items(playlist_id, unavailable)
            return json.dumps({"success": True, "message": f"Removed {len(unavailable)} unavailable tracks.", "response": response})
            
        # 10. CLEANUP ALL
        elif action == PlaylistActions.CLEANUP_ALL:
            if not playlist_id: return "Error: playlist_id is required."
            playlist = yt.get_playlist(playlist_id, limit=None)
            tracks = playlist.get("tracks", [])
            seen_video_ids = set()
            to_remove = []
            for track in tracks:
                vid = track.get("videoId")
                if not vid or not track.get("isAvailable", True):
                    to_remove.append(track)
                    continue
                if vid in seen_video_ids:
                    to_remove.append(track)
                else:
                    seen_video_ids.add(vid)
            if not to_remove:
                return json.dumps({"success": True, "message": "Playlist is already clean."})
            if dry_run:
                return json.dumps({"success": True, "message": f"Dry Run: Would remove {len(to_remove)} tracks (duplicates + unavailable)."})
            response = yt.remove_playlist_items(playlist_id, to_remove)
            return json.dumps({"success": True, "message": f"Removed {len(to_remove)} tracks (duplicates + unavailable).", "response": response})

        # 11. ADD SONG
        elif action == PlaylistActions.ADD_SONG:
            if not playlist_id or not song_query: return "Error: playlist_id and song_query are required."
            report = process_and_add_tracks(yt, playlist_id, [song_query], min_confidence=0.5, dry_run=dry_run)
            return json.dumps(report, indent=2)

        # 12. REMOVE SONG
        elif action == PlaylistActions.REMOVE_SONG:
            if not playlist_id or not song_query: return "Error: playlist_id and song_query are required."
            playlist = yt.get_playlist(playlist_id, limit=None)
            tracks = playlist.get("tracks", [])
            
            # Find best match in playlist
            best_score = 0.0
            best_track = None
            
            for t in tracks:
                title = t.get("title", "")
                artists = [a.get("name") if isinstance(a, dict) else str(a) for a in t.get("artists", [])]
                score = calculate_match_score(song_query, title, artists)
                if score > best_score:
                    best_score = score
                    best_track = t
                    
            if best_score < 0.3 or not best_track:
                return json.dumps({"success": False, "message": f"Could not find a song matching '{song_query}' in the playlist."})
                
            if dry_run:
                return json.dumps({
                    "success": True, 
                    "message": f"Dry Run: Would remove '{best_track.get('title')}' (Score: {best_score:.2f})."
                })
                
            response = yt.remove_playlist_items(playlist_id, [best_track])
            return json.dumps({
                "success": True,
                "message": f"Removed '{best_track.get('title')}' from the playlist.",
                "response": response
            })
            
        return "Error: Unknown action."
