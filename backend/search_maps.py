import re

with open('my1.html', 'r', encoding='utf-8', errors='ignore') as f:
    html = f.read()

matches = re.findall(r'<div[^>]*id=[\'"][^\'"]*map[^\'"]*[\'"][^>]*>', html, re.I)
for m in matches:
    print('Map element in HTML:', m)

# Also check for any leaflet references
matches = re.findall(r'(\b[a-zA-Z0-9_]*map[a-zA-Z0-9_]*\s*=\s*[^;]+;)', html)
for m in matches[:10]:
    print('Map assignment:', m)
