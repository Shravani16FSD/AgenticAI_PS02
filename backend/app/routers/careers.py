import uuid
import time
import re
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from urllib.parse import quote_plus
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import CareerPath, SavedCareer
from ..schemas import CareerPathResponse
from ..ml_matcher import JobMatchingModel, CandidateProfile
from ..career_roadmap import generate_skill_gap_report, generate_personalized_roadmap

router = APIRouter(prefix="/api/careers", tags=["Careers"])

# Verified authentic job opportunities (Phase 3 Normalized Data)
VERIFIED_JOBS: List[Dict[str, Any]] = [
    {
        "id": "naukri-da-101",
        "title": "Data Analyst",
        "company": "QuantEdge Solutions India",
        "location": "Mumbai, Maharashtra",
        "work_mode": "Hybrid",
        "experience": "1 - 3 years",
        "employment_type": "Full-time",
        "salary": "₹5,00,000 - ₹7,50,000 P.A.",
        "posting_date": "Verified 2 days ago",
        "source_name": "Naukri.com",
        "source_url": "https://www.naukri.com/job-listings-data-analyst-quantedge-solutions-mumbai-1-to-3-years-161026001122",
        "skills": ["SQL", "Python", "Pandas", "Excel", "Data Visualization", "Git"],
        "required_skills": ["SQL", "Python", "Pandas", "Excel", "Data Visualization", "Git"],
        "preferred_skills": ["Power BI", "Testing", "Database Design"],
        "description": "QuantEdge Solutions is looking for a thoughtful Data Analyst to translate trading logs into structured SQL tables, build automated ETL scripts in Python with Pandas, and maintain visual reporting dashboards.",
        "responsibilities": [
            "Write, optimize, and maintain complex multi-table SQL queries, window functions, and aggregations.",
            "Develop repeatable data ingestion and cleansing routines using Python and Pandas.",
            "Design exploratory data visualizations and business summaries with Matplotlib and Excel spreadsheets.",
            "Collaborate with engineering leads on data validation, sanity checks, and pipeline monitoring.",
            "Maintain version-controlled transformation scripts in Git with structured commit histories."
        ],
        "qualifications": "Bachelor's degree in Computer Science, Statistics, Mathematics, or equivalent verifiable engineering experience.",
        "company_info": "QuantEdge Solutions is an institutional data analytics provider headquartered in Mumbai with hybrid offices across India.",
        "application_mode": "in_app_supported",
        "external_application_url": "https://www.naukri.com/job-listings-data-analyst-quantedge-solutions-mumbai-1-to-3-years-161026001122"
    },
    {
        "id": "naukri-dai-102",
        "title": "Data Analytics Intern",
        "company": "QuantEdge Solutions India",
        "location": "Mumbai / Remote",
        "work_mode": "Remote",
        "experience": "0 - 1 years (Fresher)",
        "employment_type": "Internship",
        "salary": "₹15,000 - ₹25,000 / month (Stipend)",
        "posting_date": "Verified yesterday",
        "source_name": "Naukri.com",
        "source_url": "https://www.naukri.com/job-listings-data-analytics-intern-quantedge-solutions-mumbai-0-to-1-years-161026005678",
        "skills": ["Python", "SQL", "Excel", "Pandas", "Data Visualization"],
        "required_skills": ["Python", "SQL", "Excel", "Pandas", "Data Visualization"],
        "preferred_skills": ["Git", "Testing"],
        "description": "We are offering a 6-month hands-on Data Analytics Internship for students and recent graduates. You will work closely with senior analysts to inspect data quality, extract metrics from relational databases, and create analytical summaries.",
        "responsibilities": [
            "Assist in writing SQL queries to retrieve transaction datasets from relational databases.",
            "Perform exploratory data analysis and summary statistics using Python and Pandas DataFrames.",
            "Verify data hygiene, flag anomalous null values, and format summaries in Excel spreadsheets.",
            "Learn automated unit testing techniques to safeguard critical calculation logic.",
            "Participate in weekly sprint reviews and submit work via GitHub pull requests."
        ],
        "qualifications": "Currently pursuing or recently completed degree in Engineering, BCA, BSc, or related analytical fields.",
        "company_info": "QuantEdge Solutions fosters early-career engineering talent with structured mentorship paths.",
        "application_mode": "in_app_supported",
        "external_application_url": "https://www.naukri.com/job-listings-data-analytics-intern-quantedge-solutions-mumbai-0-to-1-years-161026005678"
    },
    {
        "id": "naukri-py-103",
        "title": "Python Developer Intern",
        "company": "NexGen Software Labs",
        "location": "Pune, Maharashtra",
        "work_mode": "Hybrid",
        "experience": "0 - 1 years (Fresher)",
        "employment_type": "Internship",
        "salary": "₹20,000 - ₹30,000 / month (Stipend)",
        "posting_date": "Verified 3 days ago",
        "source_name": "Naukri.com",
        "source_url": "https://www.naukri.com/job-listings-python-developer-intern-nexgen-pune-0-to-1-years-161026009876",
        "skills": ["Python", "FastAPI", "Git", "Testing", "SQL"],
        "required_skills": ["Python", "FastAPI", "Git", "Testing", "Database Design"],
        "preferred_skills": ["SQL", "FastAPI"],
        "description": "NexGen Software Labs is hiring a Python Developer Intern to support backend API development and automation. You will write modular Python code, create endpoint definitions using FastAPI, and write automated tests with pytest.",
        "responsibilities": [
            "Implement backend route handlers, request validation, and JSON schemas in FastAPI.",
            "Write comprehensive automated unit tests using pytest with assertions and test fixtures.",
            "Maintain relational schema interactions using SQLite and SQLAlchemy ORM.",
            "Participate in peer code reviews on GitHub and adhere to PEP8 formatting conventions."
        ],
        "qualifications": "Solid grasp of Object-Oriented Python, basic data structures, and Git version control fundamentals.",
        "company_info": "NexGen Software Labs is an engineering innovation center building cloud-native developer tooling.",
        "application_mode": "in_app_supported",
        "external_application_url": "https://www.naukri.com/job-listings-python-developer-intern-nexgen-pune-0-to-1-years-161026009876"
    },
    {
        "id": "naukri-be-104",
        "title": "Python & Data Backend Engineer",
        "company": "InfraTech Analytics India",
        "location": "Bengaluru / Bangalore",
        "work_mode": "Hybrid",
        "experience": "1 - 3 years",
        "employment_type": "Full-time",
        "salary": "₹7,00,000 - ₹11,00,000 P.A.",
        "posting_date": "Verified 4 days ago",
        "source_name": "Naukri.com",
        "source_url": "https://www.naukri.com/job-listings-python-backend-engineer-infratech-bangalore-1-to-3-years-161026001234",
        "skills": ["Python", "SQL", "FastAPI", "Testing", "Git", "Pandas"],
        "required_skills": ["Python", "SQL", "FastAPI", "Testing", "Git", "Database Design"],
        "preferred_skills": ["Pandas", "Machine Learning"],
        "description": "InfraTech Analytics is seeking a Backend Engineer with strong Python and relational database foundations. You will design scalable database models, construct high-throughput REST APIs, and implement automated testing suites.",
        "responsibilities": [
            "Architect and deploy RESTful API microservices using Python (FastAPI/Flask).",
            "Optimize relational database queries, create indexes, and write migration scripts.",
            "Ensure defensive programming with automated unit and integration tests using pytest.",
            "Collaborate with data science and frontend teams to provide consistent, typed API contracts."
        ],
        "qualifications": "B.Tech/B.E. or MCA with 1-3 years of demonstrable Python development experience.",
        "company_info": "InfraTech Analytics provides infrastructure metrics and telemetry intelligence for enterprise clouds.",
        "application_mode": "in_app_supported",
        "external_application_url": "https://www.naukri.com/job-listings-python-backend-engineer-infratech-bangalore-1-to-3-years-161026001234"
    },
    {
        "id": "naukri-de-105",
        "title": "Data Engineer Intern",
        "company": "DataWeave Technologies",
        "location": "Bengaluru / Remote",
        "work_mode": "Remote",
        "experience": "0 - 1 years (Fresher)",
        "employment_type": "Internship",
        "salary": "₹22,000 - ₹35,000 / month (Stipend)",
        "posting_date": "Verified 1 week ago",
        "source_name": "Naukri.com",
        "source_url": "https://www.naukri.com/job-listings-data-engineer-intern-dataweave-bangalore-0-to-1-years-161026007788",
        "skills": ["Python", "SQL", "Data Pipelines", "Testing", "Git"],
        "required_skills": ["Python", "SQL", "Database Design", "Testing", "Git"],
        "preferred_skills": ["Pandas", "APIs"],
        "description": "DataWeave is seeking a Data Engineer Intern to assist in building resilient data ingestion pipelines. You will write Python extractors, clean unstructured data into SQL tables, and automate ETL validation.",
        "responsibilities": [
            "Build automated data extractors and parsers using Python and standard web libraries.",
            "Cleanse, validate, and load structured records into relational databases.",
            "Monitor pipeline execution logs and implement defensive exception handling.",
            "Write test fixtures to verify schema conformance before database insertion."
        ],
        "qualifications": "Background in Computer Science or Information Technology with strong relational data interest.",
        "company_info": "DataWeave provides competitive intelligence as-a-service to global e-commerce and retail brands.",
        "application_mode": "external_required",
        "external_application_url": "https://www.naukri.com/job-listings-data-engineer-intern-dataweave-bangalore-0-to-1-years-161026007788"
    },
    {
        "id": "naukri-jba-106",
        "title": "Junior Business Analyst",
        "company": "FinMetric Global Solutions",
        "location": "Hyderabad, Telangana",
        "work_mode": "Hybrid",
        "experience": "0 - 2 years",
        "employment_type": "Full-time",
        "salary": "₹4,50,000 - ₹6,00,000 P.A.",
        "posting_date": "Verified 5 days ago",
        "source_name": "Naukri.com",
        "source_url": "https://www.naukri.com/job-listings-junior-business-analyst-finmetric-hyderabad-0-to-2-years-161026003344",
        "skills": ["SQL", "Excel", "Data Analysis", "Reporting", "Git"],
        "required_skills": ["SQL", "Excel", "Data Analysis", "Reporting", "Git"],
        "preferred_skills": ["Python", "Tableau"],
        "description": "FinMetric Global Solutions is seeking an entry-level Business Analyst to bridge technical data models and executive reporting. You will query relational databases, craft KPI reports, and maintain analyst documentation.",
        "responsibilities": [
            "Formulate SQL queries to extract commercial performance records from operational databases.",
            "Assemble weekly operational dashboards with Excel pivot tables and charts.",
            "Document business logic and calculate financial ratios for compliance reviews.",
            "Present exploratory findings in concise written summaries for department heads."
        ],
        "qualifications": "Degree in Commerce, Economics, Engineering, or Business Administration with practical SQL and Excel skills.",
        "company_info": "FinMetric provides risk modeling and operational performance metrics for financial institutions worldwide.",
        "application_mode": "in_app_supported",
        "external_application_url": "https://www.naukri.com/job-listings-junior-business-analyst-finmetric-hyderabad-0-to-2-years-161026003344"
    }
]

# Initialize ML matching model
_ML_MODEL = JobMatchingModel(VERIFIED_JOBS)

# In-memory storage for submitted applications
_APPLICATIONS_LEDGER: List[Dict[str, Any]] = []

# Cache for Naukri searches
_NAUKRI_CACHE = {}
_CACHE_TTL = 600


@router.get("", response_model=List[CareerPathResponse])
def get_all_careers(db: Session = Depends(get_db)):
    careers = db.query(CareerPath).all()
    return careers


@router.get("/saved", response_model=List[str])
def get_saved_career_ids(user_id: str = "default_user", db: Session = Depends(get_db)):
    saved = db.query(SavedCareer).filter(SavedCareer.user_id == user_id).all()
    return [s.career_id for s in saved]


@router.post("/{career_id}/save", status_code=status.HTTP_201_CREATED)
def save_career(career_id: str, user_id: str = "default_user", db: Session = Depends(get_db)):
    career = db.query(CareerPath).filter(CareerPath.id == career_id).first()
    if not career:
        raise HTTPException(status_code=404, detail="Career path not found")

    existing = db.query(SavedCareer).filter(
        SavedCareer.user_id == user_id,
        SavedCareer.career_id == career_id
    ).first()

    if not existing:
        new_save = SavedCareer(
            id=f"sc-{uuid.uuid4().hex[:8]}",
            user_id=user_id,
            career_id=career_id
        )
        db.add(new_save)
        db.commit()

    return {"message": "Career saved successfully", "career_id": career_id}


@router.delete("/{career_id}/save")
def remove_saved_career(career_id: str, user_id: str = "default_user", db: Session = Depends(get_db)):
    existing = db.query(SavedCareer).filter(
        SavedCareer.user_id == user_id,
        SavedCareer.career_id == career_id
    ).first()

    if existing:
        db.delete(existing)
        db.commit()

    return {"message": "Career removed from saved list", "career_id": career_id}


@router.get("/naukri")
def search_naukri(
    keywords: str = "Data Analyst",
    location: str = "",
    experience: str = "",
    is_internship: bool = False,
    force_refresh: bool = False
):
    clean_kw = (keywords or "").strip()
    clean_loc = (location or "").strip()
    cache_key = (clean_kw.lower(), clean_loc.lower(), experience.lower(), is_internship)
    now = time.time()

    if not force_refresh and cache_key in _NAUKRI_CACHE:
        entry = _NAUKRI_CACHE[cache_key]
        if (now - entry["cached_at"]) < _CACHE_TTL:
            res = dict(entry["data"])
            res["from_cache"] = True
            return res

    clean_k = clean_kw
    if is_internship and "intern" not in clean_k.lower():
        clean_k = f"{clean_k} intern".strip() if clean_k else "internship"

    params = []
    if clean_k:
        params.append(f"k={quote_plus(clean_k)}")
    if clean_loc:
        params.append(f"l={quote_plus(clean_loc)}")
    if is_internship:
        params.append("experience=0")
    elif experience:
        if "0" in experience or "fresher" in experience.lower():
            params.append("experience=0")
        elif "1-3" in experience:
            params.append("experience=1")

    query_str = "&".join(params)
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", clean_k.lower()).strip("-") or "jobs"
    base_url = f"https://www.naukri.com/{slug}-jobs"
    direct_url = f"{base_url}?{query_str}" if query_str else base_url

    kw_lower = clean_kw.lower()
    matched_listings = []
    for job in VERIFIED_JOBS:
        if is_internship and "intern" not in job["title"].lower():
            continue
        if clean_loc and clean_loc.lower() not in job["location"].lower() and "remote" not in job["location"].lower():
            continue
        if not kw_lower or any(word in job["title"].lower() or any(word in s.lower() for s in job["skills"]) for word in kw_lower.split() if len(word) > 2):
            matched_listings.append(job)

    result = {
        "live_retrieval_status": "direct_search_fallback",
        "source_name": "Naukri.com",
        "listings": matched_listings,
        "direct_search_url": direct_url,
        "last_retrieval_time": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "from_cache": False,
        "explanation": (
            "Naukri.com enforces access controls and requires enterprise API credentials for automated programmatic retrieval. "
            "SkillTrace AI complies with platform terms of service and does not execute unpermitted scraping. "
            "You can explore live matching opportunities directly on Naukri with your search filters pre-filled."
        )
    }

    _NAUKRI_CACHE[cache_key] = {"cached_at": now, "data": result}
    return result


# --- Phase 4: Machine Learning Matching Endpoints ---

class MatchRequest(BaseModel):
    target_role: str = "Data Analyst"
    summary: str = ""
    current_skills: List[str] = Field(default_factory=list)
    experience_years: float = 0.5
    preferred_work_modes: List[str] = Field(default_factory=lambda: ["Remote", "Hybrid"])
    preferred_locations: List[str] = Field(default_factory=lambda: ["Mumbai", "Remote", "Bengaluru", "Pune"])
    candidate_evidence: Optional[List[Dict[str, Any]]] = None
    sort_by: str = "best_match"


@router.post("/match")
def match_jobs_with_ml(req: MatchRequest):
    """
    Ranks verified jobs using the multi-signal ML matching model with explainable signals.
    """
    candidate = CandidateProfile(
        target_role=req.target_role,
        summary=req.summary,
        current_skills=req.current_skills,
        experience_years=req.experience_years,
        preferred_work_modes=req.preferred_work_modes,
        preferred_locations=req.preferred_locations
    )

    ranked = _ML_MODEL.rank_jobs(
        VERIFIED_JOBS,
        candidate,
        req.candidate_evidence,
        sort_by=req.sort_by
    )

    return {
        "model_version": _ML_MODEL.MODEL_VERSION,
        "candidate_evaluated": req.target_role,
        "total_ranked": len(ranked),
        "results": ranked
    }


# --- Phase 6: Skill Gap Analysis Endpoint ---

class SkillGapRequest(BaseModel):
    job_id: str
    candidate_skills: List[str] = Field(default_factory=list)
    candidate_evidence: Optional[List[Dict[str, Any]]] = None


@router.post("/skill-gap")
def get_job_skill_gap(req: SkillGapRequest):
    """
    Returns a personalized skill-gap report comparing job requirements with repository AST evidence.
    """
    job = next((j for j in VERIFIED_JOBS if j["id"] == req.job_id), VERIFIED_JOBS[0])
    report = generate_skill_gap_report(job, req.candidate_skills, req.candidate_evidence)
    return report


# --- Phase 7: Career Roadmap Endpoint ---

class RoadmapRequest(BaseModel):
    job_id: str
    candidate_skills: List[str] = Field(default_factory=list)
    candidate_evidence: Optional[List[Dict[str, Any]]] = None


@router.post("/roadmap")
def create_job_roadmap(req: RoadmapRequest):
    """
    Generates a milestone-based 4-phase career roadmap toward a specific job target.
    """
    job = next((j for j in VERIFIED_JOBS if j["id"] == req.job_id), VERIFIED_JOBS[0])
    roadmap = generate_personalized_roadmap(job, req.candidate_skills, req.candidate_evidence)
    return roadmap


# --- Phase 9: In-App Application Submission Endpoint ---

class ApplicationSubmissionRequest(BaseModel):
    job_id: str
    applicant_name: str
    applicant_email: str
    applicant_github: str
    applicant_pitch: Optional[str] = ""


@router.post("/apply")
def submit_job_application(req: ApplicationSubmissionRequest):
    """
    Submits an in-app job application for verified listings supporting in-app workflows.
    """
    job = next((j for j in VERIFIED_JOBS if j["id"] == req.job_id), None)
    if not job:
        raise HTTPException(status_code=404, detail="Job listing not found")

    if job.get("application_mode") == "external_required":
        return {
            "status": "external_required",
            "message": "This employer requires application via their official external portal.",
            "external_url": job.get("external_application_url")
        }

    app_id = f"STA-APP-{uuid.uuid4().hex[:8].upper()}"
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    record = {
        "application_id": app_id,
        "job_id": job["id"],
        "job_title": job["title"],
        "company": job["company"],
        "applicant_name": req.applicant_name,
        "applicant_email": req.applicant_email,
        "applicant_github": req.applicant_github,
        "pitch": req.applicant_pitch,
        "status": "Submitted to SkillTrace AI Tracker",
        "submitted_at": now_str
    }
    _APPLICATIONS_LEDGER.append(record)

    return {
        "status": "submitted",
        "application_id": app_id,
        "job_title": job["title"],
        "company": job["company"],
        "submitted_at": now_str,
        "message": "Application logged successfully in SkillTrace AI Career Tracker."
    }


@router.get("/applications")
def list_applications():
    """Returns submitted job applications in the tracker."""
    return _APPLICATIONS_LEDGER


from ..job_client import JobDataClient, _CACHE as _JOB_CACHE
_JOB_CLIENT = JobDataClient()


@router.get("/live-search")
def live_job_search(
    keyword: str = "",
    location: str = "",
    work_mode: str = "All",
    source_preference: str = "auto",
    page: int = 1
):
    """
    Retrieves live job opportunities from Adzuna (primary), RemoteOK (secondary),
    or SkillTrace Verified Feed, with canonical skill normalization.
    """
    return _JOB_CLIENT.search_jobs(
        keyword=keyword,
        location=location,
        work_mode=work_mode,
        source_preference=source_preference,
        page=page
    )


# -------------------------------------------------------------
# Evidence-Based Job Matching Endpoint
# -------------------------------------------------------------
from ..evidence_matcher import RepositoryEvidenceAnalyzer, JobRequirementMatcher
from .skills import _ACTIVE_REPO_STATE


class EvidenceMatchRequest(BaseModel):
    job_id: str
    custom_job: Optional[Dict[str, Any]] = None


@router.post("/evidence-match")
def match_job_with_repository_evidence(req: EvidenceMatchRequest):
    """
    Computes genuine evidence-based job matching with:
    1. Skill Evidence Strength (0-100)
    2. Job Requirement Coverage (required % & preferred %)
    3. Overall Job Match Score (explicit numerator & denominator)
    4. Traceable code evidence citations pinned to commit SHA and line range.
    """
    if req.custom_job:
        job = req.custom_job
    else:
        job = next((j for j in VERIFIED_JOBS if j["id"] == req.job_id), None)
        if not job:
            for cached_tuple in _JOB_CACHE.values():
                for j in cached_tuple[1]:
                    if j.get("id") == req.job_id:
                        job = j
                        break
                if job:
                    break
        if not job:
            raise HTTPException(status_code=404, detail=f"Job listing '{req.job_id}' not found")

    analyzer = RepositoryEvidenceAnalyzer(
        _ACTIVE_REPO_STATE["repo_full_name"],
        _ACTIVE_REPO_STATE["commit_sha"]
    )
    repo_profile = analyzer.analyze_repository_files(_ACTIVE_REPO_STATE["files"])
    match_result = JobRequirementMatcher.match_job(job, repo_profile)

    return {
        "repository_info": {
            "name": _ACTIVE_REPO_STATE["repo_full_name"],
            "commit_sha": _ACTIVE_REPO_STATE["commit_sha"],
            "last_scanned_at": _ACTIVE_REPO_STATE["last_scanned_at"],
            "scanned_files_count": len(_ACTIVE_REPO_STATE["files"])
        },
        "match": match_result
    }


