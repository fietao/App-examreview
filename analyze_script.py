import study_app
import json

html = study_app.HTML_PAGE.replace('__QUESTIONS__', json.dumps(study_app.QUESTIONS))

# Extract script content
script_start = html.find('<script>')
script_end = html.find('</script>')
script_content = html[script_start+8:script_end]

# Count all braces, brackets, and parens throughout
print('Analyzing entire script...')
braces = {'open': 0, 'close': 0}
brackets = {'open': 0, 'close': 0}
parens = {'open': 0, 'close': 0}

inString = False
escape = False

for i, char in enumerate(script_content):
    if escape:
        escape = False
        continue
    if char == '\\':
        escape = True
        continue
    if char == '"' and not inString:
        inString = True
    elif char == '"' and inString:
        inString = False
    
    if not inString:
        if char == '{': braces['open'] += 1
        elif char == '}': braces['close'] += 1
        elif char == '[': brackets['open'] += 1
        elif char == ']': brackets['close'] += 1
        elif char == '(': parens['open'] += 1
        elif char == ')': parens['close'] += 1

print(f"Braces: {braces['open']} open, {braces['close']} close, diff: {braces['open'] - braces['close']}")
print(f"Brackets: {brackets['open']} open, {brackets['close']} close, diff: {brackets['open'] - brackets['close']}")
print(f"Parens: {parens['open']} open, {parens['close']} close, diff: {parens['open'] - parens['close']}")
