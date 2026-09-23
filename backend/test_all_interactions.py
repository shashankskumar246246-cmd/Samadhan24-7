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
    print("Connecting to tab URL:", page_tab.get("url"))
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

    # Wait for page to fully load
    time.sleep(2.0)

    # Test interactions
    send_text(json.dumps({
        "id": 10,
        "method": "Runtime.evaluate",
        "params": {
            "expression": """
            (function() {
                const results = {};
                
                // 1. Navigate to submit
                showPage('submit');
                results.pageSwitched = document.getElementById('submit').classList.contains('active-page');
                
                // 2. Check map elements
                const mapEl = document.getElementById('problemLocationMap');
                results.mapWidth = mapEl ? mapEl.offsetWidth : 0;
                results.mapHeight = mapEl ? mapEl.offsetHeight : 0;
                
                // 3. Test applyLocationCoordinates directly
                if (typeof applyLocationCoordinates === 'function') {
                    applyLocationCoordinates(23.3441, 85.3096, true, 'test_click');
                    results.appliedLat = document.getElementById('latitude').value;
                    results.appliedLon = document.getElementById('longitude').value;
                    results.districtVal = document.getElementById('district').value;
                }
                
                // 4. Test useCurrentLocation function existence
                results.hasUseCurrentLoc = typeof useCurrentLocation === 'function';
                results.hasCopyGps = typeof copyCurrentGpsToProblemLocation === 'function';
                results.hasToggleLive = typeof toggleLiveLocation === 'function';
                results.hasConfirmLoc = typeof confirmSelectedLocation === 'function';

                // 5. Test leaflet map state
                results.hasProblemLeafletMap = typeof problemLeafletMap !== 'undefined' && problemLeafletMap !== null;
                if (results.hasProblemLeafletMap) {
                    const center = problemLeafletMap.getCenter();
                    results.leafletCenter = center ? [center.lat, center.lng] : null;
                    results.leafletZoom = problemLeafletMap.getZoom();
                }

                // 6. Test Google map state
                results.hasProblemGoogleMap = typeof problemGoogleMap !== 'undefined' && problemGoogleMap !== null;

                return results;
            })()
            """,
            "returnByValue": True
        }
    }))

    while True:
        m = recv_text()
        if not m: break
        d = json.loads(m)
        if d.get("id") == 10:
            print("Full D:", json.dumps(d, indent=2))
            break

finally:
    proc.terminate()
