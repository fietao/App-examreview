import subprocess
import sys

with open('run_log.txt', 'w') as f:
    try:
        process = subprocess.Popen([sys.executable, 'study_app.py'], stdout=f, stderr=f)
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.terminate()
        print("Process timed out after 5s (expected if it's a server)")
    except Exception as e:
        print(f"Error: {e}")
