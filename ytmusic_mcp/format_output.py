import json

def format_track_list(tracks: list[dict], title: str = "Tracks") -> str:
    """Formats a list of tracks into a clean Markdown table."""
    if not tracks:
        return f"### {title}\nNo tracks found."
        
    lines = [f"### {title}\n"]
    lines.append("| Title | Artist | Album | Duration | Video ID |")
    lines.append("|---|---|---|---|---|")
    
    for t in tracks:
        t_title = str(t.get("title", "Unknown")).replace("|", "\\|")
        
        artists = t.get("artists", [])
        if isinstance(artists, list):
            artists_str = ", ".join([a.get("name", str(a)) for a in artists if isinstance(a, dict) or isinstance(a, str)])
        else:
            artists_str = str(artists)
        artists_str = artists_str.replace("|", "\\|")
        
        album_data = t.get("album", {})
        album_name = album_data.get("name", "Unknown") if isinstance(album_data, dict) else "Unknown"
        album_name = album_name.replace("|", "\\|")
        
        duration = t.get("duration", "N/A")
        video_id = t.get("videoId", "N/A")
        
        lines.append(f"| {t_title} | {artists_str} | {album_name} | {duration} | {video_id} |")
        
    return "\n".join(lines)

def format_playlist_list(playlists: list[dict], title: str = "Playlists") -> str:
    """Formats a list of playlists into a clean Markdown list."""
    if not playlists:
        return f"### {title}\nNo playlists found."
        
    lines = [f"### {title}\n"]
    for p in playlists:
        p_title = p.get("title", "Unknown")
        p_id = p.get("playlistId", "Unknown")
        track_count = p.get("count", p.get("trackCount", "Unknown"))
        lines.append(f"- **{p_title}** (ID: {p_id}) - {track_count} tracks")
        
    return "\n".join(lines)

def format_artist(artist: dict) -> str:
    """Formats detailed artist information."""
    if not artist:
        return "Artist not found."
        
    name = artist.get("name", "Unknown")
    desc = artist.get("description", "No description available.")
    views = artist.get("views", "N/A")
    subscribers = artist.get("subscribers", "N/A")
    
    lines = [
        f"# {name}",
        f"**Subscribers:** {subscribers} | **Views:** {views}",
        f"\n**Description:**\n{desc}\n"
    ]
    
    # Top Songs
    songs = artist.get("songs", {}).get("results", [])
    if songs:
        lines.append(format_track_list(songs, title="Top Songs"))
        
    # Albums
    albums = artist.get("albums", {}).get("results", [])
    if albums:
        lines.append("\n### Albums")
        for a in albums:
            a_title = a.get("title", "Unknown")
            a_id = a.get("browseId", "Unknown")
            a_year = a.get("year", "N/A")
            lines.append(f"- **{a_title}** ({a_year}) [ID: {a_id}]")
            
    return "\n".join(lines)

def format_album(album: dict) -> str:
    """Formats detailed album information."""
    if not album:
        return "Album not found."
        
    title = album.get("title", "Unknown")
    artists = ", ".join([a.get("name", "Unknown") for a in album.get("artists", [])])
    track_count = album.get("trackCount", "N/A")
    duration = album.get("duration", "N/A")
    year = album.get("year", "N/A")
    
    lines = [
        f"# {title}",
        f"**Artist:** {artists}",
        f"**Year:** {year} | **Tracks:** {track_count} | **Total Duration:** {duration}\n"
    ]
    
    tracks = album.get("tracks", [])
    if tracks:
        lines.append(format_track_list(tracks, title="Tracklist"))
        
    return "\n".join(lines)

def format_history(history: list[dict]) -> str:
    """Formats listening history into a clean Markdown table."""
    return format_track_list(history, title="Listening History")

def format_search_results(results: list[dict], query: str) -> str:
    """Formats search results based on the result types (songs, albums, etc.)."""
    if not results:
        return f"No results found for '{query}'."
        
    # We can handle generic results, but since YTMusic returns mixed types, 
    # we'll try to extract common fields or fallback to JSON for unknown structures.
    # Usually, if we search for songs, we get a list of dicts that look like tracks.
    is_track_list = all("videoId" in item for item in results[:3] if isinstance(item, dict))
    if is_track_list:
        return format_track_list(results, title=f"Search Results for '{query}'")
        
    # If they are playlists
    is_playlist_list = all("playlistId" in item or "browseId" in item for item in results[:3] if isinstance(item, dict) and "videoId" not in item)
    if is_playlist_list:
        lines = [f"### Search Results for '{query}'\n"]
        for p in results:
            title = p.get("title", "Unknown")
            pid = p.get("playlistId", p.get("browseId", "Unknown"))
            author = p.get("author", "Unknown")
            lines.append(f"- **{title}** by {author} (ID: {pid})")
        return "\n".join(lines)
        
    # Fallback to json dump but pretty
    return f"### Search Results for '{query}'\n```json\n" + json.dumps(results, indent=2) + "\n```"
