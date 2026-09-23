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

def run_tests():
    chrome_path = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
    if not os.path.exists(chrome_path):
        chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

    proc = subprocess.Popen([
        chrome_path,
        "--headless=new",
        "--remote-debugging-port=9226",
        "--disable-gpu",
        "--no-sandbox",
        "http://127.0.0.1:5500/my1.html"
    ])

    try:
        time.sleep(3.0)
        with urllib.request.urlopen("http://127.0.0.1:9226/json") as resp:
            tabs = json.loads(resp.read().decode("utf-8"))
        
        tab = [t for t in tabs if "my1.html" in t.get("url", "")][0]
        ws_url = tab["webSocketDebuggerUrl"]
        parts = ws_url.replace("ws://", "").split("/", 1)
        hp = parts[0].split(":")
        ws = SimpleWebSocket(hp[0], int(hp[1]), "/" + parts[1])

        ws.send_text(json.dumps({"id": 1, "method": "Runtime.enable"}))
        ws.send_text(json.dumps({"id": 2, "method": "Console.enable"}))

        # Check step by step in the browser
        js_code = """
        (async function() {
            let waited = 0;
            while (typeof showPage === 'undefined' && waited < 8000) {
                await new Promise(r => setTimeout(r, 200));
                waited += 200;
            }
            if (typeof showPage === 'undefined') return { error: 'Timed out waiting for my1.js' };

            // Navigate to Submit Problem
            showPage('submit');
            await new Promise(r => setTimeout(r, 1000));

            // 1. API key resolution
            const keyResolved = getGoogleMapsApiKey();
            const envObj = window.ENV || {};

            // 2. Google Maps state
            const scriptTag = document.getElementById('googleMapsApiScript');
            const scriptSrc = scriptTag ? scriptTag.src : null;
            const isGoogleLoaded = !!(window.google && window.google.maps && window.google.maps.Map);
            const diagPill = document.getElementById('diagErrorCodePill');
            const diagDesc = document.getElementById('diagErrorDesc');
            const diagNotice = document.getElementById('mapDiagnosticNotice');
            const diagVisible = diagNotice ? (diagNotice.style.display !== 'none') : false;

            // 3. Leaflet fallback state
            const leafletMapExists = !!problemLeafletMap;
            const leafletTilesCount = document.querySelectorAll('.leaflet-tile').length;
            const problemMarkerExists = !!leafletProblemMarker;

            // 4. Test Native Browser GPS (independent of Google Maps)
            const hasGeo = 'geolocation' in navigator;
            let currentPositionResult = null;
            let isSecureContext = window.isSecureContext;

            try {
                currentPositionResult = await new Promise((resolve) => {
                    const timeoutId = setTimeout(() => {
                        resolve({ status: 'TIMEOUT', message: 'getCurrentPosition timed out after 2000ms' });
                    }, 2000);

                    navigator.geolocation.getCurrentPosition(
                        (pos) => {
                            clearTimeout(timeoutId);
                            resolve({
                                status: 'SUCCESS',
                                lat: pos.coords.latitude,
                                lon: pos.coords.longitude,
                                accuracy: pos.coords.accuracy
                            });
                        },
                        (err) => {
                            clearTimeout(timeoutId);
                            const names = { 1: 'PERMISSION_DENIED', 2: 'POSITION_UNAVAILABLE', 3: 'TIMEOUT' };
                            resolve({
                                status: 'ERROR',
                                code: err.code,
                                codeName: names[err.code] || 'UNKNOWN_ERROR',
                                message: err.message
                            });
                        },
                        { timeout: 1500, enableHighAccuracy: false, maximumAge: 60000 }
                    );
                });
            } catch (e) {
                currentPositionResult = { status: 'EXCEPTION', message: e.message };
            }

            // 5. Test watchPosition availability
            let watchResult = null;
            try {
                if (typeof navigator.geolocation.watchPosition === 'function') {
                    const testWatchId = navigator.geolocation.watchPosition(
                        () => {},
                        () => {},
                        { timeout: 1000 }
                    );
                    navigator.geolocation.clearWatch(testWatchId);
                    watchResult = { supported: true, cleared: true };
                } else {
                    watchResult = { supported: false };
                }
            } catch (e) {
                watchResult = { supported: false, error: e.message };
            }

            // 6. Test Problem Marker Draggable & Click
            let markerDraggable = false;
            if (leafletProblemMarker && leafletProblemMarker.dragging) {
                markerDraggable = leafletProblemMarker.dragging.enabled();
            }

            return {
                keyResolved: keyResolved ? (keyResolved.substring(0, 4) + '... (length: ' + keyResolved.length + ')') : 'EMPTY',
                envObj: envObj,
                scriptSrc: scriptSrc,
                isGoogleLoaded: isGoogleLoaded,
                diagVisible: diagVisible,
                diagCode: diagPill ? diagPill.textContent : '',
                diagDesc: diagDesc ? diagDesc.textContent : '',
                leafletMapExists: leafletMapExists,
                leafletTilesCount: leafletTilesCount,
                problemMarkerExists: problemMarkerExists,
                markerDraggable: markerDraggable,
                isSecureContext: isSecureContext,
                hasGeo: hasGeo,
                currentPositionResult: currentPositionResult,
                watchResult: watchResult
            };
        })()
        """

        ws.send_text(json.dumps({
            "id": 10,
            "method": "Runtime.evaluate",
            "params": {
                "expression": js_code,
                "awaitPromise": True,
                "returnByValue": True
            }
        }))

        start = time.time()
        result = None
        while time.time() - start < 8.0:
            msg = ws.recv_text(timeout=1.0)
            if not msg:
                continue
            data = json.loads(msg)
            if data.get("id") == 10:
                result = data.get("result", {}).get("result", {}).get("value")
                break

        print("\n================== FULL RUNNING BROWSER DIAGNOSTICS ==================")
        print(json.dumps(result, indent=2))
        return result

    finally:
        try:
            proc.terminate()
        except Exception:
            pass

if __name__ == "__main__":
    run_tests()
