#!/usr/bin/env python3
import urllib.request
import json

# Fetch the HTML from the running server
url = 'http://localhost:5000/'
print("Fetching HTML from", url)
response = urllib.request.urlopen(url)
html = response.read().decode('utf-8')

# Find the script content
script_start = html.find('<script>')
script_end = html.find('</script>', script_start)
if script_start == -1 or script_end == -1:
    print("Script tag not found!")
else:
    script_content = html[script_start+8:script_end]
    print(f"Script tag found, length: {len(script_content)} chars")
    
    # Try to find QUESTIONS
    q_start = script_content.find('const QUESTIONS = [')
    if q_start == -1:
        print("QUESTIONS definition not found!")
    else:
        print(f"QUESTIONS starts at position {q_start}")
        # Find the end of the array
        bracket_depth = 0
        in_string = False
        escape = False
        end_pos = -1
        
        for i in range(q_start, len(script_content)):
            char = script_content[i]
            
            if escape:
                escape = False
                continue
            
            if char == '\\':
                escape = True
                continue
                
            if char == '"' and not escape:
                in_string = not in_string
                continue
            
            if not in_string:
                if char == '[':
                    bracket_depth += 1
                elif char == ']':
                    bracket_depth -= 1
                    if bracket_depth == 0:
                        end_pos = i + 1
                        break
        
        if end_pos == -1:
            print("Could not find closing ] for QUESTIONS!")
        else:
            print(f"QUESTIONS ends at position {end_pos}")
            questions_def = script_content[q_start:end_pos+1]
            
            # Try to parse the JSON
            try:
                # Extract just the JSON part (after = [)
                json_start = q_start + len('const QUESTIONS = ')
                json_str = script_content[json_start:end_pos]
                parsed = json.loads(json_str)
                print(f"✓ JSON parses successfully! Found {len(parsed)} questions")
                print(f"  First question ch: {parsed[0].get('ch')}")
                print(f"  Last question type: {parsed[-1].get('type')}")
            except json.JSONDecodeError as e:
                print(f"✗ JSON parse error: {e}")
                # Show context
                error_pos = json_start + e.pos
                context_start = max(0, error_pos - 100)
                context_end = min(len(script_content), error_pos + 100)
                print(f"  Error at position {e.pos} (overall: {error_pos})")
                print(f"  Context: ...{script_content[context_start:context_end]}...")

print(f"\nTotal HTML size: {len(html)} chars")
print(f"Script tag size: {len(script_content)} chars" if script_start != -1 else "Script tag not found")
