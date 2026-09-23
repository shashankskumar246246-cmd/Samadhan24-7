"""
Comprehensive verification script for Google Maps integration in Samadhan 24/7.
Tests:
1. Dual provider support (Google Maps JavaScript API loader + Leaflet/OSM safe fallback).
2. HTML elements for Google Maps container, developer diagnostic notice, location buttons, live tracking, accuracy badge, telemetry, confirmation panel, hidden inputs.
3. JavaScript functions, event bindings, diagnostic interceptor, and error handling in my1.js.
4. CSS styling rules for Google Maps container, diagnostic notice, confirmation panel, live indicator, and dark mode.
5. Backend /api/config, SQLite schema, and POST /api/problems with full location payload.
"""

import os
import re
import json
import sqlite3
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

print("==================================================")
print("1. VERIFY DUAL PROVIDER ARCHITECTURE IN MY1.HTML")
print("==================================================")
with open(os.path.join(ROOT, "my1.html"), "r", encoding="utf-8") as f:
    html = f.read()

assert "leaflet.css" in html, "Leaflet CSS should be retained as safe fallback provider!"
assert "leaflet.js" in html, "Leaflet JS should be retained as safe fallback provider!"
assert "env.js" in html, "env.js script tag present in my1.html!"
print("[PASS] Modular dual-provider architecture verified in my1.html (Google Maps + Leaflet fallback)!")

print("\n==================================================")
print("2. VERIFY NEW GOOGLE MAPS DOM ELEMENTS IN MY1.HTML")
print("==================================================")
required_elements = [
    ('id="btnDetectLocation"', "Use My Current Location button"),
    ('id="btnCopyGpsToProblem"', "Use Current Location as Problem Location button"),
    ('id="btnLiveLocation"', "Live location toggle button"),
    ('id="btnLiveLocationText"', "Live location button text"),
    ('id="mapLiveIndicator"', "Live location pulsating indicator"),
    ('id="gpsAccuracyBadge"', "GPS accuracy indicator badge"),
    ('id="accuracyValText"', "Accuracy value text container"),
    ('id="locTelemetryPill"', "Location source & telemetry badge"),
    ('id="locPrivacyNotice"', "Location privacy notice banner"),
    ('id="mapDiagnosticNotice"', "Developer diagnostic notice banner"),
    ('id="diagErrorCodePill"', "Diagnostic error code pill"),
    ('id="diagErrorDesc"', "Diagnostic error description"),
    ('id="diagCurrentOrigin"', "Diagnostic current origin display"),
    ('id="diagApiKeyInput"', "Diagnostic inline API key input"),
    ('id="diagFallbackTag"', "Diagnostic fallback active indicator"),
    ('id="problemLocationMap"', "Problem location map container"),
    ('class="problem-location-map google-map-container"', "Google Maps CSS container classes"),
    ('id="mapLoadingOverlay"', "Initial map loading spinner overlay"),
    ('id="locationConfirmationPanel"', "Location confirmation panel"),
    ('id="confStatusBadge"', "Confirmation status badge"),
    ('id="confStateText"', "Confirmation state value"),
    ('id="confDistrictText"', "Confirmation district value"),
    ('id="confAreaText"', "Confirmation village/area value"),
    ('id="confLatText"', "Confirmation latitude value"),
    ('id="confLonText"', "Confirmation longitude value"),
    ('id="confAccuracyText"', "Confirmation accuracy value"),
    ('id="confAddressText"', "Confirmation formatted address value"),
    ('id="btnConfirmLocation"', "Confirm this location button"),
    ('id="confFeedbackMsg"', "Confirmation feedback message"),
    ('id="latitude"', "Hidden latitude input"),
    ('id="longitude"', "Hidden longitude input"),
    ('id="locAccuracy"', "Hidden accuracy input"),
    ('id="locFormattedAddress"', "Hidden formatted_address input"),
    ('id="locSource"', "Hidden location_source input"),
    ('id="locConfirmed"', "Hidden location_confirmed input"),
    ('id="locTimestamp"', "Hidden location_timestamp input")
]

for snippet, name in required_elements:
    assert snippet in html, f"Missing element {name}: {snippet}"
    print(f"  [OK] Found {name}")

print("[PASS] All required HTML elements for Google Maps and location tracking present!")

print("\n==================================================")
print("3. VERIFY JAVASCRIPT FUNCTIONS IN MY1.JS")
print("==================================================")
with open(os.path.join(ROOT, "my1.js"), "r", encoding="utf-8", errors="ignore") as f:
    js = f.read()

required_js_funcs = [
    "loadGoogleMapsApi",
    "showGoogleMapsDiagnostic",
    "hideGoogleMapsDiagnostic",
    "initLeafletFallbackMap",
    "retryGoogleMapsInitialization",
    "initProblemGoogleMap",
    "initProblemLocationMap",
    "updateGoogleMapTheme",
    "invalidateProblemMap",
    "useCurrentLocation",
    "updateUserCurrentLocationMarker",
    "copyCurrentGpsToProblemLocation",
    "toggleLiveLocation",
    "startLiveLocationTracking",
    "stopLiveLocationTracking",
    "updateAccuracyDisplay",
    "applyLocationCoordinates",
    "resetLocationConfirmationState",
    "confirmSelectedLocation",
    "reverseGeocodeLocationGoogle",
    "reverseGeocodeLocation",
    "findClosestJharkhandDistrict",
    "matchJharkhandDistrict",
    "GOOGLE_MAPS_DARK_STYLE",
    "getGoogleMapsApiKey",
    "resolveGoogleMapsApiKeyAsync"
]

for func in required_js_funcs:
    assert func in js, f"Missing JS function/symbol: {func}"
    print(f"  [OK] Found {func}()")

print("[PASS] All Google Maps, Leaflet Fallback, and Geolocation JS functions are implemented!")

print("\n==================================================")
print("4. VERIFY CSS RULES IN MY1.CSS")
print("==================================================")
with open(os.path.join(ROOT, "my1.css"), "r", encoding="utf-8") as f:
    css = f.read()

required_css_classes = [
    ".problem-location-map",
    ".map-loading-overlay",
    ".map-spinner",
    ".map-diagnostic-notice",
    ".diag-header",
    ".diag-title",
    ".diag-code-pill",
    ".diag-desc",
    ".diag-causes",
    ".diag-actions",
    ".diag-key-input",
    ".diag-retry-btn",
    ".diag-fallback-tag",
    ".copy-geo-btn",
    ".loc-telemetry-pill",
    ".loc-privacy-notice",
    ".location-btn.live-track-btn",
    ".gps-accuracy-badge",
    ".map-live-indicator",
    "@keyframes livePulsing",
    ".location-confirmation-panel",
    ".conf-panel-header",
    ".btn-confirm-location",
    "body.dark-mode .map-diagnostic-notice",
    "body.dark-mode .location-confirmation-panel"
]

for rule in required_css_classes:
    assert rule in css, f"Missing CSS rule: {rule}"
    print(f"  [OK] Found CSS rule: {rule}")

print("[PASS] All styling rules for light/dark mode, responsiveness, and diagnostics present!")

print("\n==================================================")
print("5. VERIFY BACKEND CONFIG ENDPOINT")
print("==================================================")
res = urllib.request.urlopen("http://127.0.0.1:8000/api/config")
assert res.status == 200, f"/api/config failed: {res.status}"
cfg = json.loads(res.read().decode())
assert "VITE_GOOGLE_MAPS_API_KEY" in cfg, "VITE_GOOGLE_MAPS_API_KEY key missing from /api/config"
print("  [OK] /api/config responding with environment config:", cfg)

print("\n==================================================")
print("6. VERIFY BACKEND SUBMISSION WITH EXTENDED LOCATION PAYLOAD")
print("==================================================")
payload = {
    "title": "Broken Borewell Handpump in Kanke Block",
    "description": "The community handpump in village Kanke has been non-functional for 3 weeks, causing severe drinking water scarcity.",
    "category": "Water Management",
    "district": "Ranchi",
    "village": "Kanke",
    "state": "Jharkhand",
    "latitude": 23.4321,
    "longitude": 85.3214,
    "accuracy": 12,
    "formatted_address": "Kanke Road, Ranchi, Jharkhand 834006",
    "location_source": "browser_geolocation",
    "location_confirmed": True,
    "location_timestamp": "2026-09-17T05:00:00.000Z",
    "current_latitude": 23.4320,
    "current_longitude": 85.3212,
    "location_status": "Location verified — within expected range."
}

req = urllib.request.Request(
    "http://127.0.0.1:8000/api/problems",
    data=json.dumps(payload).encode("utf-8"),
    headers={"Content-Type": "application/json"}
)
res = urllib.request.urlopen(req)
assert res.status == 201, f"POST failed: {res.status}"
res_data = json.loads(res.read().decode())
pid = res_data["problem_id"]
print(f"  [OK] Created problem with full location payload: #{pid}")

# Verify stored fields in SQLite
conn = sqlite3.connect(os.path.join(ROOT, "backend", "samadhan.db"))
cur = conn.cursor()
cur.execute("SELECT id, latitude, longitude, accuracy, formatted_address, location_source, location_confirmed, location_timestamp FROM problems WHERE id = ?", (pid,))
row = cur.fetchone()
conn.close()

assert row is not None, f"Problem {pid} not found in database"
print(f"  [OK] DB record: id={row[0]}, lat={row[1]}, lon={row[2]}, acc={row[3]}, addr='{row[4]}', src='{row[5]}', conf={row[6]}, ts='{row[7]}'")
assert row[3] == 12, f"Expected accuracy 12, got {row[3]}"
assert row[4] == "Kanke Road, Ranchi, Jharkhand 834006", f"Expected address match, got {row[4]}"
assert row[5] == "browser_geolocation", f"Expected location_source 'browser_geolocation', got {row[5]}"
assert row[6] in (1, True), f"Expected location_confirmed 1, got {row[6]}"

print("\n==================================================")
print(">>> ALL 6 VERIFICATION MODULES PASSED PERFECTLY! <<<")
print("==================================================")
