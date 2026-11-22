import json
import csv
import openpyxl
from pathlib import Path
from mcp.server.fastmcp import FastMCP
from ytmusic_mcp.client import get_ytmusic
from ytmusic_mcp.models import FileFormat
from ytmusic_mcp.helper import process_and_add_tracks

def register_import_export_tools(mcp: FastMCP):
    """Registers import/export tools with the FastMCP server."""
    
    @mcp.tool()
    def export_playlist(
        playlist_id: str,
        file_path: str,
        format: FileFormat
    ) -> str:
        """
        Export a YouTube Music playlist's tracks to a local file (CSV, JSON, TXT, Excel).
        
        Args:
            playlist_id: The ID of the playlist to export. REQUIRED.
            file_path: Absolute or relative path to save the file. REQUIRED.
            format: Format to save as (csv, json, txt, excel). REQUIRED.
        """
        if not playlist_id or not file_path or not format:
            return "Error: playlist_id, file_path, and format are all required."

        yt = get_ytmusic()
        playlist = yt.get_playlist(playlist_id, limit=None)
        tracks = playlist.get("tracks", [])
        
        if not tracks:
            return "Error: Playlist is empty or not found."
            
        path = Path(file_path).resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        
        formatted_tracks = []
        for t in tracks:
            artists_str = ", ".join([a.get("name", "Unknown") for a in t.get("artists", [])])
            formatted_tracks.append({
                "title": t.get("title", "Unknown"),
                "artists": artists_str,
                "album": t.get("album", {}).get("name", "Unknown") if t.get("album") else "Unknown",
                "duration": t.get("duration", "0:00"),
                "videoId": t.get("videoId", "")
            })
            
        if format == FileFormat.JSON:
            path.write_text(json.dumps(formatted_tracks, indent=2), encoding="utf-8")
        elif format == FileFormat.TXT:
            lines = [f"{t['title']} - {t['artists']}" for t in formatted_tracks]
            path.write_text("\n".join(lines), encoding="utf-8")
        elif format == FileFormat.CSV:
            with path.open(mode="w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["title", "artists", "album", "duration", "videoId"])
                writer.writeheader()
                writer.writerows(formatted_tracks)
        elif format == FileFormat.EXCEL:
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Exported Playlist"
            ws.append(["Title", "Artists", "Album", "Duration", "VideoID"])
            for t in formatted_tracks:
                ws.append([t["title"], t["artists"], t["album"], t["duration"], t["videoId"]])
            wb.save(path)
            
        return json.dumps({
            "success": True,
            "message": f"Successfully exported {len(formatted_tracks)} tracks to '{path}'"
        }, indent=2)

    @mcp.tool()
    def import_playlist(
        playlist_name_or_id: str,
        file_path: str,
        format: FileFormat,
        min_confidence: float = 0.5,
        dry_run: bool = False
    ) -> str:
        """
        Import songs from a local file (CSV, JSON, TXT, Excel) and add them to a playlist.
        
        Args:
            playlist_name_or_id: Name of new playlist or ID of existing. REQUIRED.
            file_path: Path to the file containing tracks. REQUIRED.
            format: Format of the file (csv, json, txt, excel). REQUIRED.
            min_confidence: Confidence score threshold (0.0 - 1.0) for search matching. Default 0.5.
            dry_run: If True, simulates the import without actually adding tracks.
        """
        if not playlist_name_or_id or not file_path or not format:
            return "Error: playlist_name_or_id, file_path, and format are all required."

        yt = get_ytmusic()
        path = Path(file_path).resolve()
        
        if not path.exists():
            return f"Error: File '{file_path}' does not exist."
            
        tracks = []
        
        if format == FileFormat.JSON:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, str):
                        tracks.append(item)
                    elif isinstance(item, dict):
                        t_name = item.get("title") or item.get("name")
                        a_name = item.get("artists") or item.get("artist")
                        if t_name:
                            tracks.append(f"{t_name} - {a_name}" if a_name else t_name)
        elif format == FileFormat.TXT:
            tracks = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        elif format == FileFormat.CSV:
            with path.open(mode="r", encoding="utf-8") as f:
                reader = csv.reader(f)
                header = next(reader, None)
                if header:
                    header_lower = [h.lower().strip() for h in header]
                    title_idx = next((i for i, h in enumerate(header_lower) if "title" in h or "name" in h), 0)
                    artist_idx = next((i for i, h in enumerate(header_lower) if "artist" in h), -1)
                    for row in reader:
                        if len(row) > title_idx:
                            t_val = row[title_idx].strip()
                            a_val = row[artist_idx].strip() if (artist_idx != -1 and len(row) > artist_idx) else ""
                            if t_val:
                                tracks.append(f"{t_val} - {a_val}" if a_val else t_val)
        elif format == FileFormat.EXCEL:
            wb = openpyxl.load_workbook(path, data_only=True)
            ws = wb.active
            header = [str(cell.value).lower().strip() if cell.value else "" for cell in ws[1]]
            title_idx = next((i for i, h in enumerate(header) if "title" in h or "name" in h), 0)
            artist_idx = next((i for i, h in enumerate(header) if "artist" in h), -1)
            for row in ws.iter_rows(min_row=2, values_only=True):
                if len(row) > title_idx and row[title_idx]:
                    t_val = str(row[title_idx]).strip()
                    a_val = str(row[artist_idx]).strip() if (artist_idx != -1 and len(row) > artist_idx and row[artist_idx]) else ""
                    if t_val:
                        tracks.append(f"{t_val} - {a_val}" if a_val else t_val)
                        
        if not tracks:
            return "Error: No tracks parsed from the import file."
            
        target_id = playlist_name_or_id
        if not dry_run and not playlist_name_or_id.startswith("PL"):
            target_id = yt.create_playlist(playlist_name_or_id, "Imported Playlist")
            
        if dry_run:
            target_id = f"DRY_RUN_TARGET_({target_id})"
            
        report = process_and_add_tracks(
            yt=yt, target_id=target_id, tracks=tracks, min_confidence=min_confidence, dry_run=dry_run
        )
        
        return json.dumps(report, indent=2)
