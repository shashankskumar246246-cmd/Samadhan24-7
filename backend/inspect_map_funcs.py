with open("my1.js", "r", encoding="utf-8", errors="ignore") as f:
    js = f.read()

import re

def print_fn(name, max_len=3000):
    idx = js.find("function " + name)
    if idx == -1:
        idx = js.find(name + " =")
    if idx != -1:
        print(f"\n==================== {name} ====================")
        print(js[idx:idx+max_len])
    else:
        print(f"\nFunction {name} not found!")

print_fn("initProblemLocationMap", 2000)
print_fn("loadGoogleMapsApi", 2500)
print_fn("initProblemGoogleMap", 2500)
print_fn("initLeafletFallbackMap", 2500)
print_fn("retryGoogleMapsInitialization", 1500)
print_fn("showGoogleMapsDiagnostic", 2000)
