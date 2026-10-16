from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, Text, DateTime, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.orm import relationship
from .database import Base

class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(String(100), primary_key=True, default="default_user")
    name = Column(String(255), nullable=False, default="Alex Morgan")
    study_status = Column(String(255), nullable=False, default="Third-year CS & HCI Student")
    target_career_id = Column(String(100), nullable=False, default="ai-product-engineer")
    interests = Column(JSON, nullable=False, default=list)
    current_skills = Column(JSON, nullable=False, default=list)
    primary_goal = Column(Text, nullable=False, default="Secure a Summer 2027 AI Product Engineering Internship")
    weekly_hours = Column(Integer, nullable=False, default=8)
    onboarding_completed = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    saved_careers = relationship("SavedCareer", back_populates="user", cascade="all, delete-orphan")
    roadmap_tasks = relationship("RoadmapTask", back_populates="user", cascade="all, delete-orphan")
    skills = relationship("UserSkill", back_populates="user", cascade="all, delete-orphan")
    chat_messages = relationship("ChatMessage", back_populates="user", cascade="all, delete-orphan")


class CareerPath(Base):
    __tablename__ = "career_paths"

    id = Column(String(100), primary_key=True)
    title = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)
    tagline = Column(Text, nullable=False)
    match_reason = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    responsibilities = Column(JSON, nullable=False, default=list)
    required_skills = Column(JSON, nullable=False, default=list)
    learning_phases = Column(JSON, nullable=False, default=list)
    recommended_next_step = Column(JSON, nullable=False, default=dict)
    entry_points = Column(JSON, nullable=False, default=list)


class SavedCareer(Base):
    __tablename__ = "saved_careers"

    id = Column(String(100), primary_key=True)
    user_id = Column(String(100), ForeignKey("user_profiles.id"), nullable=False)
    career_id = Column(String(100), ForeignKey("career_paths.id"), nullable=False)
    saved_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("user_id", "career_id", name="uq_user_saved_career"),
    )

    user = relationship("UserProfile", back_populates="saved_careers")
    career = relationship("CareerPath")


class RoadmapTask(Base):
    __tablename__ = "roadmap_tasks"

    id = Column(String(100), primary_key=True)
    user_id = Column(String(100), ForeignKey("user_profiles.id"), nullable=False)
    career_id = Column(String(100), ForeignKey("career_paths.id"), nullable=True, index=True)
    phase_id = Column(Integer, nullable=False)
    phase_name = Column(String(255), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    skill = Column(String(255), nullable=False)
    estimated_time = Column(String(100), nullable=False)
    deadline = Column(String(100), nullable=True)
    status = Column(String(50), nullable=False, default="not_started")  # not_started, in_progress, completed
    resource_name = Column(String(255), nullable=True)
    resource_type = Column(String(100), nullable=True)
    resource_url = Column(String(500), nullable=True)
    notes = Column(Text, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("UserProfile", back_populates="roadmap_tasks")
    career = relationship("CareerPath")


class UserSkill(Base):
    __tablename__ = "user_skills"

    id = Column(String(100), primary_key=True)
    user_id = Column(String(100), ForeignKey("user_profiles.id"), nullable=False)
    name = Column(String(255), nullable=False)
    category = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False, default="learning")  # learning, practicing, proficient
    hours_spent = Column(Float, nullable=False, default=0.0)
    target_hours = Column(Float, nullable=False, default=30.0)
    is_gap = Column(Boolean, nullable=False, default=False)
    last_practiced = Column(String(100), nullable=False, default="Recently")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("UserProfile", back_populates="skills")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(String(100), primary_key=True)
    user_id = Column(String(100), ForeignKey("user_profiles.id"), nullable=False)
    session_id = Column(String(100), nullable=False, default="default_session", index=True)
    sender = Column(String(20), nullable=False)  # user or assistant
    text = Column(Text, nullable=False)
    status = Column(String(50), nullable=False, default="delivered")
    suggested_actions = Column(JSON, nullable=True, default=list)
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("UserProfile", back_populates="chat_messages")
