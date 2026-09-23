with open("my1.js", "r", encoding="utf-8", errors="ignore") as f:
    js = f.read()

idx = js.find("function invalidateProblemMap()")
if idx != -1:
    print(js[idx:idx+1200])

idx2 = js.find("function initLeafletFallbackMap()")
if idx2 != -1:
    print("\n--- initLeafletFallbackMap ---")
    print(js[idx2:idx2+1200].encode('ascii', errors='replace').decode('ascii'))
