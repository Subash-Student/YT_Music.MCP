import json
from ytmusicapi import YTMusic

def process_and_add_tracks(
    yt: YTMusic,
    target_id: str,
    tracks: list[str],
    min_confidence: float,
    dry_run: bool
) -> dict:
    """
    Core business logic to search, score, and add list of queries to a playlist.
    Returns a dictionary report.
    """
    added_tracks = []
    skipped_tracks = []
    video_ids_to_add = []
    
    # 1. Iterate and match
    for query in tracks:
        results = yt.search(query, filter="songs", limit=3)
        
        if not results:
            skipped_tracks.append({"query": query, "reason": "No search results found"})
            continue
            
        top_match = results[0]
        title = top_match.get("title", "")
        artists = top_match.get("artists", [])
        video_id = top_match.get("videoId")
        
        if not video_id:
            skipped_tracks.append({"query": query, "reason": "Match had no videoId"})
            continue
            
        score = calculate_match_score(query, title, artists)
        
        if score >= min_confidence:
            video_ids_to_add.append(video_id)
            added_tracks.append({
                "query": query,
                "matched_title": title,
                "matched_artists": [a.get("name") if isinstance(a, dict) else str(a) for a in artists],
                "video_id": video_id,
                "confidence_score": round(score, 2)
            })
        else:
            skipped_tracks.append({
                "query": query,
                "matched_title": title,
                "confidence_score": round(score, 2),
                "reason": f"Low confidence match (< {min_confidence})"
            })
            
    # 2. Execute additions
    api_response = None
    if not dry_run and video_ids_to_add and not target_id.startswith("DRY_RUN"):
        api_response = yt.add_playlist_items(target_id, video_ids_to_add)
        
    return {
        "success": True,
        "dry_run": dry_run,
        "target_playlist_id": target_id,
        "summary": {
            "total_requested": len(tracks),
            "successfully_matched": len(added_tracks),
            "skipped_ambiguous": len(skipped_tracks)
        },
        "added_tracks": added_tracks,
        "skipped_tracks": skipped_tracks,
        "api_response": api_response
    }



def calculate_match_score(query: str, title: str, artists: list) -> float:
    """
    Calculates a confidence score (0.0 to 1.0) comparing the search query
    to the returned song title and artist names.
    """
    # 1. Tokenize query into unique lowercased words
    query_words = set(query.lower().replace("-", " ").split())
    if not query_words:
        return 0.0
        
    # 2. Combine title and artist names into a single target text string
    target_text = title.lower()
    for artist in artists:
        if isinstance(artist, dict) and "name" in artist:
            target_text += " " + artist["name"].lower()
        elif isinstance(artist, str):
            target_text += " " + artist.lower()
            
    # Tokenize target text
    target_words = set(target_text.replace("-", " ").split())
    
    # 3. Calculate ratio of matched words
    matched_words = query_words.intersection(target_words)
    return len(matched_words) / len(query_words)
