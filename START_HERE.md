# 🎓 How to Read This Codebase - A Learning Path

Stop vibe coding. Here's your guided tour of the Java Study App, starting with **exactly** where to begin.

---

## 📚 Documentation You Have

| File | Purpose | Read When |
|------|---------|-----------|
| **ARCHITECTURE.md** | Complete overview + key functions | Start here first |
| **CODE_MAP.md** | Visual map + where things are | Quick reference |
| **TRACE_TUTORIAL.md** | Step-by-step user action walkthrough | Learn how pieces connect |
| **study_app.py** | The actual code (1854 lines) | After reading guides |

---

## 🚀 Learning Path (Recommended Order)

### **Level 1: Big Picture (15 minutes)**

1. Read: [ARCHITECTURE.md](ARCHITECTURE.md) - Full Overview
   - Understand: 📊 Architecture Overview (lines 4-44)
   - Understand: 🚀 Entry Point (lines 47-80)
   
2. Read: [CODE_MAP.md](CODE_MAP.md) - Visual Map
   - Understand: 🗺️ Code Map (lines 3-50)
   - Reference: 🔍 Find-It-Fast Guide (lines 53-71)

**After this:** You know what each piece does and where it is.

---

### **Level 2: Key Functions (30 minutes)**

Read: [ARCHITECTURE.md](ARCHITECTURE.md) - Key Functions Section
- Learn: `load_saves()` (saves user progress)
- Learn: `write_saves()` (reads user progress)  
- Learn: `grade_with_ollama()` (AI grading)
- Learn: `Handler` class (HTTP endpoints)

**After this:** You understand the core logic.

---

### **Level 3: Real Flow (20 minutes)**

Read: [TRACE_TUTORIAL.md](TRACE_TUTORIAL.md) - Complete User Journey
- Trace: User opens app
- Trace: User starts quiz
- Trace: **User answers short answer** ← The interesting part
- Trace: Server grades with AI
- Trace: User saves progress

**After this:** You see how the pieces work together.

---

### **Level 4: Read the Code (As needed)**

Now open: [study_app.py](study_app.py)

**Start with these sections:**

1. **Config (Lines 23-31)**
   ```python
   OLLAMA_MODEL = os.getenv(...)
   SERVER_HOST = os.getenv(...)
   ```
   💡 This is how the app is configured. Currently using environment variables.

2. **Functions (Lines 290-340)**
   ```python
   def load_saves(): ...
   def write_saves(data): ...
   def grade_with_ollama(...): ...
   ```
   💡 These are the core operations. Read slowly.

3. **Handler Class (Lines 1737-1807)**
   ```python
   class Handler(BaseHTTPRequestHandler):
       def do_GET(self): ...
       def do_POST(self): ...
   ```
   💡 This handles HTTP requests. Matches what you learned in TRACE_TUTORIAL.

4. **Main Entry (Lines 1809-1854)**
   ```python
   def main():
       ...
       server = ThreadedHTTPServer((SERVER_HOST, SERVER_PORT), Handler)
       server.serve_forever()
   
   if __name__ == "__main__":
       main()
   ```
   💡 This starts the server. Fairly simple.

---

## 🎯 Three Key Concepts

### **1. HTTP Server**
The app is a **Python HTTP server** (not a web framework like Flask).

```python
class Handler(BaseHTTPRequestHandler):  # Handles each request
    def do_GET(self): ...               # GET requests
    def do_POST(self): ...              # POST requests
```

When browser sends request → Handler processes it → Sends response

### **2. REST API**
Browser and server communicate via **JSON over HTTP**.

```python
# Browser: GET /api/saves
# Server: return {"sessions": [...]}

# Browser: POST /api/grade {question, correct_answer, student_answer}
# Server: return {"verdict": "CORRECT", ...}
```

### **3. Ollama Integration**
Server calls external **Ollama AI service** to grade essays.

```python
def grade_with_ollama(q, correct, student):
    # Make HTTP call to Ollama
    requests.post("http://localhost:11434/api/generate", ...)
    # Ollama returns: AI's grading
```

---

## ❓ Now Answer These Questions

Can you answer these without looking? If yes = you understand it!

1. **Where are the questions stored?**
   <details><summary>Answer</summary>QUESTIONS array at line 47</details>

2. **What function saves progress?**
   <details><summary>Answer</summary>write_saves() at line 301</details>

3. **How does the browser send a grade request?**
   <details><summary>Answer</summary>POST /api/grade with {question, correct_answer, student_answer}</details>

4. **What happens in grade_with_ollama()?**
   <details><summary>Answer</summary>Formats prompt for AI, calls Ollama API, parses response, returns verdict/missing/feedback</details>

5. **Where's the HTML/CSS/JavaScript?**
   <details><summary>Answer</summary>HTML_PAGE variable around line 363</details>

6. **What file stores user progress?**
   <details><summary>Answer</summary>checkpoints.json (generated at runtime)</details>

If you got 5+: **You're ready to code!** 🎉

---

## 💡 Common Modifications

Now that you understand the code:

### **Add a New Question**
```python
# Open study_app.py
# Go to line 47: QUESTIONS = [...]
# Add new dict:
{"ch": 6, "type": "sa", "q": "Your question?", "answer": "Correct answer", "explain": "Why this is right"}
```

### **Change AI Model**
```bash
# Edit .env file
OLLAMA_MODEL=qwen2.5:7b  # Change to smaller model
```

### **Add New API Endpoint**
```python
# In do_GET() or do_POST() (around line 1768-1790)
elif path == "/api/newfeature":
    self.send_json({"data": "whatever"})
```

### **Change Grading Prompt**
```python
# In grade_with_ollama() (line 312)
# Edit the: prompt = f"""...""" part
# This changes what the AI sees and how it grades
```

---

## 🐛 Debugging Workflow

If something's broken:

1. **Read relevant docs first** (ARCHITECTURE.md or TRACE_TUTORIAL.md)
2. **Find the relevant code section**
3. **Add print() statements** to see what's happening
4. **Check the flow** - does data move where it should?
5. **Use browser console** (F12) to see JavaScript errors
6. **Check server logs** for Python errors

Example:
```python
# If saves aren't working, add debugging:
def write_saves(data):
    print(f"DEBUG: Saving {len(data['sessions'])} sessions")
    print(f"DEBUG: Data = {data}")  # See what we're saving
    with open(SAVE_PATH, "w") as f:
        json.dump(data, f, indent=2)
    print(f"DEBUG: Saved to {SAVE_PATH}")
```

---

## 📖 File Organization

```
study_app.py (1854 lines)
├─ Lines 1-45: Config
├─ Lines 47-288: Questions data
├─ Lines 290-340: Core functions
│  ├─ load_saves()
│  ├─ write_saves()
│  └─ grade_with_ollama() ← Most complex
├─ Lines 363-1735: Frontend (HTML/CSS/JS)
├─ Lines 1737-1807: HTTP Server
│  ├─ class Handler
│  ├─ do_GET()
│  └─ do_POST()
└─ Lines 1809-1854: Main entry

Support files:
├─ checkpoints.json (generated, user progress)
├─ questions.json (can also load from file)
├─ .env (configuration)
├─ requirements.txt (Python dependencies)
└─ setup.py (automated setup)
```

---

## ✅ Confidence Checklist

Before you start coding, check:

- [ ] I've read ARCHITECTURE.md
- [ ] I've read CODE_MAP.md  
- [ ] I've read TRACE_TUTORIAL.md
- [ ] I can find `load_saves()` in the code
- [ ] I understand what POST `/api/grade` does
- [ ] I know where the HTML/CSS/JS is
- [ ] I can trace a user action through the code
- [ ] I know how to add a new endpoint
- [ ] I know how to modify the grading prompt
- [ ] I know how to add a debug print statement

**Score:**
- 8-10: You're a code expert now 🚀
- 5-7: You've got the gist, keep going 💪
- <5: Read the docs again and come back

---

## 🎓 Pro Tips

### **Tip 1: Read the Error Message**
99% of bugs come from reading what Python/browser tells you.

### **Tip 2: Use Print Debugging**
```python
print(f"About to grade: {question}")
result = grade_with_ollama(...)
print(f"Got result: {result}")
```

### **Tip 3: Browser DevTools is Your Friend**
Press **F12** → Console tab → See JavaScript errors real-time

### **Tip 4: Version Control**
Before you modify code, make a backup:
```bash
cp study_app.py study_app.py.bak
```

### **Tip 5: Read Related Code Together**
When debugging `/api/grade`:
- See frontend call: HTML_PAGE → fetch("/api/grade", ...)
- See backend handler: do_POST() → grade_with_ollama()
- Understand them together, not separately

---

## 🚀 Next Steps

1. ✅ Read all the documentation (you are here)
2. ✅ Run the app: `python setup.py` then `python study_app.py`
3. ✅ Add a simple question to QUESTIONS array
4. ✅ Restart server and verify it shows up
5. ✅ Add a debug print statement in `grade_with_ollama()`
6. ✅ Answer a short essay and check the server logs
7. ✅ Try changing the grading prompt slightly
8. ✅ Add a new API endpoint that returns a custom message

After these steps, you'll have **real understanding**, not vibe coding! 💪

---

## 📞 Still Confused?

Questions? Here's where to look:

| Question | Look Here |
|----------|-----------|
| How does X work? | TRACE_TUTORIAL.md (see real flow) |
| Where is X in the code? | CODE_MAP.md (find-it-fast) |
| What is the overall design? | ARCHITECTURE.md (complete overview) |
| How do I modify Y? | CODE_MAP.md (modify-it guide) |
| Something is broken! | ARCHITECTURE.md (debug checklist) |

---

**You've got this! Stop guessing, start understanding!** 🎉

Now close this file and open [ARCHITECTURE.md](ARCHITECTURE.md) and start reading.
