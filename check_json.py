import json

# Read the study_app.py file
with open('study_app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the QUESTIONS array
questions_start = content.find('QUESTIONS = [')
questions_end = content.find(']', questions_start)

# Extract and try to parse
json_str = content[questions_start+13:questions_end+1]

try:
    questions = json.loads(json_str)
    print(f"Successfully loaded {len(questions)} questions")
except json.JSONDecodeError as e:
    print(f"JSON Error: {e}")
    print(f"Error at position {e.pos}")
    # Show context around the error
    start = max(0, e.pos - 200)
    end = min(len(json_str), e.pos + 200)
    print(f"\nContext around error:")
    print(json_str[start:end])
    print("^" * 50)
    print(" " * (e.pos - start) + "^^^ ERROR HERE ^^^")
