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
    github_accounts = relationship("GitHubAccount", back_populates="user", cascade="all, delete-orphan")
    assessments = relationship("SkillAssessment", back_populates="user", cascade="all, delete-orphan")



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


# -------------------------------------------------------------
# GitHub Account & Repository Models
# -------------------------------------------------------------
class GitHubAccount(Base):
    __tablename__ = "github_accounts"

    id = Column(String(100), primary_key=True)
    user_id = Column(String(100), ForeignKey("user_profiles.id"), nullable=False, index=True)
    github_username = Column(String(255), nullable=False)
    github_user_id = Column(String(100), nullable=True)
    access_token = Column(String(500), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    html_url = Column(String(500), nullable=True)
    scope = Column(String(255), nullable=True)
    connected_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("UserProfile", back_populates="github_accounts")
    repositories = relationship("GitHubRepository", back_populates="account", cascade="all, delete-orphan")


class GitHubRepository(Base):
    __tablename__ = "github_repositories"

    id = Column(String(100), primary_key=True)
    user_id = Column(String(100), ForeignKey("user_profiles.id"), nullable=False, index=True)
    account_id = Column(String(100), ForeignKey("github_accounts.id"), nullable=True, index=True)
    repo_full_name = Column(String(255), nullable=False, index=True)
    default_branch = Column(String(100), nullable=False, default="main")
    is_private = Column(Boolean, nullable=False, default=False)
    html_url = Column(String(500), nullable=True)
    is_authorized = Column(Boolean, nullable=False, default=True)
    last_synced_at = Column(DateTime, nullable=True)
    last_commit_sha = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    account = relationship("GitHubAccount", back_populates="repositories")


# -------------------------------------------------------------
# Job Listing & Requirement Models
# -------------------------------------------------------------
class JobListing(Base):
    __tablename__ = "job_listings"

    id = Column(String(100), primary_key=True)
    source_url = Column(String(1000), nullable=False, unique=True, index=True)
    title = Column(String(255), nullable=False)
    employer = Column(String(255), nullable=False)
    location = Column(String(255), nullable=True)
    work_mode = Column(String(100), nullable=True)
    employment_type = Column(String(100), nullable=True)
    experience_level = Column(String(100), nullable=True)
    source_name = Column(String(100), nullable=False, default="Direct URL")
    description_raw = Column(Text, nullable=False)
    retrieval_status = Column(String(50), nullable=False, default="active")  # active, stale, failed
    failure_reason = Column(Text, nullable=True)
    retrieved_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    requirements = relationship("JobRequirement", back_populates="job", cascade="all, delete-orphan")


class JobRequirement(Base):
    __tablename__ = "job_requirements"

    id = Column(String(100), primary_key=True)
    job_id = Column(String(100), ForeignKey("job_listings.id"), nullable=False, index=True)
    skill_name = Column(String(255), nullable=False)
    skill_category = Column(String(100), nullable=True)
    requirement_type = Column(String(50), nullable=False, default="required")  # required (explicit) vs preferred
    importance = Column(String(50), nullable=False, default="Essential")
    created_at = Column(DateTime, default=datetime.utcnow)

    job = relationship("JobListing", back_populates="requirements")


# -------------------------------------------------------------
# Assessment & Evidence Models
# -------------------------------------------------------------
class SkillAssessment(Base):
    __tablename__ = "skill_assessments"

    id = Column(String(100), primary_key=True)
    user_id = Column(String(100), ForeignKey("user_profiles.id"), nullable=False, index=True)
    job_id = Column(String(100), ForeignKey("job_listings.id"), nullable=True, index=True)
    repo_full_name = Column(String(255), nullable=False, index=True)
    commit_sha = Column(String(100), nullable=False)
    version = Column(Integer, nullable=False, default=1)
    previous_assessment_id = Column(String(100), ForeignKey("skill_assessments.id"), nullable=True)
    overall_score = Column(Float, nullable=True)
    match_percentage = Column(Float, nullable=True)
    status = Column(String(50), nullable=False, default="completed")  # completed, processing, failed
    summary = Column(Text, nullable=True)
    total_skills_assessed = Column(Integer, nullable=False, default=0)
    skills_demonstrated = Column(Integer, nullable=False, default=0)
    skills_partially_demonstrated = Column(Integer, nullable=False, default=0)
    skills_not_demonstrated = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("UserProfile", back_populates="assessments")
    job = relationship("JobListing")
    evidence = relationship("RepositoryEvidence", back_populates="assessment", cascade="all, delete-orphan")
    skill_results = relationship("AssessmentSkillResult", back_populates="assessment", cascade="all, delete-orphan")
    previous_assessment = relationship("SkillAssessment", remote_side=[id])


class AssessmentSkillResult(Base):
    __tablename__ = "assessment_skill_results"

    id = Column(String(100), primary_key=True)
    assessment_id = Column(String(100), ForeignKey("skill_assessments.id"), nullable=False, index=True)
    skill_name = Column(String(255), nullable=False)
    requirement_type = Column(String(50), nullable=False, default="required")  # required vs preferred
    status = Column(String(50), nullable=False)  # Demonstrated, Partially demonstrated, Not demonstrated in this scope
    score = Column(Float, nullable=False, default=0.0)
    rationale = Column(Text, nullable=True)
    evidence_count = Column(Integer, nullable=False, default=0)
    direct_evidence_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    assessment = relationship("SkillAssessment", back_populates="skill_results")


class RepositoryEvidence(Base):
    __tablename__ = "repository_evidences"

    id = Column(String(100), primary_key=True)
    assessment_id = Column(String(100), ForeignKey("skill_assessments.id"), nullable=False, index=True)
    skill_name = Column(String(255), nullable=False, index=True)
    repo_full_name = Column(String(255), nullable=False)
    commit_sha = Column(String(100), nullable=False)
    file_path = Column(String(500), nullable=False)
    start_line = Column(Integer, nullable=False, default=1)
    end_line = Column(Integer, nullable=False, default=1)
    code_snippet = Column(Text, nullable=False)
    evidence_category = Column(String(50), nullable=False, default="Moderate evidence")
    is_direct_evidence = Column(Boolean, nullable=False, default=True)  # Direct code AST/invocation vs AI inference
    confidence_score = Column(Float, nullable=False, default=1.0)
    ast_node_type = Column(String(100), nullable=True)
    rationale = Column(Text, nullable=True)
    github_url = Column(String(1000), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    assessment = relationship("SkillAssessment", back_populates="evidence")


# -------------------------------------------------------------
# Commit Records & Webhook Events
# -------------------------------------------------------------
class CommitRecord(Base):
    __tablename__ = "commit_records"

    id = Column(String(100), primary_key=True)
    repo_full_name = Column(String(255), nullable=False, index=True)
    commit_sha = Column(String(100), nullable=False, index=True)
    author_name = Column(String(255), nullable=True)
    commit_message = Column(Text, nullable=True)
    committed_at = Column(DateTime, nullable=True)
    files_added = Column(JSON, nullable=False, default=list)
    files_modified = Column(JSON, nullable=False, default=list)
    files_removed = Column(JSON, nullable=False, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)


class WebhookEvent(Base):
    __tablename__ = "webhook_events"

    id = Column(String(100), primary_key=True)  # X-GitHub-Delivery GUID
    event_type = Column(String(50), nullable=False, index=True)  # push, ping, etc.
    repo_full_name = Column(String(255), nullable=True, index=True)
    sender = Column(String(255), nullable=True)
    payload = Column(JSON, nullable=False)
    signature_valid = Column(Boolean, nullable=False, default=True)
    status = Column(String(50), nullable=False, default="received")  # received, processed, ignored, failed
    error_message = Column(Text, nullable=True)
    processed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# -------------------------------------------------------------
# Background Jobs
# -------------------------------------------------------------
class BackgroundJob(Base):
    __tablename__ = "background_jobs"

    id = Column(String(100), primary_key=True)
    job_type = Column(String(100), nullable=False)  # webhook_reassessment, initial_assessment, job_import
    status = Column(String(50), nullable=False, default="pending")  # pending, in_progress, completed, failed
    target_id = Column(String(100), nullable=True)
    error_message = Column(Text, nullable=True)
    result_summary = Column(JSON, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

