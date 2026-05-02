# Java Study App - Code Architecture Walkthrough

## 🎯 Stop Vibe Coding: Understand the Structure

Let me walk you through the codebase systematically so you know exactly where to look for things.

---

## 📊 Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│ Browser (Frontend)                                       │
│ - UI: HTML/CSS/JavaScript in HTML_PAGE variable        │
│ - Makes HTTP requests to /api/* endpoints              │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP Requests
                     ▼
┌─────────────────────────────────────────────────────────┐
│ Python HTTP Server (study_app.py)                       │
│                                                          │
│ ┌──────────────────────────────────────────────────────┐│
│ │ Handler Class (BaseHTTPRequestHandler)              ││
│ │ ├─ do_GET()  → Serves pages & read APIs             ││
│ │ └─ do_POST() → Processes data & saves              ││
│ │                                                      ││
│ │ API Endpoints:                                       ││
│ │ ├─ GET  / → Serve HTML page                         ││
│ │ ├─ GET  /api/saves → Read checkpoints.json         ││
│ │ ├─ GET  /api/config → Return settings              ││
│ │ ├─ GET  /api/health → Check Ollama status          ││
│ │ ├─ POST /api/saves → Save checkpoints              ││
│ │ └─ POST /api/grade → Grade with Ollama             ││
│ │                                                      ││
│ │ Helper Functions:                                    ││
│ │ ├─ load_saves() → Read checkpoints.json            ││
│ │ ├─ write_saves() → Write to checkpoints.json       ││
│ │ └─ grade_with_ollama() → Call Ollama AI            ││
│ └──────────────────────────────────────────────────────┘│
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        ▼                         ▼
┌───────────────────┐   ┌────────────────────┐
│ checkpoints.json  │   │ Ollama AI Server   │
│ (User Progress)   │   │ (grade_with_ollama)│
│                   │   │ Port: 11434        │
│ - Sessions        │   │ Model: qwen2.5:14b │
│ - Chapters        │   │                    │
│ - Scores          │   │ REST API:          │
│ - Answers         │   │ /api/generate      │
└───────────────────┘   └────────────────────┘

┌─────────────────────────────────────────┐
│ questions.json                          │
│ (Embedded in QUESTIONS variable)        │
│                                         │
│ Array of objects:                       │
│ - ch: chapter (6-11)                    │
│ - type: mc|tf|fte|aw|sa                 │
│ - q: question text                      │
│ - answer: correct answer                │
│ - explain: explanation                  │
└─────────────────────────────────────────┘
```

---

## 🚀 Entry Point: Where to Start

**File:** [study_app.py](study_app.py#L1)

The file is a single Python script (~1850 lines):

### 1. **Top Section (Config)** - Lines 1-45
```python
# Config from environment variables
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:14b")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
SERVER_HOST = os.getenv("SERVER_HOST", "127.0.0.1")
SERVER_PORT = int(os.getenv("SERVER_PORT", 5000))
SAVE_FILE = os.getenv("SAVE_FILE", "checkpoints.json")
```

**What it does:** Loads settings from `.env` file or uses defaults.  
**Start here if:** You want to change port, host, AI model, or file path.

### 2. **Questions Data** - Lines 47-288
```python
QUESTIONS = [
  {"ch":6, "type":"mc", "q":"...", "answer":"a", "explain":"..."},
  ...
]
```

**What it is:** All 800+ exam questions stored as JSON array.  
**Start here if:** You want to add/edit questions.

---

## 🔑 Key Functions (In Order of Execution)

### **1. `load_saves()` - Line 290** 
```python
def load_saves():
    if os.path.exists(SAVE_PATH):
        with open(SAVE_PATH, "r") as f:
            return json.load(f)
    return {"sessions": []}
```

**Purpose:** Reads user progress from `checkpoints.json`  
**Returns:** Dictionary with format:
```json
{
  "sessions": [
    {
      "chapter": 6,
      "scores": {"mc": 0.85, "tf": 0.9},
      "responses": [...],
      "timestamp": "2026-04-27..."
    }
  ]
}
```

**Where used:** Called by GET `/api/saves` endpoint

---

### **2. `write_saves(data)` - Line 301**
```python
def write_saves(data):
    with open(SAVE_PATH, "w") as f:
        json.dump(data, f, indent=2)
```

**Purpose:** Saves user progress to `checkpoints.json`  
**When called:** Every time a study session ends

---

### **3. `grade_with_ollama()` - Line 312** ⭐ **Most Complex**
```python
def grade_with_ollama(question: str, correct_answer: str, student_answer: str) -> dict:
    # Creates a detailed prompt asking Ollama (AI) to grade
    prompt = """You are Professor Misti Clark...
    
QUESTION: {question}
EXPECTED: {correct_answer}  
STUDENT: {student_answer}

Return ONLY these 3 lines:
VERDICT: [CORRECT/PARTIAL/INCORRECT]
MISSING: [what they missed]
FEEDBACK: [2-3 sentences to help them]"""
    
    # Calls Ollama API
    response = requests.post(OLLAMA_URL, json={
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }, timeout=60)
    
    # Parses response and extracts grading info
    ...
```

**Purpose:** Uses AI (Ollama) to intelligently grade Short Answer questions  
**Input:** Question text, expected answer, student's answer  
**Output:** Verdict (CORRECT/PARTIAL/INCORRECT), what's missing, feedback  
**Where used:** POST `/api/grade` endpoint  
**Key point:** This is where the "magic" happens — AI evaluates essay answers

---

## 🌐 HTTP Server: The Handler Class

**File:** [study_app.py](study_app.py#L1737)

### **Handler Class - Line 1737**

This is your HTTP request handler. It's like a "router" that decides what to do based on the request.

```python
class Handler(BaseHTTPRequestHandler):
```

#### **Helper Methods:**

```python
def send_json(self, data, status=200):
    # Sends JSON response to browser
    
def send_html(self, html: str):
    # Sends HTML page to browser
    
def read_body(self):
    # Reads JSON data from POST request
```

#### **GET Endpoints - Line 1768**

```python
def do_GET(self):
    path = urlparse(self.path).path
    
    if path == "/" or path == "/index.html":
        # Serve the main HTML page
        # Embed questions into HTML: __QUESTIONS__ → json.dumps(QUESTIONS)
        
    elif path == "/api/saves":
        # Return saved progress (checkpoints.json)
        
    elif path == "/api/config":
        # Return config (model name, port)
        
    elif path == "/api/health":
        # Check if Ollama is running
```

**How it works:** Browser asks for data → Handler loads it → Sends back as JSON

#### **POST Endpoints - Line 1790**

```python
def do_POST(self):
    path = urlparse(self.path).path
    
    if path == "/api/saves":
        # Save user progress to checkpoints.json
        data = self.read_body()  # Get JSON from request
        write_saves(data)        # Write to file
        
    elif path == "/api/grade":
        # Grade a short answer using Ollama
        data = self.read_body()
        result = grade_with_ollama(
            data["question"],
            data["correct_answer"], 
            data["student_answer"]
        )
        # Send back: VERDICT, MISSING, FEEDBACK
```

---

## 🎨 Frontend: The HTML/JavaScript

**Location:** [study_app.py](study_app.py) - The `HTML_PAGE` variable (approximately line 363)

### **Key JavaScript Functions:**

```javascript
// Load previously saved progress
loadSaves()  

// Check if Ollama is running
checkHealth()

// Get list of chapters available
renderStudyUnitList()

// Shuffle questions
shuffleQuestions()

// Grade a short answer via AI
gradeQuestion(question, correctAnswer, studentAnswer)

// Save progress to server
saveSessions()
```

**The flow in browser:**

1. Page loads → JavaScript runs
2. `loadSaves()` fetches checkpoints.json
3. User selects chapters and question types
4. Questions are shuffled if needed
5. User answers questions
6. For short answers: `gradeQuestion()` calls `/api/grade`
7. When done: `saveSessions()` calls `/api/saves`

---

## 📁 Data Files

### **questions.json** (or QUESTIONS array in study_app.py)
```json
[
  {
    "ch": 6,
    "type": "mc",
    "q": "This is a collection of...",
    "answer": "a",
    "explain": "A class is the blueprint..."
  },
  ...
]
```

**Question Types:**
- `mc` = Multiple Choice (pick a/b/c/d)
- `tf` = True/False
- `fte` = Find the Error (code debugging)
- `aw` = Algorithm Workbench (write code)
- `sa` = Short Answer (essay - AI grades)

### **checkpoints.json** (User Progress)
```json
{
  "sessions": [
    {
      "chapter": 6,
      "selectedTypes": ["mc", "tf", "fte"],
      "scores": {
        "mc": {"total": 10, "correct": 8},
        "tf": {"total": 5, "correct": 5}
      },
      "responses": [
        {
          "index": 0,
          "question": "...",
          "userAnswer": "a",
          "correct": true,
          "verdict": "CORRECT"
        }
      ],
      "timestamp": "2026-04-27T14:23:45"
    }
  ]
}
```

---

## 🔄 Complete User Journey: What Happens When?

### **Step 1: Page Loads**
```
Browser opens http://localhost:5000
  ↓
do_GET("/") called
  ↓
HTML_PAGE returned with __QUESTIONS__ replaced
  ↓
JavaScript runs: loadSaves(), checkHealth()
  ↓
Page displays chapters & question types
```

### **Step 2: User Starts Study Session**
```
User clicks "Start"
  ↓
Browser filters questions by chapter & type
  ↓
Questions shuffled if enabled
  ↓
First question displayed
```

### **Step 3: User Answers Questions**
```
User selects answer (MC) or types answer (Short Answer)
  ↓
Click Next
  ↓
For Short Answers:
  - Browser calls POST /api/grade
  - do_POST("/api/grade") called
  - grade_with_ollama() invokes Ollama API
  - Ollama returns: VERDICT, MISSING, FEEDBACK
  - Browser shows grading result
```

### **Step 4: Session Ends**
```
User finishes all questions
  ↓
Results displayed (score, review)
  ↓
Browser calls POST /api/saves
  ↓
do_POST("/api/saves") called
  ↓
write_saves() writes to checkpoints.json
  ↓
Progress saved ✓
```

---

## 🎯 Where to Look for Specific Tasks

### **I want to ADD a new question:**
👉 Edit `questions.json` (or QUESTIONS array in study_app.py)  
Structure: `{"ch": 6, "type": "mc", "q": "?", "answer": "a", "explain": "..."}`

### **I want to CHANGE how grading works:**
👉 Modify `grade_with_ollama()` function (line 312)  
Current: Uses Ollama AI  
Could change: Prompt, verdict format, model

### **I want to ADD a new API endpoint:**
👉 Add condition in `do_GET()` or `do_POST()` (lines 1768, 1790)  
Example: `elif path == "/api/newfeature": ...`

### **I want to CHANGE the UI:**
👉 Edit `HTML_PAGE` variable (around line 363)  
Contains: HTML/CSS/JavaScript all in one string

### **I want to CHANGE config:**
👉 Use `.env` file (already done!)  
Or edit defaults at top of study_app.py (lines 23-31)

### **I want to FIX checkpoint saving:**
👉 Look at `load_saves()` and `write_saves()` (lines 290-310)

### **I want to CHECK if Ollama is working:**
👉 See `/api/health` endpoint in `do_GET()` (line 1778)

---

## 🚨 Common Issues & Where to Debug

| Problem | Where to Look |
|---------|---|
| Questions not loading | QUESTIONS array (line 47) or `/api/saves` endpoint |
| Progress not saving | `write_saves()` function or POST endpoint |
| AI grading not working | `grade_with_ollama()` function or `/api/grade` endpoint |
| Page won't load | `do_GET("/")` or HTML_PAGE variable |
| Port already in use | `main()` function or SERVER_PORT config |
| Ollama not connecting | `grade_with_ollama()` or `/api/health` endpoint |

---

## ✅ Quick Reference: Key Line Numbers

```
Config:           Lines 23-31
Questions data:   Lines 47-288
load_saves():     Line 290
write_saves():    Line 301
grade_with_ollama():  Line 312 ← Complex!
HTML_PAGE:        ~Line 363
Handler class:    Line 1737
do_GET():         Line 1768
do_POST():        Line 1790
main():           Line 1809
Entry point:      Line 1854 (if __name__ == "__main__")
```

---

## 🎓 Study Path: How to Learn This Code

1. **Start:** Read the config section (top 50 lines)
2. **Then:** Understand the QUESTIONS data structure
3. **Then:** Read `load_saves()` and `write_saves()` 
4. **Then:** Read the Handler class methods (do_GET, do_POST)
5. **Complex:** Read `grade_with_ollama()` - understand Ollama integration
6. **Finally:** Look at HTML_PAGE to see how UI connects

---

## 🤔 Key Concepts to Understand

**HTTP Server:** Python's built-in HTTP server handles requests  
**Stateless:** Each request is independent (no session state)  
**JSON:** All data transfer is JSON format  
**REST API:** Browser → `/api/*` endpoints → Server responds with JSON  
**Ollama:** External LLM service used for AI grading  
**Checkpoints:** User progress saved as JSON file on disk

---

**Now you're no longer vibe coding!** 🎉 You know exactly where each piece is and how they connect.
