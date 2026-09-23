import subprocess
import time
import json
import urllib.request
import re

# Launch Chrome with remote debugging on port 9222
chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
import os
if not os.path.exists(chrome_path):
    chrome_path = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
if not os.path.exists(chrome_path):
    # try find in local app data
    local = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe")
    if os.path.exists(local):
        chrome_path = local

print("Using chrome:", chrome_path)

# Let's run chrome with remote debugging to inspect http://127.0.0.1:8000/my1.html
cmd = [
    chrome_path,
    "--headless=new",
    "--remote-debugging-port=9222",
    "--disable-gpu",
    "--no-sandbox",
    "http://127.0.0.1:8000/my1.html"
]

proc = subprocess.Popen(cmd)
try:
    time.sleep(2)
    # query version
    with urllib.request.urlopen("http://127.0.0.1:9222/json") as resp:
        tabs = json.loads(resp.read().decode("utf-8"))
        print("Open tabs:", len(tabs))
        ws_url = tabs[0].get("webSocketDebuggerUrl")
        print("WebSocket URL:", ws_url)
finally:
    proc.terminate()
