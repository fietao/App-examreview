import requests

r = requests.get('http://localhost:5000')
html = r.text

# Find the script tag
script_start = html.find('<script>')
script_end = html.find('</script>', script_start)
script = html[script_start+8:script_end]

# Find where QUESTIONS ends
questions_end = script.find('];')
if questions_end > 0:
    print(f'Found ]; at position {questions_end}')
    print('Text after ];:', repr(script[questions_end:questions_end+200]))
    
    # Check if the syntax looks valid
    # Count opening and closing braces
    opens = script[:questions_end].count('{')
    closes = script[:questions_end].count('}')
    print(f'Opening braces: {opens}, Closing braces: {closes}')
    print(f'Balance: {opens - closes}')
else:
    print('Could not find ];')

# Check for syntax errors
print(f'Script length: {len(script)}')
print(f'Script starts with: {script[:100]}')
