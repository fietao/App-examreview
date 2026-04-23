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

# Count quotes properly, ignoring comments and content inside strings
quote_count = 0
positions = []

i = 0
in_double = False
in_single = False
in_backtick = False

while i < len(script_content):
    char = script_content[i]
    
    # Skip line comments
    if char == '/' and i + 1 < len(script_content) and script_content[i + 1] == '/' and not in_double and not in_single and not in_backtick:
        # Skip until end of line
        while i < len(script_content) and script_content[i] != '\n':
            i += 1
        i += 1  # Skip the newline
        continue
    
    # Skip block comments
    if char == '/' and i + 1 < len(script_content) and script_content[i + 1] == '*' and not in_double and not in_single and not in_backtick:
        # Skip until */
        i += 2
        while i + 1 < len(script_content):
            if script_content[i] == '*' and script_content[i + 1] == '/':
                i += 2
                break
            i += 1
        continue
    
    # Handle escapes
    if char == '\\' and i + 1 < len(script_content) and (in_double or in_single or in_backtick):
        i += 2
        continue
    
    # Track string states
    if char == '"' and not in_single and not in_backtick:
        in_double = not in_double
    elif char == "'" and not in_double and not in_backtick:
        in_single = not in_single
        if in_single or not in_single:  # Track for debugging
            quote_count += 1
            positions.append(i)
    elif char == '`' and not in_double and not in_single:
        in_backtick = not in_backtick
    
    i += 1

print(f"Single quote count (ignoring comments): {quote_count} ({'EVEN' if quote_count % 2 == 0 else 'ODD'})")

if quote_count % 2 == 1 and len(positions) > 0:
    print(f"PROBLEM: Odd number of single quotes!")
    last_pos = positions[-1]
    print(f"Last unclosed quote at position {last_pos}")
    
    context_start = max(0, last_pos - 150)
    context_end = min(len(script_content), last_pos + 150)
    context = script_content[context_start:context_end]
    rel_pos = last_pos - context_start
    
    print(f"\nContext:")
    print(context[:rel_pos] + "[UNCLOSED]" + context[rel_pos+1:])
else:
    print("✓ All single quotes are properly paired!")
