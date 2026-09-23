import sqlite3

conn = sqlite3.connect("backend/samadhan.db")
cur = conn.cursor()
cur.execute("SELECT COUNT(*) FROM problems")
total = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM problems WHERE verification_status = 'Verified'")
verified = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM problems WHERE (distance_km IS NOT NULL AND distance_km > 50) OR location_status IN ('mismatch', 'Location Mismatch')")
mismatch = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM problems WHERE duplicate_score >= 0.60 OR duplicate_status IN ('Reported Anyway', 'Duplicate Supported')")
dup = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM problems WHERE verification_status = 'Needs Verification'")
needs_ver = cur.fetchone()[0]

print(f"Total: {total}, Verified: {verified}, Mismatch: {mismatch}, Duplicates: {dup}, Needs Verification: {needs_ver}")

cur.execute("SELECT category, COUNT(*) FROM problems GROUP BY category")
print("Categories:", cur.fetchall())

cur.execute("SELECT district, COUNT(*) FROM problems GROUP BY district")
print("Districts:", cur.fetchall())

conn.close()
