"""
SkillTrace AI — Career Roadmap & Skill Gap Intelligence Engine.
Generates:
1. Personalized Skill-Gap Reports tailored to specific job specifications and candidate AST evidence
2. Verifiable Actionable Project Recommendations
3. 4-Phase Step-by-Step Milestones Roadmap with progress persistence
"""

from __future__ import annotations
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone


SKILL_RECOMMENDATION_TEMPLATES = {
    "sql": {
        "title": "Production SQL Analysis Project",
        "description": "Construct a multi-table relational schema with transactions. Implement window functions (ROW_NUMBER, DENSE_RANK, LAG/LEAD) and aggregation queries in PostgreSQL or SQLite.",
        "deliverable": "A GitHub repository with schema migrations, SQL query scripts, and sample output CSVs.",
        "resource": "https://mode.com/sql-tutorial/",
        "estimated_hours": 12
    },
    "pandas": {
        "title": "Automated Data Ingestion & Cleansing Pipeline",
        "description": "Build an ETL script using Python & Pandas that parses messy raw datasets, handles nulls, normalizes date formats, and computes rolling statistical summaries.",
        "deliverable": "A Python module with clean functions, type hints, and an exploratory notebook.",
        "resource": "https://pandas.pydata.org/docs/user_guide/index.html",
        "estimated_hours": 10
    },
    "python": {
        "title": "Modular Python Application with CLI & Logging",
        "description": "Write a clean object-oriented Python program following PEP8 standards, structured directory layouts, and structured logging.",
        "deliverable": "GitHub repository with requirements.txt, pyproject.toml, and clean commit history.",
        "resource": "https://docs.python.org/3/tutorial/",
        "estimated_hours": 14
    },
    "fastapi": {
        "title": "RESTful API Microservice with FastAPI",
        "description": "Architect a REST service with Pydantic request validation, dependency injection, SQLite/SQLAlchemy ORM integration, and Swagger documentation.",
        "deliverable": "A FastAPI service with modular routers and OpenAPI documentation.",
        "resource": "https://fastapi.tiangolo.com/tutorial/",
        "estimated_hours": 15
    },
    "testing": {
        "title": "Automated Unit & Integration Test Suite",
        "description": "Implement a test suite using pytest with parameterized test cases, mock fixtures, and edge condition verifications.",
        "deliverable": "A tests/ directory containing unit tests passing with pytest -v.",
        "resource": "https://docs.pytest.org/en/stable/",
        "estimated_hours": 8
    },
    "git": {
        "title": "Structured Git Feature Branch Workflow",
        "description": "Practice conventional commit messages, feature branches, pull request descriptions, and merge workflows on GitHub.",
        "deliverable": "A GitHub repository with a transparent commit tree and merged PRs.",
        "resource": "https://git-scm.com/doc",
        "estimated_hours": 6
    },
    "data visualization": {
        "title": "Executive Business Metric Dashboard",
        "description": "Design clear exploratory charts with Matplotlib/Seaborn and interactive summary views for departmental KPIs.",
        "deliverable": "Clean charts exported as PNGs with an analytical summary markdown report.",
        "resource": "https://seaborn.pydata.org/tutorial.html",
        "estimated_hours": 8
    }
}


def generate_skill_gap_report(
    job: Dict[str, Any],
    candidate_skills: List[str],
    candidate_evidence: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Generates a rigorous skill-gap report comparing job requirements with candidate evidence.
    Categorizes skills strictly without claiming missing evidence proves incompetence.
    """
    required_skills = job.get("required_skills", job.get("skills", []))
    evidence_by_skill: Dict[str, List[Dict[str, Any]]] = {}
    for ev in (candidate_evidence or []):
        cat = ev.get("skill_category") if isinstance(ev, dict) else getattr(ev, "skill_category", None)
        if cat:
            evidence_by_skill.setdefault(cat.lower(), []).append(ev)

    cand_skills_lower = {s.lower() for s in candidate_skills}

    demonstrated = []
    partial = []
    not_demonstrated = []
    recommendations = []

    for s in required_skills:
        s_lower = s.lower()
        citations = evidence_by_skill.get(s_lower, [])

        if len(citations) >= 2:
            demonstrated.append({
                "skill": s,
                "status": "Demonstrated",
                "evidence_type": "Repository AST Code Citations",
                "citations": citations[:2],
                "note": f"Verified with {len(citations)} code citations in repository scope."
            })
        elif len(citations) == 1:
            partial.append({
                "skill": s,
                "status": "Partially demonstrated",
                "evidence_type": "Single Code Citation",
                "citations": citations,
                "note": "1 verifiable citation found. Additional repository references recommended for full verification."
            })
            tmpl = SKILL_RECOMMENDATION_TEMPLATES.get(s_lower)
            if tmpl:
                recommendations.append({"skill": s, "priority": "High", **tmpl})
        elif s_lower in cand_skills_lower:
            demonstrated.append({
                "skill": s,
                "status": "Demonstrated",
                "evidence_type": "Profile Skill",
                "citations": [],
                "note": "Demonstrated in candidate profile skills."
            })
        else:
            not_demonstrated.append({
                "skill": s,
                "status": "Not demonstrated in analysed scope",
                "evidence_type": "No Repository Evidence Found",
                "citations": [],
                "note": "Not demonstrated in analysed scope (does not imply lack of skill)."
            })
            tmpl = SKILL_RECOMMENDATION_TEMPLATES.get(s_lower, {
                "title": f"Hands-on {s} Practice Project",
                "description": f"Build a practical demonstration project showcasing core {s} fundamentals.",
                "deliverable": f"GitHub repository containing functional {s} code.",
                "resource": "https://developer.mozilla.org/ or official docs",
                "estimated_hours": 10
            })
            recommendations.append({"skill": s, "priority": "Medium", **tmpl})

    return {
        "job_id": job.get("id", "custom-job"),
        "job_title": job.get("title", "Target Role"),
        "company": job.get("company", "Target Employer"),
        "evaluated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "demonstrated_skills": demonstrated,
        "partial_skills": partial,
        "not_demonstrated_skills": not_demonstrated,
        "actionable_recommendations": recommendations,
        "summary": {
            "total_required": len(required_skills),
            "demonstrated_count": len(demonstrated),
            "partial_count": len(partial),
            "not_demonstrated_count": len(not_demonstrated)
        },
        "disclaimer": "SkillTrace AI assesses skills strictly within analysed repository scope. Absence of evidence does not indicate absence of skill."
    }


def generate_personalized_roadmap(
    job: Dict[str, Any],
    candidate_skills: List[str],
    candidate_evidence: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Builds a milestone-driven, 4-phase personal career roadmap for the user toward a specific target role.
    """
    gap_report = generate_skill_gap_report(job, candidate_skills, candidate_evidence)
    role_title = job.get("title", "Data Analyst")

    # Phase 1: Skill Gap Remediation
    phase1_tasks = []
    for rec in gap_report["actionable_recommendations"][:2]:
        phase1_tasks.append({
            "id": f"task-p1-{rec['skill'].lower()}",
            "title": rec["title"],
            "skill": rec["skill"],
            "description": rec["description"],
            "estimated_hours": rec["estimated_hours"],
            "status": "not_started",
            "resource_url": rec["resource"]
        })
    if not phase1_tasks:
        phase1_tasks.append({
            "id": "task-p1-refine",
            "title": f"Advanced Code Review for {role_title}",
            "skill": "Code Quality",
            "description": "Refactor existing repository code to add comprehensive type hints and automated testing.",
            "estimated_hours": 6,
            "status": "not_started",
            "resource_url": "https://peps.python.org/pep-0008/"
        })

    # Phase 2: Domain Project
    phase2_tasks = [{
        "id": "task-p2-project",
        "title": f"End-to-End {role_title} Showcase Application",
        "skill": "Applied Engineering",
        "description": f"Design and implement a realistic end-to-end project aligning with {job.get('company', 'target company')} responsibilities: {job.get('responsibilities', ['Build data pipelines'])[0]}",
        "estimated_hours": 16,
        "status": "not_started",
        "resource_url": "https://github.com"
    }]

    # Phase 3: Repository Proof & Testing
    phase3_tasks = [{
        "id": "task-p3-testing",
        "title": "Automated Unit Tests & Code Hygiene",
        "skill": "Testing & QA",
        "description": "Equip your showcase project with automated pytest suites, test fixtures, and continuous integration checks.",
        "estimated_hours": 8,
        "status": "not_started",
        "resource_url": "https://docs.pytest.org"
    }]

    # Phase 4: Portfolio Packaging
    phase4_tasks = [{
        "id": "task-p4-docs",
        "title": "Technical Documentation & Portfolio Presentation",
        "skill": "Technical Communication",
        "description": "Craft an architectural README with architecture diagrams, setup instructions, and verifiable line citations.",
        "estimated_hours": 4,
        "status": "not_started",
        "resource_url": "https://skilltrace.ai"
    }]

    phases = [
        {"phase_id": 1, "phase_name": "Phase 1: Remediation of Priority Skill Gaps", "focus": "Bridge identified requirements", "tasks": phase1_tasks},
        {"phase_id": 2, "phase_name": "Phase 2: Showcase Portfolio Project", "focus": "Demonstrate real-world application", "tasks": phase2_tasks},
        {"phase_id": 3, "phase_name": "Phase 3: Repository Verification & Testing", "focus": "Verify evidence citations", "tasks": phase3_tasks},
        {"phase_id": 4, "phase_name": "Phase 4: Application Preparation", "focus": "Packaging & In-App Application", "tasks": phase4_tasks}
    ]

    return {
        "roadmap_id": f"rdm-{job.get('id', 'custom')}-{int(datetime.now().timestamp())}",
        "target_role": role_title,
        "target_company": job.get("company", "Target Employer"),
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "gap_summary": gap_report["summary"],
        "phases": phases,
        "total_estimated_hours": sum(t["estimated_hours"] for p in phases for t in p["tasks"])
    }
