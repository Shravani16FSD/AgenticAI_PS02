"""
Job Requirement Discovery Router for SkillTrace AI.
Provides:
- POST /api/jobs/import
- GET /api/jobs
- GET /api/jobs/{job_id}
- POST /api/jobs/{job_id}/extract-requirements
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import JobListing, JobRequirement
from ..schemas import JobImportRequest, JobListingResponse, JobRequirementResponse
from ..services.job_discovery_service import job_discovery_service

router = APIRouter(prefix="/api/jobs", tags=["Job Discovery"])


@router.post("/import", response_model=JobListingResponse, status_code=status.HTTP_201_CREATED)
async def import_job_listing(req: JobImportRequest, db: Session = Depends(get_db)):
    """
    Import and store a real job or internship listing from its original public URL.
    Extracts explicit vs preferred skills without inventing jobs.
    """
    try:
        job = await job_discovery_service.import_job_from_url(req.url, db)
        return job
    except ValueError as val_err:
        raise HTTPException(status_code=400, detail=str(val_err))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to import job listing: {str(e)}")


@router.get("", response_model=List[JobListingResponse])
def list_job_listings(db: Session = Depends(get_db)):
    """List all imported job listings."""
    jobs = db.query(JobListing).order_by(JobListing.retrieved_at.desc()).all()
    return jobs


@router.get("/{job_id}", response_model=JobListingResponse)
def get_job_listing(job_id: str, db: Session = Depends(get_db)):
    """Get a specific imported job listing and its extracted requirements."""
    job = db.query(JobListing).filter(JobListing.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job listing not found.")
    return job


@router.post("/{job_id}/extract-requirements", response_model=JobListingResponse)
def re_extract_requirements(job_id: str, db: Session = Depends(get_db)):
    """Re-extract explicit and preferred skills from the saved description text."""
    job = db.query(JobListing).filter(JobListing.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job listing not found.")

    req_skills, pref_skills = job_discovery_service.extract_skills_from_text(job.description_raw)

    db.query(JobRequirement).filter(JobRequirement.job_id == job.id).delete()
    import uuid
    from ..taxonomy import taxonomy_registry

    for s in req_skills:
        defn = taxonomy_registry.get(s)
        cat = defn.category if defn else "General"
        db.add(JobRequirement(
            id=f"req-{uuid.uuid4().hex[:8]}",
            job_id=job.id,
            skill_name=s,
            skill_category=cat,
            requirement_type="required",
            importance="Essential"
        ))

    for p in pref_skills:
        if p in req_skills:
            continue
        defn = taxonomy_registry.get(p)
        cat = defn.category if defn else "General"
        db.add(JobRequirement(
            id=f"req-{uuid.uuid4().hex[:8]}",
            job_id=job.id,
            skill_name=p,
            skill_category=cat,
            requirement_type="preferred",
            importance="Valuable"
        ))

    db.commit()
    db.refresh(job)
    return job
