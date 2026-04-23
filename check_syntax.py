#!/usr/bin/env python3
import study_app
import json

# Get the full HTML with QUESTIONS injected
html = study_app.HTML_PAGE.replace(
    "__QUESTIONS__", 
    json.dumps(study_app.QUESTIONS, ensure_ascii=False)
)

# Extract the script content
script_start = html.find('<script>')
script_end = html.find('</script>')
script_content = html[script_start + 8:script_end]

# Try to validate JavaScript syntax using a simple check
# This won't fully parse but will catch common issues

print("=" * 60)
print("SCRIPT SYNTAX CHECK")
print("=" * 60)

# Check if there are any obvious syntax errors
issues = []

# 1. Check for unclosed strings
single_quotes = 0
double_quotes = 0
backticks = 0
escaped = False

for i, char in enumerate(script_content):
    if escaped:
        escaped = False
        continue
    
    if char == '\\':
        escaped = True
        continue
    
    if char == "'":
        single_quotes += 1
    elif char == '"':
        double_quotes += 1
    elif char == '`':
        backticks += 1

print(f"\nString quote counts:")
print(f"  Single quotes: {single_quotes} {'✓' if single_quotes % 2 == 0 else '✗ ODD'}")
print(f"  Double quotes: {double_quotes} {'✓' if double_quotes % 2 == 0 else '✗ ODD'}")
print(f"  Backticks: {backticks} {'✓' if backticks % 2 == 0 else '✗ ODD'}")

# 2. Check for proper closing of braces, brackets, parens
braces = {"open": 0, "close": 0, "balance": []}
brackets = {"open": 0, "close": 0, "balance": []}
parens = {"open": 0, "close": 0, "balance": []}

in_string = False
string_char = None
escaped = False

for i, char in enumerate(script_content):
    if escaped:
        escaped = False
        continue
    
    if char == '\\':
        escaped = True
        continue
    
    if char in ['"', "'", '`'] and not in_string:
        in_string = True
        string_char = char
    elif char == string_char and in_string:
        in_string = False
        string_char = None
    
    if not in_string:
        if char == '{':
            braces["open"] += 1
            braces["balance"].append(1)
        elif char == '}':
            braces["close"] += 1
            braces["balance"].append(-1)
        elif char == '[':
            brackets["open"] += 1
            brackets["balance"].append(1)
        elif char == ']':
            brackets["close"] += 1
            brackets["balance"].append(-1)
        elif char == '(':
            parens["open"] += 1
            parens["balance"].append(1)
        elif char == ')':
            parens["close"] += 1
            parens["balance"].append(-1)

print(f"\nBrace/Bracket/Paren counts:")
print(f"  Braces: {braces['open']} open, {braces['close']} close {'✓' if braces['open'] == braces['close'] else '✗ UNBALANCED'}")
print(f"  Brackets: {brackets['open']} open, {brackets['close']} close {'✓' if brackets['open'] == brackets['close'] else '✗ UNBALANCED'}")
print(f"  Parens: {parens['open']} open, {parens['close']} close {'✓' if parens['open'] == parens['close'] else '✗ UNBALANCED'}")

# 3. Check if script starts with valid JavaScript
first_500 = script_content[:500]
print(f"\nScript starts with:")
print(repr(first_500))

# 4. Check if const QUESTIONS is properly terminated
questions_line = script_content.find('const QUESTIONS = ')
if questions_line >= 0:
    # Find the semicolon that should end this statement
    next_semicolon = script_content.find(';', questions_line)
    if next_semicolon >= 0:
        questions_section = script_content[questions_line:next_semicolon + 50]
        print(f"\nQUESTIONS declaration looks like:")
        # Just show the beginning and end
        if len(questions_section) > 100:
            print(f"  {questions_section[:50]}...")
            print(f"  ...{questions_section[-50:]}")
        else:
            print(f"  {questions_section}")
    else:
        print(f"\n✗ No semicolon found after QUESTIONS declaration!")

print("\n" + "=" * 60)
