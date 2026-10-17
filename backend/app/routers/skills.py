import uuid
from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import UserSkill, GitHubRepository, SkillAssessment
from ..schemas import UserSkillResponse, UserSkillCreate, LogPracticeRequest

router = APIRouter(prefix="/api/skills", tags=["Skills"])

@router.get("", response_model=List[UserSkillResponse])
def get_user_skills(user_id: str = "default_user", db: Session = Depends(get_db)):
    skills = db.query(UserSkill).filter(UserSkill.user_id == user_id).all()
    return skills

@router.post("", response_model=UserSkillResponse, status_code=status.HTTP_201_CREATED)
def create_skill(
    skill_in: UserSkillCreate,
    user_id: str = "default_user",
    db: Session = Depends(get_db)
):
    new_skill = UserSkill(
        id=f"skill-{uuid.uuid4().hex[:8]}",
        user_id=user_id,
        name=skill_in.name,
        category=skill_in.category or "General",
        status=skill_in.status or "learning",
        hours_spent=skill_in.hours_spent,
        target_hours=skill_in.target_hours,
        last_practiced="Just added"
    )
    db.add(new_skill)
    db.commit()
    db.refresh(new_skill)
    return new_skill

@router.post("/{skill_id}/log", response_model=UserSkillResponse)
def log_practice_hours(
    skill_id: str,
    log_in: LogPracticeRequest,
    user_id: str = "default_user",
    db: Session = Depends(get_db)
):
    skill = db.query(UserSkill).filter(
        UserSkill.id == skill_id,
        UserSkill.user_id == user_id
    ).first()

    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    skill.hours_spent += log_in.hours
    if skill.hours_spent >= skill.target_hours:
        skill.status = "proficient"
    elif skill.hours_spent >= (skill.target_hours * 0.4):
        skill.status = "practicing"
    else:
        skill.status = "learning"

    skill.last_practiced = "Today"
    skill.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(skill)
    return skill


# -------------------------------------------------------------
# Evidence-Based Repository Skill Profile & Reanalysis
# -------------------------------------------------------------
from ..evidence_matcher import RepositoryEvidenceAnalyzer, EvidenceCategory
from ..taxonomy import taxonomy_registry

_DEFAULT_DEMO_FILES = [
    {
        "path": "pipelines/financial_etl.py",
        "content": (
            "import pandas as pd\n"
            "def ingest_trading_logs(file_path: str) -> pd.DataFrame:\n"
            "    df = pd.read_csv(file_path, parse_dates=['timestamp'])\n"
            "    df.dropna(subset=['trade_id', 'volume', 'price'], inplace=True)\n"
            "    df['notional'] = df['volume'] * df['price']\n"
            "    df['rolling_vwap'] = df['notional'].cumsum() / df['volume'].cumsum()\n"
            "    grouped = df.groupby('symbol').agg({'notional': 'sum', 'volume': 'sum'})\n"
            "    return grouped.reset_index()\n"
        )
    },
    {
        "path": "sql/marts/portfolio_summary.sql",
        "content": (
            "WITH latest_positions AS (\n"
            "    SELECT symbol, quantity, mark_price, updated_at,\n"
            "           ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY updated_at DESC) as rn\n"
            "    FROM portfolio_snapshots\n"
            ")\n"
            "SELECT p.symbol, p.quantity * p.mark_price AS current_equity, b.sector\n"
            "FROM latest_positions p\n"
            "INNER JOIN instrument_reference b ON p.symbol = b.symbol\n"
            "WHERE p.rn = 1\n"
            "GROUP BY p.symbol, p.quantity, p.mark_price, b.sector\n"
            "HAVING (p.quantity * p.mark_price) > 50000;\n"
        )
    },
    {
        "path": "app/routers/risk_api.py",
        "content": (
            "from fastapi import APIRouter, HTTPException, status\n"
            "router = APIRouter(prefix='/api/v1/risk', tags=['Risk'])\n\n"
            "@router.get('/metrics/{portfolio_id}', status_code=status.HTTP_200_OK)\n"
            "async def get_portfolio_risk_metrics(portfolio_id: str):\n"
            "    if not portfolio_id:\n"
            "        raise HTTPException(status_code=400, detail='Missing portfolio identifier')\n"
            "    return {'portfolio_id': portfolio_id, 'var_95': 14250.0, 'status': 'HEALTHY'}\n"
        )
    },
    {
        "path": "app/models/portfolio.py",
        "content": (
            "from sqlalchemy import Column, String, Integer, Float, ForeignKey\n"
            "from sqlalchemy.orm import relationship\n"
            "from ..database import Base\n\n"
            "class PortfolioEntity(Base):\n"
            "    __tablename__ = 'portfolios'\n"
            "    id = Column(String(36), primary_key=True)\n"
            "    owner_id = Column(String(36), ForeignKey('users.id'), nullable=False, index=True)\n"
            "    total_equity = Column(Float, default=0.0)\n"
        )
    },
    {
        "path": "tests/test_financial_etl.py",
        "content": (
            "import pytest\n"
            "from pipelines.financial_etl import ingest_trading_logs\n\n"
            "def test_ingest_trading_logs_clean():\n"
            "    assert True, 'Test suite asserts trading log integrity'\n"
            "    assert 1 + 1 == 2\n"
        )
    },
    {
        "path": "viz/portfolio_charts.py",
        "content": (
            "import matplotlib.pyplot as plt\n"
            "import seaborn as sns\n\n"
            "def generate_exposure_chart(df, output_path='charts/exposure.png'):\n"
            "    fig, ax = plt.subplots(figsize=(10, 6))\n"
            "    sns.barplot(x='symbol', y='notional', data=df, ax=ax, palette='Blues_d')\n"
            "    ax.set_title('Portfolio Exposure Distribution', fontsize=14, weight='bold')\n"
            "    plt.tight_layout()\n"
            "    plt.savefig(output_path)\n"
        )
    },
    {
        "path": ".github/workflows/ci.yml",
        "content": (
            "name: Repository CI\n"
            "on: [push, pull_request]\n"
            "jobs:\n"
            "  test:\n"
            "    runs-on: ubuntu-latest\n"
            "    steps:\n"
            "      - uses: actions/checkout@v4\n"
            "      - run: pip install -r requirements.txt\n"
            "      - run: pytest tests/\n"
        )
    }
]

_USER_REPO_STATES = {
    "default_user": {
        "repo_full_name": "alex-morgan/data-pipeline-lab",
        "commit_sha": "8f92a1c4e2b",
        "last_scanned_at": datetime.now(timezone.utc).isoformat(),
        "files": list(_DEFAULT_DEMO_FILES)
    },
    "user_jordan_chen": {
        "repo_full_name": "jordan-chen/accessible-tokens-core",
        "commit_sha": "7a8b9c0d1e2f",
        "last_scanned_at": datetime.now(timezone.utc).isoformat(),
        "files": [
            {
                "path": "src/tokens/typography.tokens.json",
                "content": '{\n  "fontFamily": { "editorial": { "value": "Newsreader, Georgia, serif" } },\n  "fontSize": { "scale-sm": { "value": "0.875rem" } }\n}'
            },
            {
                "path": "src/utils/contrast.ts",
                "content": (
                    "export function getContrastRatio(fgLuminance: number, bgLuminance: number): number {\n"
                    "  const l1 = Math.max(fgLuminance, bgLuminance);\n"
                    "  const l2 = Math.min(fgLuminance, bgLuminance);\n"
                    "  return (l1 + 0.05) / (l2 + 0.05);\n"
                    "}\n"
                )
            },
            {
                "path": "src/components/AccessibleButton.tsx",
                "content": (
                    "import React from 'react';\n"
                    "export interface AccessibleButtonProps {\n"
                    "  variant?: 'primary' | 'secondary';\n"
                    "  ariaLabel?: string;\n"
                    "}\n"
                    "export const AccessibleButton: React.FC<AccessibleButtonProps> = ({ variant = 'primary', ariaLabel }) => {\n"
                    "  return <button aria-label={ariaLabel} className={`btn-${variant}`}>Action</button>;\n"
                    "};\n"
                )
            },
            {
                "path": "tests/test_tokens.ts",
                "content": (
                    "import { getContrastRatio } from '../src/utils/contrast';\n"
                    "export function testContrastCompliance() {\n"
                    "  const ratio = getContrastRatio(0.9, 0.08);\n"
                    "  return ratio >= 4.5;\n"
                    "}\n"
                )
            },
            {
                "path": ".github/workflows/audit.yml",
                "content": (
                    "name: Design Token Audit\n"
                    "on: [push, pull_request]\n"
                    "jobs:\n"
                    "  audit:\n"
                    "    runs-on: ubuntu-latest\n"
                    "    steps:\n"
                    "      - uses: actions/checkout@v4\n"
                )
            }
        ]
    },
    "user_priya_sharma": {
        "repo_full_name": "priya-sharma/financial-analytics-marts",
        "commit_sha": "4c5d6e7f8a9b",
        "last_scanned_at": datetime.now(timezone.utc).isoformat(),
        "files": [
            {
                "path": "models/marts/finance/fct_daily_revenue_cohorts.sql",
                "content": (
                    "SELECT customer_id, transaction_date, amount,\n"
                    "  SUM(amount) OVER (PARTITION BY customer_id ORDER BY transaction_date ROWS BETWEEN 29 PRECEDING AND CURRENT ROW) as rolling_30d_spend,\n"
                    "  DENSE_RANK() OVER (PARTITION BY cohort_month ORDER BY total_spend DESC) as cohort_rank\n"
                    "FROM base_transactions\n"
                    "WHERE status = 'settled';\n"
                )
            },
            {
                "path": "models/marts/core/dim_customers.sql",
                "content": (
                    "WITH customer_orders AS (\n"
                    "  SELECT customer_id, MIN(order_date) as first_order_date, COUNT(order_id) as lifetime_orders\n"
                    "  FROM base_orders\n"
                    "  GROUP BY customer_id\n"
                    ")\n"
                    "SELECT c.customer_id, c.signup_date, co.lifetime_orders\n"
                    "FROM base_customers c\n"
                    "LEFT JOIN customer_orders co ON c.customer_id = co.customer_id;\n"
                )
            },
            {
                "path": "pipelines/dbt_runner.py",
                "content": (
                    "import subprocess\n"
                    "def run_dbt_marts():\n"
                    "    return subprocess.run(['dbt', 'build'], capture_output=True)\n"
                )
            },
            {
                "path": "pipelines/reconcile.py",
                "content": (
                    "import pandas as pd\n"
                    "def reconcile_ledger(df: pd.DataFrame) -> pd.DataFrame:\n"
                    "    df = df.dropna(subset=['account_id', 'amount'])\n"
                    "    df['rolling_bal'] = df.groupby('account_id')['amount'].cumsum()\n"
                    "    return df\n"
                )
            },
            {
                "path": "viz/cohort_heatmaps.py",
                "content": (
                    "import matplotlib.pyplot as plt\n"
                    "import seaborn as sns\n"
                    "def plot_cohorts(df):\n"
                    "    fig, ax = plt.subplots(figsize=(10, 6))\n"
                    "    sns.heatmap(df, ax=ax, cmap='YlGnBu')\n"
                    "    return fig\n"
                )
            },
            {
                "path": "tests/test_data_marts.py",
                "content": (
                    "def test_referential_integrity():\n"
                    "    assert True\n"
                )
            },
            {
                "path": ".github/workflows/dbt_ci.yml",
                "content": (
                    "name: dbt CI\n"
                    "on: [push, pull_request]\n"
                    "jobs:\n"
                    "  dbt:\n"
                    "    runs-on: ubuntu-latest\n"
                    "    steps:\n"
                    "      - uses: actions/checkout@v4\n"
                )
            }
        ]
    },
    "user_marcus_vance": {
        "repo_full_name": "marcus-vance/virtualized-canvas-grid",
        "commit_sha": "9e8d7c6b5a4f",
        "last_scanned_at": datetime.now(timezone.utc).isoformat(),
        "files": [
            {
                "path": "src/engine/ViewportScheduler.ts",
                "content": (
                    "export class ViewportScheduler {\n"
                    "  private rafId: number | null = null;\n"
                    "  scheduleRender(callback: FrameRequestCallback) {\n"
                    "    if (this.rafId) cancelAnimationFrame(this.rafId);\n"
                    "    this.rafId = requestAnimationFrame(callback);\n"
                    "  }\n"
                    "}\n"
                )
            },
            {
                "path": "src/components/VirtualGrid.tsx",
                "content": (
                    "import React from 'react';\n"
                    "export interface GridProps<T> { items: T[]; }\n"
                    "export function VirtualGrid<T>({ items }: GridProps<T>) {\n"
                    "  return <div>{items.length} items rendered</div>;\n"
                    "}\n"
                )
            },
            {
                "path": "src/security/ZeroTrustClient.ts",
                "content": (
                    "export async function verifySignatureHeader(payload: string, signature: string, key: CryptoKey): Promise<boolean> {\n"
                    "  const encoder = new TextEncoder();\n"
                    "  return await crypto.subtle.verify('ECDSA', key, new Uint8Array(), encoder.encode(payload));\n"
                    "}\n"
                )
            },
            {
                "path": "tests/test_scheduler.ts",
                "content": (
                    "import { ViewportScheduler } from '../src/engine/ViewportScheduler';\n"
                    "export function testScheduler() {\n"
                    "  const s = new ViewportScheduler();\n"
                    "  return s !== null;\n"
                    "}\n"
                )
            },
            {
                "path": ".github/workflows/benchmarks.yml",
                "content": (
                    "name: Benchmarks\n"
                    "on: [push, pull_request]\n"
                    "jobs:\n"
                    "  bench:\n"
                    "    runs-on: ubuntu-latest\n"
                    "    steps:\n"
                    "      - uses: actions/checkout@v4\n"
                )
            }
        ]
    }
}
_ACTIVE_REPO_STATE = _USER_REPO_STATES["default_user"]

def _resolve_user_id(uid: Optional[str]) -> str:
    if not uid:
        return "default_user"
    clean = uid.lower().strip()
    if "jordan" in clean:
        return "user_jordan_chen"
    if "priya" in clean:
        return "user_priya_sharma"
    if "marcus" in clean:
        return "user_marcus_vance"
    if "alex" in clean or clean in ("default_user", "default"):
        return "default_user"
    return uid if uid in _USER_REPO_STATES else "default_user"


@router.get("/repository-profile")
def get_repository_skill_profile(
    user_id: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Returns the evidence-based skill profile derived from inspected repository code for the user.
    """
    resolved_id = _resolve_user_id(user_id)
    repo_state = _USER_REPO_STATES.get(resolved_id, _USER_REPO_STATES["default_user"])

    analyzer = RepositoryEvidenceAnalyzer(
        repo_state["repo_full_name"],
        repo_state["commit_sha"]
    )
    result = analyzer.analyze_repository_files(repo_state["files"])
    result["user_id"] = resolved_id
    result["last_scanned_at"] = repo_state["last_scanned_at"]
    return result


@router.post("/reanalyse")
def trigger_repository_reanalysis(
    user_id: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Simulates continuous reassessment: pulls latest commit SHA and reanalyzes code for the user.
    """
    resolved_id = _resolve_user_id(user_id)
    repo_state = _USER_REPO_STATES.get(resolved_id, _USER_REPO_STATES["default_user"])

    new_sha = f"c{uuid.uuid4().hex[:11]}"
    repo_state["commit_sha"] = new_sha
    repo_state["last_scanned_at"] = datetime.now(timezone.utc).isoformat()

    analyzer = RepositoryEvidenceAnalyzer(
        repo_state["repo_full_name"],
        new_sha
    )
    result = analyzer.analyze_repository_files(repo_state["files"])
    result["user_id"] = resolved_id
    result["last_scanned_at"] = repo_state["last_scanned_at"]
    result["message"] = f"Repository reassessment complete for commit {new_sha}."
    return result


@router.get("/taxonomy")
def get_standard_skill_taxonomy():
    """Returns the full extensible standard skill taxonomy across all domains."""
    return [
        {
            "canonical_name": s.canonical_name,
            "category": s.category,
            "aliases": s.aliases,
            "relevant_roles": s.relevant_roles,
            "evidence_criteria": s.evidence_criteria
        }
        for s in taxonomy_registry.definitions
    ]
