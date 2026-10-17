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
    conversation_id: Optional[str] = None
    history: Optional[List[Dict[str, str]]] = Field(default_factory=list)

    class Config:
        extra = "ignore"

class ChatResponse(BaseModel):
    conversation_id: str
    message_id: str
    sender: str = "assistant"
    reply: str
    text: str
    suggested_actions: List[str] = Field(default_factory=list)
    status: str = "delivered"
    timestamp: datetime

    class Config:
        from_attributes = True


# --- GitHub Integration Schemas ---
class GitHubConnectRequest(BaseModel):
    token: str = Field(..., min_length=4, description="GitHub Personal Access Token or OAuth Token")
    username: Optional[str] = None


class GitHubAccountResponse(BaseModel):
    id: str
    github_username: str
    avatar_url: Optional[str] = None
    html_url: Optional[str] = None
    connected_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class GitHubRepoResponse(BaseModel):
    id: str
    repo_full_name: str
    default_branch: str
    is_private: bool
    html_url: Optional[str] = None
    is_authorized: bool
    last_synced_at: Optional[datetime] = None
    last_commit_sha: Optional[str] = None

    class Config:
        from_attributes = True


class AuthorizeRepoRequest(BaseModel):
    authorized: bool = True


# --- Job Requirement Discovery Schemas ---
class JobImportRequest(BaseModel):
    url: str = Field(..., min_length=5, description="Original public job listing URL")


class JobRequirementResponse(BaseModel):
    id: str
    skill_name: str
    skill_category: Optional[str] = None
    requirement_type: str  # "required" vs "preferred"
    importance: str

    class Config:
        from_attributes = True


class JobListingResponse(BaseModel):
    id: str
    source_url: str
    title: str
    employer: str
    location: Optional[str] = None
    work_mode: Optional[str] = None
    employment_type: Optional[str] = None
    experience_level: Optional[str] = None
    source_name: str
    description_raw: str
    retrieval_status: str
    failure_reason: Optional[str] = None
    retrieved_at: datetime
    requirements: List[JobRequirementResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True


# --- Evidence & Assessment Schemas ---
class StartAssessmentRequest(BaseModel):
    repo_full_name: str = Field(..., description="Full repository name, e.g. octocat/hello-world")
    job_id: Optional[str] = Field(None, description="Optional target JobListing id to assess against")
    commit_sha: Optional[str] = Field(None, description="Optional commit SHA, defaults to latest HEAD")
    branch: Optional[str] = Field(None, description="Branch to scan if commit_sha is not specified")


class EvidenceCitationResponse(BaseModel):
    id: str
    skill_name: str
    repo_full_name: str
    commit_sha: str
    file_path: str
    start_line: int
    end_line: int
    code_snippet: str
    evidence_category: str
    is_direct_evidence: bool
    confidence_score: float
    ast_node_type: Optional[str] = None
    rationale: Optional[str] = None
    github_url: Optional[str] = None

    class Config:
        from_attributes = True


class AssessmentSkillResultResponse(BaseModel):
    id: str
    skill_name: str
    requirement_type: str
    status: str  # "Demonstrated", "Partially demonstrated", "Not demonstrated in this scope"
    score: float
    rationale: Optional[str] = None
    evidence_count: int
    direct_evidence_count: int

    class Config:
        from_attributes = True


class SkillAssessmentResponse(BaseModel):
    id: str
    user_id: str
    job_id: Optional[str] = None
    repo_full_name: str
    commit_sha: str
    version: int
    previous_assessment_id: Optional[str] = None
    overall_score: Optional[float] = None
    match_percentage: Optional[float] = None
    status: str
    summary: Optional[str] = None
    total_skills_assessed: int
    skills_demonstrated: int
    skills_partially_demonstrated: int
    skills_not_demonstrated: int
    created_at: datetime

    class Config:
        from_attributes = True


class AssessmentDetailResponse(SkillAssessmentResponse):
    skill_results: List[AssessmentSkillResultResponse] = Field(default_factory=list)
    evidence: List[EvidenceCitationResponse] = Field(default_factory=list)


class AssessmentDiffResponse(BaseModel):
    version_a: int
    version_b: int
    assessment_id_a: str
    assessment_id_b: str
    commit_sha_a: str
    commit_sha_b: str
    score_change: float
    newly_demonstrated_skills: List[str]
    regressed_skills: List[str]
    new_evidence_count: int
    removed_evidence_count: int
    summary_diff: str


# --- Webhook & Background Job Schemas ---
class WebhookResponse(BaseModel):
    status: str
    event_id: str
    event_type: str
    message: str
    queued_job_id: Optional[str] = None


class BackgroundJobResponse(BaseModel):
    id: str
    job_type: str
    status: str
    target_id: Optional[str] = None
    error_message: Optional[str] = None
    result_summary: Optional[Dict[str, Any]] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True



