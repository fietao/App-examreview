import re

# Read the file
with open('study_app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the QUESTIONS array
match = re.search(r'QUESTIONS = \[(.*?)\]\s*SAVE_PATH', content, re.DOTALL)
if not match:
    print("Could not find QUESTIONS array")
    exit(1)

json_content = '[' + match.group(1) + ']'

# Try to parse it
import json
try:
    data = json.loads(json_content)
    print(f"Successfully loaded {len(data)} questions")
except json.JSONDecodeError as e:
    print(f"JSON Error: {e}")
    print(f"Position: {e.pos}")
    print(f"Line: {e.lineno}, Column: {e.colno}")
    
    # Get more context
    lines = json_content.split('\n')
    line_num = e.lineno - 1
    if 0 <= line_num < len(lines):
        print(f"\nError context (line {e.lineno}):")
        # Show 3 lines before and after
        for i in range(max(0, line_num-3), min(len(lines), line_num+4)):
            marker = ">>> " if i == line_num else "    "
            print(f"{marker}{i+1}: {lines[i][:120]}")
