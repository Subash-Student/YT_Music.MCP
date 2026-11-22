# Paste your YouTube Music cURL command here

Copy the request as cURL from your browser's Developer Tools (Network tab -> filter 'browse' -> right-click -> Copy as cURL), and paste the entire command below replacing this content.

Example structure:
```bash
curl 'https://music.youtube.com/youtubei/v1/browse?prettyPrint=false' \
  -H 'accept: */*' \
  -H 'accept-language: en-US,en;q=0.9' \
  -H 'authorization: SAPISIDHASH ...' \
  -b 'VISITOR_INFO1_LIVE=...; SID=...; __Secure-3PAPISID=...;' \
  -H 'user-agent: Mozilla/5.0 ...' \
  -H 'x-origin: https://music.youtube.com'
```

Then run:
```bash
python generate_browser_json.py
```
This will automatically extract all necessary session cookies & headers into `browser.json`.
