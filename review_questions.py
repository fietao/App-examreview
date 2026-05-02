#!/usr/bin/env python3
import json
import re

# Read study_app.py and extract QUESTIONS
with open('study_app.py', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()
    
# Find QUESTIONS array
match = re.search(r'QUESTIONS = \[(.*?)\](?=\s*def )', content, re.DOTALL)
if match:
    questions_str = '[' + match.group(1) + ']'
    try:
        questions = json.loads(questions_str)
        
        # Find multiple choice questions
        mc_questions = [q for q in questions if q.get('type') == 'mc']
        print(f"Total MC questions: {len(mc_questions)}\n")
        
        # Show all to review
        for i, q in enumerate(mc_questions, 1):
            ch = q['ch']
            ans = q['answer']
            q_text = q['q']
            
            # Extract options
            lines = q_text.split('\n')
            print(f"Q{i} (Ch {ch}): {lines[0]}")
            for line in lines[1:]:
                if line.strip():
                    print(f"  {line}")
            print(f"  ✓ Answer: {ans}")
            print()
    except Exception as e:
        print(f"Error: {e}")
