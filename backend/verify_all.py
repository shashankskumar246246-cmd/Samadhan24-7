import urllib.request
import urllib.parse
import json
import re

base_url = "http://127.0.0.1:8000"

print("==================================================")
print("1. VERIFY BACKEND STATS (BLUE SECTION)")
print("==================================================")
res = urllib.request.urlopen(f"{base_url}/api/reports/stats")
stats = json.loads(res.read().decode())
print("Stats response:", json.dumps(stats, indent=2))
assert stats["total_reports"] >= 20, "Total reports should be at least 20"
assert stats["location_mismatch_reports"] > 0, "Location mismatch should be > 0"
assert stats["duplicate_reports"] > 0, "Duplicate reports should be > 0"
assert stats["reports_under_verification"] > 0, "Needs verification should be > 0"
assert stats["verified_reports"] > 0, "Verified reports should be > 0"
print("[PASS] Blue section stats are fully dynamic and > 0!")

print("\n==================================================")
print("2. VERIFY DOMAIN STATS & DISTRICT FILTERING (RED SECTION)")
print("==================================================")
districts_to_test = ["All Districts", "Ranchi", "Gumla", "Dhanbad", "Deoghar", "Bokaro", "Simdega"]
for dist in districts_to_test:
    q = urllib.parse.quote(dist)
    res = urllib.request.urlopen(f"{base_url}/api/reports/domain-stats?district={q}")
    d_stats = json.loads(res.read().decode())
    print(f"District: '{dist}' -> Total: {d_stats['total_filtered']}, Counts: {d_stats['counts']}, Max: {d_stats['max_count']}, Bars: {d_stats['percentages']}")

    # Simdega has 0 reports
    if dist == "Simdega":
        assert d_stats["total_filtered"] == 0
        assert all(v == 0 for v in d_stats["counts"].values())
        assert all(v == 0 for v in d_stats["percentages"].values())
        print("  -> Correctly handled 0 reports with 0% progress bars and no division-by-zero errors!")
    else:
        assert d_stats["total_filtered"] > 0
        assert d_stats["max_count"] > 0
print("[PASS] District filtering dynamically calculates domain counts and progress bars!")

print("\n==================================================")
print("3. VERIFY NEW PROBLEM SUBMISSION UPDATES DASHBOARD")
print("==================================================")
stats_before = json.loads(urllib.request.urlopen(f"{base_url}/api/reports/stats").read().decode())
ranchi_before = json.loads(urllib.request.urlopen(f"{base_url}/api/reports/domain-stats?district=Ranchi").read().decode())

new_prob_payload = {
    "title": "Rural Tele-Health Kiosk Shortage in Angara",
    "description": "Villagers in Angara block need primary diagnostic blood testing kits and tele-medicine connectivity to RIMS Ranchi.",
    "category": "Healthcare",
    "district": "Ranchi",
    "state": "Jharkhand",
    "latitude": 23.412,
    "longitude": 85.521,
    "current_latitude": 23.410,
    "current_longitude": 85.523,
    "location_status": "verified"
}

req = urllib.request.Request(
    f"{base_url}/api/problems",
    data=json.dumps(new_prob_payload).encode("utf-8"),
    headers={"Content-Type": "application/json"}
)
post_res = urllib.request.urlopen(req)
submit_data = json.loads(post_res.read().decode())
new_id = submit_data["problem_id"]
print(f"Submitted new problem: {new_id}")

stats_after = json.loads(urllib.request.urlopen(f"{base_url}/api/reports/stats").read().decode())
ranchi_after = json.loads(urllib.request.urlopen(f"{base_url}/api/reports/domain-stats?district=Ranchi").read().decode())

print(f"Total reports: {stats_before['total_reports']} -> {stats_after['total_reports']}")
assert stats_after["total_reports"] == stats_before["total_reports"] + 1, "Total reports should increment by 1"

print(f"Ranchi Healthcare count: {ranchi_before['counts']['Healthcare']} -> {ranchi_after['counts']['Healthcare']}")
assert ranchi_after["counts"]["Healthcare"] == ranchi_before["counts"]["Healthcare"] + 1, "Ranchi healthcare should increment by 1"
print("[PASS] Submission flow immediately updates Blue total reports and Red domain counts!")

print("\n==================================================")
print("4. VERIFY ADMIN VERIFICATION ACTION")
print("==================================================")
verify_req = urllib.request.Request(f"{base_url}/api/reports/{new_id}/verify", data=b"", headers={"Content-Type": "application/json"})
v_res = urllib.request.urlopen(verify_req)
v_data = json.loads(v_res.read().decode())
print("Admin verify response:", v_data)
assert v_data["status"] == "Verified"
print("[PASS] Admin verify endpoint works!")

print("\n==================================================")
print("5. VERIFY HTML DOM BINDINGS & ELEMENTS")
print("==================================================")
with open("my1.html", "r", encoding="utf-8") as f:
    html_text = f.read()

required_html_elements = [
    'id="dashStatTotalReports"',
    'id="dashStatVerifiedReports"',
    'id="dashStatMismatchReports"',
    'id="dashStatDuplicateReports"',
    'id="dashStatUnderVerification"',
    'id="btnReviewSuspicious"',
    'id="btnReviewDuplicates"',
    'id="dashboardDistrictFilter"',
    'id="domainCountEducation"',
    'id="domainBarEducation"',
    'id="domainCountHealthcare"',
    'id="domainBarHealthcare"',
    'id="domainCountAgriculture"',
    'id="domainBarAgriculture"',
    'id="domainCountWater"',
    'id="domainBarWater"',
    'id="domainCountEnvironment"',
    'id="domainBarEnvironment"',
    'id="suspiciousReportsModal"',
    'id="suspiciousReportsTableBody"',
    'id="duplicateReportsModal"',
    'id="duplicateReportsTableBody"'
]

for elem in required_html_elements:
    assert elem in html_text, f"Missing element in my1.html: {elem}"
    print(f"  [OK] Found {elem}")

print("\n==================================================")
print("6. VERIFY JAVASCRIPT FUNCTIONS IN MY1.JS")
print("==================================================")
with open("my1.js", "r", encoding="utf-8") as f:
    js_text = f.read()

required_js_symbols = [
    "normalizeProblemDomain",
    "getDomainStatistics",
    "updateDomainStatistics",
    "updateIntegrityDashboardStats",
    "openSuspiciousReviewModal",
    "closeSuspiciousReviewModal",
    "renderSuspiciousReportsTable",
    "openDuplicatesReviewModal",
    "closeDuplicatesReviewModal",
    "renderDuplicatesReportsTable",
    "adminVerifyReport",
    "adminRejectReport",
    "adminResolveDuplicate",
    "syncProblems",
    "fetchDomainStats"
]

for sym in required_js_symbols:
    assert sym in js_text, f"Missing symbol in my1.js: {sym}"
    print(f"  [OK] Found {sym}()")

print("\n>>> ALL VALIDATION CHECKS PASSED PERFECTLY! <<<")
