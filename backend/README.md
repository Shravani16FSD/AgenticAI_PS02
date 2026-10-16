# Chapter AI Career Coach — Backend API

FastAPI backend providing persistent database storage, input validation with Pydantic v2, and streaming AI mentoring endpoints for Chapter.

---

## Architecture Overview

- **Framework**: FastAPI (Asynchronous Python REST API)
- **Database ORM**: SQLAlchemy 2.0
- **Database Engine**:
  - **Local Development**: SQLite (`backend/career_coach.db`) with zero setup overhead.
  - **Production Deployment**: PostgreSQL (configurable via `DATABASE_URL` environment variable).
- **Interactive Documentation**: Swagger UI at `http://localhost:8000/docs`.

---

## Folder Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application, CORS middleware, lifespan events
│   ├── config.py        # Pydantic BaseSettings environment loader
│   ├── database.py      # SQLAlchemy engine, session maker, get_db dependency
│   ├── models.py        # Database tables (UserProfile, CareerPath, RoadmapTask, etc.)
│   ├── schemas.py       # Pydantic v2 request/response validation schemas
│   ├── seed.py          # Pre-seeding catalog of career tracks & starter roadmap
│   └── routers/
│       ├── profile.py   # GET /api/profile, PUT /api/profile
│       ├── careers.py   # GET /api/careers, POST/DELETE /api/careers/{id}/save
│       ├── roadmap.py   # GET /api/roadmap, POST /tasks, PATCH /tasks/{id}, DELETE
│       ├── skills.py    # GET /api/skills, POST /api/skills, POST /{id}/log
│       └── chat.py      # GET /history, POST /api/chat (streaming SSE), DELETE
├── run.py               # Local server runner
├── requirements.txt     # Python dependencies
├── .env.example         # Environment template
└── README.md
```

---

## Local Development Setup

### 1. Create and Activate Virtual Environment
```bash
# In the backend directory:
cd backend

# Create virtual environment
python -m venv venv

# Activate on Windows:
venv\Scripts\activate

# Or on macOS/Linux:
# source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
```bash
cp .env.example .env
```

### 4. Run the Backend Server
```bash
python run.py
```
*The server will start at `http://localhost:8000`. Database tables will be automatically created and seeded on initial startup.*

### 5. Verify & Test Endpoints
- **Health Check**: `http://localhost:8000/api/health`
- **Interactive API Docs**: `http://localhost:8000/docs`

---

## Production Deployment

### Environment Variables
Set the following on your cloud hosting platform (Render, Railway, Fly.io, AWS):

| Variable | Description | Example |
|---|---|---|
| `DATABASE_URL` | Production PostgreSQL connection string | `postgresql://user:pass@host:5432/career_coach` |
| `ENVIRONMENT` | Deployment mode | `production` |
| `PORT` | Web port | `8000` |
| `CORS_ORIGINS` | Production frontend domain(s) | `https://your-domain.vercel.app` |
| `GEMINI_API_KEY` | (Optional) Google Gemini key | `AIzaSy...` |

### Production Run Command
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```
