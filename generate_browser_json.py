import os
import sys
import re
import json

def parse_curl_file(file_path: str = "req-hed.md", output_path: str = "browser.json"):
    """
    Parses a cURL command from a file and extracts headers & cookies required
    by ytmusicapi, saving them to browser.json.
    """
    if not os.path.exists(file_path):
        print(f"❌ Error: '{file_path}' not found!")
        print(f"👉 Please create '{file_path}' and paste your copied cURL command from music.youtube.com into it.")
        print("   (Refer to req-hed.example.md or the README for step-by-step instructions)")
        sys.exit(1)

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    if not content.strip() or "curl" not in content.lower():
        print(f"⚠️ Warning: '{file_path}' appears to be empty or does not contain a valid cURL command.")
        print("   Please paste the full cURL command copied from the Network tab.")
        sys.exit(1)

    headers = {}

    # Match -H 'Key: Value' or -H "Key: Value" or --header 'Key: Value' or --header "Key: Value"
    header_pattern = r'(?:-H|--header)\s+[\'"]([^\'"]+?)[\'"]'
    for match in re.finditer(header_pattern, content):
        header_line = match.group(1)
        if ":" in header_line:
            key, val = header_line.split(":", 1)
            headers[key.strip().lower()] = val.strip()

    # Match -b 'cookie_string' or -b "cookie_string" or --cookie '...'
    cookie_pattern = r'(?:-b|--cookie)\s+[\'"]([^\'"]+?)[\'"]'
    cookie_match = re.search(cookie_pattern, content)
    if cookie_match:
        headers["cookie"] = cookie_match.group(1).strip()
    elif "cookie" not in headers:
        # Check if cookie was passed as a header: -H "cookie: ..."
        cookie_header_pattern = r'(?:-H|--header)\s+[\'"]cookie:\s*(.+?)[\'"]'
        ch_match = re.search(cookie_header_pattern, content, re.IGNORECASE)
        if ch_match:
            headers["cookie"] = ch_match.group(1).strip()

    # Fields required or recommended by ytmusicapi
    required_fields = [
        "cookie", "x-goog-authuser", "x-goog-visitor-id", 
        "x-origin", "x-youtube-client-name", "x-youtube-client-version", 
        "accept", "accept-language", "authorization", 
        "content-type", "user-agent"
    ]

    output = {k: headers[k] for k in required_fields if k in headers}

    if "cookie" not in output:
        print("⚠️ Warning: Could not find any 'cookie' header in the provided cURL command.")
        print("   Make sure you copied a request from an active session where you are logged into YouTube Music.")
    else:
        print("✅ Found session cookies successfully!")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print(f"🎉 Created '{output_path}' with {len(output)} fields: {list(output.keys())}")
    print("👉 You can now connect your MCP client (Claude Desktop / Cursor) and start jamming!")

if __name__ == "__main__":
    target_file = sys.argv[1] if len(sys.argv) > 1 else "req-hed.md"
    parse_curl_file(target_file)
