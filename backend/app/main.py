from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .database import engine, Base, SessionLocal, migrate_database
from .seed import seed_database
from .seed_arena import seed_arena_data
from .schemas import HealthResponse
from .routers import auth, profile, careers, roadmap, skills, chat, github, jobs, assessments, webhooks, background_jobs, arena

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure tables and columns exist safely and seed initial catalog/user
    migrate_database()
    db = SessionLocal()
    try:
        seed_database(db)
        seed_arena_data(db)
    finally:
        db.close()
    yield
    # Shutdown

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Backend API for SkillTrace AI Career Coach",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root and Health Check Endpoints
@app.get("/", tags=["Health"])
@app.get("/health", response_model=HealthResponse, tags=["Health"])
@app.get("/api/health", response_model=HealthResponse, tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "database": "connected"
    }

# Mount feature routers
app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(careers.router)
app.include_router(roadmap.router)
app.include_router(skills.router)
app.include_router(chat.router)
app.include_router(github.router)
app.include_router(jobs.router)
app.include_router(assessments.router)
app.include_router(webhooks.router)
app.include_router(background_jobs.router)
app.include_router(arena.router)

