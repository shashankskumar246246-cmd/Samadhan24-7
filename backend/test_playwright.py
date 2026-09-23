import subprocess
import time
import json
import urllib.request
import os

# Let's run a test with Chrome in headless mode or using Playwright if installed
# Let's check what packages we have
try:
    import playwright
    print("Playwright is available!")
except ImportError:
    print("Playwright not installed")
