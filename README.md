# Java Study App — Chapters 6–11

**Interactive Java exam prep app** for practicing and understanding key concepts from Java programming chapters 6-11. Built with Python + Flask, uses Ollama for AI-powered grading of written answers. 

## 🎯 Features

- ✅ **All question types**: Multiple Choice, True/False, Find the Error, Algorithm Workbench, Short Answer
- 📚 **Mix & match chapters**: Select any combination of chapters 6-11
- 🔀 **Shuffle mode**: Randomize question order for better retention
- 🤖 **AI grading**: Ollama-powered local LLM evaluates written answers (no API key, no cloud)
- 💾 **Auto-save progress**: Checkpoints saved per chapter — resume anytime
- 🔄 **Retry failed questions**: Review and retry wrong answers at end of session
- 🌍 **Network accessible**: Share with classmates on the same network
- ⚡ **Lightweight**: Runs entirely locally, no external dependencies

---

## 🚀 Quick Start (1 Minute)

### 1️⃣ Automated Setup (Recommended)

```bash
# Download and extract the app, then run:
python setup.py

# Follow the prompts — setup checks everything automatically
```

### 2️⃣ Run the App

**Terminal 1** — Start Ollama AI server:
```bash
ollama serve
```

**Terminal 2** — Start the study app:
```bash
python study_app.py
```

Browser opens automatically at `http://localhost:5000` ✨

---

## 📋 System Requirements

- **Python**: 3.8 or newer
- **Ollama**: [Download here](https://ollama.com/download)
- **Internet** (for initial Ollama model download, not needed after)
- **RAM**: 
  - 8GB+ for qwen2.5:14b (recommended, balanced)
  - 6GB+ for qwen2.5:7b (faster, lighter)
  - 24GB+ for qwen2.5:32b (highest quality)

---

## 🔧 Installation Guide

### Windows

1. **Install Python**
   - Download: https://www.python.org/downloads/
   - ✅ Check "Add Python to PATH" during installation
   - Verify: Open Command Prompt, type `python --version`

2. **Install Ollama**
   - Download: https://ollama.com/download
   - Run the installer
   - Verify: Open Command Prompt, type `ollama --version`

3. **Run Setup**
   ```cmd
   cd path\to\java_study_app
   python setup.py
   ```

4. **Launch**
   - Open Command Prompt
   - Terminal 1: `ollama serve`
   - Terminal 2: `python study_app.py`

### macOS

1. **Install Python**
   ```bash
   # Using Homebrew (recommended)
   brew install python@3.11
   
   # Or download from: https://www.python.org/downloads/
   ```

2. **Install Ollama**
   - Download: https://ollama.com/download
   - Or: `brew install ollama`

3. **Run Setup**
   ```bash
   cd /path/to/java_study_app
   python3 setup.py
   ```

4. **Launch**
   ```bash
   # Terminal 1
   ollama serve
   
   # Terminal 2
   python3 study_app.py
   ```

### Linux (Ubuntu/Debian)

1. **Install Python**
   ```bash
   sudo apt update
   sudo apt install python3.11 python3-pip
   ```

2. **Install Ollama**
   ```bash
   # Official installer (recommended)
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Or via package manager
   # Check: https://ollama.com/download/linux
   ```

3. **Run Setup**
   ```bash
   cd /path/to/java_study_app
   python3 setup.py
   ```

4. **Launch**
   ```bash
   # Terminal 1
   ollama serve
   
   # Terminal 2
   python3 study_app.py
   ```

---

## ⚙️ Configuration

The app reads settings from `.env` file. Copy and customize:

```bash
# Copy the example (first time only)
cp .env.example .env

# Edit .env in your favorite text editor
```

### Configuration Options

```env
# Which AI model to use for grading
# Options: qwen2.5:7b (fast), qwen2.5:14b (balanced), qwen2.5:32b (best)
OLLAMA_MODEL=qwen2.5:14b

# Ollama API server
OLLAMA_BASE_URL=http://localhost:11434

# Who can access the app
# 127.0.0.1 or localhost = local only (secure)
# 0.0.0.0 = network accessible (share with classmates)
SERVER_HOST=127.0.0.1

# Web server port
SERVER_PORT=5000

# Auto-launch browser on start (true/false)
AUTO_OPEN_BROWSER=true

# Enable debug logging (true/false)
DEBUG_MODE=false
```

### Changing the Model

If your machine has limited RAM or you want faster performance:

```env
# For lighter hardware (~6GB RAM)
OLLAMA_MODEL=qwen2.5:7b

# For high-end hardware (~24GB RAM)  
OLLAMA_MODEL=qwen2.5:32b
```

Then run: `ollama pull qwen2.5:7b` before starting the app.

### Network Access

To share the app with classmates on the same network:

```env
SERVER_HOST=0.0.0.0
```

Then other machines can access it at: `http://<your-machine-ip>:5000`

Find your IP:
- **Windows**: `ipconfig` (look for "IPv4 Address")
- **macOS/Linux**: `ifconfig` or `hostname -I`

---

## 📖 Usage

1. **Select chapters**: Click the chapter chips (6-11) to choose which to study
2. **Select question types**: Choose from Multiple Choice, True/False, etc.
3. **Choose quantity**: Pick how many questions (or leave random)
4. **Toggle shuffle**: Randomize order if desired
5. **Start session**: Begin studying
6. **Answer questions**: Read carefully, think through each one
7. **AI grades written answers**: System evaluates Short Answer questions
8. **Review results**: See your score and explanations
9. **Retry weak areas**: Answer incorrectly-graded questions again

Your progress is automatically saved to `checkpoints.json` — you can resume anytime.

---

## 🐳 Docker (Optional)

Run the entire app in Docker — no local setup needed:

```bash
# Build the Docker image
docker build -t java-study-app .

# Run the container
# Local access only:
docker run -p 5000:5000 java-study-app

# Network accessible:
docker run -p 5000:5000 -e SERVER_HOST=0.0.0.0 java-study-app

# With custom model:
docker run -p 5000:5000 -e OLLAMA_MODEL=qwen2.5:7b java-study-app
```

---

## 🐛 Troubleshooting

### "Ollama not found" / "Can't connect to Ollama"
- Make sure `ollama serve` is running in another terminal
- On macOS/Linux, Ollama might be installed but not in PATH — try: `/Applications/Ollama.app/Contents/MacOS/ollama serve`

### "Model not found" / "Permission denied"
- Pull the model first: `ollama pull qwen2.5:14b`
- Check available models: `ollama list`

### App is slow / Using too much RAM
- Try a smaller model: `OLLAMA_MODEL=qwen2.5:7b`
- Close other applications

### "Port 5000 is already in use"
- Change the port in `.env`: `SERVER_PORT=5001`
- Or kill the process using port 5000:
  - **Windows**: `netstat -ano | findstr :5000` then `taskkill /PID <PID> /F`
  - **macOS/Linux**: `lsof -i :5000` then `kill -9 <PID>`

### Browser won't auto-open
- Set `AUTO_OPEN_BROWSER=false` in `.env`
- Manually open: `http://localhost:5000`

---

## 🛠️ Development

### Project Structure

```
java_study_app/
├── study_app.py           # Main app (Flask + HTTP server)
├── questions.json         # Question bank
├── checkpoints.json       # User progress (auto-created)
├── requirements.txt       # Python dependencies
├── setup.py              # Interactive setup wizard
├── .env.example          # Config template
├── .env                  # Your config (created by setup)
├── Dockerfile            # Docker configuration
└── README.md             # This file
```

### Running Tests

```bash
python run_test.py
```

### Modifying Questions

Edit `questions.json` directly (JSON format):

```json
{
  "ch": 6,
  "type": "mc",
  "q": "Question text?",
  "answer": "a",
  "explain": "Explanation text..."
}
```

### Updating UI

The HTML/CSS/JavaScript is embedded in `study_app.py`. Edit the `HTML_PAGE` string.

---

## 📝 Question Types Explained

| Type | Abbr | Description |
|------|------|-------------|
| **Multiple Choice** | `mc` | Select one of four options (a, b, c, d) |
| **True/False** | `tf` | Answer True or False |
| **Find the Error** | `fte` | Identify bugs in code snippets |
| **Algorithm Workbench** | `aw` | Write or complete Java code |
| **Short Answer** | `sa` | Write a detailed explanation (AI-graded) |

---

## 📞 Support & Contributing

### Issues?
Check the [Troubleshooting](#-troubleshooting) section above.

### Want to contribute?
1. Test the app thoroughly
2. Submit bug reports or feature requests
3. Improve question bank
4. Suggest UI enhancements

---

## 📄 License

This project is for educational purposes.

---

## 🎓 About

Built by students, for students. Designed to make Java Chapter 6-11 concepts stick through interactive practice, immediate feedback, and AI-powered grading.

**Happy studying!** 🚀

ollama pull llama3.2
# then set OLLAMA_MODEL = "llama3.2" in study_app.py
```

## Checkpoints

Your progress is saved automatically to `checkpoints.json` in the same folder. Each chapter has its own save slot. You can resume, clear, or start fresh from the home screen.

## Stopping the server

Press `Ctrl+C` in the terminal. Your checkpoints are saved automatically.
