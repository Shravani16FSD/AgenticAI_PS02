from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field
from datetime import datetime

# --- Health Schema ---
class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str
    database: str

# --- User Profile Schemas ---
class UserProfileBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    study_status: str = Field(..., min_length=1, max_length=255)
    target_career_id: str = Field(default="ai-product-engineer")
    interests: List[str] = Field(default_factory=list)
    current_skills: List[str] = Field(default_factory=list)
    primary_goal: str = Field(..., min_length=1)
    weekly_hours: int = Field(default=8, ge=1, le=80)
    onboarding_completed: bool = Field(default=True)

class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    study_status: Optional[str] = None
    target_career_id: Optional[str] = None
    interests: Optional[List[str]] = None
    current_skills: Optional[List[str]] = None
    primary_goal: Optional[str] = None
    weekly_hours: Optional[int] = Field(None, ge=1, le=80)
    onboarding_completed: Optional[bool] = None

class UserProfileResponse(UserProfileBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# --- Career Path Schemas ---
class CareerSkillItem(BaseModel):
    name: str
    importance: str
    category: str

class CareerPhaseItem(BaseModel):
    phase: str
    focus: str
    estimatedMonths: str

class CareerNextStepItem(BaseModel):
    title: str
    whyItMatters: str
    duration: str
    resourceName: str
    resourceUrl: str

class CareerPathResponse(BaseModel):
    id: str
    title: str
    category: str
    tagline: str
    match_reason: str
    description: str
    responsibilities: List[str]
    required_skills: List[Dict[str, Any]]
    learning_phases: List[Dict[str, Any]]
    recommended_next_step: Dict[str, Any]
    entry_points: List[str]

    class Config:
        from_attributes = True

# --- Roadmap Task Schemas ---
class RoadmapTaskBase(BaseModel):
    career_id: Optional[str] = None
    phase_id: int = Field(..., ge=1, le=5)
    phase_name: str
    title: str = Field(..., min_length=1, max_length=255)
    description: str
    skill: str
    estimated_time: str
    deadline: Optional[str] = None
    status: str = Field(default="not_started")
    resource_name: Optional[str] = None
    resource_type: Optional[str] = None
    resource_url: Optional[str] = None
    notes: Optional[str] = None

class RoadmapTaskCreate(RoadmapTaskBase):
    pass

class RoadmapTaskUpdate(BaseModel):
    career_id: Optional[str] = None
    status: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    skill: Optional[str] = None
    estimated_time: Optional[str] = None
    deadline: Optional[str] = None
    resource_name: Optional[str] = None
    resource_url: Optional[str] = None
    notes: Optional[str] = None

class RoadmapTaskResponse(RoadmapTaskBase):
    id: str
    user_id: str
    completed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# --- Skills Schemas ---
class UserSkillBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    category: str = Field(default="General")
    status: str = Field(default="learning")
    hours_spent: float = Field(default=0.0, ge=0.0)
    target_hours: float = Field(default=30.0, gt=0.0)
    is_gap: bool = Field(default=False)
    last_practiced: str = Field(default="Recently")

class UserSkillCreate(UserSkillBase):
    pass

class LogPracticeRequest(BaseModel):
    hours: float = Field(..., gt=0.0, le=24.0)

class UserSkillResponse(UserSkillBase):
    id: str
    user_id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# --- Chat & AI Schemas ---
class ChatMessageResponse(BaseModel):
    id: str
    session_id: str = "default_session"
    sender: str
    text: str
    status: str
    suggested_actions: Optional[List[str]] = None
    timestamp: datetime

    class Config:
        from_attributes = True

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    session_id: Optional[str] = "default_session"
    history: Optional[List[Dict[str, str]]] = Field(default_factory=list)

    class Config:
        extra = "ignore"


