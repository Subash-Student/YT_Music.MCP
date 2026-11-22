import os
import sys
import re
import json
from ytmusicapi import YTMusic

# Cache instance so we don't re-authenticate on every tool call
_ytmusic_instance = None

def get_ytmusic() -> YTMusic:
    """
    Returns an authenticated YTMusic instance using browser.json if available.
    Otherwise, returns an unauthenticated public instance.
    """
    global _ytmusic_instance
    if _ytmusic_instance:
        return _ytmusic_instance

    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(current_dir)
    auth_file = os.path.join(project_dir, "browser.json")
    
    if os.path.exists(auth_file):
        try:
            yt = YTMusic(auth_file)
            # Override request timeout to 5 seconds to prevent network blackholes/hangs
            from functools import partial
            yt._session.request = partial(yt._session.request, timeout=5)
            
            _ytmusic_instance = yt
            try:
                # Retrieve account info to confirm who is authenticated
                info = yt.get_account_info()
                account_name = info.get("accountName", "Unknown Account")
                print(f"✅ Successfully authenticated to YouTube Music as: {account_name}", file=sys.stderr)
            except Exception as auth_err:
                print(f"⚠️ Authenticated client initialized, but account verification failed: {auth_err}", file=sys.stderr)
            return _ytmusic_instance
        except Exception as e:
            print(f"❌ Failed to parse '{auth_file}': {e}", file=sys.stderr)

    # Fallback to unauthenticated public client
    print("⚠️ Starting unauthenticated public client (browser.json not found or invalid)", file=sys.stderr)
    _ytmusic_instance = YTMusic()
    return _ytmusic_instance

def reset_authentication():
    """Clears the cached YTMusic instance to force re-authentication on the next call."""
    global _ytmusic_instance
    _ytmusic_instance = None

def parse_curl_to_browser_json(curl_command: str) -> dict:
    """Parses a cURL command string and extracts headers for browser.json."""
    headers = {}
    
    # 1. Match -H 'Key: Value' or -H "Key: Value" or --header 'Key: Value'
    header_pattern = r'(?:-H|--header)\s+[\'"]([^\'"]+?)[\'"]'
    for match in re.finditer(header_pattern, curl_command):
        header_line = match.group(1)
        if ":" in header_line:
            key, val = header_line.split(":", 1)
            headers[key.strip().lower()] = val.strip()
            
    # 2. Match -b 'cookie' or -b "cookie" or --cookie 'cookie'
    cookie_pattern = r'(?:-b|--cookie)\s+[\'"]([^\'"]+?)[\'"]'
    cookie_match = re.search(cookie_pattern, curl_command)
    if cookie_match:
        headers['cookie'] = cookie_match.group(1)
        
    # List of fields required/recommended by ytmusicapi
    required_fields = [
        "cookie", "x-goog-authuser", "x-goog-visitor-id", 
        "x-origin", "x-youtube-client-name", "x-youtube-client-version", 
        "accept", "accept-language", "authorization", 
        "content-type", "user-agent"
    ]
    
    return {k: headers[k] for k in required_fields if k in headers}