# 🎓 TutorRAG — AI Teaching Assistant with Login & Personalisation

<div align="center">

![Architecture Diagram](diagram.png)

### 🌐 Live Deployment

| Service | URL |
|---|---|
| 🚀 **Backend API** | [teaching-assistant-full-deploy-login.onrender.com](https://teaching-assistant-full-deploy-login.onrender.com) |
| 🖥️ **Frontend App** | [Open on Streamlit Cloud ↗](https://teaching-assistant-full-deploy-app-personalisation-jn5txzjeibj.streamlit.app/) |

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-47A248?logo=mongodb&logoColor=white)
![Pinecone](https://img.shields.io/badge/Pinecone-000000?logo=pinecone&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-F55036?logoColor=white)
![Render](https://img.shields.io/badge/Render-46E3B7?logo=render&logoColor=black)

</div>

---

## 🧠 What Is This?

**TutorRAG** is a fully deployed, **role-based AI teaching assistant** that brings personalised learning to every student. Teachers upload curriculum PDFs — the system indexes them per grade. Students log in, ask questions in plain English, and get AI answers grounded in their exact grade-level material. They can also generate custom quizzes on any topic, submit their answers, get instant scores, and review their full quiz history.

Every feature is personalised: a Grade 5 student only ever sees Grade 5 content. A Grade 10 student never gets results from a Grade 3 document. It's RAG — but with identity, role, and grade baked into every retrieval.

---

## ✨ Feature Highlights

| | Feature | Who |
|---|---|---|
| 🔐 | **Secure Signup & Login** | Students + Teachers |
| 🔒 | **bcrypt Password Hashing** | System |
| 🎭 | **Role-Based Access** | Students ask · Teachers upload |
| 📚 | **Grade-Aware PDF Ingestion** | Teachers |
| 💬 | **AI Chat — RAG from their own grade docs** | Students |
| 📝 | **Auto-Generated MCQ Quizzes** | Students |
| ✅ | **Instant Quiz Scoring with Feedback** | Students |
| 📜 | **Full Quiz History with Review** | Students |
| 🏫 | **Multi-School Support** | Both |
| 🌐 | **Fully Deployed** (Render + Streamlit Cloud) | Everyone |

---


## 🏗️ System Architecture

```mermaid
flowchart TD
    S(["👤 User"])

    SIGN["📝 Sign Up"]
    LOG["🔑 Login"]
    TEACH(["🧑‍🏫 Teacher"])
    STUD(["🧑‍🎓 Student"])

    PDF["📄 Upload PDF"]
    CHUNK["✂️ Chunk"]
    EMBED["🔢 Embed"]
    STORE["🗄️ MongoDB + Pinecone"]

    ASK["❓ Ask Question"]
    VEC1["🌲 Grade-Filtered Search"]
    ANS["🤖 Generate Answer"]

    TOPIC["📌 Choose Topic"]
    VEC2["🌲 Grade-Filtered Search"]
    MCQ["🤖 Generate Quiz"]
    SCORE["✅ Score + Feedback"]

    S --> SIGN & LOG
    LOG --> TEACH & STUD
    TEACH --> PDF --> CHUNK --> EMBED --> STORE

    STUD --> ASK --> VEC1 --> ANS
    STUD --> TOPIC --> VEC2 --> MCQ --> SCORE

    classDef user    fill:#7c3aed,stroke:#5b21b6,color:#ffffff
    classDef auth    fill:#f59e0b,stroke:#d97706,color:#ffffff
    classDef role    fill:#475569,stroke:#334155,color:#ffffff
    classDef ingest  fill:#10b981,stroke:#059669,color:#ffffff
    classDef chat    fill:#3b82f6,stroke:#2563eb,color:#ffffff
    classDef quiz    fill:#a855f7,stroke:#9333ea,color:#ffffff

    class S user
    class SIGN,LOG auth
    class TEACH,STUD role
    class PDF,CHUNK,EMBED,STORE ingest
    class ASK,VEC1,ANS chat
    class TOPIC,VEC2,MCQ,SCORE quiz
```

---

## 🗂️ Project Structure

```
Teaching-Assistant-Full-Deploy-Login-Personalisation/
│
├── client/                             # 🖥️ Streamlit Frontend
│   ├── main.py                         # All pages: landing, login, signup, dashboards
│   ├── requirements.txt                # streamlit, requests, python-dotenv
│   └── assets/                         # UI images (landing, login, signup, dashboards)
│
├── server/                             # 🚀 FastAPI Backend
│   ├── main.py                         # App entry: registers all 3 routers
│   │
│   ├── config/
│   │   └── db.py                       # MongoDB client + 5 collections
│   │
│   ├── auth/
│   │   ├── model.py                    # Pydantic: StudentUser, TeacherUser
│   │   ├── hash_utils.py               # bcrypt hash + verify
│   │   └── route.py                    # POST /signup/student · /signup/teacher · GET /login
│   │
│   ├── docs/
│   │   ├── vectorstore.py              # PDF ingest: load → split → embed → dual-store
│   │   └── route.py                    # POST /upload_docs/ (Teacher only)
│   │
│   ├── chat/
│   │   ├── chat_query.py               # answer_query() + quiz_query() with grade filter
│   │   └── route.py                    # POST /chat · /quiz · /quiz/check · GET /quiz/history
│   │
│   ├── requirements.txt                # All server dependencies
│   └── upload_docs/                    # Temporary PDF storage
│
├── main.py                             # Root entry point
├── pyproject.toml                      # Project metadata
└── requirements.txt                    # Root lockfile
```

---

## 👥 User Roles

### 🧑‍🏫 Teacher
- Signs up with: `fullname`, `email`, `username`, `password`, `school`
- Can upload PDFs with a **grade tag** (1–12)
- Documents are chunked, embedded, and stored — accessible only to students of that grade

### 🧑‍🎓 Student
- Signs up with: `fullname`, `email`, `username`, `password`, `grade`, `school`
- Can chat with the AI — answers come only from their grade's documents
- Can generate MCQ quizzes on any topic from their grade content
- Can review all past quiz attempts with full per-question breakdowns

---

## 🔐 Authentication

This project uses **HTTP Basic Auth** — credentials are sent with every API request and validated against MongoDB on the server using `bcrypt`:

```python
# Signup — passwords are hashed before storage
hashed_password = bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt())

# Login / every protected route — credentials verified per request
bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
```

The `authenticate` dependency is injected on every protected route:
```python
@router.post("/chat")
async def chat(user=Depends(authenticate), query: str = Body(...)):
    if user['role'] != "Student":
        raise HTTPException(status_code=403, detail="Only students can ask questions")
```

---

## 📊 MongoDB Collections

| Collection | Stores |
|---|---|
| `users` | All user accounts (students + teachers) with hashed passwords |
| `text` | Every text chunk from every uploaded PDF with `grade`, `source`, `role` |
| `chat_history` | Every chat exchange: `user_id`, `query`, `response`, `sources`, `timestamp` |
| `quizzes` | Generated quiz content: `user_id`, `topic`, `quiz_data`, `sources` |
| `history` | Quiz attempt results: `score`, `total`, `per-question breakdown`, `timestamp` |

---

## 🔍 Grade-Aware Retrieval

The core personalisation feature. Every Pinecone query includes a metadata filter so a Grade 5 student can never see a Grade 10 document, even if the semantic content matches:

```python
results = await asyncio.to_thread(
    index.query,
    vector=embedding,
    top_k=5,
    include_metadata=True,
    filter={
        "grade": user_grade,          # exact grade match
        "role": {"$in": ["Public", user_role]}  # public OR role-specific
    }
)
```

After Pinecone returns the top-5 chunk IDs, the full text is fetched from MongoDB (Pinecone only stores metadata, MongoDB stores the actual content):

```python
chunk_ids = [m['id'] for m in results['matches']]
docs = list(chunk_collection.find({"chunk_id": {"$in": chunk_ids}}))
context = "\n\n".join(d['text'] for d in ordered_docs)
```

---

## 📝 Quiz System

Students generate quizzes, submit answers, and get instant detailed feedback — all stored for later review.

**Generate:**
```python
POST /quiz
{ "topic": "Photosynthesis", "num_questions": 5 }
```

**LLM prompt format (strictly enforced):**
```
Question 1: What is the primary product of photosynthesis?
A) Oxygen
B) Glucose
C) Carbon dioxide
Correct Answer: B
```

**Submit answers:**
```python
POST /quiz/check
{ "quiz_id": "...", "answers": ["B", "A", "C", "B", "A"] }
```

**Result:**
```json
{
  "message": "Quiz Completed, You scored: 4/5",
  "score": 4,
  "total": 5,
  "results": [
    { "question_number": 1, "user_answer": "B", "correct_answer": "B", "is_correct": true },
    ...
  ]
}
```

---

## 🌐 API Reference

Base URL: **`https://teaching-assistant-full-deploy-login.onrender.com`**

### Auth

| Method | Endpoint | Body | Description |
|---|---|---|---|
| `POST` | `/signup/student` | `StudentUser` JSON | Register a new student |
| `POST` | `/signup/teacher` | `TeacherUser` JSON | Register a new teacher |
| `GET` | `/login` | HTTP Basic Auth | Authenticate + return role/grade |

### Documents (Teacher only)

| Method | Endpoint | Body | Description |
|---|---|---|---|
| `POST` | `/upload_docs/` | `file` (PDF) + `grade` (int) | Chunk, embed, and dual-store a PDF |

### Chat & Quiz (Student only)

| Method | Endpoint | Body | Description |
|---|---|---|---|
| `POST` | `/chat` | `{ "query": "..." }` | RAG answer from grade docs |
| `POST` | `/quiz` | `{ "topic": "...", "num_questions": 5 }` | Generate MCQ quiz |
| `POST` | `/quiz/check` | `{ "quiz_id": "...", "answers": [...] }` | Score a quiz submission |
| `GET` | `/quiz/history` | — | All past quiz attempts |

---

## 📦 Installation & Local Setup

### Prerequisites

- Python 3.12+
- [MongoDB Atlas](https://www.mongodb.com/atlas) (free tier)
- [Pinecone](https://pinecone.io) account (free tier)
- [Groq](https://console.groq.com) API key (free tier)
- [OpenAI](https://platform.openai.com) API key (for embeddings)

### 1. Clone

```bash
git clone https://github.com/paras160500/Teaching-Assistant-Full-Deploy-Login-Personalisation.git
cd Teaching-Assistant-Full-Deploy-Login-Personalisation
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure the backend

Create a `.env` file inside `server/`:

```env
# MongoDB
MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/
DB_NAME=tutorrag

# Pinecone
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX_NAME=tutorrag

# OpenAI (embeddings only)
OPEN_AI_API=your_openai_api_key

# Groq (LLM generation)
GROQ_API_KEY=your_groq_api_key
```

### 4. Configure the frontend

Create a `.env` file inside `client/`:

```env
# Point to local or live backend
BACKEND_URL=http://localhost:8000
# or for production:
# BACKEND_URL=https://teaching-assistant-full-deploy-login.onrender.com
```

---

## ▶️ Running Locally

```bash
# Terminal 1 — FastAPI backend
cd server
uvicorn main:app --reload --port 8000

# Terminal 2 — Streamlit frontend
cd client
streamlit run main.py
```

Open [http://localhost:8501](http://localhost:8501).

---

## ☁️ Deploying to Render + Streamlit Cloud

### Backend → Render

| Setting | Value |
|---|---|
| **Root Directory** | `server` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn main:app --host 0.0.0.0 --port $PORT` |

Add all `.env` keys in the Render **Environment Variables** dashboard.

### Frontend → Streamlit Cloud

| Setting | Value |
|---|---|
| **Repository** | `paras160500/Teaching-Assistant-Full-Deploy-Login-Personalisation` |
| **Branch** | `main` |
| **Main file path** | `client/main.py` |

Add `BACKEND_URL=https://teaching-assistant-full-deploy-login.onrender.com` in the Streamlit **Secrets** panel.

---

## ⚡ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Streamlit (multi-page via session state) |
| **Backend** | FastAPI + Uvicorn |
| **Authentication** | HTTP Basic Auth + bcrypt |
| **Database** | MongoDB Atlas (users, chunks, chats, quizzes, history) |
| **Vector Store** | Pinecone Serverless (1536-dim, dotproduct, grade-filtered) |
| **Embeddings** | OpenAI `text-embedding-3-small` |
| **LLM** | Groq `llama-3.3-70b-versatile` · `temp=0.3` |
| **PDF Parsing** | LangChain `PyPDFLoader` |
| **Chunking** | `RecursiveCharacterTextSplitter` — 500 tokens · 50 overlap |
| **Deployment** | Render (backend) + Streamlit Cloud (frontend) |
| **Language** | Python 3.12+ |

---

## 🔮 Future Improvements

- [ ] JWT token authentication to replace HTTP Basic Auth (tokens expire, are revocable, and don't expose credentials on every request)
- [ ] Teacher dashboard to view upload history and delete documents by grade
- [ ] Chat history page for students to browse past Q&A sessions
- [ ] Leaderboard — top quiz scores by grade or school
- [ ] Support for DOCX and PowerPoint ingestion alongside PDF
- [ ] Streaming LLM responses so answers appear token-by-token in the chat

---

## ⚠️ Note on HTTP Basic Auth

This project uses **HTTP Basic Auth** for simplicity and learning purposes. In a production system handling real student data, you would replace this with **JWT tokens** (stateless, expirable, non-credential-exposing) and add HTTPS enforcement at the infrastructure level.

---

## 👨‍💻 Author

Built and deployed by **[paras160500](https://github.com/paras160500)**

AI Teaching Assistant · FastAPI · Streamlit · MongoDB · Pinecone · Groq · Render