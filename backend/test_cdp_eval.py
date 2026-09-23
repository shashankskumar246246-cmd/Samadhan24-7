import socket
import base64
import os
import hashlib
import json
import subprocess
import time
import urllib.request

class SimpleWebSocket:
    def __init__(self, host, port, path):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((host, port))
        key = base64.b64encode(os.urandom(16)).decode('ascii')
        handshake = (
            f"GET {path} HTTP/1.1\r\n"
            f"Host: {host}:{port}\r\n"
            f"Upgrade: websocket\r\n"
            f"Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\n"
            f"Sec-WebSocket-Version: 13\r\n\r\n"
        )
        self.s.sendall(handshake.encode('utf-8'))
        resp = self.s.recv(4096).decode('utf-8', errors='ignore')
        if "101" not in resp:
            raise Exception("WebSocket handshake failed:\n" + resp)

    def send_text(self, text):
        data = text.encode('utf-8')
        length = len(data)
        frame = bytearray([0x81]) # FIN + text opcode
        if length <= 125:
            frame.append(0x80 | length)
        elif length <= 65535:
            frame.append(0x80 | 126)
            frame.extend(length.to_bytes(2, 'big'))
        else:
            frame.append(0x80 | 127)
            frame.extend(length.to_bytes(8, 'big'))
        mask = os.urandom(4)
        frame.extend(mask)
        masked = bytearray(b ^ mask[i % 4] for i, b in enumerate(data))
        frame.extend(masked)
        self.s.sendall(frame)

    def recv_text(self, timeout=5.0):
        self.s.settimeout(timeout)
        data = self.s.recv(2)
        if not data:
            return None
        b1, b2 = data[0], data[1]
        length = b2 & 0x7F
        if length == 126:
            length = int.from_bytes(self.s.recv(2), 'big')
        elif length == 127:
            length = int.from_bytes(self.s.recv(8), 'big')
        payload = b""
        while len(payload) < length:
            chunk = self.s.recv(min(length - len(payload), 65536))
            if not chunk:
                break
            payload += chunk
        return payload.decode('utf-8', errors='ignore')

    def close(self):
        self.s.close()

chrome_path = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
if not os.path.exists(chrome_path):
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

print("Starting Chrome...")
proc = subprocess.Popen([
    chrome_path,
    "--headless=new",
    "--remote-debugging-port=9222",
    "--disable-gpu",
    "--no-sandbox",
    "http://127.0.0.1:8000/my1.html"
])

try:
    time.sleep(2.5)
    with urllib.request.urlopen("http://127.0.0.1:9222/json") as resp:
        tabs = json.loads(resp.read().decode("utf-8"))
    
    matching = [t for t in tabs if "my1.html" in t.get("url", "")]
    if not matching:
        time.sleep(1.0)
        with urllib.request.urlopen("http://127.0.0.1:9222/json") as resp:
            tabs = json.loads(resp.read().decode("utf-8"))
        matching = [t for t in tabs if "my1.html" in t.get("url", "")]
    page_tab = matching[0]
    ws_url = page_tab["webSocketDebuggerUrl"]
    print("Found tab:", page_tab["url"])

    # parse host, port, path
    # ws://127.0.0.1:9222/devtools/page/...
    parts = ws_url.replace("ws://", "").split("/", 1)
    host_port = parts[0].split(":")
    host = host_port[0]
    port = int(host_port[1])
    path = "/" + parts[1]

    ws = SimpleWebSocket(host, port, path)
    print("Connected to Chrome via WebSocket!")

    # Enable console and runtime
    ws.send_text(json.dumps({"id": 1, "method": "Console.enable"}))
    ws.send_text(json.dumps({"id": 2, "method": "Runtime.enable"}))

    # Evaluate showing submit page and getting status
    call_eval = {
        "id": 10,
        "method": "Runtime.evaluate",
        "params": {
            "expression": """
            (async function() {
                try {
                    let waited = 0;
                    while (typeof showPage === 'undefined' && waited < 10000) {
                        await new Promise(r => setTimeout(r, 200));
                        waited += 200;
                    }
                    if (typeof showPage === 'undefined') return { error: 'Timed out waiting for showPage' };

                    showPage('submit');
                    await new Promise(r => setTimeout(r, 1200));

                    const mapEl = document.getElementById('problemLocationMap');
                    const diagEl = document.getElementById('mapDiagnosticNotice');
                    const badgeEl = document.getElementById('activeMapProviderBadge');
                    const imgs = Array.from(document.querySelectorAll('.leaflet-tile'));
                    const loaded = imgs.filter(img => img.complete && img.naturalWidth > 0).length;

                    return {
                        activePage: document.querySelector('.page.active-page') ? document.querySelector('.page.active-page').id : 'NONE',
                        mapElExists: !!mapEl,
                        mapWidth: mapEl ? mapEl.offsetWidth : -1,
                        mapHeight: mapEl ? mapEl.offsetHeight : -1,
                        hasLeafletMap: typeof problemLeafletMap !== 'undefined' && problemLeafletMap !== null,
                        totalTiles: imgs.length,
                        loadedTiles: loaded,
                        diagVisible: diagEl ? (window.getComputedStyle(diagEl).display !== 'none') : false,
                        diagCode: document.getElementById('diagErrorCodePill') ? document.getElementById('diagErrorCodePill').textContent : '',
                        badgeText: badgeEl ? badgeEl.innerText.trim() : ''
                    };
                } catch(e) {
                    return { error: e.toString() };
                }
            })()
            """,
            "awaitPromise": True,
            "returnByValue": True
        }
    }
    ws.send_text(json.dumps(call_eval))

    while True:
        msg = ws.recv_text(timeout=10.0)
        if not msg:
            break
        data = json.loads(msg)
        if data.get("id") == 10:
            print("\nEVAL RESULT:")
            print(json.dumps(data.get("result", {}).get("result", {}).get("value"), indent=2))
            break
    # Scroll to show map and diagnostic notice
    ws.send_text(json.dumps({
        "id": 11,
        "method": "Runtime.evaluate",
        "params": {
            "expression": "window.scrollTo(0, 500);"
        }
    }))
    time.sleep(1.0)

    ws.send_text(json.dumps({"id": 20, "method": "Page.captureScreenshot", "params": {"format": "png"}}))

    while True:
        msg = ws.recv_text(timeout=5.0)
        if not msg:
            break
        data = json.loads(msg)
        if data.get("id") == 20:
            img_b64 = data["result"]["data"]
            out_path = r"C:\Users\asus\.gemini\antigravity-ide\brain\7a387ca2-5d8c-4190-aa95-008c020cefbc\map_working_screenshot.png"
            with open(out_path, "wb") as f:
                f.write(base64.b64decode(img_b64))
            print("Screenshot saved to:", out_path)
            break

finally:
    proc.terminate()
