import os
import sys
import json
import time
import socket
import base64
import urllib.request
import subprocess

from test_location_fraud_suite import CdpClient, find_chrome

def capture_card():
    chrome_bin = find_chrome()
    port = 9335
    user_data = os.path.abspath("temp_chrome_card_shot")
    os.makedirs(user_data, exist_ok=True)

    cmd = [
        chrome_bin,
        f"--remote-debugging-port={port}",
        f"--user-data-dir={user_data}",
        "--headless=new",
        "--window-size=1280,1100",
        "--disable-gpu",
        "http://127.0.0.1:5500/my1.html"
    ]

    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(3.5)

    try:
        req = urllib.request.urlopen(f"http://127.0.0.1:{port}/json/list")
        tabs = json.loads(req.read().decode('utf-8'))
        tab = [t for t in tabs if "my1.html" in t.get("url", "")][0]
        cdp = CdpClient(tab["webSocketDebuggerUrl"])
        cdp.send("Runtime.enable")
        cdp.send("Page.enable")
        time.sleep(1.0)

        cdp.evaluate("""
        (async () => {
            let waited = 0;
            while ((typeof window.showPage === 'undefined' || typeof window.performLocalLocationVerification === 'undefined') && waited < 12000) {
                await new Promise(r => setTimeout(r, 200));
                waited += 200;
            }
            if (typeof window.showPage !== 'undefined') {
                window.showPage('submit');
                await new Promise(r => setTimeout(r, 800));
            }

            // Populate sample location verification with slight distance
            const curLat = 26.8467, curLon = 80.9462, curAcc = 18.0;
            const repLat = 26.8471, repLon = 80.9468;
            window.userCurrentGps = { latitude: curLat, longitude: curLon, accuracy: curAcc, timestamp: Date.now() };
            const res = window.performLocalLocationVerification(curLat, curLon, curAcc, repLat, repLon, "Ranchi");
            window.renderLocationVerificationCard(res, curLat, curLon, repLat, repLon, "Ranchi");
            window.toggleLocationExplanation();

            const card = document.getElementById('aiLocationVerificationCard');
            if (card) {
                card.scrollIntoView({ behavior: 'instant', block: 'center' });
            }
        })()
        """)
        time.sleep(1.0)

        shot_path = os.path.abspath(r"C:\Users\asus\.gemini\antigravity-ide\brain\57345f01-d21a-448b-b929-d46569f3a509\location_verification_card_view.png")
        cdp.capture_screenshot(shot_path)
        print("Captured:", shot_path)
        cdp.close()
    finally:
        try:
            proc.terminate()
            proc.wait(timeout=2.0)
        except:
            pass

if __name__ == "__main__":
    capture_card()
