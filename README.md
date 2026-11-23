# 🎵 YouTube Music MCP Server

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Model Context Protocol](https://img.shields.io/badge/MCP-Standard-8A2BE2.svg?style=flat)](https://modelcontextprotocol.io/)
[![FastMCP](https://img.shields.io/badge/FastMCP-Server-00C7B7.svg?style=flat)](https://github.com/jlowin/fastmcp)
[![YouTube Music](https://img.shields.io/badge/YouTube_Music-API-FF0000.svg?style=flat&logo=youtubemusic&logoColor=white)](https://music.youtube.com/)

> **Turn Claude Desktop into your personal AI music manager.**  
> Seamlessly control YouTube Music through natural conversation — search tracks, curate playlists, fetch lyrics, clean duplicates, analyze listening habits, import/export libraries, and discover personalized music recommendations.

---

## 🌟 Highlights

- **🗣️ 100% Natural Language Control:** No API keys or technical syntax required. Just talk to Claude: *"Create a workout playlist with high-tempo rock songs"*, *"Clean up all duplicate tracks in my Favorites"*, or *"What are the lyrics to Bohemian Rhapsody?"*
- **⚡ 25+ Powerful Capabilities:** Search, playlist curation, library management, song credits, global charts, mood playlists, history tracking, and local file import/export.
- **✨ Clean Markdown Formatting:** Instead of messy JSON blobs, responses are neatly formatted as Markdown tables, cards, and structured lists optimized for conversational AI.
- **🎯 Smart Fuzzy Matching:** Add or remove songs simply by name. The server searches and scores candidates using confidence algorithms to select the exact right track.
- **🔒 Privacy-First & Local:** Runs entirely on your local machine via STDIO. Your session tokens never leave your computer.

---

## 🛠️ Feature Matrix

| Module | MCP Tool | What You Can Do |
|---|---|---|
| **🔍 Search** | `search_music` | Search songs, albums, artists, playlists, or music videos with clean tabular summaries. |
| **📑 Playlist Control** | `manage_playlist` | Create, rename, delete, duplicate, merge, or empty playlists. Add/remove songs by title with smart fuzzy scoring. |
| **🧹 Playlist Cleanup** | `manage_playlist` | Automatically detect and remove duplicate tracks or unavailable/deleted videos. Includes a `dry_run` preview mode. |
| **🌐 Music Browsing** | `browse_music` | Browse library playlists, track listings, artist profiles, album discography, explore home feed, and fetch radio/up-next queues. |
| **🎤 Lyrics & Credits** | `browse_music` | Extract full synchronized/plain song lyrics and detailed production credits (composers, producers, performers). |
| **📈 Charts & Moods** | `browse_music` | Explore trending global/regional charts, mood categories (*Chill, Workout, Focus, Party*), and mood-tailored playlists. |
| **❤️ Library** | `manage_library` | Like/unlike songs, save/remove albums, follow/unfollow artists, and retrieve your liked songs collection. |
| **💾 Import & Export** | `export_playlist`<br>`import_playlist` | Export playlists to **CSV, Excel (.xlsx), JSON, or TXT**. Import tracklists from files with confidence threshold matching. |
| **🤖 AI Recommendations**| `recommend_music` | Generate tailored music suggestions based on your recent listening history, liked songs, or a specific playlist. |
| **🔐 Auth Status** | `get_auth_status` | Check authentication health, cookie validity, and connected account name directly from the chat. |

---

## 📋 Prerequisites

- **Python 3.10** or higher
- **Claude Desktop** (or Cursor / Windsurf / any MCP-compatible client)
- A **Google / YouTube Music account** (Free or Premium)
- Any modern web browser (*Chrome, Brave, Edge, or Firefox*)

---

## 🚀 Quickstart Guide

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/ytmusic-mcp.git
cd ytmusic-mcp
```

### 2. Set Up Virtual Environment & Dependencies

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS / Linux:
source venv/bin/activate
# On Windows (Command Prompt):
# venv\Scripts\activate.bat
# On Windows (PowerShell):
# .\venv\Scripts\Activate.ps1

# Install required packages
pip install -r requirements.txt
```

---

## 🔐 Authentication (One-Time Setup)

To interact with your personal library, playlists, and history, the server authenticates using standard browser session headers:

### Step 1: Copy your cURL Request from YouTube Music

1. Open **Google Chrome** (or Edge/Brave/Firefox) and navigate to [music.youtube.com](https://music.youtube.com).
2. Ensure you are **logged in** to your YouTube Music account.
3. Open **Developer Tools** (`F12` or `Cmd + Option + I` on Mac / `Ctrl + Shift + I` on Windows).
4. Click on the **Network** tab.
5. In the filter box, type `browse`.
6. Click on any playlist or navigate to your Library so network requests appear.
7. Look for a request named `browse` (e.g. `browse?prettyPrint=false`).
8. **Right-click** on that request → **Copy** → **Copy as cURL** (bash / POSIX).

> [!TIP]
> Make sure to choose **Copy as cURL**, not *Copy as fetch* or *Copy URL*.

### Step 2: Generate `browser.json`

1. Create a file named `req-hed.md` in the project root:
   ```bash
   touch req-hed.md
   ```
2. Paste the copied cURL command into `req-hed.md` and save the file.
3. Run the generation script:
   ```bash
   python generate_browser_json.py
   ```
4. You should see:
   ```text
   ✅ Found session cookies successfully!
   🎉 Created 'browser.json' with 11 fields
   👉 You can now connect your MCP client (Claude Desktop / Cursor) and start jamming!
   ```

> [!IMPORTANT]
> `browser.json` and `req-hed.md` contain your private session cookies. They are strictly excluded by `.gitignore`. **Never commit or share these files publicly.**

---

## 🖥️ Connecting to Claude Desktop

Configure Claude Desktop to launch the server over STDIO.

### Config File Location

- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux:** `~/.config/Claude/claude_desktop_config.json`

### Configuration Snippet

Open or create `claude_desktop_config.json` and add the `ytmusic` entry under `mcpServers`:

#### macOS / Linux
```json
{
  "mcpServers": {
    "ytmusic": {
      "command": "/ABSOLUTE/PATH/TO/ytmusic-mcp/venv/bin/python",
      "args": [
        "/ABSOLUTE/PATH/TO/ytmusic-mcp/server.py"
      ]
    }
  }
}
```

#### Windows
```json
{
  "mcpServers": {
    "ytmusic": {
      "command": "C:\\path\\to\\ytmusic-mcp\\venv\\Scripts\\python.exe",
      "args": [
        "C:\\path\\to\\ytmusic-mcp\\server.py"
      ]
    }
  }
}
```

> [!NOTE]
> Replace `/ABSOLUTE/PATH/TO/ytmusic-mcp/` with the actual path where you cloned this repository. You can run `pwd` inside the repository directory on Mac/Linux to get the exact path.

### Restart Claude Desktop

Completely quit Claude Desktop (**`Cmd + Q`** on Mac or right-click the system tray icon on Windows → **Quit**) and reopen it.

---

## 💬 Sample Prompts & Use Cases

Once connected, simply talk to Claude naturally! Here are examples you can try right away:

### 🔍 Search & Exploration
- *"Search for the latest acoustic songs by Ed Sheeran."*
- *"Show me the top 10 trending music tracks on global charts."*
- *"Show me mood playlists for late-night focus and coding."*
- *"Tell me about the artist Daft Punk and list their popular albums."*

### 🎧 Playlist Management
- *"List all my saved playlists."*
- *"What tracks are in my 'Road Trip' playlist?"*
- *"Create a new playlist named 'Lo-Fi Chill Zone' with description 'Relaxing beats to study to'."*
- *"Add the song 'Starboy' by The Weeknd to my 'Lo-Fi Chill Zone' playlist."*
- *"Remove 'Old Town Road' from my 'Party' playlist."*
- *"Duplicate my 'Gym 2024' playlist and call it 'Gym 2025'."*

### 🧹 Cleaning Up Playlists
- *"Check my 'Driving Hits' playlist for duplicate songs and remove them."*
- *"Perform a dry run cleanup on my 'Favorites' playlist to see what unavailable tracks exist."*

### 📜 Lyrics & Song Info
- *"Get the lyrics for Bohemian Rhapsody by Queen."*
- *"Who produced and wrote the song 'Blinding Lights'?"*
- *"Find related songs to 'Get Lucky' by Daft Punk and start a radio queue."*

### 💾 Backup, Import & Export
- *"Export my 'Workout' playlist to an Excel file at ~/Desktop/workout.xlsx."*
- *"Export my liked songs to a JSON file."*
- *"I have a file `songs.txt` with song names. Import them into a new playlist called 'Imported Classics'."*

### 💡 AI Recommendations
- *"Analyze my recent listening history and recommend 10 new tracks I might like."*
- *"Based on my liked songs, suggest 5 lesser-known indie artists."*

### 🔐 Authentication Status
- *"Check my YouTube Music connection status."*

---

## 📂 Project Architecture

```text
ytmusic-mcp/
├── server.py                  # MCP server entry point (FastMCP STDIO)
├── generate_browser_json.py   # cURL parser to generate browser.json
├── requirements.txt           # Python package dependencies
├── req-hed.example.md         # Template guide for copying cURL headers
├── .gitignore                 # Keeps credentials & virtualenv safe
└── ytmusic_mcp/               # Core server package
    ├── client.py              # Authenticated YTMusic client manager
    ├── models.py              # Pydantic schemas & Action Enums
    ├── format_output.py       # Markdown table & list output formatters
    ├── helper.py              # Fuzzy song matching & confidence scoring
    └── tools/                 # Modular FastMCP tool handlers
        ├── search.py          # search_music tool
        ├── playlist.py        # manage_playlist tool
        ├── browse.py          # browse_music tool (22 browse actions)
        ├── library.py         # manage_library tool
        ├── recommend.py       # recommend_music tool
        ├── import_export.py   # import_playlist & export_playlist tools
        └── auth.py            # get_auth_status tool
```

