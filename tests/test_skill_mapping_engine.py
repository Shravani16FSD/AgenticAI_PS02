"""
Automated Test Suite for the Evidence-Based Skill Mapping Engine.

Verifies:
1. Mapping of structured repository evidence to canonical skills (Python, Data Analysis, API, DB, Testing, Git, Docs).
2. Omission of skills unsupported by repository evidence.
3. Proper handling of import-only / declared dependencies without AST calls (Low confidence + warning).
4. Identification of concrete skill gaps (missing tests, missing README, API routes without tests, missing notebook).
5. Generation of 3 prioritized personalized next steps (immediate improvement, mini-project, verification).
6. Resilient AI synthesis with graceful fallback on errors.
7. FastAPI REST API endpoints: GET /api/skills/evidence-report & POST /api/skills/evidence-report/analyze.
"""

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.services.skill_mapping_engine import (
    skill_mapping_engine,
    EvidenceSkillItem,
    SkillGapItem,
    PrioritizedNextStep,
    EvidenceReportData
)
from backend.app.gemini_service import gemini_service
from unittest.mock import MagicMock


@pytest.fixture
def client():
    return TestClient(app)


# ---------------------------------------------------------------------------
# Test 1: Python repo with Data Analysis, API endpoints, ORM, Tests, and Docs
# ---------------------------------------------------------------------------
def test_comprehensive_repository_analysis():
    files = [
        {
            "path": "pipelines/etl.py",
            "content": (
                "import pandas as pd\n\n"
                "def process_transactions(file_path: str) -> pd.DataFrame:\n"
                "    df = pd.read_csv(file_path)\n"
                "    df.dropna(subset=['amount', 'symbol'], inplace=True)\n"
                "    grouped = df.groupby('symbol').agg({'amount': 'sum'}).reset_index()\n"
                "    return grouped\n"
            )
        },
        {
            "path": "api/endpoints.py",
            "content": (
                "from fastapi import APIRouter\n"
                "router = APIRouter()\n\n"
                "@router.get('/metrics')\n"
                "def get_metrics():\n"
                "    return {'status': 'ok'}\n\n"
                "@router.post('/upload')\n"
                "def upload_data(payload: dict):\n"
                "    return {'received': True}\n"
            )
        },
        {
            "path": "models/database.py",
            "content": (
                "from sqlalchemy import Column, Integer, String\n"
                "from sqlalchemy.orm import declarative_base\n"
                "Base = declarative_base()\n\n"
                "class TransactionModel(Base):\n"
                "    __tablename__ = 'transactions'\n"
                "    id = Column(Integer, primary_key=True)\n"
                "    symbol = Column(String(10))\n"
            )
        },
        {
            "path": "tests/test_etl.py",
            "content": (
                "import pytest\n"
                "from pipelines.etl import process_transactions\n\n"
                "def test_process_transactions():\n"
                "    assert 1 + 1 == 2\n"
                "    assert True\n"
                "    assert 'symbol' == 'symbol'\n"
            )
        },
        {
            "path": "README.md",
            "content": (
                "# Financial Data Lab\n\n"
                "An end-to-end data pipeline service for financial analytics.\n\n"
                "## Setup & Installation\n"
                "```bash\n"
                "pip install -r requirements.txt\n"
                "pytest tests/\n"
                "```\n"
            )
        },
        {
            "path": ".github/workflows/ci.yml",
            "content": "name: CI\non: push\njobs:\n  test:\n    runs-on: ubuntu-latest\n    steps:\n      - run: pytest\n"
        },
        {
            "path": "requirements.txt",
            "content": "fastapi>=0.110.0\npandas>=2.1.0\nsqlalchemy>=2.0.0\npytest>=8.0.0\n"
        }
    ]

    report = skill_mapping_engine.analyze_repository(
        files=files,
        repo_name="alex-morgan/data-pipeline-lab",
        commit_sha="c987654321"
    )

    assert isinstance(report, EvidenceReportData)
    assert report.repository_name == "alex-morgan/data-pipeline-lab"
    assert report.scanned_files_count == 7

    # Verify detected skills
    detected_names = [s.skill_name for s in report.detected_skills]
    assert "Python Programming" in detected_names
    assert "Data Analysis" in detected_names
    assert "API Development" in detected_names
    assert "Database Management" in detected_names
    assert "Software Engineering" in detected_names
    assert "Testing and Debugging" in detected_names
    assert "Git and GitHub" in detected_names
    assert "Documentation and Project Organization" in detected_names

    # CRITICAL: JavaScript and TypeScript should NOT be detected (zero JS/TS files in repo)
    assert "JavaScript and TypeScript" not in detected_names

    # Check Data Analysis evidence specifics
    data_skill = next(s for s in report.detected_skills if s.skill_name == "Data Analysis")
    assert data_skill.confidence in ("Medium", "High")
    assert any("pandas" in ind.lower() for ind in data_skill.observed_indicators)
    assert any("groupby" in ind.lower() or "read_csv" in ind.lower() for ind in data_skill.observed_indicators)
    assert len(data_skill.file_paths) > 0


# ---------------------------------------------------------------------------
# Test 2: Import-only dependency handling (No implementation claimed as proven)
# ---------------------------------------------------------------------------
def test_import_only_dependency_not_claimed_as_proven():
    files = [
        {
            "path": "script.py",
            "content": (
                "import pandas as pd\n"
                "# Declared import but never invoked any DataFrame methods\n"
                "print('Ready')\n"
            )
        },
        {
            "path": "requirements.txt",
            "content": "pandas>=2.1.0\n"
        }
    ]

    report = skill_mapping_engine.analyze_repository(files=files, repo_name="demo/import-only")

    # Data Analysis is detected because dependency is declared, BUT confidence must be Low
    data_skill = next((s for s in report.detected_skills if s.skill_name == "Data Analysis"), None)
    assert data_skill is not None
    assert data_skill.confidence == "Low"
    assert "no substantive dataframe transformation" in data_skill.evidence_summary.lower()
    assert "no dataframe transformations" in " ".join(data_skill.observed_indicators).lower()

    # Gap flagged for import depth
    assert any("Implementation Depth" in g.area for g in report.skill_gaps)


# ---------------------------------------------------------------------------
# Test 3: Skill Gap Detection
# ---------------------------------------------------------------------------
def test_skill_gap_detection_missing_tests_and_readme():
    files = [
        {
            "path": "main.py",
            "content": "print('Hello World')\n"
        }
    ]

    report = skill_mapping_engine.analyze_repository(files=files, repo_name="demo/no-tests-no-doc")

    gap_areas = [g.area for g in report.skill_gaps]

    # Must flag missing automated tests
    assert any("Automated Testing" in a for a in gap_areas)
    # Must flag missing README
    assert any("Project Documentation" in a for a in gap_areas)
    # Must flag missing CI workflow
    assert any("CI/CD" in a for a in gap_areas)


def test_skill_gap_api_without_tests_and_data_without_notebook():
    files = [
        {
            "path": "api/server.py",
            "content": (
                "from fastapi import FastAPI\n"
                "app = FastAPI()\n"
                "@app.get('/items')\n"
                "def get_items():\n"
                "    return []\n"
            )
        },
        {
            "path": "analysis/clean.py",
            "content": (
                "import pandas as pd\n"
                "def clean(df):\n"
                "    return df.dropna()\n"
            )
        },
        {
            "path": "requirements.txt",
            "content": "fastapi\npandas\n"
        }
    ]

    report = skill_mapping_engine.analyze_repository(files=files, repo_name="demo/api-data-gaps")
    gap_areas = [g.area for g in report.skill_gaps]

    # API integration testing gap flagged because routes exist without test suite
    assert any("API Integration" in a for a in gap_areas)
    # Notebook gap flagged because data analysis code exists without .ipynb
    assert any("Notebooks" in a for a in gap_areas)


# ---------------------------------------------------------------------------
# Test 4: Three Prioritized Next Actions
# ---------------------------------------------------------------------------
def test_prioritized_next_actions_structure():
    files = [
        {
            "path": "main.py",
            "content": "def add(a, b): return a + b\n"
        }
    ]

    report = skill_mapping_engine.analyze_repository(files=files)

    assert len(report.prioritized_actions) == 3
    priorities = [a.priority for a in report.prioritized_actions]
    assert priorities == [1, 2, 3]

    types = [a.type for a in report.prioritized_actions]
    assert types == ["immediate", "mini_project", "verification"]

    # Action 1 should address testing gap
    assert "Test" in report.prioritized_actions[0].title or "README" in report.prioritized_actions[0].title
    assert report.prioritized_actions[0].action_label

    # Action 2 should have mini project target_id
    assert report.prioritized_actions[1].target_id is not None

    # Action 3 should have verification target_id
    assert report.prioritized_actions[2].target_id is not None


# ---------------------------------------------------------------------------
# Test 5: Fallback on AI error without crash
# ---------------------------------------------------------------------------
def test_ai_synthesis_fallback_when_gemini_fails():
    files = [{"path": "code.py", "content": "x = 42\n"}]

    # Mock gemini to throw an error
    original_client = gemini_service._mock_client
    try:
        mock = MagicMock()
        mock.models.generate_content.side_effect = RuntimeError("Quota exceeded")
        gemini_service.set_mock_client(mock)

        report = skill_mapping_engine.analyze_repository(files=files, repo_name="demo/fallback-test")
        assert report.ai_synthesis is not None
        assert "demo/fallback-test" in report.ai_synthesis
    finally:
        gemini_service._mock_client = original_client


# ---------------------------------------------------------------------------
# Test 6: FastAPI API Endpoints integration
# ---------------------------------------------------------------------------
def test_api_get_evidence_report(client):
    response = client.get("/api/skills/evidence-report?user_id=default_user")
    assert response.status_code == 200
    data = response.json()

    assert "repository_name" in data
    assert "detected_skills" in data
    assert "skill_gaps" in data
    assert "prioritized_actions" in data
    assert len(data["prioritized_actions"]) == 3
    assert len(data["detected_skills"]) > 0


def test_api_post_analyze_custom_repository(client):
    payload = {
        "repo_url": "jordan-chen/accessible-tokens-core",
        "user_id": "user_jordan_chen"
    }
    response = client.post("/api/skills/evidence-report/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert "jordan-chen" in data["repository_name"]
    detected_names = [s["skill_name"] for s in data["detected_skills"]]
    assert "JavaScript and TypeScript" in detected_names
    assert len(data["prioritized_actions"]) == 3
