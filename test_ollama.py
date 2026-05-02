#!/usr/bin/env python3
import requests
import json

# Test grading with qwen2.5:14b
url = 'http://localhost:11434/api/generate'
payload = {
    'model': 'qwen2.5:14b',
    'prompt': 'What is 2+2? Answer with just the number.',
    'stream': False,
    'options': {
        'num_predict': 50,
        'temperature': 0.0
    }
}

try:
    resp = requests.post(url, json=payload, timeout=30)
    if resp.status_code == 200:
        result = resp.json()
        print('✓ Ollama API test PASSED')
        print(f'Model response: {result.get("response", "")[:100]}')
    else:
        print(f'✗ API returned status {resp.status_code}')
except Exception as e:
    print(f'✗ Error: {e}')
