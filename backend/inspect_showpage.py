with open("my1.js", "r", encoding="utf-8", errors="ignore") as f:
    js = f.read()

import re

# Find showPage definition
pos = js.find("function showPage(")
if pos != -1:
    print("--- showPage implementation ---")
    print(js[pos:pos+1500])

# Find all calls or occurrences of initProblemLocationMap
print("\n--- initProblemLocationMap occurrences ---")
for m in re.finditer(r'.{0,100}initProblemLocationMap.{0,100}', js):
    print(m.group(0).strip())

# Find all calls to invalidateProblemMap
print("\n--- invalidateProblemMap occurrences ---")
for m in re.finditer(r'.{0,100}invalidateProblemMap.{0,100}', js):
    print(m.group(0).strip())
