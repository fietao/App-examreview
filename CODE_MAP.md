# Java Study App - Visual Map & Quick Lookups

## 🗺️ Code Map (Where Things Are)

```
study_app.py (1854 lines) - THE ENTIRE APP IN ONE FILE
│
├─ TOP (Lines 1-45)
│  ├─ Imports (requests, json, threading, BaseHTTPRequestHandler, dotenv)
│  └─ CONFIG (OLLAMA_MODEL, SERVER_HOST, SERVER_PORT, SAVE_FILE, DEBUG_MODE)
│
├─ DATA (Lines 47-288)
│  └─ QUESTIONS = [800+ exam questions]
│     └─ Each question: {ch, type, q, answer, explain}
│
├─ FUNCTIONS (Lines 290-340)
│  ├─ load_saves() → Read checkpoints.json
│  ├─ write_saves(data) → Write to checkpoints.json
│  └─ grade_with_ollama() → Call Ollama AI for grading
│
├─ FRONTEND (Lines 363-1735)
│  └─ HTML_PAGE = """
│     <html>
│     <style> ... UI styling ...
│     <script> ... JavaScript for interactivity ...
│     <body> ... DOM elements ...
│
├─ HTTP SERVER (Lines 1737-1807)
│  └─ class Handler(BaseHTTPRequestHandler):
│     ├─ do_GET(path)
│     │  ├─ "/" → Serve HTML page
│     │  ├─ "/api/saves" → Load checkpoints
│     │  ├─ "/api/config" → Show settings
│     │  └─ "/api/health" → Check Ollama
│     │
│     └─ do_POST(path)
│        ├─ "/api/saves" → Save checkpoints
│        └─ "/api/grade" → Grade with AI
│
└─ MAIN (Lines 1809-1854)
   └─ main() → Start server
      └─ if __name__ == "__main__": main()
```

---

## 🎯 What You Actually Need to Know

### **The Big 3 Operations:**

#### **1. LOAD** (Reading data)
```python
Browser → GET /api/saves → load_saves() → checkpoints.json → Browser
```
**File to edit:** `checkpoints.json` or `load_saves()` function

#### **2. SAVE** (Writing data)
```python
Browser → POST /api/saves → write_saves() → checkpoints.json → Saved
```
**File to edit:** `write_saves()` function or checkpoints format

#### **3. GRADE** (AI evaluation)
```python
Browser → POST /api/grade → grade_with_ollama() → Ollama API → Grade result → Browser
```
**File to edit:** `grade_with_ollama()` function or Ollama prompt

---

## 🔍 Find-It-Fast Guide

### **"Where's the...?"**

| Looking for | Location | Line |
|---|---|---|
| **Questions** | QUESTIONS array | 47 |
| **Saved progress** | checkpoints.json | N/A (generated) |
| **Server config** | .env file | N/A (auto) |
| **Load function** | load_saves() | 290 |
| **Save function** | write_saves() | 301 |
| **Grade function** | grade_with_ollama() | 312 |
| **API endpoints** | do_GET / do_POST | 1768 / 1790 |
| **HTML/CSS/JS** | HTML_PAGE variable | ~363 |
| **Main entry** | if __name__ == "__main__" | 1854 |

---

## 🔧 Modify-It Guide

### **To add a new question:**
```
1. Open QUESTIONS array (line 47)
2. Add new dict: {"ch": 6, "type": "mc", "q": "...", "answer": "a", "explain": "..."}
3. Save and restart
```

### **To change the AI model:**
```
1. Edit .env file
2. Change: OLLAMA_MODEL=qwen2.5:7b (or qwen2.5:32b)
3. Run: ollama pull qwen2.5:7b
```

### **To change grading prompt:**
```
1. Find: grade_with_ollama() function (line 312)
2. Edit the: prompt = f"""...""" part
3. That's the prompt Ollama reads
```

### **To add new endpoint:**
```
1. Add condition in do_GET() or do_POST()
2. Example:
   elif path == "/api/custom":
       self.send_json({"data": ...})
3. Browser can now call /api/custom
```

### **To change the UI:**
```
1. Find HTML_PAGE variable (~line 363)
2. It's one big string containing HTML/CSS/JS
3. Edit it directly
4. Restart server to see changes
```

---

## 🐛 Debug Checklist

### **"My app won't start"**
- [ ] Python 3.8+ installed? `python --version`
- [ ] Dependencies installed? `pip install -r requirements.txt`
- [ ] Config correct? Check `.env` file
- [ ] Port 5000 free? Try: `netstat -ano | findstr :5000`
- [ ] Ollama running? Check: `ollama serve` in another terminal

### **"Questions don't load"**
- [ ] QUESTIONS array has data? (line 47)
- [ ] JSON syntax valid? Use `python check_json.py`
- [ ] Browser console errors? (F12 → Console tab)
- [ ] Call to `/api/saves` working? (Check do_GET)

### **"Progress won't save"**
- [ ] checkpoints.json exists? Check: `ls checkpoints.json`
- [ ] write_saves() called? Add: `print("Saving...")` to debug
- [ ] POST /api/saves reaching server? Check console
- [ ] File permissions? Can write to directory?

### **"AI grading broken"**
- [ ] Ollama running? Call: `ollama serve`
- [ ] Model pulled? Run: `ollama pull qwen2.5:14b`
- [ ] API reachable? Try: `curl http://localhost:11434/api/tags`
- [ ] Prompt syntax correct? Check: `grade_with_ollama()` function
- [ ] Timeout? Grade takes 30+ seconds - check logs

---

## 📊 Data Flow Diagram

```
USER OPENS APP
    ↓
[Browser] GET http://localhost:5000/
    ↓
[Server] do_GET("/") 
    ├─ Load HTML_PAGE string
    ├─ Replace __QUESTIONS__ with QUESTIONS array
    ├─ Send HTML to browser
    ↓
[Browser] Page loaded, JavaScript runs
    ├─ loadSaves() → fetch /api/saves
    ├─ checkHealth() → fetch /api/health
    ├─ Display chapters
    ↓

USER SELECTS CHAPTERS & STARTS QUIZ
    ↓
[Browser] Filter & shuffle questions
    ├─ Call: shuffleQuestions()
    ├─ Display first question
    ↓

USER ANSWERS QUESTION
    ↓
    IF Multiple Choice/True-False/Find Error:
        ├─ Check answer locally in browser
        ├─ Display result immediately
    ↓
    IF Short Answer:
        ├─ POST /api/grade
        ↓
        [Server] do_POST("/api/grade")
        ├─ Extract: question, correctAnswer, studentAnswer
        ├─ Call: grade_with_ollama(...)
        ├─ grade_with_ollama():
        │   ├─ Format prompt for Ollama
        │   ├─ POST to http://localhost:11434/api/generate
        │   ├─ Ollama returns response
        │   ├─ Parse: VERDICT, MISSING, FEEDBACK
        │   ├─ Return to browser
        ├─ Browser displays grade
    ↓

USER FINISHES QUIZ
    ↓
[Browser] saveSessions()
    ├─ POST /api/saves with session data
    ↓
[Server] do_POST("/api/saves")
    ├─ Call: write_saves(data)
    ├─ Write checkpoints.json
    ├─ Return: {"ok": true}
    ↓
[Browser] Progress saved ✓
```

---

## 🚨 Most Complex Functions Explained

### **grade_with_ollama() - THE BIG ONE**

This function is 50+ lines and might look intimidating. Here's what it does step-by-step:

```python
def grade_with_ollama(question: str, correct_answer: str, student_answer: str) -> dict:
    
    # STEP 1: Build the prompt
    prompt = f"""You are Professor Misti Clark...
    QUESTION: {question}
    EXPECTED: {correct_answer}
    STUDENT: {student_answer}
    
    Return ONLY:
    VERDICT: [CORRECT/PARTIAL/INCORRECT]
    MISSING: [what they missed]
    FEEDBACK: [help message]"""
    
    # STEP 2: Call Ollama AI
    try:
        response = requests.post(
            OLLAMA_URL,  # http://localhost:11434/api/generate
            json={
                "model": OLLAMA_MODEL,    # e.g., qwen2.5:14b
                "prompt": prompt,
                "stream": False           # Wait for full response
            },
            timeout=60  # 60 seconds max wait
        )
    except requests.exceptions.Timeout:
        return {
            "verdict": "ERROR",
            "missing": "Grading took too long",
            "feedback": "Try again or restart Ollama"
        }
    
    # STEP 3: Parse Ollama's response
    data = response.json()
    full_response = data.get("response", "")  # Ollama's answer
    
    # STEP 4: Extract the 3 lines we want
    lines = full_response.split("\n")
    result = {
        "verdict": "ERROR",
        "missing": "",
        "feedback": ""
    }
    
    for line in lines:
        if line.startswith("VERDICT:"):
            result["verdict"] = line.replace("VERDICT:", "").strip()
        elif line.startswith("MISSING:"):
            result["missing"] = line.replace("MISSING:", "").strip()
        elif line.startswith("FEEDBACK:"):
            result["feedback"] = line.replace("FEEDBACK:", "").strip()
    
    # STEP 5: Return result
    return result
```

**Key insight:** It's just string manipulation + HTTP call. Not magic!

---

## 📋 Quick API Reference

### **GET Endpoints**

```
GET /
├─ Returns: HTML page
└─ When: Browser first loads

GET /api/saves
├─ Returns: {"sessions": [...]}
└─ When: Page loads, app needs saved progress

GET /api/config
├─ Returns: {"model": "qwen2.5:14b", "port": 5000}
└─ When: App needs to show settings

GET /api/health
├─ Returns: {"ollama": true/false, "model": "..."}
└─ When: App checks if Ollama is running
```

### **POST Endpoints**

```
POST /api/saves
├─ Body: {"sessions": [...]}
├─ Returns: {"ok": true}
└─ When: User finishes quiz

POST /api/grade
├─ Body: {"question": "...", "correct_answer": "...", "student_answer": "..."}
├─ Returns: {"verdict": "CORRECT", "missing": "...", "feedback": "..."}
└─ When: User submits short answer
```

---

## ✅ Confidence Check: Do You Understand?

You should now be able to answer:

- [ ] Where are the questions stored?
- [ ] How does progress get saved?
- [ ] What happens when you click "Grade" on a short answer?
- [ ] What does the Handler class do?
- [ ] Where's the HTML/CSS/JavaScript?
- [ ] How do you add a new endpoint?
- [ ] What's Ollama and how does it work?
- [ ] Where would you go to fix a bug?

If you can answer 6+, **you've conquered the vibe coding!** 🎉

---

## 🎓 Next Steps

1. **Read** ARCHITECTURE.md (comprehensive guide)
2. **Trace** a single user action through the code
3. **Modify** something small (change a question, update config)
4. **Debug** by adding print() statements and checking logs
5. **Build** new features with confidence!

Now you're a **real developer**, not a vibe coder! 💪
