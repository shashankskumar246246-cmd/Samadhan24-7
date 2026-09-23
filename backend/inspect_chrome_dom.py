import re

with open('chrome_dom.html', 'r', encoding='utf-8', errors='ignore') as f:
    dom = f.read()

print('DOM Length:', len(dom))
print('Has leaflet-container:', 'leaflet-container' in dom)
print('Has mapDiagnosticNotice:', 'id="mapDiagnosticNotice"' in dom)
diag_matches = re.findall(r'<div[^>]*id="mapDiagnosticNotice"[^>]*>', dom)
print('Diagnostic tag:', diag_matches)
diag_desc = re.findall(r'<p[^>]*id="diagErrorDesc"[^>]*>(.*?)</p>', dom)
print('Diagnostic description:', diag_desc)
diag_code = re.findall(r'<span[^>]*id="diagErrorCodePill"[^>]*>(.*?)</span>', dom)
print('Diagnostic code pill:', diag_code)
origin_code = re.findall(r'<code[^>]*id="diagCurrentOrigin"[^>]*>(.*?)</code>', dom)
print('Diagnostic origin code:', origin_code)
print('Has leaflet-tile-pane:', 'leaflet-tile-pane' in dom)
print('Has leaflet-marker-icon:', 'leaflet-marker-icon' in dom)
coord_matches = re.findall(r'<span[^>]*id="coordinatesText"[^>]*>(.*?)</span>', dom)
print('Coordinates text:', coord_matches)
prov_badge = re.findall(r'<span[^>]*id="activeMapProviderBadge"[^>]*>(.*?)</span>', dom)
print('Provider badge:', provBadge if 'provBadge' in locals() else prov_badge)
