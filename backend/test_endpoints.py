"""
Integration test script testing the HTTP endpoints of backend/app.py:
1. POST /api/ai/detect-category
2. GET /api/location/reverse-geocode
3. POST /api/location/reverse-geocode
4. POST /api/problems with coordinates, state, and category
"""

import http.client
import json
import os
import subprocess
import sys
import time

PYTHON_EXE = sys.executable
APP_PY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.py")
PORT = 8011

def main():
    # 1. Start server on PORT 8011
    server_proc = subprocess.Popen(
        [PYTHON_EXE, APP_PY, str(PORT)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    time.sleep(1.5)

    try:
        conn = http.client.HTTPConnection("127.0.0.1", PORT, timeout=5)

        # -------------------------------------------------------------
        # 1. Health check
        # -------------------------------------------------------------
        conn.request("GET", "/api/health")
        resp = conn.getresponse()
        assert resp.status == 200, f"Health check failed with {resp.status}"
        data = json.loads(resp.read().decode())
        print(f"[OK] Health check passed: {data}")

        # -------------------------------------------------------------
        # 2. AI Category Detection: POST /api/ai/detect-category
        # -------------------------------------------------------------
        prompts = [
            ("Village has no clean drinking water", "Water Management"),
            ("Students in our village do not have proper classrooms", "Education"),
            ("Primary health centre has no essential facilities", "Healthcare"),
            ("Farmers are facing crop irrigation problems", "Agriculture"),
            ("Garbage is not being collected regularly", "Sanitation"),
            ("Roads are damaged after heavy rainfall", "Urban Infrastructure"),
            ("People are facing electricity supply problems", "Energy"),
            ("River water is becoming polluted", "Environment")
        ]

        for title, expected_cat in prompts:
            payload = json.dumps({"title": title, "description": ""})
            headers = {"Content-Type": "application/json"}
            conn.request("POST", "/api/ai/detect-category", payload, headers)
            resp = conn.getresponse()
            assert resp.status == 200, f"detect-category failed: {resp.status}"
            res = json.loads(resp.read().decode())
            assert res["category"] == expected_cat, f"Expected {expected_cat}, got {res['category']}"
            assert res["confidence"] >= 0.70, f"Low confidence: {res['confidence']}"
            print(f"[OK] POST /api/ai/detect-category: '{title}' -> {res['category']} ({int(res['confidence']*100)}%) Keywords: {res['keywords']}")

        # -------------------------------------------------------------
        # 3. Reverse Geocode: GET /api/location/reverse-geocode
        # -------------------------------------------------------------
        conn.request("GET", "/api/location/reverse-geocode?latitude=23.3441&longitude=85.3096")
        resp = conn.getresponse()
        assert resp.status == 200, f"GET reverse-geocode failed: {resp.status}"
        geo_res = json.loads(resp.read().decode())
        assert geo_res["district"] == "Ranchi"
        assert geo_res["state"] == "Jharkhand"
        print(f"[OK] GET /api/location/reverse-geocode: {geo_res['district']}, {geo_res['state']}")

        # -------------------------------------------------------------
        # 4. Reverse Geocode: POST /api/location/reverse-geocode
        # -------------------------------------------------------------
        payload = json.dumps({"latitude": 23.7957, "longitude": 86.4304})
        conn.request("POST", "/api/location/reverse-geocode", payload, headers)
        resp = conn.getresponse()
        assert resp.status == 200, f"POST reverse-geocode failed: {resp.status}"
        post_geo = json.loads(resp.read().decode())
        assert post_geo["district"] == "Dhanbad"
        print(f"[OK] POST /api/location/reverse-geocode: {post_geo['district']}, {post_geo['state']}")

        # -------------------------------------------------------------
        # 5. Submit Problem with Geo fields: POST /api/problems
        # -------------------------------------------------------------
        prob_payload = json.dumps({
            "title": "Clean drinking water shortage in Bishunpur village",
            "description": "Bishunpur rural villagers lack clean tap water and borewell is dry.",
            "category": "Water Management",
            "district": "Gumla",
            "state": "Jharkhand",
            "area": "Bishunpur Block",
            "latitude": 23.0441,
            "longitude": 84.5414
        })
        conn.request("POST", "/api/problems", prob_payload, headers)
        resp = conn.getresponse()
        assert resp.status == 201, f"POST /api/problems failed: {resp.status}"
        new_prob = json.loads(resp.read().decode())
        print(f"[OK] POST /api/problems: Problem created #{new_prob['problem_id']}, category: {new_prob['analysis']['category']}")

        # -------------------------------------------------------------
        # 6. Retrieve problem and verify fields
        # -------------------------------------------------------------
        conn.request("GET", f"/api/problems/{new_prob['problem_id']}")
        resp = conn.getresponse()
        assert resp.status == 200, f"GET problem failed: {resp.status}"
        saved = json.loads(resp.read().decode())
        assert saved["state"] == "Jharkhand"
        assert saved["latitude"] == 23.0441
        assert saved["longitude"] == 84.5414
        print(f"[OK] Problem retrieved: Lat={saved['latitude']}, Lon={saved['longitude']}, State={saved['state']}, District={saved['district']}")

        print("\nALL BACKEND API & GEOLOCATION ENDPOINTS VERIFIED SUCCESSFULLY!")

    finally:
        server_proc.terminate()

if __name__ == "__main__":
    main()
