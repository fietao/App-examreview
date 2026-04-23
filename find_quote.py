#!/usr/bin/env python3
import study_app
import json

html = study_app.HTML_PAGE.replace(
    "__QUESTIONS__", 
    json.dumps(study_app.QUESTIONS, ensure_ascii=False)
)

script_start = html.find('<script>')
script_end = html.find('</script>')
script_content = html[script_start + 8:script_end]

# Find the unclosed single quote
quote_count = 0
positions = []

escaped = False
in_double = False
in_backtick = False

for i, char in enumerate(script_content):
    if escaped:
        escaped = False
        continue
    
    if char == '\\':
        escaped = True
        continue
    
    # Track double quotes and backticks to know if we're inside them
    if char == '"' and not in_backtick:
        in_double = not in_double
    elif char == '`' and not in_double:
        in_backtick = not in_backtick
    elif char == "'" and not in_double and not in_backtick:
        quote_count += 1
        positions.append(i)

print(f"Single quote count: {quote_count} ({'EVEN' if quote_count % 2 == 0 else 'ODD'})")

if quote_count % 2 == 1:
    print(f"\nTotal single quotes found: {len(positions)}")
    print(f"Last 10 positions: {positions[-10:]}")
    
    # Show context around the odd quote
    last_pos = positions[-1]
    context_start = max(0, last_pos - 100)
    context_end = min(len(script_content), last_pos + 100)
    
    context = script_content[context_start:context_end]
    rel_pos = last_pos - context_start
    
    print(f"\nContext around odd quote (position {last_pos}):")
    print(f"...{context[:rel_pos]}[QUOTE HERE]{context[rel_pos+1:]}...")

# Also check the quotes before and after it
if len(positions) >= 2:
    second_last_pos = positions[-2]
    print(f"\nBetween last two quotes (positions {second_last_pos} to {last_pos}):")
    between = script_content[second_last_pos:last_pos + 1]
    # Count newlines
    newlines = between.count('\n')
    print(f"Content length: {len(between)} chars, {newlines} newlines")
    if len(between) < 500:
        print(f"Content:\n{between}")
    else:
        print(f"First 200 chars:\n{between[:200]}")
        print(f"...\nLast 200 chars:\n{between[-200:]}")
