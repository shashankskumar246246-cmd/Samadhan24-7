import socket
import base64
import os
import json
import subprocess
import time
import urllib.request

chrome_path = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
if not os.path.exists(chrome_path):
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

proc = subprocess.Popen([
    chrome_path,
    "--headless=new",
    "--remote-debugging-port=9222",
    "--window-size=1280,900",
    "--disable-gpu",
    "--no-sandbox",
    "http://127.0.0.1:8000/my1.html"
])

try:
    time.sleep(2.0)
    with urllib.request.urlopen("http://127.0.0.1:9222/json") as resp:
        tabs = json.loads(resp.read().decode("utf-8"))
    page_tab = next(t for t in tabs if "my1.html" in t.get("url", ""))
    ws_url = page_tab["webSocketDebuggerUrl"]
    parts = ws_url.replace("ws://", "").split("/", 1)
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((parts[0].split(":")[0], int(parts[0].split(":")[1])))
    key = base64.b64encode(os.urandom(16)).decode('ascii')
    s.sendall(f"GET /{parts[1]} HTTP/1.1\r\nHost: {parts[0]}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n".encode('utf-8'))
    s.recv(4096)
    
    def send_text(text):
        data = text.encode('utf-8')
        length = len(data)
        frame = bytearray([0x81])
        if length <= 125: frame.append(0x80 | length)
        elif length <= 65535:
            frame.append(0x80 | 126)
            frame.extend(length.to_bytes(2, 'big'))
        else:
            frame.append(0x80 | 127)
            frame.extend(length.to_bytes(8, 'big'))
        mask = os.urandom(4)
        frame.extend(mask)
        frame.extend(bytearray(b ^ mask[i % 4] for i, b in enumerate(data)))
        s.sendall(frame)

    def recv_text():
        s.settimeout(5.0)
        try: d = s.recv(2)
        except: return None
        if not d: return None
        length = d[1] & 0x7F
        if length == 126: length = int.from_bytes(s.recv(2), 'big')
        elif length == 127: length = int.from_bytes(s.recv(8), 'big')
        p = b""
        while len(p) < length:
            c = s.recv(min(length - len(p), 65536))
            if not c: break
            p += c
        return p.decode('utf-8', errors='ignore')

    send_text(json.dumps({"id": 1, "method": "Runtime.enable"}))
    send_text(json.dumps({"id": 2, "method": "Page.enable"}))
    time.sleep(1.0)

    # Let's run a test where showPage('submit') is called, then Leaflet invalidateSize is called
    send_text(json.dumps({
        "id": 10,
        "method": "Runtime.evaluate",
        "params": {
            "expression": """
            new Promise((resolve) => {
                const navSubmit = document.querySelector('.sidebar .nav-link[onclick*=\"submit\"]');
                if (navSubmit) navSubmit.click();
                else showPage('submit');

                setTimeout(() => {
                    const m = document.getElementById('problemLocationMap');
                    if (m) m.scrollIntoView();

                    setTimeout(() => {
                        const imgs = Array.from(document.querySelectorAll('.leaflet-tile'));
                        const loaded = imgs.filter(img => img.complete && img.naturalWidth > 0).length;
                        resolve({
                            activeSection: document.querySelector('.page.active-page') ? document.querySelector('.page.active-page').id : null,
                            totalTiles: imgs.length,
                            loadedTiles: loaded,
                            mapWidth: m ? m.offsetWidth : 0,
                            mapHeight: m ? m.offsetHeight : 0
                        });
                    }, 1500);
                }, 400);
            })
            """,
            "awaitPromise": True,
            "returnByValue": True
        }
    }))

    while True:
        m = recv_text()
        if not m: break
        d = json.loads(m)
        if d.get("id") == 10:
            print("RESULT:", json.dumps(d.get("result", {}).get("result", {}).get("value"), indent=2))
            break

    # Take screenshot
    send_text(json.dumps({
        "id": 20,
        "method": "Page.captureScreenshot",
        "params": {"format": "png"}
    }))

    while True:
        m = recv_text()
        if not m: break
        d = json.loads(m)
        if d.get("id") == 20:
            img_b64 = data = d["result"]["data"]
            out_path = r"C:\Users\asus\.gemini\antigravity-ide\brain\7a387ca2-5d8c-4190-aa95-008c020cefbc\leaflet_full_test.png"
            with open(out_path, "wb") as f:
                f.write(base64.b64decode(img_b64))
            print("Screenshot saved to:", out_path)
            break

finally:
    proc.terminate()
