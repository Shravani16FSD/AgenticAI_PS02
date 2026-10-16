from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .database import engine, Base, SessionLocal, migrate_database
from .seed import seed_database
from .schemas import HealthResponse
from .routers import profile, careers, roadmap, skills, chat

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure tables and columns exist safely and seed initial catalog/user
    migrate_database()
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
    yield
    # Shutdown

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Backend API for Chapter AI Career Coach",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health Check Endpoint
@app.get("/api/health", response_model=HealthResponse, tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "database": "connected"
    }

# Mount feature routers
app.include_router(profile.router)
app.include_router(careers.router)
app.include_router(roadmap.router)
app.include_router(skills.router)
app.include_router(chat.router)
