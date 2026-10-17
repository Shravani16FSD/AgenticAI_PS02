"""
Skill Assessment & Evidence Router for SkillTrace AI.
Provides:
- POST /api/assessments/start
- GET /api/assessments/latest
- GET /api/assessments/history
- GET /api/assessments/{assessment_id}
- GET /api/assessments/diff/{version_a_id}/{version_b_id}
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import SkillAssessment, GitHubRepository, GitHubAccount
from ..schemas import (
    StartAssessmentRequest,
    SkillAssessmentResponse,
    AssessmentDetailResponse,
    AssessmentDiffResponse
)
from ..services.assessment_engine import assessment_engine

router = APIRouter(prefix="/api/assessments", tags=["Skill Assessments"])


@router.post("/start", response_model=AssessmentDetailResponse, status_code=status.HTTP_201_CREATED)
async def start_repository_assessment(
    req: StartAssessmentRequest,
    user_id: str = "default_user",
    db: Session = Depends(get_db)
):
    """
    Executes grounded static and AST evidence extraction on the repository,
    evaluating against target job requirements or all code evidence.
    """
    account = db.query(GitHubAccount).filter(GitHubAccount.user_id == user_id).first()
    token = account.access_token if account else None

    try:
        assessment = await assessment_engine.execute_assessment(
            db=db,
            user_id=user_id,
            repo_full_name=req.repo_full_name,
            commit_sha=req.commit_sha,
            job_id=req.job_id,
            token=token
        )
        return assessment
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Assessment failed: {str(e)}")


@router.get("/latest", response_model=AssessmentDetailResponse)
def get_latest_assessment(
    repo_full_name: Optional[str] = Query(None),
    user_id: str = "default_user",
    db: Session = Depends(get_db)
):
    """Retrieve the latest skill assessment and code evidence citations."""
    query = db.query(SkillAssessment).filter(SkillAssessment.user_id == user_id)
    if repo_full_name:
        query = query.filter(SkillAssessment.repo_full_name == repo_full_name)

    latest = query.order_by(SkillAssessment.created_at.desc()).first()
    if not latest:
        raise HTTPException(status_code=404, detail="No assessments found.")
    return latest


@router.get("/history", response_model=List[SkillAssessmentResponse])
def list_assessment_history(
    repo_full_name: Optional[str] = Query(None),
    user_id: str = "default_user",
    db: Session = Depends(get_db)
):
    """List historical assessment versions to observe progression."""
    query = db.query(SkillAssessment).filter(SkillAssessment.user_id == user_id)
    if repo_full_name:
        query = query.filter(SkillAssessment.repo_full_name == repo_full_name)

    history = query.order_by(SkillAssessment.version.desc()).all()
    return history


@router.get("/diff/{version_a_id}/{version_b_id}", response_model=AssessmentDiffResponse)
def get_assessment_diff(
    version_a_id: str,
    version_b_id: str,
    db: Session = Depends(get_db)
):
    """Calculate and return difference and progression between two assessment versions."""
    try:
        diff = assessment_engine.compute_assessment_diff(db, version_a_id, version_b_id)
        return diff
    except ValueError as val_err:
        raise HTTPException(status_code=404, detail=str(val_err))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to compute diff: {str(e)}")


@router.get("/{assessment_id}", response_model=AssessmentDetailResponse)
def get_assessment_by_id(assessment_id: str, db: Session = Depends(get_db)):
    """Retrieve an assessment by ID with all evidence citations and requirement statuses."""
    assessment = db.query(SkillAssessment).filter(SkillAssessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found.")
    return assessment
