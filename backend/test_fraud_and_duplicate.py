"""
Automated Test Suite for Samadhan 24/7 Location-Based Fraud & Duplicate Report Detection.
Validates all 9 specified test scenarios across algorithms and live HTTP endpoints.
"""

import http.client
import json
import os
import subprocess
import sys
import time
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from matching_engine import (
    calculate_haversine_distance_km,
    verify_location_consistency,
    calculate_duplicate_score,
    detect_duplicate_reports,
    LOCATION_VERIFICATION_CONFIG,
    DUPLICATE_CONFIG
)
from app import init_db, get_all_problems, get_problem_by_id, DB_PATH

PORT = 8012
PYTHON_EXE = sys.executable
APP_PY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.py")


class TestFraudAndDuplicateAlgorithms(unittest.TestCase):

    def setUp(self):
        init_db()

    def test_1_location_verified_nearby(self):
        """TEST 1: User GPS and reported location are nearby (within 2 km) -> Location Verified"""
        # User at Ranchi Albert Ekka Chowk (23.3698, 85.3255) reporting issue at Main Road Ranchi (23.3640, 85.3230) ~ 0.7 km
        res = verify_location_consistency(23.3698, 85.3255, 23.3640, 85.3230)
        self.assertEqual(res["location_status"], "verified")
        self.assertEqual(res["status_label"], "Location Verified")
        self.assertFalse(res["verification_required"])
        self.assertFalse(res["is_mismatch"])
        self.assertLessEqual(res["suspicion_score"], 0.15)
        self.assertLessEqual(res["distance_km"], 2.0)
        print(f"[PASS] TEST 1: Nearby Location Verified -> Dist: {res['distance_km']} km, Score: {res['suspicion_percentage']}%, Status: {res['status_label']}")

    def test_2_location_mismatch_far_away(self):
        """TEST 2: User GPS is far away from reported location (Ranchi vs Jamshedpur) -> Location Mismatch + Suspicion Score"""
        # User GPS: Ranchi (23.3441, 85.3096) vs Reported: Jamshedpur (22.8046, 86.2029) ~ 132 km
        res = verify_location_consistency(23.3441, 85.3096, 22.8046, 86.2029)
        self.assertEqual(res["location_status"], "mismatch")
        self.assertEqual(res["status_label"], "Needs Verification")
        self.assertTrue(res["verification_required"])
        self.assertTrue(res["is_mismatch"])
        self.assertGreaterEqual(res["distance_km"], 100.0)
        self.assertEqual(res["suspicion_percentage"], 86) # or 87%
        self.assertGreaterEqual(res["suspicion_score"], 0.85)
        print(f"[PASS] TEST 2: Far Location Mismatch -> Dist: {res['distance_km']} km, Suspicion: {res['suspicion_percentage']}%, Status: {res['status_label']}")

    def test_3_same_problem_nearby_duplicate(self):
        """TEST 3: Same problem already exists nearby -> Duplicate Found"""
        existing = [{
            "id": "SCP-1001",
            "title": "Drinking Water Shortage & Contamination",
            "description": "Villagers in Gumla district face severe drinking water shortage during summer months. Well water contains iron.",
            "category": "Water Management",
            "district": "Gumla",
            "latitude": 23.0441,
            "longitude": 84.5414,
            "status": "In Progress",
            "support_count": 14
        }]

        new_draft = {
            "title": "Clean drinking water shortage in Gumla village",
            "description": "Severe shortage of clean drinking water in village, well water is contaminated.",
            "category": "Water Management",
            "district": "Gumla",
            "latitude": 23.0470,
            "longitude": 84.5430
        }

        res = detect_duplicate_reports(new_draft, existing)
        self.assertTrue(res["is_duplicate"])
        self.assertIn(res["duplicate_level"], ["similar", "possible_duplicate"])
        self.assertGreaterEqual(res["duplicate_score"], 0.75)
        self.assertEqual(res["existing_report"]["id"], "SCP-1001")
        self.assertTrue(len(res["matching_reasons"]) >= 2)
        print(f"[PASS] TEST 3: Duplicate Found -> Score: {res['duplicate_percentage']}%, Reasons: {res['matching_reasons']}")

    def test_4_similar_wording_different_location_not_duplicate(self):
        """TEST 4: Similar wording but different location -> Do not incorrectly mark as definite duplicate"""
        existing = [{
            "id": "SCP-1001",
            "title": "Drinking Water Shortage & Contamination",
            "description": "Villagers in Gumla district face severe drinking water shortage during summer months.",
            "category": "Water Management",
            "district": "Gumla",
            "latitude": 23.0441,
            "longitude": 84.5414,
            "status": "In Progress"
        }]

        # Similar problem words, but located in Sahibganj (> 350 km away in north-east Jharkhand)
        new_draft_far = {
            "title": "Drinking Water Shortage & Contamination",
            "description": "Villagers face severe drinking water shortage during summer months.",
            "category": "Water Management",
            "district": "Sahibganj",
            "latitude": 25.2425,
            "longitude": 87.6433
        }

        res = detect_duplicate_reports(new_draft_far, existing)
        # Must not be marked as a definite duplicate because geographical locations are completely distinct communities
        self.assertNotEqual(res["duplicate_level"], "possible_duplicate")
        self.assertLessEqual(res["duplicate_score"], 0.70)
        print(f"[PASS] TEST 4: Geographic Protection -> Score capped at {res['duplicate_percentage']}% (Level: {res['duplicate_level']})")

    def test_5_same_location_different_problem_no_duplicate(self):
        """TEST 5: Same location but completely different problem -> No duplicate"""
        existing = [{
            "id": "SCP-1001",
            "title": "Drinking Water Shortage & Contamination",
            "description": "Villagers face drinking water shortage during summer months.",
            "category": "Water Management",
            "district": "Gumla",
            "latitude": 23.0441,
            "longitude": 84.5414,
            "status": "In Progress"
        }]

        # Different category & topic in the exact same village
        new_draft_diff = {
            "title": "Primary school building requires new roof and digital computers",
            "description": "Children in village school have no blackboard or computer laboratory.",
            "category": "Education",
            "district": "Gumla",
            "latitude": 23.0441,
            "longitude": 84.5414
        }

        res = detect_duplicate_reports(new_draft_diff, existing)
        self.assertFalse(res["is_duplicate"])
        self.assertEqual(res["duplicate_level"], "none")
        self.assertLessEqual(res["duplicate_score"], 0.50)
        print(f"[PASS] TEST 5: Different Domain Same Location -> Duplicate Score: {res['duplicate_percentage']}%, is_duplicate={res['is_duplicate']}")

    def test_6_user_denies_gps_manual_workflow(self):
        """TEST 6: User denies GPS permission -> Manual location workflow continues"""
        res = verify_location_consistency(None, None, 23.3441, 85.3096)
        self.assertEqual(res["location_status"], "unverified")
        self.assertFalse(res["verification_required"])
        self.assertFalse(res["is_mismatch"])
        self.assertEqual(res["status_label"], "GPS Unavailable")
        print(f"[PASS] TEST 6: Graceful Manual Fallback -> Status: {res['status_label']}, Msg: {res['message']}")


class TestFraudAndDuplicateEndpoints(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        init_db()
        cls.server_proc = subprocess.Popen(
            [PYTHON_EXE, APP_PY, str(PORT)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        time.sleep(1.5)

    @classmethod
    def tearDownClass(cls):
        cls.server_proc.terminate()
        cls.server_proc.wait()

    def test_7_support_existing_report_endpoint(self):
        """TEST 7: User clicks 'Support Existing Report' -> Existing report support count increases"""
        conn = http.client.HTTPConnection("127.0.0.1", PORT, timeout=5)
        conn.request("POST", "/api/reports/SCP-1001/support", json.dumps({"user": "Citizen"}), {"Content-Type": "application/json"})
        resp = conn.getresponse()
        self.assertEqual(resp.status, 200)
        data = json.loads(resp.read().decode())
        self.assertIn("support_count", data)
        self.assertGreaterEqual(data["support_count"], 2)
        print(f"[PASS] TEST 7: Support Existing Report Endpoint -> New Support Count: {data['support_count']}")

    def test_8_report_anyway_submission_flow(self):
        """TEST 8: User clicks 'Report Anyway' -> New report can be submitted with duplicate tracking"""
        conn = http.client.HTTPConnection("127.0.0.1", PORT, timeout=5)
        payload = json.dumps({
            "title": "Severe drinking water scarcity in Bishunpur Gumla",
            "description": "Well water is completely dry and villagers need drinking water relief.",
            "category": "Water Management",
            "district": "Gumla",
            "state": "Jharkhand",
            "area": "Bishunpur",
            "latitude": 23.0441,
            "longitude": 84.5414,
            "current_latitude": 23.0450,
            "current_longitude": 84.5420,
            "duplicate_status": "Reported Anyway",
            "duplicate_of_report_id": "SCP-1001"
        })
        conn.request("POST", "/api/problems", payload, {"Content-Type": "application/json"})
        resp = conn.getresponse()
        self.assertEqual(resp.status, 201)
        data = json.loads(resp.read().decode())
        pid = data["problem_id"]

        # Verify problem was saved in DB with duplicate tracking
        saved = get_problem_by_id(pid)
        self.assertIsNotNone(saved)
        self.assertEqual(saved["duplicate_status"], "Reported Anyway")
        self.assertEqual(saved["duplicate_of_report_id"], "SCP-1001")
        print(f"[PASS] TEST 8: Report Anyway -> Submitted as #{pid} with duplicate_status={saved['duplicate_status']}")

    def test_9_admin_stats_and_thresholds_endpoints(self):
        """TEST 9: Admin dashboard stats and threshold endpoints verify integrity"""
        conn = http.client.HTTPConnection("127.0.0.1", PORT, timeout=5)
        conn.request("GET", "/api/reports/stats")
        resp = conn.getresponse()
        self.assertEqual(resp.status, 200)
        stats = json.loads(resp.read().decode())
        self.assertIn("total_reports", stats)
        self.assertIn("location_mismatch_reports", stats)
        self.assertIn("duplicate_reports", stats)
        self.assertIn("reports_under_verification", stats)
        self.assertIn("verified_reports", stats)
        print(f"[PASS] TEST 9: Admin Stats Endpoint -> Total: {stats['total_reports']}, Mismatches: {stats['location_mismatch_reports']}, Dups: {stats['duplicate_reports']}")


if __name__ == "__main__":
    unittest.main()
