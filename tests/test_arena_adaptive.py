"""
End-to-End & Integration Tests for SkillProof Arena:
1. Diagnostic assessment fetching (no answer leak) & submission with objective scoring.
2. Isolated sandbox code runner: execution, syntax errors, failed test feedback, and security blocking.
3. Full practical mini-project evaluation with rubrics and hidden test suites.
4. Adaptive challenge engine: rule-based progression, cross-modality balancing, and weakness targeting.
5. Skill mastery evidence persistence and dashboard aggregation.
6. User authentication isolation (one user cannot access or mutate another's submissions).
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database import SessionLocal
from backend.app.models import (
    UserProfile,
    DiagnosticAssessment,
    DiagnosticAttempt,
    MiniProjectDefinition,
    ProjectSubmission,
    SkillMasteryRecord
)
from backend.app.seed import seed_database
from backend.app.seed_arena import seed_arena_data
from backend.app.services.sandbox_service import sandbox_service
from backend.app.services.adaptive_engine import adaptive_engine

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    db = SessionLocal()
    seed_database(db)
    seed_arena_data(db)
    yield
    db.close()


def test_arena_catalog_and_security_sanitization():
    """Verify catalog exists and diagnostic questions hide correct answers and explanations."""
    res = client.get("/api/arena/catalog")
    assert res.status_code == 200
    data = res.json()
    assert "diagnostics" in data
    assert "projects" in data
    assert len(data["diagnostics"]) >= 2
    assert len(data["projects"]) >= 2

    # Fetch a specific diagnostic
    diag_id = data["diagnostics"][0]["id"]
    res_diag = client.get(f"/api/arena/diagnostic/{diag_id}")
    assert res_diag.status_code == 200
    diag_data = res_diag.json()

    for q in diag_data["questions"]:
        assert "correct_answer" not in q, "Security vulnerability: correct answer leaked in diagnostic API!"
        assert "explanation" not in q, "Security vulnerability: explanation leaked prior to submission!"
        assert "id" in q
        assert "text" in q


def test_diagnostic_submission_and_objective_scoring():
    """Verify diagnostic answers are scored objectively and persist attempt with strengths/weaknesses."""
    submit_payload = {
        "answers": {
            "q1": "O(1) average for set, O(n) for list",
            "q2": "The same list instance is reused across invocations, retaining state across calls.",
            "q3": "functools",
            "q4": "[x**2 for x in data if x % 2 == 0]",
            "q5": "4"
        }
    }

    res = client.post(
        "/api/arena/diagnostic/diag-py-101/submit",
        json=submit_payload,
        headers={"X-User-ID": "default_user"}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["score"] == 100.0
    assert data["passed"] is True
    assert data["correct_count"] == 5
    assert len(data["strengths"]) > 0
    assert len(data["weaknesses"]) == 0

    # Verify results persist in database
    db = SessionLocal()
    attempt = db.query(DiagnosticAttempt).filter(DiagnosticAttempt.id == data["attempt_id"]).first()
    assert attempt is not None
    assert attempt.user_id == "default_user"
    assert attempt.score == 100.0

    # Verify skill mastery record updated
    mastery = db.query(SkillMasteryRecord).filter(
        SkillMasteryRecord.user_id == "default_user",
        SkillMasteryRecord.skill_name == "Python Fundamentals"
    ).first()
    assert mastery is not None
    assert mastery.diagnostic_score == 100.0
    db.close()


def test_sandbox_runner_isolated_and_secure():
    """Verify code runs in isolated sandbox, produces output, catches failures, and blocks dangerous calls."""
    # 1. Valid code
    res_valid = sandbox_service.run_tests(
        code="def solve(a, b):\n    return a * b",
        test_cases=[{"name": "multiply", "function_name": "solve", "args": [4, 5], "expected": 20}]
    )
    assert res_valid["success"] is True
    assert res_valid["score"] == 100.0

    # 2. Failed test case
    res_failed = sandbox_service.run_tests(
        code="def solve(a, b):\n    return a + b",
        test_cases=[{"name": "multiply", "function_name": "solve", "args": [4, 5], "expected": 20}]
    )
    assert res_failed["success"] is False
    assert res_failed["score"] == 0.0
    assert "Expected 20, but got 9" in res_failed["test_results"][0]["error"]

    # 3. Security violation blocked
    res_sec = sandbox_service.run_tests(
        code="import os\nos.system('dir')",
        test_cases=[{"name": "test"}]
    )
    assert res_sec["status"] == "security_violation"
    assert "Disallowed security pattern detected" in res_sec["error"]


def test_project_dry_run_and_submission():
    """Verify live dry-run against public tests and full evaluation against hidden tests."""
    # Fetch project definition
    res_proj = client.get("/api/arena/project/py-data-cleaner-101")
    assert res_proj.status_code == 200
    proj_data = res_proj.json()
    assert "starter_code" in proj_data
    assert "public_test_cases" in proj_data
    assert "hidden_test_cases" not in proj_data, "Hidden tests must not be sent to client!"

    valid_solution = """
def clean_transactions(records: list) -> dict:
    if not isinstance(records, list) or len(records) == 0:
        return {
            'valid_count': 0,
            'total_volume': 0.0,
            'unique_symbols': [],
            'cleaned_records': []
        }

    valid_records = []
    total_volume = 0.0
    symbols = set()

    for item in records:
        if not isinstance(item, dict):
            continue
        trade_id = item.get('trade_id')
        if not trade_id:
            continue
        amount = item.get('amount')
        if amount is None or amount <= 0:
            continue
        status = str(item.get('status', '')).upper()
        if status == 'FAILED':
            continue

        raw_sym = str(item.get('symbol', '')).strip().upper()
        if not raw_sym:
            continue
        raw_curr = str(item.get('currency', 'USD')).strip().upper()

        cleaned_item = {
            'trade_id': str(trade_id),
            'symbol': raw_sym,
            'amount': float(amount),
            'currency': raw_curr,
            'status': status
        }
        valid_records.append(cleaned_item)
        total_volume += float(amount)
        symbols.add(raw_sym)

    sorted_records = sorted(valid_records, key=lambda x: x['trade_id'])
    return {
        'valid_count': len(valid_records),
        'total_volume': round(total_volume, 2),
        'unique_symbols': sorted(list(symbols)),
        'cleaned_records': sorted_records
    }
"""

    # 1. Test Dry Run endpoint
    res_run = client.post(
        "/api/arena/project/py-data-cleaner-101/run",
        json={"code": valid_solution},
        headers={"X-User-ID": "default_user"}
    )
    assert res_run.status_code == 200
    run_data = res_run.json()
    assert run_data["success"] is True
    assert run_data["tests_passed"] == run_data["tests_total"]

    # 2. Test Official Submit endpoint
    res_submit = client.post(
        "/api/arena/project/py-data-cleaner-101/submit",
        json={"code": valid_solution, "hints_used": 1},
        headers={"X-User-ID": "default_user"}
    )
    assert res_submit.status_code == 200
    sub_data = res_submit.json()
    assert sub_data["status"] == "passed"
    assert sub_data["tests_passed"] == sub_data["tests_total"]
    assert sub_data["score"] >= 80.0
    assert "adaptive_next_challenge" in sub_data
    assert len(sub_data["rubric_evaluation"]) >= 3


def test_adaptive_challenge_engine_rules():
    """Verify adaptive engine responds to low, moderate, high, and cross-modality scores."""
    db = SessionLocal()
    diags = db.query(DiagnosticAssessment).all()
    projs = db.query(MiniProjectDefinition).all()

    # Scenario 1: Low score (<40%) -> Guided beginner project
    rec_low = adaptive_engine.determine_adaptive_challenge(
        user_id="default_user",
        career_id="ai-product-engineer",
        skill_name="Python Fundamentals",
        diagnostic_attempts=[
            DiagnosticAttempt(
                id="a1", user_id="default_user", assessment_id="d1",
                career_id="ai-product-engineer", skill_name="Python Fundamentals",
                score=30.0, passed=False
            )
        ],
        project_submissions=[],
        available_assessments=diags,
        available_projects=projs
    )
    assert rec_low["difficulty"] == "beginner"
    assert "foundational gaps" in rec_low["reason"].lower()

    # Scenario 2: Cross-modality (High diagnostic 90%, but weak practical 30%)
    rec_cross = adaptive_engine.determine_adaptive_challenge(
        user_id="default_user",
        career_id="ai-product-engineer",
        skill_name="Python Fundamentals",
        diagnostic_attempts=[
            DiagnosticAttempt(
                id="a1", user_id="default_user", assessment_id="d1",
                career_id="ai-product-engineer", skill_name="Python Fundamentals",
                score=90.0, passed=True
            )
        ],
        project_submissions=[
            ProjectSubmission(
                id="s1", user_id="default_user", project_id="p1",
                career_id="ai-product-engineer", skill_name="Python Fundamentals",
                score=30.0, submitted_code=""
            )
        ],
        available_assessments=diags,
        available_projects=projs
    )
    assert rec_cross["action_type"] == "project"
    assert "practical implementation needs practice" in rec_cross["reason"].lower()

    # Scenario 3: High score (>85%) -> Intermediate or Advanced challenge
    rec_high = adaptive_engine.determine_adaptive_challenge(
        user_id="default_user",
        career_id="ai-product-engineer",
        skill_name="Python Fundamentals",
        diagnostic_attempts=[
            DiagnosticAttempt(
                id="a1", user_id="default_user", assessment_id="d1",
                career_id="ai-product-engineer", skill_name="Python Fundamentals",
                score=95.0, passed=True
            )
        ],
        project_submissions=[
            ProjectSubmission(
                id="s1", user_id="default_user", project_id="p1",
                career_id="ai-product-engineer", skill_name="Python Fundamentals",
                score=92.0, submitted_code=""
            )
        ],
        available_assessments=diags,
        available_projects=projs
    )
    assert rec_high["difficulty"] in ("intermediate", "advanced")
    assert "mastery" in rec_high["reason"].lower()

    db.close()


def test_arena_dashboard_aggregation():
    """Verify dashboard aggregates diagnostic history, project history, demonstrated skills, and mastery."""
    res = client.get("/api/arena/dashboard", headers={"X-User-ID": "default_user"})
    assert res.status_code == 200
    dash = res.json()
    assert "diagnostic_history" in dash
    assert "project_history" in dash
    assert "demonstrated_skills" in dash
    assert "skills_to_practice" in dash
    assert "mastery_records" in dash
    assert "adaptive_recommendation" in dash
    assert "study_time_hours" in dash


def test_user_authorization_isolation():
    """Verify User B cannot see or tamper with User A's attempts."""
    # User A submits
    client.post(
        "/api/arena/diagnostic/diag-py-101/submit",
        json={"answers": {"q1": "O(1) average for set, O(n) for list"}},
        headers={"X-User-ID": "default_user"}
    )

    # User B queries dashboard
    res_b = client.get("/api/arena/dashboard", headers={"X-User-ID": "user_jordan_chen"})
    assert res_b.status_code == 200
    dash_b = res_b.json()
    assert dash_b["user_id"] == "user_jordan_chen"
    # User B must not see User A's diagnostic history
    for d in dash_b["diagnostic_history"]:
        assert d["id"] != "default_user"
