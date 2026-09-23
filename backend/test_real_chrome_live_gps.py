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

print("Launching Chrome against http://127.0.0.1:5500/my1.html...")
proc = subprocess.Popen([
    chrome_path,
    "--headless=new",
    "--remote-debugging-port=9223",
    "--disable-gpu",
    "--no-sandbox",
    "http://127.0.0.1:5500/my1.html"
])

try:
    time.sleep(3.0)
    with urllib.request.urlopen("http://127.0.0.1:9223/json") as resp:
        tabs = json.loads(resp.read().decode("utf-8"))
    
    matching = [t for t in tabs if "my1.html" in t.get("url", "")]
    if not matching:
        time.sleep(1.5)
        with urllib.request.urlopen("http://127.0.0.1:9223/json") as resp:
            tabs = json.loads(resp.read().decode("utf-8"))
        matching = [t for t in tabs if "my1.html" in t.get("url", "")]
    
    page_tab = matching[0]
    ws_url = page_tab["webSocketDebuggerUrl"]
    print("Attached to tab:", page_tab["url"])

    parts = ws_url.replace("ws://", "").split("/", 1)
    host_port = parts[0].split(":")
    host = host_port[0]
    port = int(host_port[1])
    path = "/" + parts[1]

    ws = SimpleWebSocket(host, port, path)
    print("WebSocket connection established with Chrome CDP!")

    ws.send_text(json.dumps({"id": 1, "method": "Runtime.enable"}))
    ws.send_text(json.dumps({"id": 2, "method": "Console.enable"}))

    # Evaluate navigation and GPS interaction on Live Server
    eval_script = """
    (async function() {
        try {
            let waited = 0;
            while (typeof showPage === 'undefined' && waited < 10000) {
                await new Promise(r => setTimeout(r, 200));
                waited += 200;
            }
            if (typeof showPage === 'undefined') return { error: 'Timed out waiting for showPage' };

            // 1. Navigate to Submit Problem
            showPage('submit');
            await new Promise(r => setTimeout(r, 1200));

            const mapEl = document.getElementById('problemLocationMap');
            const diagEl = document.getElementById('mapDiagnosticNotice');
            const originEl = document.getElementById('diagCurrentOrigin');
            const codePill = document.getElementById('diagErrorCodePill');
            const copyBtn = document.getElementById('btnCopyGpsToProblem');

            // 2. Mock Geolocation for browser environment
            window.navigator.geolocation.getCurrentPosition = function(success, error, options) {
                success({
                    coords: {
                        latitude: 23.3441,
                        longitude: 85.3096,
                        accuracy: 14.5
                    },
                    timestamp: Date.now()
                });
            };

            // 3. Click Use My Current Location
            useCurrentLocation();
            await new Promise(r => setTimeout(r, 500));

            const coordsText = document.getElementById('coordinatesText');
            const accBadge = document.getElementById('gpsAccuracyBadge');
            const telemetryText = document.getElementById('locTelemetryText');
            const confLat = document.getElementById('confLatText');

            const hasLeafletTiles = document.querySelectorAll('.leaflet-tile').length > 0;
            const hasUserGpsPin = !!document.querySelector('.leaflet-user-gps-pin');

            // 4. Test explicit copy to problem location
            copyCurrentGpsToProblemLocation();
            await new Promise(r => setTimeout(r, 500));
            const problemLatAfterCopy = document.getElementById('latitude').value;
            const districtAfterCopy = document.getElementById('district').value;

            return {
                url: window.location.href,
                activePage: document.querySelector('.page.active-page') ? document.querySelector('.page.active-page').id : 'NONE',
                mapVisible: mapEl && mapEl.offsetWidth > 0,
                diagVisible: diagEl && diagEl.style.display !== 'none',
                diagCode: codePill ? codePill.textContent : '',
                diagOrigin: originEl ? originEl.textContent : '',
                copyBtnVisible: copyBtn && copyBtn.style.display !== 'none',
                coordsText: coordsText ? coordsText.textContent : '',
                accBadgeText: accBadge ? accBadge.textContent.trim() : '',
                telemetryText: telemetryText ? telemetryText.textContent : '',
                hasLeafletTiles: hasLeafletTiles,
                hasUserGpsPin: hasUserGpsPin,
                problemLatAfterCopy: problemLatAfterCopy,
                districtAfterCopy: districtAfterCopy
            };
        } catch(e) {
            return { error: e.message, stack: e.stack };
        }
    })()
    """

    ws.send_text(json.dumps({
        "id": 10,
        "method": "Runtime.evaluate",
        "params": {
            "expression": eval_script,
            "awaitPromise": True,
            "returnByValue": True
        }
    }))

    while True:
        msg = ws.recv_text(timeout=10.0)
        if not msg:
            break
        data = json.loads(msg)
        if data.get("id") == 10:
            result = data.get("result", {}).get("result", {}).get("value")
            print("\nREAL CHROME TEST RESULTS ON PORT 5500:")
            print(json.dumps(result, indent=2))
            break

    # Capture a visual screenshot
    ws.send_text(json.dumps({"id": 20, "method": "Page.captureScreenshot", "params": {"format": "png"}}))
    while True:
        msg = ws.recv_text(timeout=5.0)
        if not msg:
            break
        data = json.loads(msg)
        if data.get("id") == 20:
            img_b64 = data["result"]["data"]
            out_path = r"C:\Users\asus\.gemini\antigravity-ide\brain\57345f01-d21a-448b-b929-d46569f3a509\live_gps_chrome_verified.png"
            with open(out_path, "wb") as f:
                f.write(base64.b64decode(img_b64))
            print("Verified Chrome Screenshot saved to:", out_path)
            break

finally:
    try:
        proc.terminate()
    except Exception:
        pass
