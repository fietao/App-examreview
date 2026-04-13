# Java Study App — Chapters 6–11

Interactive study app for Java exam prep. Runs locally using Ollama for AI grading of written answers. Checkpoints are saved to a local JSON file so you can resume where you left off.

## Features

- All question types: Multiple Choice, True/False, Find the Error, Algorithm Workbench, Short Answer
- Mix and match any chapters and question types before each session
- Shuffle mode
- AI grading for written answers via Ollama (local, no API key needed)
- Checkpoint saves per chapter — resume anytime
- Retry wrong answers at end of session

## Requirements

- Python 3.8+
- [Ollama](https://ollama.com) installed and running
- Qwen2.5 14B pulled (or any other model — see Config below)

## Setup

```bash
# 1. Install Python dependency
pip install -r requirements.txt

# 2. Make sure Ollama is running
ollama serve

# 3. Pull the model (first time only)
ollama pull qwen2.5:14b

# 4. Run the app
python study_app.py
```

The app opens automatically in your browser at `http://localhost:5000`.

## Config

Edit the top of `study_app.py` to change settings:

```python
OLLAMA_MODEL  = "qwen2.5:14b"       # any model you have pulled
OLLAMA_URL    = "http://localhost:11434/api/generate"
SERVER_PORT   = 5000
SAVE_FILE     = "checkpoints.json"  # saved next to this script
```

To use a different model:
```bash
ollama pull llama3.2
# then set OLLAMA_MODEL = "llama3.2" in study_app.py
```

## Checkpoints

Your progress is saved automatically to `checkpoints.json` in the same folder. Each chapter has its own save slot. You can resume, clear, or start fresh from the home screen.

## Stopping the server

Press `Ctrl+C` in the terminal. Your checkpoints are saved automatically.
