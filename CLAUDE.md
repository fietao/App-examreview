# Java Study App — Claude Instructions

## What this project is

Interactive Java exam prep app (Chapters 6–11). Python + Flask backend, runs locally. Uses Ollama for AI grading of written answers. Progress saved to `checkpoints.json`.

## Stack

- **Backend:** Python 3.8+, Flask, `study_app.py` is the single entry point
- **AI grading:** Ollama — local LLM inference, OpenAI-compatible API at `http://localhost:11434`
- **Default model:** `qwen2.5:14b` (configured at top of `study_app.py`)
- **Data:** `questions.json` (question bank), `checkpoints.json` (user progress)
- **Port:** 5000

## Ollama integration rules

- Ollama runs at `http://localhost:11434/api/generate` (non-chat endpoint) or `/v1` (OpenAI-compatible)
- Always check Ollama is reachable before grading — surface a clear error if not
- Model is configurable via `OLLAMA_MODEL` constant — never hardcode `qwen2.5:14b` elsewhere
- For lighter hardware: `qwen2.5:7b` works; for higher quality: `qwen2.5:32b` (needs 24GB VRAM)
- `nomic-embed-text` is available via Ollama if embeddings are ever needed

## Key files

- `study_app.py` — all app logic and config constants at the top
- `questions.json` — question bank (Multiple Choice, True/False, Find the Error, Algorithm Workbench, Short Answer)
- `checkpoints.json` — per-chapter save slots, auto-written on progress
- `run_test.py` — test runner
- `start.bat` — Windows launcher

## Coding rules

- Keep all config (model, URL, port, save file) as constants at the top of `study_app.py`
- Checkpoints must be saved atomically — never leave `checkpoints.json` in a partial state
- AI grading is async from the user's perspective — show a loading state, don't block the UI
- Question types: Multiple Choice, True/False, Find the Error, Algorithm Workbench, Short Answer — all must be handled
- Shuffle mode must work across all question types

## Do not

- Do not add cloud API dependencies — this app is fully local by design
- Do not require API keys
- Do not break checkpoint resume — it's a core feature
