#!/usr/bin/env python3
"""
Java Study App - Interactive Setup Script
Works on Windows, macOS, and Linux
"""

import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

    @staticmethod
    def disable():
        """Disable colors on Windows (they're not always supported)"""
        if platform.system() == 'Windows':
            for attr in ['HEADER', 'BLUE', 'CYAN', 'GREEN', 'YELLOW', 'RED', 'ENDC', 'BOLD']:
                setattr(Colors, attr, '')


def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}  {text}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.ENDC}\n")


def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.ENDC}")


def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.ENDC}")


def print_warning(text):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.ENDC}")


def print_info(text):
    print(f"{Colors.BLUE}ℹ {text}{Colors.ENDC}")


def run_command(cmd, description, silent=False):
    """Run a command and return success status"""
    try:
        if silent:
            subprocess.run(cmd, shell=True, check=True, capture_output=True, timeout=300)
        else:
            subprocess.run(cmd, shell=True, check=True, timeout=300)
        return True
    except subprocess.TimeoutExpired:
        print_error(f"{description}: Command timed out (5 minutes)")
        return False
    except subprocess.CalledProcessError as e:
        print_error(f"{description}: Command failed with exit code {e.returncode}")
        return False
    except Exception as e:
        print_error(f"{description}: {str(e)}")
        return False


def check_python():
    """Check if Python 3.8+ is installed"""
    print_header("Checking Python Installation")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print_error(f"Python 3.8+ required. You have {version.major}.{version.minor}.{version.micro}")
        print_info("Download from: https://www.python.org/downloads/")
        return False
    print_success(f"Python {version.major}.{version.minor}.{version.micro} is installed")
    return True


def check_ollama():
    """Check if Ollama is installed"""
    print_header("Checking Ollama Installation")
    if shutil.which("ollama") is None:
        print_error("Ollama is not installed")
        print_info("Download from: https://ollama.com/download")
        print_info("\nAfter installing Ollama, run: ollama serve")
        return False
    
    if not run_command("ollama --version", "Getting Ollama version", silent=True):
        print_error("Ollama not accessible from command line")
        return False
    
    print_success("Ollama is installed")
    return True


def install_python_deps():
    """Install Python dependencies"""
    print_header("Installing Python Dependencies")
    
    req_file = Path(__file__).parent / "requirements.txt"
    if not req_file.exists():
        print_error(f"requirements.txt not found at {req_file}")
        return False
    
    cmd = f"{sys.executable} -m pip install -r requirements.txt"
    if run_command(cmd, "Installing packages from requirements.txt"):
        print_success("Python dependencies installed")
        return True
    else:
        print_error("Failed to install dependencies")
        return False


def setup_env_file():
    """Create .env file if it doesn't exist"""
    print_header("Setting Up Configuration File")
    
    env_file = Path(__file__).parent / ".env"
    env_example = Path(__file__).parent / ".env.example"
    
    if env_file.exists():
        print_info(".env file already exists")
        print_info("Current configuration:")
        with open(env_file) as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    print(f"  {line.rstrip()}")
        return True
    
    if not env_example.exists():
        print_error(".env.example not found")
        return False
    
    # Copy example to .env
    shutil.copy(env_example, env_file)
    print_success(".env created from .env.example")
    
    print_info("\nConfiguration options available in .env:")
    print_info("  OLLAMA_MODEL - AI model (default: qwen2.5:14b)")
    print_info("  OLLAMA_BASE_URL - Ollama API URL (default: http://localhost:11434)")
    print_info("  SERVER_HOST - Server host (default: 127.0.0.1, use 0.0.0.0 for network access)")
    print_info("  SERVER_PORT - Server port (default: 5000)")
    print_info("  DEBUG_MODE - Enable debug logging (default: false)")
    
    return True


def pull_ollama_model(model="qwen2.5:14b"):
    """Pull the Ollama model if not already present"""
    print_header("Setting Up Ollama Model")
    
    # Check if model is already pulled
    try:
        result = subprocess.run(
            "ollama list",
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        if model in result.stdout:
            print_success(f"Model '{model}' is already pulled")
            return True
    except:
        pass
    
    print_info(f"Pulling model '{model}' (this may take a few minutes on first run)...")
    if run_command(f"ollama pull {model}", f"Pulling {model}"):
        print_success(f"Model '{model}' is ready")
        return True
    else:
        print_error(f"Failed to pull model '{model}'")
        print_info("Make sure 'ollama serve' is running in another terminal")
        return False


def run_tests():
    """Run the test script if available"""
    print_header("Testing Installation")
    
    test_file = Path(__file__).parent / "run_test.py"
    if not test_file.exists():
        print_warning("Test file not found")
        return True
    
    print_info("Running tests...")
    if run_command(f"{sys.executable} run_test.py", "Running tests"):
        print_success("Tests passed!")
        return True
    else:
        print_warning("Tests had issues (non-critical)")
        return True


def show_quick_start():
    """Display quick start instructions"""
    print_header("Quick Start Guide")
    
    print("To run the Java Study App:\n")
    print(f"  1. Make sure Ollama is running in another terminal:")
    print(f"     {Colors.BOLD}ollama serve{Colors.ENDC}\n")
    
    print(f"  2. In a new terminal, run the app:")
    print(f"     {Colors.BOLD}python study_app.py{Colors.ENDC}\n")
    
    print(f"  3. Your browser should open automatically at:")
    print(f"     {Colors.BOLD}http://localhost:5000{Colors.ENDC}\n")
    
    print("To access from other machines on your network:")
    print(f"  1. Edit .env and change SERVER_HOST to 0.0.0.0")
    print(f"  2. Run the app: python study_app.py")
    print(f"  3. Other machines can access it at:")
    print(f"     {Colors.BOLD}http://<your-machine-ip>:5000{Colors.ENDC}\n")
    
    print("Need help?")
    print(f"  • Check .env for configuration options")
    print(f"  • Read README.md for detailed documentation")
    print(f"  • Visit https://ollama.com/download for Ollama setup\n")


def main():
    """Main setup flow"""
    # Disable colors on Windows if needed
    if platform.system() == 'Windows':
        try:
            os.system("color")  # Enable ANSI support on Windows 10+
        except:
            Colors.disable()
    
    print(f"\n{Colors.BOLD}{Colors.CYAN}")
    print("╔════════════════════════════════════════════════════════╗")
    print("║     Java Study App - Setup & Configuration             ║")
    print("╚════════════════════════════════════════════════════════╝")
    print(Colors.ENDC)
    
    steps = [
        ("Checking Python", check_python),
        ("Installing dependencies", install_python_deps),
        ("Setting up config file", setup_env_file),
        ("Checking Ollama", check_ollama),
        ("Pulling Ollama model", pull_ollama_model),
        ("Running tests", run_tests),
    ]
    
    failed_steps = []
    
    for step_name, step_func in steps:
        try:
            if not step_func():
                failed_steps.append(step_name)
                if step_name in ["Checking Python", "Installing dependencies"]:
                    # These are critical
                    print_error(f"Setup cannot continue without {step_name}")
                    return False
        except Exception as e:
            print_error(f"Unexpected error in {step_name}: {str(e)}")
            failed_steps.append(step_name)
    
    print_header("Setup Summary")
    
    if failed_steps:
        print_warning(f"Completed with {len(failed_steps)} issue(s):")
        for step in failed_steps:
            print(f"  • {step}")
        print()
    else:
        print_success("All setup steps completed successfully!")
        print()
    
    show_quick_start()
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
