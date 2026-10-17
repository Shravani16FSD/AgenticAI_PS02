"""
SkillProof Arena Router.
Provides evidence-based diagnostic assessments, in-browser practical mini-project evaluation,
isolated Python sandbox test runner, and adaptive challenge progression.
"""

import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import (
    UserProfile,
    DiagnosticAssessment,
    DiagnosticAttempt,
    MiniProjectDefinition,
    ProjectSubmission,
    SkillMasteryRecord,
    UserSkill
)
from ..auth import get_authenticated_user
from ..services.sandbox_service import sandbox_service
from ..services.adaptive_engine import adaptive_engine

router = APIRouter(prefix="/api/arena", tags=["SkillProof Arena"])


# -------------------------------------------------------------
# Request & Response Schemas
# -------------------------------------------------------------
class DiagnosticSubmitRequest(BaseModel):
    answers: Dict[str, str] = Field(..., description="Map of question_id to user's selected/typed answer")


class ProjectRunRequest(BaseModel):
    code: str = Field(..., description="Python source code to test in isolated sandbox")


class ProjectSubmitRequest(BaseModel):
    code: str = Field(..., description="Python source code to evaluate")
    hints_used: int = Field(default=0, ge=0, le=10, description="Count of progressive hints unlocked")


# -------------------------------------------------------------
# Endpoints
# -------------------------------------------------------------
@router.get("/catalog")
def get_arena_catalog(
    career_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Returns available diagnostic assessments and practical mini-projects.
    Hides answers and hidden test suites from the catalog list.
    """
    diag_query = db.query(DiagnosticAssessment)
    proj_query = db.query(MiniProjectDefinition)

    if career_id:
        diag_query = diag_query.filter(DiagnosticAssessment.career_id == career_id)
        proj_query = proj_query.filter(MiniProjectDefinition.career_id == career_id)

    diagnostics = diag_query.all()
    projects = proj_query.all()

    return {
        "diagnostics": [
            {
                "id": d.id,
                "career_id": d.career_id,
                "skill_name": d.skill_name,
                "title": d.title,
                "difficulty": d.difficulty,
                "time_limit_mins": d.time_limit_mins,
                "question_count": len(d.questions or [])
            }
            for d in diagnostics
        ],
        "projects": [
            {
                "id": p.id,
                "career_id": p.career_id,
                "skill_name": p.skill_name,
                "difficulty": p.difficulty,
                "title": p.title,
                "tagline": p.tagline,
                "public_tests_count": len(p.public_test_cases or []),
                "hints_count": len(p.hints or [])
            }
            for p in projects
        ]
    }


@router.get("/diagnostic/{assessment_id}")
def get_diagnostic_assessment(
    assessment_id: str,
    db: Session = Depends(get_db)
):
    """
    Retrieves an assessment with its question papers.
    Strictly sanitizes questions to omit correct answers and backend explanations.
    """
    diag = db.query(DiagnosticAssessment).filter(DiagnosticAssessment.id == assessment_id).first()
    if not diag:
        raise HTTPException(status_code=404, detail=f"Diagnostic assessment '{assessment_id}' not found.")

    sanitized_questions = []
    for q in (diag.questions or []):
        sanitized_questions.append({
            "id": q.get("id"),
            "type": q.get("type", "mcq"),
            "text": q.get("text"),
            "options": q.get("options", []),
            "skill_tag": q.get("skill_tag", diag.skill_name)
        })

    return {
        "id": diag.id,
        "career_id": diag.career_id,
        "skill_name": diag.skill_name,
        "title": diag.title,
        "difficulty": diag.difficulty,
        "time_limit_mins": diag.time_limit_mins,
        "questions": sanitized_questions
    }


@router.post("/diagnostic/{assessment_id}/submit")
def submit_diagnostic_assessment(
    assessment_id: str,
    req: DiagnosticSubmitRequest,
    current_user: UserProfile = Depends(get_authenticated_user),
    db: Session = Depends(get_db)
):
    """
    Objectively scores diagnostic questions, records question-level outcomes,
    determines strengths and weaknesses, updates skill mastery, and persists the attempt.
    """
    diag = db.query(DiagnosticAssessment).filter(DiagnosticAssessment.id == assessment_id).first()
    if not diag:
        raise HTTPException(status_code=404, detail="Diagnostic assessment not found.")

    questions = diag.questions or []
    total_q = len(questions)
    if total_q == 0:
        raise HTTPException(status_code=400, detail="Diagnostic assessment has no configured questions.")

    correct_count = 0
    question_results = []
    strengths = []
    weaknesses = []

    for q in questions:
        q_id = q.get("id")
        user_ans = (req.answers.get(q_id) or "").strip()
        correct_ans = (q.get("correct_answer") or "").strip()
        skill_tag = q.get("skill_tag") or diag.skill_name

        # Case-insensitive whitespace-normalized comparison
        is_correct = False
        if q.get("type") == "short_answer":
            is_correct = user_ans.lower() == correct_ans.lower()
        else:
            is_correct = user_ans.lower() == correct_ans.lower()

        if is_correct:
            correct_count += 1
            if skill_tag not in strengths:
                strengths.append(skill_tag)
        else:
            if skill_tag not in weaknesses:
                weaknesses.append(skill_tag)

        question_results.append({
            "question_id": q_id,
            "question_text": q.get("text"),
            "user_answer": user_ans,
            "correct_answer": correct_ans,
            "is_correct": is_correct,
            "explanation": q.get("explanation", "")
        })

    score = round((correct_count / total_q) * 100.0, 1)
    passed = score >= 70.0

    confidence = "high" if score >= 80.0 else ("moderate" if score >= 50.0 else "low")

    attempt = DiagnosticAttempt(
        id=f"attempt-{uuid.uuid4().hex[:10]}",
        user_id=current_user.id,
        assessment_id=diag.id,
        career_id=diag.career_id,
        skill_name=diag.skill_name,
        difficulty=diag.difficulty,
        score=score,
        passed=passed,
        total_questions=total_q,
        correct_count=correct_count,
        strengths=strengths,
        weaknesses=weaknesses,
        question_results=question_results,
        confidence_level=confidence,
        created_at=datetime.utcnow()
    )
    db.add(attempt)

    # Update or create SkillMasteryRecord
    mastery = db.query(SkillMasteryRecord).filter(
        SkillMasteryRecord.user_id == current_user.id,
        SkillMasteryRecord.skill_name == diag.skill_name
    ).first()

    attempts_count = db.query(DiagnosticAttempt).filter(
        DiagnosticAttempt.user_id == current_user.id,
        DiagnosticAttempt.skill_name == diag.skill_name
    ).count() + 1

    practical_score = mastery.practical_score if mastery else None
    mastery_level, mastery_score = adaptive_engine.calculate_skill_mastery(
        diagnostic_score=score,
        practical_score=practical_score,
        attempts_count=attempts_count
    )

    if mastery:
        mastery.diagnostic_score = score
        mastery.mastery_score = mastery_score
        mastery.mastery_level = mastery_level
        mastery.evidence_count += 1
        mastery.last_evidence_at = datetime.utcnow()
    else:
        db.add(SkillMasteryRecord(
            id=f"smr-{uuid.uuid4().hex[:8]}",
            user_id=current_user.id,
            skill_name=diag.skill_name,
            category="Programming",
            mastery_level=mastery_level,
            mastery_score=mastery_score,
            diagnostic_score=score,
            practical_score=None,
            evidence_count=1,
            last_evidence_at=datetime.utcnow()
        ))

    db.commit()

    return {
        "attempt_id": attempt.id,
        "score": score,
        "passed": passed,
        "correct_count": correct_count,
        "total_questions": total_q,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "confidence_level": confidence,
        "question_results": question_results
    }


@router.get("/project/{project_id}")
def get_project_definition(
    project_id: str,
    db: Session = Depends(get_db)
):
    """
    Returns workspace instructions, starter code, sample data, progressive hints,
    and public test cases. Hides hidden trusted assertions.
    """
    proj = db.query(MiniProjectDefinition).filter(MiniProjectDefinition.id == project_id).first()
    if not proj:
        raise HTTPException(status_code=404, detail=f"Project '{project_id}' not found.")

    return {
        "id": proj.id,
        "career_id": proj.career_id,
        "skill_name": proj.skill_name,
        "difficulty": proj.difficulty,
        "title": proj.title,
        "tagline": proj.tagline,
        "description": proj.description,
        "starter_code": proj.starter_code,
        "sample_data": proj.sample_data,
        "hints": proj.hints or [],
        "rubric": proj.rubric or [],
        "public_test_cases": proj.public_test_cases or []
    }


@router.post("/project/{project_id}/run")
def run_project_test(
    project_id: str,
    req: ProjectRunRequest,
    current_user: UserProfile = Depends(get_authenticated_user),
    db: Session = Depends(get_db)
):
    """
    Executes user's code against public test cases inside the isolated sandbox runtime.
    Does not persist an official submission.
    """
    proj = db.query(MiniProjectDefinition).filter(MiniProjectDefinition.id == project_id).first()
    if not proj:
        raise HTTPException(status_code=404, detail="Project definition not found.")

    public_tests = proj.public_test_cases or []
    result = sandbox_service.run_tests(
        code=req.code,
        test_cases=public_tests,
        sample_data=proj.sample_data,
        is_dry_run=True
    )
    return result


@router.post("/project/{project_id}/submit")
def submit_project(
    project_id: str,
    req: ProjectSubmitRequest,
    current_user: UserProfile = Depends(get_authenticated_user),
    db: Session = Depends(get_db)
):
    """
    Submits user's project solution for full evaluation:
    1. Executes against public and hidden test cases in sandbox
    2. Evaluates code with objective rubrics and AST inspection
    3. Persists ProjectSubmission record
    4. Updates SkillMasteryRecord
    5. Calculates next adaptive challenge
    """
    proj = db.query(MiniProjectDefinition).filter(MiniProjectDefinition.id == project_id).first()
    if not proj:
        raise HTTPException(status_code=404, detail="Project definition not found.")

    all_tests = list(proj.public_test_cases or []) + list(proj.hidden_test_cases or [])
    sandbox_res = sandbox_service.run_tests(
        code=req.code,
        test_cases=all_tests,
        sample_data=proj.sample_data,
        is_dry_run=False
    )

    eval_result = adaptive_engine.evaluate_project(
        code=req.code,
        project=proj,
        sandbox_res=sandbox_res,
        hints_used=req.hints_used
    )

    # Sanitize hidden test cases from client response
    client_test_results = []
    for idx, t_res in enumerate(sandbox_res.get("test_results", [])):
        is_hidden = idx >= len(proj.public_test_cases or [])
        client_test_results.append({
            "name": f"Hidden Validation #{idx + 1}" if is_hidden else t_res.get("name"),
            "passed": t_res.get("passed", False),
            "actual": t_res.get("actual"),
            "expected": t_res.get("expected") if not is_hidden else "(Hidden expectation)",
            "error": t_res.get("error"),
            "execution_time_ms": t_res.get("execution_time_ms", 0.0),
            "is_hidden": is_hidden
        })

    submission = ProjectSubmission(
        id=f"sub-{uuid.uuid4().hex[:10]}",
        user_id=current_user.id,
        project_id=proj.id,
        career_id=proj.career_id,
        skill_name=proj.skill_name,
        submitted_code=req.code,
        status=eval_result["status"],
        score=eval_result["composite_score"],
        tests_passed=sandbox_res.get("tests_passed", 0),
        tests_total=sandbox_res.get("tests_total", len(all_tests)),
        test_results=client_test_results,
        rubric_evaluation=eval_result["rubric_evaluation"],
        feedback=eval_result["feedback"],
        hints_used=req.hints_used,
        execution_output=sandbox_res.get("output", ""),
        error_output=sandbox_res.get("error", ""),
        execution_time_ms=sandbox_res.get("execution_time_ms", 0.0),
        created_at=datetime.utcnow()
    )
    db.add(submission)

    # Update SkillMasteryRecord
    mastery = db.query(SkillMasteryRecord).filter(
        SkillMasteryRecord.user_id == current_user.id,
        SkillMasteryRecord.skill_name == proj.skill_name
    ).first()

    attempts_count = db.query(ProjectSubmission).filter(
        ProjectSubmission.user_id == current_user.id,
        ProjectSubmission.skill_name == proj.skill_name
    ).count() + 1

    diagnostic_score = mastery.diagnostic_score if mastery else None
    mastery_level, mastery_score = adaptive_engine.calculate_skill_mastery(
        diagnostic_score=diagnostic_score,
        practical_score=eval_result["composite_score"],
        attempts_count=attempts_count
    )

    if mastery:
        mastery.practical_score = eval_result["composite_score"]
        mastery.mastery_score = mastery_score
        mastery.mastery_level = mastery_level
        mastery.evidence_count += 1
        mastery.last_evidence_at = datetime.utcnow()
    else:
        db.add(SkillMasteryRecord(
            id=f"smr-{uuid.uuid4().hex[:8]}",
            user_id=current_user.id,
            skill_name=proj.skill_name,
            category="Programming",
            mastery_level=mastery_level,
            mastery_score=mastery_score,
            diagnostic_score=None,
            practical_score=eval_result["composite_score"],
            evidence_count=1,
            last_evidence_at=datetime.utcnow()
        ))

    db.commit()

    # Calculate next adaptive challenge
    diag_history = db.query(DiagnosticAttempt).filter(DiagnosticAttempt.user_id == current_user.id).order_by(DiagnosticAttempt.created_at.desc()).all()
    proj_history = db.query(ProjectSubmission).filter(ProjectSubmission.user_id == current_user.id).order_by(ProjectSubmission.created_at.desc()).all()
    all_diags = db.query(DiagnosticAssessment).all()
    all_projs = db.query(MiniProjectDefinition).all()

    adaptive_rec = adaptive_engine.determine_adaptive_challenge(
        user_id=current_user.id,
        career_id=proj.career_id,
        skill_name=proj.skill_name,
        diagnostic_attempts=diag_history,
        project_submissions=proj_history,
        available_assessments=all_diags,
        available_projects=all_projs
    )

    return {
        "submission_id": submission.id,
        "status": submission.status,
        "score": submission.score,
        "tests_passed": submission.tests_passed,
        "tests_total": submission.tests_total,
        "test_results": client_test_results,
        "rubric_evaluation": submission.rubric_evaluation,
        "feedback": submission.feedback,
        "execution_output": submission.execution_output,
        "execution_time_ms": submission.execution_time_ms,
        "adaptive_next_challenge": adaptive_rec
    }


@router.get("/dashboard")
def get_arena_dashboard(
    current_user: UserProfile = Depends(get_authenticated_user),
    db: Session = Depends(get_db)
):
    """
    Returns full evidence-based dashboard:
    - Diagnostic attempts history
    - Project submissions history
    - Demonstrated skills vs skills needing practice
    - Skill mastery records with verified score and evidence levels
    - Adaptive next challenge recommendation
    - Secondary study time hours
    """
    diag_history = db.query(DiagnosticAttempt).filter(
        DiagnosticAttempt.user_id == current_user.id
    ).order_by(DiagnosticAttempt.created_at.desc()).all()

    proj_history = db.query(ProjectSubmission).filter(
        ProjectSubmission.user_id == current_user.id
    ).order_by(ProjectSubmission.created_at.desc()).all()

    mastery_records = db.query(SkillMasteryRecord).filter(
        SkillMasteryRecord.user_id == current_user.id
    ).order_by(SkillMasteryRecord.mastery_score.desc()).all()

    all_diags = db.query(DiagnosticAssessment).all()
    all_projs = db.query(MiniProjectDefinition).all()

    # Aggregate demonstrated skills and skills needing practice
    demonstrated = set()
    to_practice = set()

    for d in diag_history:
        for s in (d.strengths or []):
            demonstrated.add(s)
        for w in (d.weaknesses or []):
            to_practice.add(w)

    for p in proj_history:
        fb = p.feedback or {}
        for s in fb.get("demonstrated_skills", []):
            demonstrated.add(s)
        for w in fb.get("skills_to_practice", []):
            to_practice.add(w)

    # Calculate secondary study hours
    user_skills = db.query(UserSkill).filter(UserSkill.user_id == current_user.id).all()
    study_hours = sum(s.hours_spent for s in user_skills)

    # Next adaptive recommendation
    target_career = current_user.target_career_id or "ai-product-engineer"
    adaptive_rec = adaptive_engine.determine_adaptive_challenge(
        user_id=current_user.id,
        career_id=target_career,
        skill_name="Python Fundamentals",
        diagnostic_attempts=diag_history,
        project_submissions=proj_history,
        available_assessments=all_diags,
        available_projects=all_projs
    )

    return {
        "user_id": current_user.id,
        "diagnostic_history": [
            {
                "id": d.id,
                "assessment_id": d.assessment_id,
                "skill_name": d.skill_name,
                "difficulty": d.difficulty,
                "score": d.score,
                "passed": d.passed,
                "total_questions": d.total_questions,
                "correct_count": d.correct_count,
                "strengths": d.strengths,
                "weaknesses": d.weaknesses,
                "confidence_level": d.confidence_level,
                "created_at": d.created_at.isoformat() if d.created_at else None
            }
            for d in diag_history
        ],
        "project_history": [
            {
                "id": p.id,
                "project_id": p.project_id,
                "skill_name": p.skill_name,
                "status": p.status,
                "score": p.score,
                "tests_passed": p.tests_passed,
                "tests_total": p.tests_total,
                "hints_used": p.hints_used,
                "feedback_summary": (p.feedback or {}).get("summary"),
                "created_at": p.created_at.isoformat() if p.created_at else None
            }
            for p in proj_history
        ],
        "demonstrated_skills": sorted(list(demonstrated)),
        "skills_to_practice": sorted(list(to_practice)),
        "mastery_records": [
            {
                "id": m.id,
                "skill_name": m.skill_name,
                "category": m.category,
                "mastery_level": m.mastery_level,
                "mastery_score": m.mastery_score,
                "diagnostic_score": m.diagnostic_score,
                "practical_score": m.practical_score,
                "evidence_count": m.evidence_count,
                "last_evidence_at": m.last_evidence_at.isoformat() if m.last_evidence_at else None
            }
            for m in mastery_records
        ],
        "adaptive_recommendation": adaptive_rec,
        "study_time_hours": study_hours
    }
