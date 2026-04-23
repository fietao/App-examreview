import requests

r = requests.get('http://localhost:5000')
html = r.text

# Find the script tag
script_start = html.find('<script>')
script_end = html.find('</script>', script_start)
script = html[script_start+8:script_end]

# Count braces by section
questions_end = script.find('];') + 2

before_questions = script[:questions_end]
after_questions = script[questions_end:]

opens_before = before_questions.count('{')
closes_before = before_questions.count('}')

opens_after = after_questions.count('{')
closes_after = after_questions.count('}')

print(f"Before QUESTIONS closing:");
print(f"  Opens: {opens_before}, Closes: {closes_before}, Balance: {opens_before - closes_before}")

print(f"\nAfter QUESTIONS closing:")
print(f"  Opens: {opens_after}, Closes: {closes_after}, Balance: {opens_after - closes_after}")

# Find the last opening brace that doesn't have a matching closing brace
lines = after_questions.split('\n')
brace_count = 0
for i, line in enumerate(lines):
    brace_count += line.count('{') - line.count('}')
    if brace_count < 0:
        print(f"\nBrace imbalance found at line {i} of after_questions:")
        print(f"  {line}")
        print(f"  Brace count: {brace_count}")
        
# Look for unclosed functions
import re
funcs = re.findall(r'function\s+(\w+)\s*\([^)]*\)\s*{', after_questions)
print(f"\nFound {len(funcs)} function definitions after QUESTIONS")
