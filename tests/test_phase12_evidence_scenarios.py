"""
Unit and Integration Test Suite for SkillTrace AI Phase 12 Required Test Scenarios.

Covers all 10 mandatory evaluation scenarios:
1. Python repository containing meaningful data analysis.
2. Repository containing only basic Python examples.
3. Repository containing a dependency but no meaningful implementation (import only).
4. Repository with relevant code but limited tests.
5. Repository with insufficient evidence to assess a requirement.
6. Job requiring Python, SQL, and data visualization.
7. Job whose requirements do not match the analysed repository.
8. Incomplete or ambiguous job description.
9. Repository updated with new relevant code (reassessment).
10. Inaccessible repository or failed API request.
"""

import pytest
from backend.app.evidence_matcher import (
    RepositoryEvidenceAnalyzer,
    JobRequirementMatcher,
    EvidenceCategory,
    RequirementStatus
)
from backend.app.taxonomy import taxonomy_registry


# -------------------------------------------------------------------------
# Scenario 1: Python repo with meaningful data analysis
# -------------------------------------------------------------------------
def test_scenario_1_meaningful_data_analysis():
    files = [
        {
            "path": "analysis/clean_pipeline.py",
            "content": (
                "import pandas as pd\n"
                "def clean_and_aggregate(csv_path: str) -> pd.DataFrame:\n"
                "    df = pd.read_csv(csv_path)\n"
                "    df.dropna(subset=['id', 'sales'], inplace=True)\n"
                "    df['rolling_avg'] = df['sales'].rolling(window=7).mean()\n"
                "    grouped = df.groupby('region').agg({'sales': 'sum', 'rolling_avg': 'mean'})\n"
                "    return grouped.reset_index()\n"
            )
        },
        {
            "path": "tests/test_pipeline.py",
            "content": (
                "import pytest\n"
                "from analysis.clean_pipeline import clean_and_aggregate\n"
                "def test_clean_pipeline():\n"
                "    assert True\n"
            )
        }
    ]
    analyzer = RepositoryEvidenceAnalyzer("data-org/sales-pipeline", "commit-abc1")
    profile = analyzer.analyze_repository_files(files)

    pandas_profile = profile["skill_profiles"]["Pandas"]
    assert pandas_profile["evidence_strength"] >= 70.0
    assert pandas_profile["evidence_category"] == EvidenceCategory.STRONG
    assert len(pandas_profile["citations"]) >= 1
    assert any("groupby" in c["detail"] or "DataFrame" in c["detail"] for c in pandas_profile["citations"])


# -------------------------------------------------------------------------
# Scenario 2: Repository containing only basic Python examples
# -------------------------------------------------------------------------
def test_scenario_2_basic_python_examples():
    files = [
        {
            "path": "lesson1.py",
            "content": (
                "# Beginner exercises\n"
                "print('Hello World')\n"
                "x = 10\n"
                "y = 20\n"
                "print(x + y)\n"
            )
        }
    ]
    analyzer = RepositoryEvidenceAnalyzer("student/intro-cs", "commit-tut1")
    profile = analyzer.analyze_repository_files(files)

    py_profile = profile["skill_profiles"]["Python"]
    assert py_profile["evidence_strength"] < 40.0
    assert py_profile["evidence_category"] == EvidenceCategory.LIMITED


# -------------------------------------------------------------------------
# Scenario 3: Dependency present but no meaningful implementation (import-only)
# -------------------------------------------------------------------------
def test_scenario_3_dependency_import_only_no_implementation():
    files = [
        {
            "path": "script.py",
            "content": (
                "import pandas as pd\n"
                "# Declared import but never invoked any DataFrame methods\n"
                "print('Ready')\n"
            )
        }
    ]
    analyzer = RepositoryEvidenceAnalyzer("dev/unused-deps", "commit-dep1")
    profile = analyzer.analyze_repository_files(files)

    pandas_profile = profile["skill_profiles"]["Pandas"]
    # Import penalty applied (-20)
    assert pandas_profile["evidence_category"] == EvidenceCategory.LIMITED
    assert pandas_profile["citations"][0]["is_import_only"] is True
    assert "Import statement only" in pandas_profile["citations"][0]["detail"]


# -------------------------------------------------------------------------
# Scenario 4: Relevant code but limited tests
# -------------------------------------------------------------------------
def test_scenario_4_relevant_code_limited_tests():
    files = [
        {
            "path": "services/processor.py",
            "content": (
                "class OrderProcessor:\n"
                "    def __init__(self, tax_rate: float = 0.08):\n"
                "        self.tax_rate = tax_rate\n"
                "    def process(self, amount: float) -> float:\n"
                "        if amount < 0: raise ValueError('Invalid amount')\n"
                "        return amount * (1.0 + self.tax_rate)\n"
            )
        }
    ]
    analyzer = RepositoryEvidenceAnalyzer("biz/orders", "commit-ord1")
    profile = analyzer.analyze_repository_files(files)

    test_profile = profile["skill_profiles"]["Testing"]
    assert test_profile["evidence_category"] == EvidenceCategory.NO_EVIDENCE
    assert test_profile["evidence_strength"] == 0.0
    # Python has implementation but test bonus is 0
    py_profile = profile["skill_profiles"]["Python"]
    assert py_profile["score_breakdown"]["test_coverage"] == 0.0
    assert py_profile["evidence_category"] in (EvidenceCategory.STRONG, EvidenceCategory.MODERATE)


# -------------------------------------------------------------------------
# Scenario 5: Insufficient evidence to assess a requirement
# -------------------------------------------------------------------------
def test_scenario_5_insufficient_evidence():
    files = []  # Empty repository or no supported source files
    analyzer = RepositoryEvidenceAnalyzer("empty/repo", "commit-empty")
    profile = analyzer.analyze_repository_files(files)

    assert profile["files_scanned"] == 0
    assert profile["status"] == EvidenceCategory.UNABLE

    job = {
        "id": "job-da",
        "title": "Data Analyst",
        "skills": ["Python", "SQL"]
    }
    match = JobRequirementMatcher.match_job(job, profile)
    assert match["overall_score"] is None
    assert match["status_label"] == "Insufficient evidence"
    assert "Insufficient repository evidence" in match["explanation"]


# -------------------------------------------------------------------------
# Scenario 6: Job requiring Python, SQL, and data visualization
# -------------------------------------------------------------------------
def test_scenario_6_job_matching_python_sql_dataviz():
    files = [
        {
            "path": "queries/report.sql",
            "content": (
                "WITH regional_sales AS (\n"
                "    SELECT region, SUM(amount) as total\n"
                "    FROM transactions\n"
                "    GROUP BY region\n"
                ")\n"
                "SELECT region, total FROM regional_sales WHERE total > 5000;\n"
            )
        },
        {
            "path": "viz/chart.py",
            "content": (
                "import matplotlib.pyplot as plt\n"
                "def plot_sales(regions, totals):\n"
                "    plt.subplots(figsize=(10, 6))\n"
                "    plt.plot(regions, totals)\n"
                "    plt.title('Sales By Region')\n"
            )
        }
    ]
    analyzer = RepositoryEvidenceAnalyzer("analytics/dashboard", "commit-viz1")
    profile = analyzer.analyze_repository_files(files)

    job = {
        "id": "job-bi",
        "title": "BI Developer",
        "required_skills": ["SQL", "Data Visualization", "Python"],
        "preferred_skills": ["Testing"]
    }
    match = JobRequirementMatcher.match_job(job, profile)

    assert match["overall_score"] is not None
    assert match["overall_score"] >= 60
    assert match["numerator"] > 0
    assert match["denominator"] > 0
    assert match["required_coverage_percent"] >= 66.0
    assert "SQL" in match["strong_matches"] or "Data Visualization" in match["strong_matches"]


# -------------------------------------------------------------------------
# Scenario 7: Job whose requirements do not match analysed repository
# -------------------------------------------------------------------------
def test_scenario_7_unmatched_job_requirements():
    # Candidate only has Python and SQL
    files = [
        {
            "path": "script.py",
            "content": "def run():\n    print('test')\n"
        }
    ]
    analyzer = RepositoryEvidenceAnalyzer("candidate/py-repo", "commit-py1")
    profile = analyzer.analyze_repository_files(files)

    # Job demands Java, C++, and Workflow Orchestration
    job = {
        "id": "job-sys",
        "title": "Systems Core Engineer",
        "required_skills": ["Java", "C++", "Workflow Orchestration"],
        "preferred_skills": ["Deep Learning"]
    }
    match = JobRequirementMatcher.match_job(job, profile)

    assert len(match["evidence_gaps"]) >= 3
    assert match["required_coverage_percent"] == 0.0
    for req in match["requirements"]:
        if req["is_required"]:
            assert req["status"] == RequirementStatus.NOT_DEMONSTRATED
            assert "Does not mean candidate lacks skill" in req["reason"]


# -------------------------------------------------------------------------
# Scenario 8: Incomplete or ambiguous job description
# -------------------------------------------------------------------------
def test_scenario_8_incomplete_ambiguous_job():
    files = [
        {"path": "main.py", "content": "def main():\n    pass\n"}
    ]
    analyzer = RepositoryEvidenceAnalyzer("test/repo", "commit-amb1")
    profile = analyzer.analyze_repository_files(files)

    # Incomplete job without skills array
    ambiguous_job = {
        "id": "amb-1",
        "title": "Vague Role",
        "company": "Mystery Corp",
        "description": "Looking for energetic teammates."
    }
    match = JobRequirementMatcher.match_job(ambiguous_job, profile)
    # Must handle gracefully without error
    assert match["assessed_requirements_count"] == 0
    assert match["required_coverage_percent"] == 100.0


# -------------------------------------------------------------------------
# Scenario 9: Repository updated with new relevant code (reassessment)
# -------------------------------------------------------------------------
def test_scenario_9_reassessment_with_new_code():
    initial_files = [
        {"path": "math_utils.py", "content": "def add(a, b):\n    return a + b\n"}
    ]
    analyzer_v1 = RepositoryEvidenceAnalyzer("app/service", "commit-v1")
    profile_v1 = analyzer_v1.analyze_repository_files(initial_files)
    assert profile_v1["skill_profiles"]["Testing"]["evidence_strength"] == 0.0

    # User adds unit tests in commit v2
    updated_files = initial_files + [
        {
            "path": "tests/test_math.py",
            "content": (
                "from math_utils import add\n"
                "def test_add():\n"
                "    assert add(2, 3) == 5\n"
            )
        }
    ]
    analyzer_v2 = RepositoryEvidenceAnalyzer("app/service", "commit-v2")
    profile_v2 = analyzer_v2.analyze_repository_files(updated_files)

    assert profile_v2["commit_sha"] == "commit-v2"
    assert profile_v2["skill_profiles"]["Testing"]["evidence_strength"] > 0.0
    assert profile_v2["skill_profiles"]["Testing"]["evidence_category"] != EvidenceCategory.NO_EVIDENCE


# -------------------------------------------------------------------------
# Scenario 10: Inaccessible repository or failed API request
# -------------------------------------------------------------------------
def test_scenario_10_inaccessible_repository():
    # When API returns None or empty
    analyzer = RepositoryEvidenceAnalyzer("private/restricted-repo", "HEAD")
    profile = analyzer.analyze_repository_files([])

    assert profile["files_scanned"] == 0
    assert profile["status"] == EvidenceCategory.UNABLE

    job = {"id": "j1", "title": "Developer", "skills": ["Python"]}
    match = JobRequirementMatcher.match_job(job, profile)
    assert match["status_label"] == "Insufficient evidence"
    assert match["overall_score"] is None


# -------------------------------------------------------------------------
# Scenario 11: Job API that returns no results or an error
# -------------------------------------------------------------------------
def test_scenario_11_job_api_error_or_empty_fallback(monkeypatch):
    import httpx
    from backend.app.job_client import JobDataClient

    client = JobDataClient()
    # Simulate API failure
    def mock_get(*args, **kwargs):
        raise httpx.ConnectError("Simulated provider outage")

    monkeypatch.setattr(httpx, "get", mock_get)
    result = client.search_jobs(keyword="nonexistentquery9999", source_preference="remoteok")

    assert result is not None
    assert "source" in result
    assert result["source"] == "SkillTrace Verified Feed"  # Graceful fallback to verified pool
    assert len(result["jobs"]) > 0


# -------------------------------------------------------------------------
# Scenario 12: Job whose description or posting status is unavailable
# -------------------------------------------------------------------------
def test_scenario_12_job_description_unavailable():
    files = [
        {"path": "core/analysis.py", "content": "import pandas as pd\ndef run(): return pd.DataFrame({'a': [1]})\n"}
    ]
    analyzer = RepositoryEvidenceAnalyzer("user/repo", "sha-12")
    profile = analyzer.analyze_repository_files(files)

    job_no_desc = {
        "id": "job-missing-desc",
        "title": "Data Specialist",
        "company": "Undisclosed",
        "description": None,
        "posting_date": None,
        "required_skills": ["Pandas", "3+ years professional experience"],
        "preferred_skills": []
    }
    match = JobRequirementMatcher.match_job(job_no_desc, profile)

    assert match["overall_score"] is not None
    assert match["overall_score"] == 100.0  # Pandas demonstrated, experience unassessable and excluded from denominator
    assert "3+ years professional experience" in match["unable_to_assess"]
    assert match["unable_to_assess_count"] == 1
    assert match["evidence_coverage_percent"] == 50.0  # 1 of 2 requirements assessable


# -------------------------------------------------------------------------
# Scenario 13: User with multiple repositories (deduplicating identical files)
# -------------------------------------------------------------------------
def test_scenario_13_multiple_repositories_deduplication():
    duplicate_content = "import pandas as pd\ndef duplicate_code():\n    return pd.DataFrame({'x': [1, 2, 3]})\n"

    repo1 = {
        "repo_name": "candidate/repo-alpha",
        "commit_sha": "sha-alpha",
        "files": [
            {"path": "data/pipeline.py", "content": duplicate_content}
        ]
    }
    repo2 = {
        "repo_name": "candidate/repo-beta-fork",
        "commit_sha": "sha-beta",
        "files": [
            # Exact duplicate code copied under a different directory
            {"path": "copied/pipeline.py", "content": duplicate_content},
            # Distinct new SQL file
            {"path": "queries/users.sql", "content": "SELECT user_id, COUNT(*) FROM logins GROUP BY user_id;"}
        ]
    }

    combined_profile = RepositoryEvidenceAnalyzer.analyze_multiple_repositories([repo1, repo2])

    assert combined_profile["repositories_analyzed"] == 2
    assert combined_profile["total_files_scanned"] == 3
    assert combined_profile["unique_files_fingerprinted"] == 2  # Deduplicated duplicate_content

    pandas_profile = combined_profile["skill_profiles"]["Pandas"]
    # Even though duplicate_content appeared in two repos, citations should not double-count the identical snippet
    assert len(pandas_profile["citations"]) == 1

    sql_profile = combined_profile["skill_profiles"]["SQL"]
    assert sql_profile["evidence_strength"] > 0.0


# -------------------------------------------------------------------------
# Scenario 14: Two jobs with similar skills but different required-skill priorities
# -------------------------------------------------------------------------
def test_scenario_14_different_required_skill_priorities():
    # Candidate with strong Pandas/Python evidence, but no SQL evidence
    files = [
        {
            "path": "app/model.py",
            "content": (
                "import pandas as pd\n"
                "def process_data(df: pd.DataFrame) -> pd.DataFrame:\n"
                "    df = df.dropna()\n"
                "    return df.groupby('category').agg({'val': 'sum'}).reset_index()\n"
            )
        }
    ]
    analyzer = RepositoryEvidenceAnalyzer("user/py-focus", "sha-priority")
    profile = analyzer.analyze_repository_files(files)

    # Job A: Python/Pandas is REQUIRED (w=3), SQL is PREFERRED (w=1)
    job_a = {
        "id": "job-python-heavy",
        "title": "Python Data Specialist",
        "required_skills": ["Pandas"],
        "preferred_skills": ["SQL"]
    }

    # Job B: SQL is REQUIRED (w=3), Pandas is PREFERRED (w=1)
    job_b = {
        "id": "job-sql-heavy",
        "title": "SQL Database Specialist",
        "required_skills": ["SQL"],
        "preferred_skills": ["Pandas"]
    }

    match_a = JobRequirementMatcher.match_job(job_a, profile)
    match_b = JobRequirementMatcher.match_job(job_b, profile)

    # Job A: (3.0 * 1.0 + 1.0 * 0.0) / (3.0 + 1.0) = 3 / 4 = 75%
    # Job B: (3.0 * 0.0 + 1.0 * 1.0) / (3.0 + 1.0) = 1 / 4 = 25%
    assert match_a["overall_score"] == 75.0
    assert match_b["overall_score"] == 25.0
    assert match_a["overall_score"] > match_b["overall_score"]

