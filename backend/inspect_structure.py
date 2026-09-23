import re
import os

with open("my1.html", "r", encoding="utf-8", errors="ignore") as f:
    html = f.read()

print("File size:", len(html))

# Check map container and surrounding context
pos = html.find('id="problemLocationMap"')
if pos != -1:
    print("\n--- Surrounding HTML for #problemLocationMap ---")
    print(html[max(0, pos - 400):min(len(html), pos + 400)])

# Check navigation to submit problem
print("\n--- Navigation mentions ---")
matches = re.findall(r'(\bonclick=[\'"][^\'"]*[\'"])', html)
for m in matches:
    if any(k in m.lower() for k in ["submit", "problem", "page", "map"]):
        print("OnClick:", m)

matches = re.findall(r'(<section[^>]*id=[\'"][^\'"]*[\'"][^>]*>)', html, re.I)
for m in matches:
    print("Section:", m)
