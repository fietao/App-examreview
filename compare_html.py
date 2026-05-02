import urllib.request
import hashlib

# Get Flask version
print("Fetching from Flask...")
response = urllib.request.urlopen('http://localhost:5000/')
flask_html = response.read()
flask_hash = hashlib.md5(flask_html).hexdigest()
print(f"Flask HTML size: {len(flask_html)}, hash: {flask_hash}")

# Get test.html version  
print("\nReading test.html...")
with open('test.html', 'rb') as f:
    test_html = f.read()
test_hash = hashlib.md5(test_html).hexdigest()
print(f"Test HTML size: {len(test_html)}, hash: {test_hash}")

# Compare just the script tag content
def extract_script(html):
    start = html.find(b'<script>')
    end = html.find(b'</script>', start)
    return html[start+8:end] if start != -1 else None

flask_script = extract_script(flask_html)
test_script = extract_script(test_html)

if flask_script and test_script:
    flask_script_hash = hashlib.md5(flask_script).hexdigest()
    test_script_hash = hashlib.md5(test_script).hexdigest()
    print(f"\nFlask script size: {len(flask_script)}, hash: {flask_script_hash}")
    print(f"Test script size: {len(test_script)}, hash: {test_script_hash}")
    
    if flask_script_hash == test_script_hash:
        print("✓ Scripts are identical!")
    else:
        print("✗ Scripts are DIFFERENT!")
        # Find first difference
        for i in range(min(len(flask_script), len(test_script))):
            if flask_script[i:i+1] != test_script[i:i+1]:
                print(f"  First difference at byte {i}")
                print(f"  Flask: {flask_script[max(0,i-20):i+50]}")
                print(f"  Test:  {test_script[max(0,i-20):i+50]}")
                break
else:
    print("Could not extract scripts")
