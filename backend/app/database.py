import os
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker
from .config import settings

# Configure connect args for SQLite vs PostgreSQL
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def migrate_database():
    """
    Non-destructive schema migration helper.
    Preserves all existing data while ensuring new columns and constraints exist.
    """
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()

    # 1. Create tables if they do not exist
    Base.metadata.create_all(bind=engine)

    # 2. Check and migrate roadmap_tasks columns if table previously existed
    if "roadmap_tasks" in existing_tables:
        columns = [c["name"] for c in inspector.get_columns("roadmap_tasks")]
        with engine.begin() as conn:
            if "career_id" not in columns:
                conn.execute(text("ALTER TABLE roadmap_tasks ADD COLUMN career_id VARCHAR(100) REFERENCES career_paths(id);"))
            if "deadline" not in columns:
                conn.execute(text("ALTER TABLE roadmap_tasks ADD COLUMN deadline VARCHAR(100);"))

    # 3. Check and migrate user_skills columns
    if "user_skills" in existing_tables:
        columns = [c["name"] for c in inspector.get_columns("user_skills")]
        with engine.begin() as conn:
            if "is_gap" not in columns:
                conn.execute(text("ALTER TABLE user_skills ADD COLUMN is_gap BOOLEAN NOT NULL DEFAULT 0;"))

    # 4. Check and migrate chat_messages columns
    if "chat_messages" in existing_tables:
        columns = [c["name"] for c in inspector.get_columns("chat_messages")]
        with engine.begin() as conn:
            if "session_id" not in columns:
                conn.execute(text("ALTER TABLE chat_messages ADD COLUMN session_id VARCHAR(100) NOT NULL DEFAULT 'default_session';"))

    # 5. Ensure Unique index on saved_careers (user_id, career_id)
    if "saved_careers" in existing_tables or "saved_careers" in Base.metadata.tables:
        with engine.begin() as conn:
            conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS uq_user_saved_career ON saved_careers (user_id, career_id);"))

