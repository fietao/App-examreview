#!/usr/bin/env python3
import re

with open('study_app.py', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()
    
# Check if there are syntax errors
try:
    compile(content, 'study_app.py', 'exec')
    print('✓ Python syntax OK')
except SyntaxError as e:
    print(f'✗ Syntax error: {e}')

# Count questions
mc_count = content.count('"type":"mc"')
print(f'✓ Found {mc_count} multiple choice questions')
