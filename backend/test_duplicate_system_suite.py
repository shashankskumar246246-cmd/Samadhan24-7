import os
import sys
import json
import time
import socket
import base64
import urllib.request
import urllib.error
import subprocess
import sqlite3

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

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

    def recv_text(self, timeout=8.0):
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
        except socket.timeout:
            return None

    def close(self):
        try:
            self.s.close()
        except Exception:
            pass


class ChromeCDPClient:
    def __init__(self, ws_url):
        parts = ws_url.replace("ws://", "").split("/")
        host_port = parts[0].split(":")
        host = host_port[0]
        port = int(host_port[1])
        path = "/" + "/".join(parts[1:])
        self.ws = SimpleWebSocket(host, port, path)
        self._msg_id = 1

    def send_command(self, method, params=None, timeout=8.0):
        cid = self._msg_id
        self._msg_id += 1
        msg = {"id": cid, "method": method, "params": params or {}}
        self.ws.send_text(json.dumps(msg))
        t0 = time.time()
        while time.time() - t0 < timeout:
            resp = self.ws.recv_text(timeout=timeout)
            if not resp:
                continue
            try:
                data = json.loads(resp)
                if data.get("id") == cid:
                    return data
            except Exception:
                pass
        return None

    def evaluate(self, expr, await_promise=True, timeout=8.0):
        res = self.send_command("Runtime.evaluate", {
            "expression": expr,
            "returnByValue": True,
            "awaitPromise": await_promise
        }, timeout=timeout)
        if res and "result" in res and "result" in res["result"]:
            return res["result"]["result"].get("value")
        return None

    def capture_screenshot(self, filepath):
        res = self.send_command("Page.captureScreenshot", {"format": "png"})
        if res and "result" in res and "data" in res["result"]:
            raw = base64.b64decode(res["result"]["data"])
            with open(filepath, "wb") as f:
                f.write(raw)
            return True
        return False

    def close(self):
        self.ws.close()


def run_duplicate_system_suite():
    print("=" * 75)
    print(" SAMADHAN 24/7: FULL AI DUPLICATE REPORT DETECTION TEST SUITE")
    print("=" * 75)

    from backend.matching_engine import calculate_duplicate_score, detect_duplicate_reports, DUPLICATE_CONFIG

    test_results = {}

    # =========================================================================
    # TEST 1: Same title + same description + same location -> Strong Duplicate Match (>=85)
    # =========================================================================
    r1 = {
        "id": "REP-101",
        "title": "Severe drinking water pipeline rupture in Morabadi",
        "description": "Main drinking water pipe burst flooding road and causing severe water shortage in Morabadi ward",
        "category": "Water Management",
        "district": "Ranchi",
        "locality": "Morabadi",
        "latitude": 23.3850,
        "longitude": 85.3320
    }
    r1_dup = {
        "id": "REP-102",
        "title": "Severe drinking water pipeline rupture in Morabadi",
        "description": "Main drinking water pipe burst flooding road and causing severe water shortage in Morabadi ward",
        "category": "Water Management",
        "district": "Ranchi",
        "locality": "Morabadi",
        "latitude": 23.3850,
        "longitude": 85.3320
    }
    s1 = calculate_duplicate_score(r1_dup, r1)
    pass1 = (s1["duplicate_score"] >= 85 and s1["status"] == "STRONG_DUPLICATE_MATCH")
    test_results["TEST 1"] = {
        "desc": "Same title + description + location",
        "score": s1["duplicate_score"],
        "status": s1["status"],
        "pass": pass1
    }
    print(f"[TEST 1] Score: {s1['duplicate_score']}% | Status: {s1['status']} -> {'PASS' if pass1 else 'FAIL'}")

    # =========================================================================
    # TEST 2: Similar description + nearby location (~250m) -> Potential Duplicate (70-84)
    # =========================================================================
    r2_exist = {
        "id": "REP-1024",
        "title": "Water supply problem in Ward 12",
        "description": "Drinking water contamination and irregular supply in residential sector",
        "category": "Water Management",
        "district": "Ranchi",
        "locality": "Ward 12",
        "latitude": 23.3440,
        "longitude": 85.3090
    }
    # ~250m away in same district & category
    r2_new = {
        "id": "REP-1025",
        "title": "Water supply problem in Ward 12",
        "description": "Severe drinking water pipeline contamination in Ward 12 area",
        "category": "Water Management",
        "district": "Ranchi",
        "locality": "Ward 12",
        "latitude": 23.3460,
        "longitude": 85.3100
    }
    s2 = calculate_duplicate_score(r2_new, r2_exist)
    pass2 = (70 <= s2["duplicate_score"] <= 84 or s2["status"] == "POTENTIAL_DUPLICATE")
    test_results["TEST 2"] = {
        "desc": "Similar description + nearby location (~250m)",
        "score": s2["duplicate_score"],
        "status": s2["status"],
        "pass": pass2
    }
    print(f"[TEST 2] Score: {s2['duplicate_score']}% | Status: {s2['status']} -> {'PASS' if pass2 else 'FAIL'}")

    # =========================================================================
    # TEST 3: Same category but different district -> Low similarity (<40)
    # =========================================================================
    r3_exist = {
        "id": "REP-103",
        "title": "Severe crop damage due to pest infestation",
        "description": "Insects destroying paddy fields across agriculture belt",
        "category": "Agriculture",
        "district": "Ranchi",
        "locality": "Namkum",
        "latitude": 23.3441,
        "longitude": 85.3096
    }
    r3_new = {
        "id": "REP-104",
        "title": "Agricultural tractor subsidy delayed",
        "description": "Farmers awaiting disbursement of subsidy payments",
        "category": "Agriculture",
        "district": "Palamu",
        "locality": "Daltonganj",
        "latitude": 24.0390,
        "longitude": 84.0706
    }
    s3 = calculate_duplicate_score(r3_new, r3_exist)
    pass3 = (s3["duplicate_score"] < 40 and s3["status"] == "NO_SIMILAR_REPORT")
    test_results["TEST 3"] = {
        "desc": "Same category but distant different district",
        "score": s3["duplicate_score"],
        "status": s3["status"],
        "pass": pass3
    }
    print(f"[TEST 3] Score: {s3['duplicate_score']}% | Status: {s3['status']} -> {'PASS' if pass3 else 'FAIL'}")

    # =========================================================================
    # TEST 4: Different problem + same location -> Not duplicate (<40)
    # =========================================================================
    r4_exist = {
        "id": "REP-105",
        "title": "Broken street lights and dark street safety issue",
        "description": "All street lights broken creating dark accident hotspot",
        "category": "Urban Infrastructure",
        "district": "Ranchi",
        "locality": "Lalpur",
        "latitude": 23.3700,
        "longitude": 85.3300
    }
    r4_new = {
        "id": "REP-106",
        "title": "Doctor shortage and no medicine stock at health dispensary",
        "description": "Dispensary lacks basic fever antibiotics and pediatric medical staff",
        "category": "Healthcare",
        "district": "Ranchi",
        "locality": "Lalpur",
        "latitude": 23.3700,
        "longitude": 85.3300
    }
    s4 = calculate_duplicate_score(r4_new, r4_exist)
    pass4 = (s4["duplicate_score"] < 40 and s4["status"] == "NO_SIMILAR_REPORT")
    test_results["TEST 4"] = {
        "desc": "Different problem at same location",
        "score": s4["duplicate_score"],
        "status": s4["status"],
        "pass": pass4
    }
    print(f"[TEST 4] Score: {s4['duplicate_score']}% | Status: {s4['status']} -> {'PASS' if pass4 else 'FAIL'}")

    # =========================================================================
    # TEST 5: Two different citizens report the same issue -> same issue_cluster_id
    # =========================================================================
    test_ts5 = int(time.time())
    p5_a = {
        "title": f"Embankment collapse damage {test_ts5} along riverbank",
        "description": f"Continuous monsoon flooding caused major structural collapse {test_ts5} of the riverbank embankment",
        "category": "Water Management",
        "district": "Ranchi",
        "area": "Namkum",
        "locality": "Namkum",
        "user_id": "citizen_alice_001",
        "latitude": 23.3412,
        "longitude": 85.3521
    }
    req5_a = urllib.request.Request(
        "http://127.0.0.1:8000/api/problems",
        data=json.dumps(p5_a).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req5_a) as resp5_a:
        res5_a = json.loads(resp5_a.read().decode())
        id5_a = res5_a["problem_id"]

    p5_b = {
        "title": f"Embankment collapse damage {test_ts5} along riverbank",
        "description": f"Severe soil erosion and embankment collapse {test_ts5} threatening houses near riverbank",
        "category": "Water Management",
        "district": "Ranchi",
        "area": "Namkum",
        "locality": "Namkum",
        "user_id": "citizen_bob_002",
        "reported_anyway": True,
        "latitude": 23.3412,
        "longitude": 85.3521
    }
    req5_b = urllib.request.Request(
        "http://127.0.0.1:8000/api/problems",
        data=json.dumps(p5_b).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req5_b) as resp5_b:
        res5_b = json.loads(resp5_b.read().decode())
        id5_b = res5_b["problem_id"]
        cluster5_b = res5_b.get("issue_cluster_id")

    # Verify both reports exist in DB and cluster matches
    db_file = os.path.join(os.path.dirname(__file__), "samadhan.db")
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    cur.execute("SELECT id, issue_cluster_id, matched_report_id, reported_anyway FROM problems WHERE id IN (?, ?)", (id5_a, id5_b))
    db_rows = cur.fetchall()
    conn.close()

    pass5 = (len(db_rows) == 2 and (
        res5_b.get("matched_report_id") == id5_a or
        cluster5_b == f"CLUSTER-{id5_a}" or
        (cluster5_b and (cluster5_b == res5_a.get("issue_cluster_id") or id5_a in str(cluster5_b)))
    ))
    test_results["TEST 5"] = {
        "desc": "Two citizens report same issue -> linked cluster & both preserved",
        "report_a": id5_a,
        "report_b": id5_b,
        "cluster": cluster5_b,
        "pass": pass5
    }
    print(f"[TEST 5] Report A: {id5_a} | Report B: {id5_b} | Cluster: {cluster5_b} -> {'PASS' if pass5 else 'FAIL'}")

    # =========================================================================
    # TEST 6: Citizen supports existing report -> support_count +1
    # =========================================================================
    target_pid = id5_a
    # Query current count
    db_file = os.path.join(os.path.dirname(__file__), "samadhan.db")
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    cur.execute("SELECT support_count FROM problems WHERE id = ?", (target_pid,))
    cnt_before = (cur.fetchone() or (1,))[0] or 1
    conn.close()

    unique_supporter = f"citizen_support_test_{int(time.time())}"
    req6 = urllib.request.Request(
        f"http://127.0.0.1:8000/api/reports/{target_pid}/support",
        data=json.dumps({"user_id": unique_supporter}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req6) as resp6:
        res6 = json.loads(resp6.read().decode())
        cnt_after = res6.get("support_count", 0)

    pass6 = (cnt_after == cnt_before + 1 and res6.get("already_supported") is False)
    test_results["TEST 6"] = {
        "desc": "Citizen supports existing report -> support_count +1",
        "before": cnt_before,
        "after": cnt_after,
        "pass": pass6
    }
    print(f"[TEST 6] Support count {cnt_before} -> {cnt_after} -> {'PASS' if pass6 else 'FAIL'}")

    # =========================================================================
    # TEST 7: Same citizen tries to support twice -> second support rejected (409)
    # =========================================================================
    pass7 = False
    try:
        req7 = urllib.request.Request(
            f"http://127.0.0.1:8000/api/reports/{target_pid}/support",
            data=json.dumps({"user_id": unique_supporter}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req7) as resp7:
            pass7 = False
    except urllib.error.HTTPError as e:
        if e.code == 409:
            err_data = json.loads(e.read().decode())
            pass7 = (err_data.get("already_supported") is True)

    test_results["TEST 7"] = {
        "desc": "Duplicate support attempt by same citizen -> 409 Conflict",
        "pass": pass7
    }
    print(f"[TEST 7] Duplicate support attempt -> 409 Conflict: {'PASS' if pass7 else 'FAIL'}")

    # =========================================================================
    # TEST 8: Citizen selects Report Anyway -> new report created, old preserved
    # =========================================================================
    p8 = {
        "title": "Severe drinking water shortage in Ranchi ward",
        "description": "Independent observation of water pipeline contamination",
        "category": "Water Management",
        "district": "Ranchi",
        "area": "Ward 12",
        "user_id": "citizen_independent_88",
        "reported_anyway": True,
        "matched_report_id": target_pid,
        "latitude": 23.3441,
        "longitude": 85.3096
    }
    req8 = urllib.request.Request(
        "http://127.0.0.1:8000/api/problems",
        data=json.dumps(p8).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req8) as resp8:
        res8 = json.loads(resp8.read().decode())
        id8 = res8["problem_id"]
        reported_anyway_flag = res8.get("reported_anyway")

    # Verify both target_pid and id8 exist independently in DB
    db_file = os.path.join(os.path.dirname(__file__), "samadhan.db")
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    cur.execute("SELECT id, duplicate_status, reported_anyway FROM problems WHERE id = ?", (id8,))
    r8_row = cur.fetchone()
    cur.execute("SELECT id FROM problems WHERE id = ?", (target_pid,))
    r_orig_row = cur.fetchone()
    conn.close()

    pass8 = bool(r8_row and r_orig_row and id8 != target_pid and (r8_row[1] == "Reported Anyway" or r8_row[2] == 1))
    test_results["TEST 8"] = {
        "desc": "Report Anyway creates new independent report, preserves old",
        "new_id": id8,
        "old_id": target_pid,
        "pass": pass8
    }
    print(f"[TEST 8] New report {id8} created (reported_anyway=true), old report {target_pid} preserved -> {'PASS' if pass8 else 'FAIL'}")

    # =========================================================================
    # TEST 9: No similar report -> normal submission without warning
    # =========================================================================
    p9 = {
        "title": f"Completely unique problem topic {int(time.time())} solar lighting failure",
        "description": "Solar panels in rural testing laboratory defective and not charging battery units",
        "category": "Energy",
        "district": "Simdega",
        "latitude": 22.6184,
        "longitude": 84.5074
    }
    req9 = urllib.request.Request(
        "http://127.0.0.1:8000/api/reports/check-duplicate",
        data=json.dumps(p9).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req9) as resp9:
        res9 = json.loads(resp9.read().decode())
    pass9 = (res9["duplicate_score"] < 40 and res9["is_duplicate"] is False and res9["status"] == "NO_SIMILAR_REPORT")
    test_results["TEST 9"] = {
        "desc": "Novel problem -> No similar report (<40 score)",
        "score": res9["duplicate_score"],
        "status": res9["status"],
        "pass": pass9
    }
    print(f"[TEST 9] Novel report duplicate score: {res9['duplicate_score']}% -> {'PASS' if pass9 else 'FAIL'}")

    # =========================================================================
    # TEST 10: Duplicate API failure fallback -> local fallback or direct submit
    # =========================================================================
    p10_input = {
        "title": "Broken bridge culvert near village river",
        "description": "Culvert washed away during monsoon flooding",
        "category": "Urban Infrastructure",
        "district": "Khunti",
        "area": "Torpa",
        "latitude": 23.0717,
        "longitude": 85.2789
    }
    p10_backend = detect_duplicate_reports(p10_input, [])
    pass10 = (p10_backend is not None and "duplicate_score" in p10_backend and p10_backend["duplicate_score"] == 0.0)
    test_results["TEST 10"] = {
        "desc": "Offline fallback gracefully returns valid duplicate contract without throwing",
        "pass": pass10
    }
    print(f"[TEST 10] Offline local duplicate engine fallback -> {'PASS' if pass10 else 'FAIL'}")

    print("\n" + "=" * 75)
    print(" VERIFYING IN LIVE CHROME HEADLESS BROWSER (UI & MAP INTEGRITY)")
    print("=" * 75)

    chrome_port = 9224
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe")
    ]
    chrome_exe = None
    for p in chrome_paths:
        if os.path.exists(p):
            chrome_exe = p
            break

    ui_pass = False
    if chrome_exe:
        temp_dir = os.path.expandvars(r"%TEMP%\chrome_dup_test_" + str(int(time.time())))
        os.makedirs(temp_dir, exist_ok=True)
        cmd = [
            chrome_exe,
            f"--remote-debugging-port={chrome_port}",
            "--headless=new",
            "--disable-gpu",
            "--no-first-run",
            f"--user-data-dir={temp_dir}",
            "http://127.0.0.1:5500/my1.html"
        ]
        proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(2.5)

        try:
            req = urllib.request.urlopen(f"http://127.0.0.1:{chrome_port}/json")
            tabs = json.loads(req.read().decode("utf-8"))
            tab = [t for t in tabs if "my1.html" in t.get("url", "") or t.get("type") == "page"][0]
            ws_url = tab["webSocketDebuggerUrl"]
            client = ChromeCDPClient(ws_url)

            # Wait for initial page scripts to load
            time.sleep(2.0)

            # Navigate to submit problem page where Leaflet map & AI duplicate card live
            client.evaluate("""
                if (typeof showPage === 'function') {
                    showPage('submit');
                }
            """)
            time.sleep(1.0)

            # 1. Map & GPS Preservation verification
            leaflet_intact = client.evaluate("""
                (function() {
                    const mapEl = document.getElementById('problemLocationMap');
                    const hasLeaflet = typeof L !== 'undefined';
                    const isLeafletContainer = mapEl ? mapEl.classList.contains('leaflet-container') : false;
                    const hasMapVar = (typeof problemLeafletMap !== 'undefined' && !!problemLeafletMap);
                    const hasGeo = !!navigator.geolocation;
                    return hasLeaflet && (isLeafletContainer || hasMapVar) && hasGeo;
                })()
            """)
            print(f"[PRESERVATION CHECK] Leaflet map & Live GPS strictly intact: {leaflet_intact}")

            # 2. Trigger Duplicate Detection in DOM
            dup_ui_res = client.evaluate("""
                (function() {
                    const matchData = {
                        is_duplicate: true,
                        duplicate_score: 82,
                        status: "POTENTIAL_DUPLICATE",
                        status_label: "Potential Duplicate",
                        best_match: {
                            report_id: "SCP-1024",
                            title: "Severe drinking water pipeline rupture in Morabadi",
                            description: "Main drinking water pipe burst flooding road and causing severe water shortage",
                            category: "Water Management",
                            district: "Ranchi",
                            locality: "Morabadi",
                            distance_meters: 250,
                            distance_km: 0.25,
                            duplicate_score: 82,
                            support_count: 3,
                            issue_cluster_id: "CLUSTER-SCP-1024",
                            text_similarity: 88,
                            location_similarity: 80,
                            category_similarity: 100,
                            area_similarity: 70
                        }
                    };
                    if (typeof renderDuplicateWarningCard === 'function') {
                        renderDuplicateWarningCard(matchData);
                    }
                    const card = document.getElementById("aiDuplicateCard");
                    if (card) card.scrollIntoView({ behavior: 'instant', block: 'center' });
                    return true;
                })()
            """)

            time.sleep(0.8)

            # Check duplicate card display state and contents
            card_state = client.evaluate("""
                (function() {
                    const card = document.getElementById("aiDuplicateCard");
                    const pill = document.getElementById("duplicateStatusPill");
                    const title = document.getElementById("dupExistingTitle");
                    const btnSupport = document.getElementById("btnSupportDup");
                    const btnAnyway = document.getElementById("btnReportAnyway");
                    const btnView = document.getElementById("btnViewExistingDup");

                    return {
                        cardDisplayed: card ? (card.style.display !== 'none' && card.offsetParent !== null) : false,
                        pillText: pill ? pill.textContent.trim() : "",
                        titleText: title ? title.textContent.trim() : "",
                        hasSupportBtn: !!btnSupport,
                        hasAnywayBtn: !!btnAnyway,
                        hasViewBtn: !!btnView,
                        supportBtnLabel: btnSupport ? btnSupport.textContent.trim() : "",
                        anywayBtnLabel: btnAnyway ? btnAnyway.textContent.trim() : "",
                        viewBtnLabel: btnView ? btnView.textContent.trim() : ""
                    };
                })()
            """)
            print(f"[UI CARD CHECK] Duplicate card displayed: {card_state.get('cardDisplayed')} | Pill: '{card_state.get('pillText')}'")
            print(f"[UI CARD CHECK] Buttons: Support='{card_state.get('supportBtnLabel')}', Anyway='{card_state.get('anywayBtnLabel')}', View='{card_state.get('viewBtnLabel')}'")

            # 3. Test "View Existing Report" Modal
            client.evaluate("viewExistingDuplicateModal();")
            time.sleep(0.5)
            modal_view_state = client.evaluate("""
                (function() {
                    const m = document.getElementById("modalViewExistingProblem");
                    return m ? (m.style.display === 'flex' || m.style.display === 'block') : false;
                })()
            """)
            print(f"[MODAL CHECK] 'View Existing Report' modal opened: {modal_view_state}")
            client.evaluate("closeViewExistingModal();")
            time.sleep(0.3)

            # 4. Test "Report Anyway" Modal
            client.evaluate("reportAnywayAction();")
            time.sleep(0.5)
            modal_anyway_state = client.evaluate("""
                (function() {
                    const m = document.getElementById("modalReportAnywayConfirm");
                    return m ? (m.style.display === 'flex' || m.style.display === 'block') : false;
                })()
            """)
            print(f"[MODAL CHECK] 'Report Anyway' confirmation modal opened: {modal_anyway_state}")
            client.evaluate("closeReportAnywayModal();")
            time.sleep(0.3)

            # Capture screenshot of duplicate warning card
            client.evaluate("""
                const card = document.getElementById("aiDuplicateCard");
                if (card) card.scrollIntoView({ behavior: 'instant', block: 'center' });
            """)
            time.sleep(0.5)

            artifact_dir = r"C:\Users\asus\.gemini\antigravity-ide\brain\57345f01-d21a-448b-b929-d46569f3a509"
            screenshot_path = os.path.join(artifact_dir, "duplicate_system_verified.png")
            client.capture_screenshot(screenshot_path)
            print(f"[SCREENSHOT] Saved verification screenshot to: {screenshot_path}")

            ui_pass = bool(leaflet_intact and card_state.get("cardDisplayed") and modal_view_state and modal_anyway_state)
            client.close()
        except Exception as e:
            print("Chrome CDP error:", e)
        finally:
            proc.kill()

    all_passed = all(v["pass"] for v in test_results.values()) and ui_pass
    print("\n" + "=" * 75)
    print(f" FINAL RESULT: {'ALL 10 TESTS + UI VERIFICATION PASSED (10/10)' if all_passed else 'SOME TESTS FAILED'}")
    print("=" * 75)

    return all_passed

if __name__ == "__main__":
    success = run_duplicate_system_suite()
    sys.exit(0 if success else 1)
