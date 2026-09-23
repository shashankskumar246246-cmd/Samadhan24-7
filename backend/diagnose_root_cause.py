import os
import sys
import json
import time
import socket
import base64
import urllib.request
import subprocess

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
        try:
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
        except Exception:
            return None

    def close(self):
        self.s.close()

def main():
    print("=== STEP 1: IDENTIFY ACTUAL PROJECT TYPE ===")
    has_package_json = os.path.exists("package.json")
    has_vite_config = os.path.exists("vite.config.js") or os.path.exists("vite.config.ts")
    has_node_modules = os.path.exists("node_modules")
    print(f"package.json present: {has_package_json}")
    print(f"vite.config present: {has_vite_config}")
    print(f"node_modules present: {has_node_modules}")
    project_type = "Plain HTML + CSS + JavaScript" if not (has_package_json or has_vite_config) else "Vite/React"
    print(f"-> PROJECT TYPE: {project_type}")

    print("\n=== STEP 2: FIND WHERE THE GOOGLE API KEY ACTUALLY COMES FROM ===")
    candidates = [
        ("env.js", "env.js"),
        (".env", ".env"),
        (".env.example", ".env.example"),
        ("my1.html", "my1.html"),
        ("backend/app.py", "backend/app.py")
    ]
    key_found = False
    key_source = "None"
    key_length = 0
    key_format = "EMPTY"

    # Check .env
    if os.path.exists(".env"):
        with open(".env", "r", encoding="utf-8") as f:
            for line in f:
                if line.strip().startswith("VITE_GOOGLE_MAPS_API_KEY=") or line.strip().startswith("GOOGLE_MAPS_API_KEY="):
                    val = line.split("=", 1)[1].strip()
                    if val:
                        key_found = True
                        key_source = ".env"
                        key_length = len(val)
                        key_format = "VALID" if (val.startswith("AIza") and len(val) == 39) else ("PLACEHOLDER" if "YOUR" in val else "NON-STANDARD")
                        break

    # Check env.js
    if not key_found and os.path.exists("env.js"):
        with open("env.js", "r", encoding="utf-8") as f:
            content = f.read()
            # Check for strings
            import re
            matches = re.findall(r'VITE_GOOGLE_MAPS_API_KEY\s*=\s*["\']([^"\']*)["\']', content)
            for m in matches:
                if m.strip():
                    key_found = True
                    key_source = "env.js"
                    key_length = len(m.strip())
                    key_format = "VALID" if (m.strip().startswith("AIza") and len(m.strip()) == 39) else ("PLACEHOLDER" if "YOUR" in m.strip() else "NON-STANDARD")
                    break

    print(f"KEY FOUND: {'YES' if key_found else 'NO'}")
    print(f"KEY SOURCE: {key_source}")
    print(f"KEY LENGTH: {key_length}")
    print(f"KEY FORMAT: {key_format}")

    print("\n=== STEP 3, 4, 5, 7, 8: CONNECT TO REAL CHROME CDP (PORT 5500) ===")
    chrome_path = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
    if not os.path.exists(chrome_path):
        chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

    proc = subprocess.Popen([
        chrome_path,
        "--headless=new",
        "--remote-debugging-port=9225",
        "--disable-gpu",
        "--no-sandbox",
        "http://127.0.0.1:5500/my1.html"
    ])

    try:
        time.sleep(3.0)
        with urllib.request.urlopen("http://127.0.0.1:9225/json") as resp:
            tabs = json.loads(resp.read().decode("utf-8"))
        
        tab = [t for t in tabs if "my1.html" in t.get("url", "")][0]
        ws_url = tab["webSocketDebuggerUrl"]
        parts = ws_url.replace("ws://", "").split("/", 1)
        hp = parts[0].split(":")
        ws = SimpleWebSocket(hp[0], int(hp[1]), "/" + parts[1])

        ws.send_text(json.dumps({"id": 1, "method": "Network.enable"}))
        ws.send_text(json.dumps({"id": 2, "method": "Console.enable"}))
        ws.send_text(json.dumps({"id": 3, "method": "Runtime.enable"}))

        # Script to inspect state and test GPS
        eval_script = """
        (async function() {
            let waited = 0;
            while (typeof showPage === 'undefined' && waited < 10000) {
                await new Promise(r => setTimeout(r, 200));
                waited += 200;
            }
            if (typeof showPage === 'undefined') return { error: 'Page load timeout' };

            showPage('submit');
            await new Promise(r => setTimeout(r, 1000));

            // Test 1: Check what key is retrieved
            const resolvedKey = getGoogleMapsApiKey();

            // Test 2: Check Google Maps script element
            const scriptEl = document.getElementById('googleMapsApiScript');
            const scriptSrc = scriptEl ? scriptEl.src : null;

            // Test 3: Check Diagnostic banner DOM
            const diagCode = document.getElementById('diagErrorCodePill') ? document.getElementById('diagErrorCodePill').textContent : '';
            const diagDesc = document.getElementById('diagErrorDesc') ? document.getElementById('diagErrorDesc').textContent : '';

            // Test 4: Check Leaflet fallback
            const hasLeaflet = typeof L !== 'undefined' && !!problemLeafletMap;
            const leafletTilesCount = document.querySelectorAll('.leaflet-tile').length;

            // Test 5: Check Geolocation support on http://127.0.0.1:5500
            const hasGeo = 'geolocation' in navigator;
            let originSecure = window.isSecureContext; // http://127.0.0.1 is treated as a secure context in modern Chrome

            // Test 6: Direct test of navigator.geolocation.getCurrentPosition
            let gpsResult = await new Promise(resolve => {
                if (!hasGeo) return resolve({ supported: false });
                navigator.geolocation.getCurrentPosition(
                    pos => resolve({
                        success: true,
                        lat: pos.coords.latitude,
                        lon: pos.coords.longitude,
                        accuracy: pos.coords.accuracy
                    }),
                    err => resolve({
                        success: false,
                        code: err.code,
                        message: err.message,
                        codeName: err.code === 1 ? 'PERMISSION_DENIED' : (err.code === 2 ? 'POSITION_UNAVAILABLE' : (err.code === 3 ? 'TIMEOUT' : 'UNKNOWN'))
                    }),
                    { timeout: 3000, maximumAge: 0 }
                );
            });

            return {
                resolvedKey: resolvedKey ? `${resolvedKey.substring(0, 4)}... (length: ${resolvedKey.length})` : 'EMPTY',
                resolvedKeyLength: resolvedKey ? resolvedKey.length : 0,
                scriptSrc: scriptSrc,
                diagCode: diagCode,
                diagDesc: diagDesc,
                hasLeaflet: hasLeaflet,
                leafletTilesCount: leafletTilesCount,
                hasGeo: hasGeo,
                originSecure: originSecure,
                origin: window.location.origin,
                gpsResult: gpsResult
            };
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

        res = None
        logs = []
        network_reqs = []
        start_t = time.time()
        while time.time() - start_t < 8.0:
            msg = ws.recv_text(0.5)
            if not msg: continue
            d = json.loads(msg)
            if d.get("id") == 10:
                res = d.get("result", {}).get("result", {}).get("value")
            if d.get("method") == "Console.messageAdded":
                logs.append(d.get("params", {}).get("message", {}).get("text", ""))
            if d.get("method") == "Network.requestWillBeSent":
                url = d.get("params", {}).get("request", {}).get("url", "")
                if "maps.googleapis" in url:
                    network_reqs.append(url)

        print("\n--- BROWSER EVALUATION RESULTS ---")
        print(json.dumps(res, indent=2))
        print("\n--- GOOGLE MAPS REQUESTS SENT ---")
        print(json.dumps(network_reqs, indent=2))
        print("\n--- CONSOLE LOGS ---")
        for l in logs:
            print("  >", l)

    finally:
        proc.terminate()

if __name__ == "__main__":
    main()
