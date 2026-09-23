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
    "about:blank"
])

try:
    time.sleep(1.5)
    with urllib.request.urlopen("http://127.0.0.1:9222/json") as resp:
        tabs = json.loads(resp.read().decode("utf-8"))
    page_tab = tabs[0]
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
        s.settimeout(2.0)
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
    send_text(json.dumps({"id": 3, "method": "Log.enable"}))
    send_text(json.dumps({"id": 4, "method": "Network.enable"}))

    time.sleep(0.5)

    # Navigate to http://127.0.0.1:8000/my1.html
    print("Navigating to http://127.0.0.1:8000/my1.html ...")
    send_text(json.dumps({
        "id": 5,
        "method": "Page.navigate",
        "params": {"url": "http://127.0.0.1:8000/my1.html"}
    }))

    start = time.time()
    while time.time() - start < 6.0:
        m = recv_text()
        if not m: continue
        d = json.loads(m)
        method = d.get("method", "")
        if method == "Runtime.exceptionThrown":
            exp = d.get("params", {}).get("exceptionDetails", {})
            print("\n*** EXCEPTION THROWN ***")
            print("Text:", exp.get("text"))
            print("Description:", exp.get("exception", {}).get("description"))
            print("URL:", exp.get("url"))
            print("Line:", exp.get("lineNumber"), "Col:", exp.get("columnNumber"))
        elif method == "Runtime.consoleAPICalled":
            args = d.get("params", {}).get("args", [])
            print("[CONSOLE]", d.get("params", {}).get("type"), " ".join(str(a.get("value", "")) for a in args))
        elif method == "Network.responseReceived":
            resp = d.get("params", {}).get("response", {})
            print("[NETWORK]", resp.get("status"), resp.get("url"))

finally:
    proc.terminate()
