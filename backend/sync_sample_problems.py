import json
import sqlite3
import re

conn = sqlite3.connect("backend/samadhan.db")
conn.row_factory = sqlite3.Row
cur = conn.cursor()
cur.execute("SELECT * FROM problems ORDER BY id ASC")
rows = [dict(r) for r in cur.fetchall()]
conn.close()

# Format as JavaScript array
js_items = []
for r in rows:
    req_skills = json.loads(r["required_skills"]) if r["required_skills"] else ["IoT", "Data Analytics"]
    req_domains = json.loads(r["required_academic_domains"]) if r["required_academic_domains"] else ["Engineering"]
    req_tech = json.loads(r["required_technology"]) if r["required_technology"] else ["Sensors"]
    req_res = json.loads(r["required_resources"]) if r["required_resources"] else ["Lab"]

    item = {
        "id": r["id"],
        "title": r["title"],
        "description": r["description"],
        "category": r["category"],
        "subCategory": r["sub_category"] or "",
        "location": r["location"] or "",
        "district": r["district"] or "Ranchi",
        "state": r["state"] or "Jharkhand",
        "latitude": r["latitude"],
        "longitude": r["longitude"],
        "current_latitude": r["current_latitude"],
        "current_longitude": r["current_longitude"],
        "distance_km": r["distance_km"],
        "mismatch_distance_km": r["distance_km"],
        "location_status": r["location_status"] or "verified",
        "suspicion_score": r["suspicion_score"] or 0.0,
        "verification_status": r["verification_status"] or "Verified",
        "is_duplicate": bool(r["duplicate_score"] and r["duplicate_score"] >= 0.60 or r["duplicate_status"] == "Reported Anyway"),
        "duplicate_score": r["duplicate_score"] or 0.0,
        "duplicate_of_id": r["duplicate_of_report_id"] or "",
        "duplicate_status": r["duplicate_status"] or "Original",
        "support_count": r["support_count"] or 1,
        "priority": r["priority"] or "Medium",
        "status": r["status"] or "Pending",
        "requiredSkills": req_skills,
        "requiredAcademicDomains": req_domains,
        "requiredTechnology": req_tech,
        "requiredResources": req_res,
        "estimatedImpact": r["estimated_impact"] or "Estimated ~10,000 local beneficiaries",
        "submittedBy": r["submitted_by"] or "Citizen Portal User",
        "submittedAt": "2026-09-14 10:00 AM"
    }
    js_items.append(item)

js_code = "const SAMPLE_PROBLEMS = " + json.dumps(js_items, indent=4) + ";"

with open("my1.js", "r", encoding="utf-8") as f:
    text = f.read()

# Replace SAMPLE_PROBLEMS definition
pattern = r"const SAMPLE_PROBLEMS = \[.*?\];"
m = re.search(pattern, text, re.DOTALL)
assert m, "const SAMPLE_PROBLEMS not found in my1.js"

text = text[:m.start()] + js_code + text[m.end():]

with open("my1.js", "w", encoding="utf-8") as f:
    f.write(text)

print("Updated SAMPLE_PROBLEMS in my1.js with", len(js_items), "problems!")
