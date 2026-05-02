# QUICK START GUIDE

## 🚀 Get Running in 5 Minutes

### Option 1: Automated Setup (Recommended)

```bash
python setup.py
```

Follow the prompts — it handles everything automatically.

### Option 2: Manual Setup

**Step 1: Install Python & Ollama**
- Python: https://www.python.org/
- Ollama: https://ollama.com/

**Step 2: Install Dependencies**
```bash
pip install -r requirements.txt
```

**Step 3: Start the Services**

Terminal 1:
```bash
ollama serve
```

Terminal 2:
```bash
python study_app.py
```

Open: `http://localhost:5000`

---

## 🐳 Docker Alternative

No local setup needed:

```bash
docker-compose up
```

Open: `http://localhost:5000`

See `DOCKER.md` for details.

---

## ✅ Verify Setup

Run this to check everything:

```bash
python verify.py
```

---

## ⚙️ Configuration

Copy `.env.example` to `.env` and customize:

```bash
cp .env.example .env
```

Key settings:
- `OLLAMA_MODEL`: AI model to use
- `SERVER_HOST`: Who can access (127.0.0.1 = local only, 0.0.0.0 = network)
- `SERVER_PORT`: Web server port (default: 5000)

---

## 📖 Full Documentation

- **README.md** — Complete setup & usage guide for all platforms
- **DOCKER.md** — Docker & docker-compose setup
- **CLAUDE.md** — Developer notes

---

## 🆘 Troubleshooting

### "Can't connect to Ollama"
Make sure `ollama serve` is running in another terminal.

### "Port 5000 already in use"
Change `SERVER_PORT` in `.env` to something else (e.g., 5001).

### "Model not found"
Run: `ollama pull qwen2.5:14b`

### Check System
Run: `python verify.py`

---

## 🎓 How to Use

1. **Select chapters** (6-11)
2. **Select question types** (MC, T/F, etc.)
3. **Shuffle?** (optional)
4. **Start session**
5. **Answer questions**
6. **Get AI graded** (for essays)
7. **Review results**
8. **Retry weak areas**

Progress auto-saves to `checkpoints.json` ✨

---

## Need Help?

- Check README.md (full documentation)
- Run `python verify.py` to diagnose issues
- See DOCKER.md if using Docker

---

**Happy studying!** 🎉
