#!/usr/bin/env python3
import urllib.request

url = 'http://localhost:5000/'
print("Fetching HTML...")
response = urllib.request.urlopen(url)

print("Response headers:")
for header, value in response.headers.items():
    print(f"  {header}: {value}")

html = response.read()
print(f"\nHTML size: {len(html)} bytes")
print(f"First 500 bytes:\n{html[:500]}")
print(f"\nScript tag position: {html.find(b'<script>')}")
print(f"Actual script tag bytes around position: {html[html.find(b'<script>'):html.find(b'<script>')+100]}")
