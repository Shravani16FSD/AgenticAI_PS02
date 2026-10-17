"""
Comprehensive Backend Agent Integration Tests for SkillTrace AI.
Tests:
1. Skill assessment with real evidence
2. No-evidence handling (status: Not demonstrated in this scope, no false claims)
3. Webhook signature validation (valid HMAC vs invalid HMAC)
4. Duplicate webhook events (idempotency via X-GitHub-Delivery)
5. Changed-file reassessment (push event updating evidence)
6. Assessment history preservation (multi-version preservation and diffing)
7. Failed background jobs (resilient error tracking and status="failed")
8. Job requirement discovery (explicit vs preferred skills separation)
"""

import hmac
import hashlib
import json
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.config import settings
from backend.app.database import SessionLocal, migrate_database
from backend.app.models import (
    UserProfile,
    GitHubAccount,
    GitHubRepository,
    JobListing,
    JobRequirement,
    SkillAssessment,
    RepositoryEvidence,
    BackgroundJob,
    WebhookEvent
)
from backend.app.services.github_service import github_service
from backend.app.services.assessment_engine import assessment_engine
from backend.app.services.webhook_service import webhook_service
from backend.app.services.job_discovery_service import job_discovery_service
from backend.app.evidence_matcher import RequirementStatus, EvidenceCategory


import uuid

@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def setup_db_and_clean():
    """Ensure tables, default user and repositories exist and clean mocks."""
    migrate_database()
    db = SessionLocal()

    try:
        user = db.query(UserProfile).filter(UserProfile.id == "default_user").first()
        if not user:
            user = UserProfile(id="default_user", name="Alex Morgan")
            db.add(user)
            db.commit()

        # Ensure test repo is registered and authorized
        repo = db.query(GitHubRepository).filter(
            GitHubRepository.repo_full_name == "alex-morgan/data-pipeline-lab"
        ).first()
        if not repo:
            repo = GitHubRepository(
                id="repo-test-lab",
                user_id="default_user",
                repo_full_name="alex-morgan/data-pipeline-lab",
                default_branch="main",
                is_authorized=True
            )
            db.add(repo)
            db.commit()

        # Clean any leftover webhook events or background jobs from past runs
        db.query(WebhookEvent).delete()
        db.query(BackgroundJob).delete()
        db.commit()
    finally:
        db.close()

    github_service.clear_mocks()
    yield
    github_service.clear_mocks()



# -------------------------------------------------------------
# 1. Skill Assessment with Real Evidence
# -------------------------------------------------------------
@pytest.mark.anyio
async def test_skill_assessment_with_real_evidence():
    """Verify positive assessment produces commit-pinned file and line citations."""
    files = [
        {
            "path": "etl/process_trades.py",
            "content": (
                "import pandas as pd\n"
                "def process_trades(filepath: str) -> pd.DataFrame:\n"
                "    df = pd.read_csv(filepath)\n"
                "    df = df.dropna(subset=['price', 'volume'])\n"
                "    df['notional'] = df['price'] * df['volume']\n"
                "    return df.groupby('ticker').agg({'notional': 'sum'}).reset_index()\n"
            )
        },
        {
            "path": "tests/test_trades.py",
            "content": (
                "import pytest\n"
                "from etl.process_trades import process_trades\n"
                "def test_process():\n"
                "    assert True\n"
            )
        }
    ]

    github_service.register_mock_repository(
        "alex-morgan/data-pipeline-lab",
        "sha-live-101",
        files
    )

    db = SessionLocal()
    try:
        assessment = await assessment_engine.execute_assessment(
            db=db,
            user_id="default_user",
            repo_full_name="alex-morgan/data-pipeline-lab",
            commit_sha="sha-live-101",
            files=files
        )

        assert assessment is not None
        assert assessment.commit_sha == "sha-live-101"
        assert assessment.status == "completed"

        # Check skill results
        pandas_result = next((r for r in assessment.skill_results if r.skill_name == "Pandas"), None)
        assert pandas_result is not None
        assert pandas_result.status in (RequirementStatus.DEMONSTRATED, RequirementStatus.PARTIALLY_DEMONSTRATED)
        assert pandas_result.evidence_count >= 1
        assert pandas_result.direct_evidence_count >= 1

        # Check repository evidence citations
        pandas_evidence = [e for e in assessment.evidence if e.skill_name == "Pandas"]
        assert len(pandas_evidence) >= 1
        evi = pandas_evidence[0]
        assert evi.repo_full_name == "alex-morgan/data-pipeline-lab"
        assert evi.commit_sha == "sha-live-101"
        assert evi.file_path == "etl/process_trades.py"
        assert evi.start_line > 0
        assert evi.end_line >= evi.start_line
        assert "pd.read_csv" in evi.code_snippet or "groupby" in evi.code_snippet
        assert evi.is_direct_evidence is True
        assert "github.com/alex-morgan/data-pipeline-lab/blob/sha-live-101" in evi.github_url
    finally:
        db.close()


# -------------------------------------------------------------
# 2. No-Evidence Handling
# -------------------------------------------------------------
@pytest.mark.anyio
async def test_no_evidence_handling():
    """Verify that absent skills are marked 'Not demonstrated in this scope' and never fabricated."""
    files = [
        {
            "path": "scripts/simple.py",
            "content": "def greet(name: str):\n    return f'Hello {name}'\n"
        }
    ]

    db = SessionLocal()
    try:
        # Create a Job with Kubernetes requirement
        job = JobListing(
            id="job-k8s-test",
            source_url="https://example.com/jobs/devops-k8s",
            title="DevOps Engineer",
            employer="CloudCorp",
            description_raw="Must have Kubernetes cluster administration experience."
        )
        db.merge(job)
        db.query(JobRequirement).filter(JobRequirement.job_id == job.id).delete()
        db.add(JobRequirement(
            id="req-k8s-1",
            job_id=job.id,
            skill_name="Kubernetes",
            requirement_type="required",
            importance="Essential"
        ))
        db.commit()

        assessment = await assessment_engine.execute_assessment(
            db=db,
            user_id="default_user",
            repo_full_name="alex-morgan/data-pipeline-lab",
            commit_sha="sha-simple-202",
            job_id=job.id,
            files=files
        )

        k8s_result = next((r for r in assessment.skill_results if r.skill_name == "Kubernetes"), None)
        assert k8s_result is not None
        assert k8s_result.status == RequirementStatus.NOT_DEMONSTRATED
        assert k8s_result.evidence_count == 0
        assert k8s_result.direct_evidence_count == 0
        assert "Absence of evidence is not proof of lack of competence" in k8s_result.rationale

        # Ensure no evidence rows were fabricated
        k8s_evidence = [e for e in assessment.evidence if e.skill_name == "Kubernetes"]
        assert len(k8s_evidence) == 0
    finally:
        db.close()


# -------------------------------------------------------------
# 3. Webhook Signature Validation
# -------------------------------------------------------------
def test_webhook_signature_validation(client):
    """Verify valid HMAC-SHA256 signature is accepted and invalid is rejected."""
    secret = "test_webhook_secret_key_456"
    settings.GITHUB_WEBHOOK_SECRET = secret

    payload = {
        "repository": {"full_name": "alex-morgan/data-pipeline-lab"},
        "after": "sha-valid-303",
        "head_commit": {
            "id": "sha-valid-303",
            "message": "Add ETL module",
            "author": {"name": "Alex Morgan"}
        }
    }
    payload_bytes = json.dumps(payload).encode("utf-8")

    # 1. Valid Signature
    deliv_valid = f"delivery-valid-{uuid.uuid4().hex[:8]}"
    valid_hmac = "sha256=" + hmac.new(secret.encode("utf-8"), payload_bytes, hashlib.sha256).hexdigest()
    headers_valid = {
        "X-GitHub-Delivery": deliv_valid,
        "X-GitHub-Event": "push",
        "X-Hub-Signature-256": valid_hmac,
        "Content-Type": "application/json"
    }
    resp1 = client.post("/api/webhooks/github", data=payload_bytes, headers=headers_valid)
    assert resp1.status_code == 200
    data1 = resp1.json()
    assert data1["status"] in ("queued", "processed")

    # 2. Invalid Signature
    deliv_invalid = f"delivery-invalid-{uuid.uuid4().hex[:8]}"
    headers_invalid = {
        "X-GitHub-Delivery": deliv_invalid,
        "X-GitHub-Event": "push",
        "X-Hub-Signature-256": "sha256=invalidhexsignature1234567890abcdef",
        "Content-Type": "application/json"
    }
    resp2 = client.post("/api/webhooks/github", data=payload_bytes, headers=headers_invalid)
    assert resp2.status_code == 401
    assert "Invalid webhook signature" in resp2.json()["detail"]


# -------------------------------------------------------------
# 4. Duplicate Webhook Events (Idempotency)
# -------------------------------------------------------------
def test_duplicate_webhook_events(client):
    """Verify repeated webhook events with identical delivery ID are handled idempotently."""
    secret = "test_webhook_secret_key_456"
    settings.GITHUB_WEBHOOK_SECRET = secret

    payload = {
        "repository": {"full_name": "alex-morgan/data-pipeline-lab"},
        "after": "sha-dup-404",
        "head_commit": {"id": "sha-dup-404", "message": "Quick fix"}
    }
    payload_bytes = json.dumps(payload).encode("utf-8")
    sig = "sha256=" + hmac.new(secret.encode("utf-8"), payload_bytes, hashlib.sha256).hexdigest()

    deliv_dup = f"delivery-dup-{uuid.uuid4().hex[:8]}"
    headers = {
        "X-GitHub-Delivery": deliv_dup,
        "X-GitHub-Event": "push",
        "X-Hub-Signature-256": sig,
        "Content-Type": "application/json"
    }

    # First call
    resp1 = client.post("/api/webhooks/github", data=payload_bytes, headers=headers)
    assert resp1.status_code == 200
    assert resp1.json()["status"] == "queued"

    # Second call (duplicate)
    resp2 = client.post("/api/webhooks/github", data=payload_bytes, headers=headers)
    assert resp2.status_code == 200
    data2 = resp2.json()
    assert data2["status"] == "duplicate"
    assert "already recorded" in data2["message"]



# -------------------------------------------------------------
# 5. Changed-File Reassessment & Assessment History Preservation
# -------------------------------------------------------------
@pytest.mark.anyio
async def test_changed_file_reassessment_and_history_preservation():
    """Verify new push event creates a new assessment version and preserves the old version."""
    db = SessionLocal()
    try:
        repo_name = f"test-org/lab-{uuid.uuid4().hex[:6]}"

        # Version 1: Python and Pandas code only
        files_v1 = [
            {
                "path": "pipeline.py",
                "content": "import pandas as pd\ndef read_data():\n    return pd.DataFrame({'val': [1, 2]})\n"
            }
        ]
        asm_v1 = await assessment_engine.execute_assessment(
            db=db,
            user_id="default_user",
            repo_full_name=repo_name,
            commit_sha="sha-version-1",
            files=files_v1
        )
        assert asm_v1.version == 1

        # Version 2: Added SQL query mart
        files_v2 = files_v1 + [
            {
                "path": "sql/marts/revenue.sql",
                "content": "SELECT customer_id, SUM(amount) FROM payments GROUP BY customer_id HAVING SUM(amount) > 100;"
            }
        ]
        asm_v2 = await assessment_engine.execute_assessment(
            db=db,
            user_id="default_user",
            repo_full_name=repo_name,
            commit_sha="sha-version-2",
            files=files_v2
        )
        assert asm_v2.version == 2
        assert asm_v2.previous_assessment_id == asm_v1.id

        # Verify both versions exist simultaneously in database
        saved_v1 = db.query(SkillAssessment).filter(SkillAssessment.id == asm_v1.id).first()
        saved_v2 = db.query(SkillAssessment).filter(SkillAssessment.id == asm_v2.id).first()
        assert saved_v1 is not None
        assert saved_v2 is not None
        assert saved_v1.version == 1
        assert saved_v2.version == 2

        # Verify Diff shows SQL as newly demonstrated
        diff = assessment_engine.compute_assessment_diff(db, asm_v1.id, asm_v2.id)
        assert diff["version_a"] == 1
        assert diff["version_b"] == 2
        assert "SQL" in diff["newly_demonstrated_skills"]
        assert diff["new_evidence_count"] > len(asm_v1.evidence)
    finally:
        db.close()


# -------------------------------------------------------------
# 6. Failed Background Jobs Handling
# -------------------------------------------------------------
@pytest.mark.anyio
async def test_failed_background_job_handling():
    """Verify background job gracefully handles errors and marks status='failed' without crashing."""
    db = SessionLocal()
    original_exec = assessment_engine.execute_assessment
    try:
        from unittest.mock import AsyncMock
        assessment_engine.execute_assessment = AsyncMock(side_effect=RuntimeError("Simulated GitHub connection timeout"))

        job_id = f"job-fail-{uuid.uuid4().hex[:8]}"
        bg_job = BackgroundJob(
            id=job_id,
            job_type="webhook_reassessment",
            status="pending",
            target_id="fail-org/fail-repo"
        )
        db.add(bg_job)
        db.commit()

        await webhook_service.execute_background_reassessment(
            db=db,
            job_id=job_id,
            repo_full_name="fail-org/fail-repo",
            commit_sha="bad-sha-000",
            files=[]
        )

        db.refresh(bg_job)
        assert bg_job.status == "failed"
        assert "Simulated GitHub connection timeout" in bg_job.error_message
        assert bg_job.completed_at is not None
    finally:
        assessment_engine.execute_assessment = original_exec
        db.close()


# -------------------------------------------------------------
# 7. Job Requirement Discovery (Explicit vs Preferred Skills)
# -------------------------------------------------------------
@pytest.mark.anyio
async def test_job_discovery_explicit_vs_preferred():
    """Verify importing a listing extracts and separates explicit requirements and preferred skills."""
    sample_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Senior Data Analyst - Acme Financial</title>
        <meta property="og:site_name" content="Acme Financial" />
    </head>
    <body>
        <h1>Senior Data Analyst</h1>
        <div>
            <h2>Role Overview</h2>
            <p>Join Acme Financial to build market risk pipelines.</p>

            <h2>Requirements and Qualifications</h2>
            <ul>
                <li>Demonstrated expertise with SQL and relational database schemas.</li>
                <li>Production experience developing with Python and Pandas for data manipulation.</li>
            </ul>

            <h2>Preferred Qualifications (Nice to Have)</h2>
            <ul>
                <li>Experience with Docker and FastAPI is a strong plus.</li>
            </ul>
        </div>
    </body>
    </html>
    """

    db = SessionLocal()
    unique_job_url = f"https://acme-finance.com/careers/data-analyst-{uuid.uuid4().hex[:6]}"
    try:
        job = await job_discovery_service.import_job_from_url(
            url=unique_job_url,
            db=db,
            custom_content=sample_html
        )

        assert job.retrieval_status == "active"
        assert "Data Analyst" in job.title
        assert job.employer == "Acme Financial"

        reqs = db.query(JobRequirement).filter(JobRequirement.job_id == job.id).all()
        required_skills = [r.skill_name for r in reqs if r.requirement_type == "required"]
        preferred_skills = [r.skill_name for r in reqs if r.requirement_type == "preferred"]

        assert "SQL" in required_skills
        assert "Python" in required_skills or "Pandas" in required_skills
        assert "Docker" in preferred_skills or "FastAPI" in preferred_skills
    finally:
        db.close()

