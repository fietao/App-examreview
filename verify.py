#!/usr/bin/env python3
"""
Java Study App - Verification Script
Checks if the app is correctly configured and ready to run
"""

import os
import sys
import json
import platform
import subprocess
from pathlib import Path
from urllib.request import urlopen
from urllib.error import URLError
import time


class Status:
    """Status indicators"""
    PASS = "✓"
    FAIL = "✗"
    WARN = "⚠"
    INFO = "ℹ"


def print_status(status, message, details=""):
    """Print a status line"""
    colors = {
        "✓": "\033[92m",  # Green
        "✗": "\033[91m",  # Red
        "⚠": "\033[93m",  # Yellow
        "ℹ": "\033[94m",  # Blue
    }
    reset = "\033[0m"
    
    if platform.system() == 'Windows':
        colors = {k: "" for k in colors}
        reset = ""
    
    color = colors.get(status, "")
    print(f"{color}{status}{reset} {message}")
    if details:
        print(f"  {details}")


def header(text):
    """Print a section header"""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")


def check_python():
    """Check Python version"""
    header("Python Environment")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print_status(Status.FAIL, f"Python 3.8+ required")
        print_status(Status.INFO, f"You have: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print_status(Status.PASS, f"Python {version.major}.{version.minor}.{version.micro}")
    print_status(Status.INFO, f"Location: {sys.executable}")
    return True


def check_dependencies():
    """Check if required packages are installed"""
    header("Python Dependencies")
    
    required = {
        "requests": "HTTP library",
        "flask": "Web framework",
        "dotenv": "Environment config",
    }
    
    all_ok = True
    for package, description in required.items():
        try:
            __import__(package if package != "dotenv" else "dotenv")
            print_status(Status.PASS, f"{package}: {description}")
        except ImportError:
            print_status(Status.FAIL, f"{package}: {description} (NOT INSTALLED)")
            all_ok = False
    
    if not all_ok:
        print_status(Status.INFO, "Run: pip install -r requirements.txt")
    
    return all_ok


def check_config_files():
    """Check if configuration files exist"""
    header("Configuration Files")
    
    required_files = {
        "study_app.py": "Main application",
        "questions.json": "Question bank",
        "requirements.txt": "Dependencies",
    }
    
    optional_files = {
        ".env": "Configuration (can auto-create)",
        "checkpoints.json": "Progress save (auto-created on first run)",
    }
    
    all_ok = True
    for filename, description in required_files.items():
        path = Path(filename)
        if path.exists():
            size = path.stat().st_size
            print_status(Status.PASS, f"{filename}: {description} ({size:,} bytes)")
        else:
            print_status(Status.FAIL, f"{filename}: {description} (MISSING)")
            all_ok = False
    
    for filename, description in optional_files.items():
        path = Path(filename)
        if path.exists():
            print_status(Status.PASS, f"{filename}: {description}")
        else:
            print_status(Status.WARN, f"{filename}: {description} (will be created)")
    
    return all_ok


def check_questions_json():
    """Validate questions.json format"""
    header("Question Bank Validation")
    
    try:
        with open("questions.json") as f:
            questions = json.load(f)
        
        if not isinstance(questions, list):
            print_status(Status.FAIL, "questions.json must be a JSON array")
            return False
        
        print_status(Status.PASS, f"Loaded {len(questions)} questions")
        
        # Count by type
        types = {}
        for q in questions:
            qtype = q.get("type", "unknown")
            types[qtype] = types.get(qtype, 0) + 1
        
        for qtype, count in sorted(types.items()):
            print_status(Status.INFO, f"  {qtype}: {count}")
        
        return True
    except json.JSONDecodeError as e:
        print_status(Status.FAIL, f"Invalid JSON: {e}")
        return False
    except FileNotFoundError:
        print_status(Status.FAIL, "questions.json not found")
        return False


def check_ollama():
    """Check if Ollama is installed and running"""
    header("Ollama AI Service")
    
    # Check if ollama command exists
    result = subprocess.run(
        "ollama --version",
        shell=True,
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print_status(Status.FAIL, "Ollama not installed")
        print_status(Status.INFO, "Download from: https://ollama.com/download")
        print_status(Status.WARN, "AI grading will not work without Ollama")
        return False
    
    version = result.stdout.strip()
    print_status(Status.PASS, f"Ollama installed: {version}")
    
    # Check if Ollama is running
    try:
        response = urlopen("http://localhost:11434/api/tags", timeout=2)
        print_status(Status.PASS, "Ollama is running at http://localhost:11434")
        
        # Parse response to see available models
        import json
        data = json.loads(response.read().decode())
        models = data.get("models", [])
        
        if models:
            print_status(Status.INFO, f"Available models: {len(models)}")
            for model in models[:5]:
                name = model.get("name", "unknown")
                print_status(Status.INFO, f"  - {name}")
            if len(models) > 5:
                print_status(Status.INFO, f"  ... and {len(models) - 5} more")
        else:
            print_status(Status.WARN, "No models installed")
            print_status(Status.INFO, "Run: ollama pull qwen2.5:14b")
        
        return True
    except URLError:
        print_status(Status.WARN, "Ollama is not running")
        print_status(Status.INFO, "Start it with: ollama serve")
        return False
    except Exception as e:
        print_status(Status.WARN, f"Could not connect: {e}")
        return False


def check_port():
    """Check if port 5000 is available"""
    header("Network Port")
    
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        result = sock.connect_ex(('localhost', 5000))
        if result == 0:
            print_status(Status.WARN, "Port 5000 is already in use")
            print_status(Status.INFO, "Change SERVER_PORT in .env or stop the other app")
            return False
        else:
            print_status(Status.PASS, "Port 5000 is available")
            return True
    finally:
        sock.close()


def check_env_file():
    """Check .env configuration file"""
    header("Configuration (.env)")
    
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists():
        if env_example.exists():
            print_status(Status.WARN, ".env not found (using defaults)")
            print_status(Status.INFO, "Create from template: cp .env.example .env")
            return True
        else:
            print_status(Status.WARN, ".env and .env.example not found")
            print_status(Status.INFO, "Using built-in defaults")
            return True
    
    print_status(Status.PASS, ".env configuration found")
    
    try:
        from dotenv import dotenv_values
        config = dotenv_values(".env")
        
        # Show key settings
        settings = {
            "OLLAMA_MODEL": "AI Model",
            "SERVER_HOST": "Server Host",
            "SERVER_PORT": "Server Port",
            "DEBUG_MODE": "Debug Mode",
        }
        
        for key, label in settings.items():
            value = config.get(key, "(default)")
            print_status(Status.INFO, f"{label}: {value}")
        
        return True
    except Exception as e:
        print_status(Status.WARN, f"Could not read .env: {e}")
        return True


def run_verification():
    """Run all verification checks"""
    print("\n" + "="*60)
    print("  Java Study App - Verification")
    print("="*60)
    
    checks = [
        ("Python Environment", check_python),
        ("Configuration Files", check_config_files),
        ("Question Bank", check_questions_json),
        ("Python Dependencies", check_dependencies),
        ("Configuration Settings", check_env_file),
        ("Network Port", check_port),
        ("Ollama AI Service", check_ollama),
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print_status(Status.FAIL, f"Error during check: {e}")
            results[name] = False
    
    # Summary
    header("Summary")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    if passed == total:
        print_status(Status.PASS, f"All checks passed! ({passed}/{total})")
        print("\nYou're ready to go! Run:")
        print("  1. ollama serve")
        print("  2. python study_app.py")
        return True
    else:
        failed_checks = [name for name, passed in results.items() if not passed]
        print_status(Status.FAIL, f"Some checks failed ({passed}/{total})")
        print("\nFailed checks:")
        for name in failed_checks:
            print(f"  • {name}")
        print("\nFix these issues and run the verification again:")
        print("  python verify.py")
        return False


if __name__ == "__main__":
    success = run_verification()
    print("\n")
    sys.exit(0 if success else 1)
