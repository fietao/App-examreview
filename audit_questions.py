#!/usr/bin/env python3
import re
import json

with open('study_app.py', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Extract QUESTIONS
match = re.search(r'QUESTIONS = \[(.*?)\](?=\s*def )', content, re.DOTALL)
if match:
    questions_str = '[' + match.group(1) + ']'
    try:
        questions = json.loads(questions_str)
        
        # Group by type
        types = {}
        for q in questions:
            qtype = q.get('type')
            if qtype not in types:
                types[qtype] = []
            types[qtype].append(q)
        
        print("=" * 60)
        print("QUESTION AUDIT REPORT")
        print("=" * 60)
        
        for qtype in sorted(types.keys()):
            qs = types[qtype]
            print(f"\n[{qtype.upper()}] - {len(qs)} questions")
            print("-" * 60)
            
            for i, q in enumerate(qs, 1):
                ch = q['ch']
                q_text = q['q']
                ans = q.get('answer', '')
                explain = q.get('explain', '')
                
                # Show first question of each type fully
                if i <= 2 or (qtype == 'aw' and i <= 3):
                    print(f"\nQ{i} (Ch {ch}):")
                    print(f"  Q: {q_text[:100]}{'...' if len(q_text) > 100 else ''}")
                    print(f"  A: {ans[:80]}{'...' if len(ans) > 80 else ''}")
                    
                    # Check for issues
                    issues = []
                    if not ans:
                        issues.append("Missing answer")
                    if not explain:
                        issues.append("Missing explanation")
                    if len(q_text) < 10:
                        issues.append("Question too short")
                    if qtype == 'mc' and 'a)' not in q_text:
                        issues.append("Missing option format")
                    
                    if issues:
                        print(f"  ⚠ Issues: {', '.join(issues)}")

    except Exception as e:
        print(f"Error: {e}")
