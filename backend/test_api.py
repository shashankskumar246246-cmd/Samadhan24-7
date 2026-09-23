import urllib.request
import urllib.parse
import json

base_url = "http://localhost:8000"

# 1. Test /api/reports/stats
stats_res = urllib.request.urlopen(f"{base_url}/api/reports/stats")
stats = json.loads(stats_res.read().decode())
print("STATS:", stats)

# 2. Test /api/reports/domain-stats
for dist in ["All Districts", "Ranchi", "Gumla", "Dhanbad", "Deoghar", "Bokaro", "Simdega"]:
    q = urllib.parse.quote(dist)
    res = urllib.request.urlopen(f"{base_url}/api/reports/domain-stats?district={q}")
    data = json.loads(res.read().decode())
    print(f"[{dist}] -> Counts: {data['counts']} | Max: {data['max_count']} | Bars: {data['percentages']}")
