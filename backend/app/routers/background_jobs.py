"""
Background Job Processing Status Router for SkillTrace AI.
Provides:
- GET /api/background-jobs/{job_id}
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import BackgroundJob
from ..schemas import BackgroundJobResponse

router = APIRouter(prefix="/api/background-jobs", tags=["Background Jobs"])


@router.get("/{job_id}", response_model=BackgroundJobResponse)
def get_background_job_status(job_id: str, db: Session = Depends(get_db)):
    """Check asynchronous background processing status and results."""
    job = db.query(BackgroundJob).filter(BackgroundJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Background job not found.")
    return job
