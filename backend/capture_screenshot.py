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

    def recv_text(self, timeout=10.0):
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
    time.sleep(2.5)
    with urllib.request.urlopen("http://127.0.0.1:9222/json") as resp:
        tabs = json.loads(resp.read().decode("utf-8"))
    
    page_tab = next(t for t in tabs if "my1.html" in t.get("url", "") or t.get("type") == "page")
    ws_url = page_tab["webSocketDebuggerUrl"]

    parts = ws_url.replace("ws://", "").split("/", 1)
    host, port = parts[0].split(":")
    path = "/" + parts[1]

    ws = SimpleWebSocket(host, int(port), path)
    ws.send_text(json.dumps({"id": 1, "method": "Runtime.enable"}))
    ws.send_text(json.dumps({"id": 2, "method": "Page.enable"}))

    time.sleep(0.5)
    # Switch to submit page
    ws.send_text(json.dumps({
        "id": 3,
        "method": "Runtime.evaluate",
        "params": {
            "expression": "showPage('submit'); const m = document.getElementById('problemLocationMap'); if(m) m.scrollIntoView();"
        }
    }))
    time.sleep(1.5)

    # Take screenshot
    ws.send_text(json.dumps({
        "id": 4,
        "method": "Page.captureScreenshot",
        "params": {"format": "png"}
    }))

    while True:
        msg = ws.recv_text(timeout=5.0)
        if not msg:
            break
        data = json.loads(msg)
        if data.get("id") == 4:
            img_b64 = data["result"]["data"]
            out_path = r"C:\Users\asus\.gemini\antigravity-ide\brain\7a387ca2-5d8c-4190-aa95-008c020cefbc\submit_page_screenshot.png"
            with open(out_path, "wb") as f:
                f.write(base64.b64decode(img_b64))
            print("Screenshot saved to:", out_path)
            break
finally:
    proc.terminate()
