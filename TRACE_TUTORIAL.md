# Java Study App - Trace-Through Tutorial

## 🎯 Learn by Tracing: Follow a User Action Line-by-Line

This guide walks you through **exactly** what happens at each step when a user interacts with the app.

---

## Scenario: User Answers a Short Answer Question

### **Step-by-Step: What Code Runs When?**

---

## **PART 1: Page Loads (User opens http://localhost:5000)**

### **Browser Side:**
```javascript
// Browser opens: http://localhost:5000
```

### **Server Side:**
```python
# [1] Browser sends: GET /
# [2] Handler.do_GET() called (line 1768)

def do_GET(self):
    path = urlparse(self.path).path
    # path = "/"
    
    if path == "/" or path == "/index.html":  # TRUE ✓
        page = HTML_PAGE.replace(
            "__QUESTIONS__",
            json.dumps(QUESTIONS, ensure_ascii=False)
        )
        # [3] Takes the HTML_PAGE variable (~line 363)
        # [4] Finds placeholder: __QUESTIONS__
        # [5] Replaces with JSON dump of all 800+ questions
        # [6] Example result: { "ch": 6, "type": "sa", "q": "...", ... }
        
        self.send_html(page)
        # [7] Sends HTML to browser
```

### **Browser Side (Page Now Loaded):**
```javascript
// JavaScript in HTML_PAGE starts running

// First: Load previous progress
loadSaves()  // Line ~1600 in HTML_PAGE

async function loadSaves() {
    const response = await fetch("/api/saves");  
    // [8] Browser: GET /api/saves
    const data = await response.json();
    saves = data;  // Example: {sessions: [{chapter: 6, scores: {...}}]}
    renderStudyUnitList();  // Display chapters
}
```

### **Server Side (Handle /api/saves):**
```python
# [9] Browser GET /api/saves
# [10] Handler.do_GET() called again

elif path == "/api/saves":  # Line 1776
    self.send_json(load_saves())
    # [11] Calls load_saves() (line 290)

def load_saves():
    if os.path.exists(SAVE_PATH):  # SAVE_PATH = "checkpoints.json"
        with open(SAVE_PATH, "r") as f:
            data = json.load(f)
            # Reads: {"sessions": [...]}
            return data
    return {"sessions": []}
    # [12] Returns empty if no previous sessions
```

### **Browser Side (Progress Loaded):**
```javascript
// [13] Browser received: {"sessions": [...]}
// [14] Page displays chapters (6, 7, 8, etc.)
// User clicks "Start with Chapter 6"
```

---

## **PART 2: User Starts Quiz**

### **Browser Side:**
```javascript
// [15] User selects:
// - Chapter: 6
// - Question types: MC, TF, SA
// - Shuffle: enabled

// [16] JavaScript filters questions:
let selectedQuestions = QUESTIONS.filter(
    q => q.ch == 6 && ["mc", "tf", "sa"].includes(q.type)
);
// Result: ~100 Chapter 6 questions

// [17] Shuffle them:
selectedQuestions = shuffleQuestions(selectedQuestions);

// [18] Display first question
displayQuestion(selectedQuestions[0]);
```

---

## **PART 3: User Types Short Answer**

### **Browser Side:**
```javascript
// [19] User sees question:
// "What is an accessor method?"
//
// User types answer:
// "A method that returns a field value without changing it"
//
// User clicks "Submit"

// [20] JavaScript detects it's Short Answer (type: "sa")
// Calls:
gradeQuestion(question, correctAnswer, studentAnswer);
```

---

## **PART 4: THE KEY MOMENT - Grading Happens** ⭐

### **Browser Side:**
```javascript
// [21] JavaScript makes HTTP request:
async function gradeQuestion(q, correct, student) {
    const response = await fetch("/api/grade", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            question: q,
            correct_answer: correct,
            student_answer: student
        })
    });
    // [22] Browser: POST /api/grade
    // Body: 
    // {
    //   "question": "What is an accessor method?",
    //   "correct_answer": "A method that returns a field value...",
    //   "student_answer": "A method that returns a field value without changing it"
    // }
    
    const grade = await response.json();
    // [23] Waits for server to respond
}
```

### **Server Side - THE AI GRADING** 🤖

```python
# [24] Server receives: POST /api/grade
# [25] Handler.do_POST() called (line 1790)

def do_POST(self):
    path = urlparse(self.path).path
    
    if path == "/api/grade":  # TRUE ✓
        data = self.read_body()  # [26] Parse JSON from browser
        # data = {
        #   "question": "What is an accessor method?",
        #   "correct_answer": "A method that returns a field value...",
        #   "student_answer": "A method that returns a field value without changing it"
        # }
        
        result = grade_with_ollama(  # [27] Call grading function
            data.get("question", ""),
            data.get("correct_answer", ""),
            data.get("student_answer", "")
        )
        # result = {"verdict": "CORRECT", "missing": "", "feedback": "..."}
        
        self.send_json(result)  # [28] Send back to browser
```

### **Inside grade_with_ollama() - THE MAGIC**

```python
# [29] Function called:
def grade_with_ollama(question, correct_answer, student_answer):
    
    # [30] Build the prompt for AI:
    prompt = f"""You are Professor Misti Clark, a strict Java professor...
    
QUESTION: {question}
EXPECTED ANSWER: {correct_answer}
STUDENT ANSWER: {student_answer}

Grading rules:
- CORRECT: student covered all or nearly all key concepts
- PARTIAL: student got some concepts but missed important parts
- INCORRECT: student missed most concepts

Return ONLY these 3 lines, nothing else:
VERDICT: [CORRECT/PARTIAL/INCORRECT]
MISSING: [what the student missed]
FEEDBACK: [2-3 plain sentences helping them]"""
    
    # [31] Make HTTP request to Ollama (the local AI):
    response = requests.post(
        OLLAMA_URL,  # http://localhost:11434/api/generate
        json={
            "model": OLLAMA_MODEL,  # e.g., "qwen2.5:14b"
            "prompt": prompt,
            "stream": False
        },
        timeout=60  # Wait up to 60 seconds
    )
    
    # [32] Ollama processes the prompt...
    # Takes ~5-30 seconds depending on model & hardware
    
    # [33] Ollama AI thinks through:
    # "Student said: 'A method that returns a field value without changing it'"
    # "Expected: 'Accessors (getters) return field values without modifying them'"
    # "Decision: These are saying the same thing → CORRECT"
    
    # [34] Ollama returns:
    data = response.json()
    full_response = data.get("response", "")
    # Example response:
    # """VERDICT: CORRECT
    # MISSING: Could mention that accessors are also called 'getters'
    # FEEDBACK: Your answer is correct! Accessors indeed return values without modification. Consider that 'getter' is the informal term for accessor."""
    
    # [35] Parse the response:
    lines = full_response.split("\n")
    result = {
        "verdict": "",
        "missing": "",
        "feedback": ""
    }
    
    for line in lines:
        if line.startswith("VERDICT:"):
            result["verdict"] = line.replace("VERDICT:", "").strip()
            # result["verdict"] = "CORRECT"
        elif line.startswith("MISSING:"):
            result["missing"] = line.replace("MISSING:", "").strip()
        elif line.startswith("FEEDBACK:"):
            result["feedback"] = line.replace("FEEDBACK:", "").strip()
    
    # [36] Return the graded result:
    return result
    # Returns:
    # {
    #   "verdict": "CORRECT",
    #   "missing": "Could mention that accessors are also called 'getters'",
    #   "feedback": "Your answer is correct!..."
    # }
```

### **Back to Server (Send Result):**
```python
# [37] Back in do_POST():
self.send_json(result)
# Sends to browser:
# {
#   "verdict": "CORRECT",
#   "missing": "Could mention...",
#   "feedback": "Your answer is correct!..."
# }
```

### **Browser Side (Show Grade):**
```javascript
// [38] JavaScript receives the grade:
const grade = {
    "verdict": "CORRECT",
    "missing": "Could mention...",
    "feedback": "Your answer is correct!..."
}

// [39] Display the result to user:
displayGradeResult(grade);
// Shows:
// ✓ CORRECT!
// Feedback: "Your answer is correct!..."
// Could improve: "Could mention that accessors are also called 'getters'"

// [40] Move to next question
displayQuestion(selectedQuestions[1]);
```

---

## **PART 5: Quiz Ends**

### **Browser Side:**
```javascript
// [41] User finishes all questions
// System calculates score:
// - Correct: 8/10
// - Partial: 1/10
// - Incorrect: 1/10

// [42] User clicks "Save Progress"
// JavaScript calls:
saveSessions();
```

```javascript
// [43] Function implementation:
function saveSessions() {
    fetch("/api/saves", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            sessions: [{
                chapter: 6,
                selectedTypes: ["mc", "tf", "sa"],
                scores: {
                    mc: {total: 3, correct: 2},
                    tf: {total: 3, correct: 3},
                    sa: {total: 4, correct: 3}
                },
                responses: [
                    {
                        index: 0,
                        question: "What is an accessor method?",
                        userAnswer: "A method that returns a field value without changing it",
                        correct: true,
                        verdict: "CORRECT"
                    },
                    // ... more responses ...
                ],
                timestamp: "2026-04-27T14:23:45"
            }]
        })
    });
    // [44] Browser: POST /api/saves
}
```

### **Server Side (Save Progress):**
```python
# [45] Server receives: POST /api/saves
# [46] Handler.do_POST() called

elif path == "/api/saves":  # TRUE ✓
    data = self.read_body()  # [47] Parse JSON
    # data = {"sessions": [{...large object...}]}
    
    write_saves(data)  # [48] Call save function

def write_saves(data):
    # [49] Ensure format is correct:
    if not isinstance(data, dict):
        data = {"sessions": []}
    
    # [50] Write to checkpoints.json:
    with open(SAVE_PATH, "w") as f:
        json.dump(data, f, indent=2)
    
    # [51] File now contains:
    # {
    #   "sessions": [{
    #     "chapter": 6,
    #     "selectedTypes": ["mc", "tf", "sa"],
    #     "scores": {...},
    #     "responses": [...],
    #     "timestamp": "2026-04-27T14:23:45"
    #   }]
    # }
```

### **Back to Server (Acknowledge):**
```python
# [52] Back in do_POST():
self.send_json({"ok": True})
# Browser receives: {"ok": true}
```

### **Browser Side (Finalize):**
```javascript
// [53] JavaScript sees: {"ok": true}
alert("Progress saved! ✓");
// [54] Quiz ends
```

---

## 📊 Summary: The Complete Journey

```
[LOAD]
Browser GET / 
  → Server returns HTML with embedded questions
  → JavaScript loads, calls GET /api/saves
  → Server returns checkpoints.json
  → Page displays chapters
    
[START]
User selects chapter & types, clicks Start
  → Questions filtered & shuffled in browser

[ANSWER - SHORT ANSWER]
User types answer, clicks Submit
  → Browser POST /api/grade {question, correct_answer, student_answer}
  → Server calls grade_with_ollama()
  → grade_with_ollama() calls Ollama AI
  → Ollama returns: VERDICT, MISSING, FEEDBACK (30 seconds)
  → Server returns grade to browser
  → Browser shows result ✓

[FINISH]
User finishes quiz
  → Browser POST /api/saves {sessions: [{...}]}
  → Server writes to checkpoints.json
  → Progress saved ✓
```

---

## 🎯 Key Takeaways

| Component | Role | Location |
|-----------|------|----------|
| **Browser** | Displays UI, handles user input, makes API calls | HTML_PAGE (~line 363) |
| **Server (do_GET)** | Serves pages and data, checks Ollama health | Line 1768 |
| **Server (do_POST)** | Saves data, grades with AI | Line 1790 |
| **grade_with_ollama()** | Formats prompt, calls Ollama, parses response | Line 312 |
| **Ollama AI** | Actually grades the answers (external service) | http://localhost:11434 |
| **checkpoints.json** | Persists user progress to disk | Generated file |

---

## 🔍 Now You Can Debug!

If something breaks, you know EXACTLY where to look:

- **Page won't load?** → Check `do_GET("/")` (line 1768) & HTML_PAGE
- **Progress not saving?** → Check `write_saves()` (line 301) & checkpoints.json
- **Grade button does nothing?** → Check browser console (F12) & `/api/grade` POST
- **AI takes forever?** → Check `grade_with_ollama()` & Ollama running
- **Wrong grade given?** → Check the prompt in `grade_with_ollama()`

You're no longer blindly guessing. **You understand the flow!** 🎉

---

## 🎓 Practice Exercise

Try to trace through this scenario yourself:

**Scenario:** User opens app, selects Chapter 7 + Multiple Choice only, answers first question with "a", goes to next question.

Can you map out:
1. What code runs on the browser?
2. What code runs on the server?
3. In what order?
4. What HTTP requests happen?

(Hint: Multiple Choice answers are graded in the browser, not by Ollama!)

---

**Congratulations!** You've gone from "vibe coding" to **understanding the actual data flow!** 💪
