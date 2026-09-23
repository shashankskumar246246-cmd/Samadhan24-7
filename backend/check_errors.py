import socket
import base64
import os
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
        frame = bytearray([0x81])
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

    def recv_text(self, timeout=3.0):
        self.s.settimeout(timeout)
        try:
            data = self.s.recv(2)
        except TimeoutError:
            return None
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
    
    page_tab = next(t for t in tabs if "my1.html" in t.get("url", "") or t.get("type") == "page")
    ws_url = page_tab["webSocketDebuggerUrl"]
    parts = ws_url.replace("ws://", "").split("/", 1)
    host, port = parts[0].split(":")
    path = "/" + parts[1]

    ws = SimpleWebSocket(host, int(port), path)
    ws.send_text(json.dumps({"id": 1, "method": "Runtime.enable"}))

    time.sleep(0.5)
    # Evaluate a simple test
    ws.send_text(json.dumps({
        "id": 10,
        "method": "Runtime.evaluate",
        "params": {
            "expression": """
            (function() {
                try {
                    showPage('submit');
                    const mapEl = document.getElementById('problemLocationMap');
                    return {
                        success: true,
                        mapEl: !!mapEl,
                        width: mapEl ? mapEl.offsetWidth : 0,
                        height: mapEl ? mapEl.offsetHeight : 0,
                        tileCount: document.querySelectorAll('.leaflet-tile').length,
                        hasGoogle: !!(window.google && window.google.maps)
                    };
                } catch(e) {
                    return { error: e.toString(), stack: e.stack };
                }
            })()
            """,
            "returnByValue": True
        }
    }))

    while True:
        msg = ws.recv_text(timeout=4.0)
        if not msg:
            break
        data = json.loads(msg)
        if data.get("id") == 10:
            print("EVAL RESULT:", json.dumps(data.get("result", {}), indent=2))
            break

finally:
    proc.terminate()
