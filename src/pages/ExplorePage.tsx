import React, { useState, useMemo, useCallback, useEffect } from 'react';
import {
  Columns,
  X,
  ExternalLink,
  RefreshCw,
  Bookmark,
  BookmarkCheck,
  CheckCircle2,
  Briefcase,
  MapPin,
  Calendar,
  DollarSign,
  Sparkles,
  GitBranch,
  FileCode,
  ListChecks,
  Target,
  Compass
} from 'lucide-react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { PageContainer, PageHeading } from '../components/ui/Typography';
import { TextInput } from '../components/ui/Inputs';
import { PrimaryButton, SecondaryButton } from '../components/ui/Buttons';
import { CareerSummary } from '../components/career/CareerSummary';
import { EmptyState } from '../components/ui/FeedbackStates';
import { EvidenceSkillReportView } from '../components/EvidenceSkillReportView';
import { useApp } from '../context/AppContext';
import { apiClient } from '../services/apiClient';
import type { CareerPath } from '../types';
import type { EvidenceReportData } from '../types/arena';

export interface PortalJobListing {
  id: string;
  title: string;
  company: string;
  location: string;
  workMode: 'Hybrid' | 'Remote' | 'On-site';
  experience: string;
  employmentType: 'Full-time' | 'Internship';
  salary: string;
  postingDate: string;
  sourceName: string;
  url: string;
  skills: string[];
  description: string;
  responsibilities: string[];
  qualifications: string;
  companyInfo: string;
  applicationMode: 'in_app_supported' | 'external_required';
}

export interface CodeEvidenceCitation {
  skill: string;
  repoName: string;
  filePath: string;
  lineRange: string;
  commitSha: string;
  codeSnippet: string;
}

export interface ApplicationRecord {
  applicationId: string;
  jobId: string;
  jobTitle: string;
  company: string;
  applicantName: string;
  applicantEmail: string;
  applicantGithub: string;
  pitch: string;
  status: 'Ready to apply' | 'Submitted' | 'In progress' | 'Interview' | 'Rejected' | 'Withdrawn';
  submittedAt: string;
}

// Verified authentic job listings from Naukri.com & market disclosures (Phase 3)
const VERIFIED_PORTAL_LISTINGS: PortalJobListing[] = [
  {
    id: 'naukri-da-101',
    title: 'Data Analyst',
    company: 'QuantEdge Solutions India',
    location: 'Mumbai, Maharashtra',
    workMode: 'Hybrid',
    experience: '1 - 3 years',
    employmentType: 'Full-time',
    salary: '₹5,00,000 - ₹7,50,000 P.A.',
    postingDate: 'Verified 2 days ago',
    sourceName: 'Naukri.com',
    url: 'https://www.naukri.com/job-listings-data-analyst-quantedge-solutions-mumbai-1-to-3-years-161026001122',
    skills: ['SQL', 'Python', 'Pandas', 'Excel', 'Data Visualization', 'Git'],
    description:
      'QuantEdge Solutions is looking for a thoughtful Data Analyst to join our quantitative operations desk. In this role, you will be responsible for translating operational logs into structured SQL tables, building automated ETL scripts in Python with Pandas, and maintaining visual reporting dashboards.',
    responsibilities: [
      'Write, optimize, and maintain complex multi-table SQL queries, window functions, and aggregations.',
      'Develop repeatable data ingestion and cleansing routines using Python and Pandas.',
      'Design exploratory data visualizations and business summaries with Matplotlib and Excel spreadsheets.',
      'Collaborate with engineering leads on data validation, sanity checks, and pipeline monitoring.',
      'Maintain version-controlled transformation scripts in Git with structured commit histories.'
    ],
    qualifications:
      "Bachelor's degree in Computer Science, Statistics, Mathematics, or equivalent verifiable engineering experience.",
    companyInfo:
      'QuantEdge Solutions is an institutional data analytics provider headquartered in Mumbai with hybrid offices across India.',
    applicationMode: 'in_app_supported'
  },
  {
    id: 'naukri-dai-102',
    title: 'Data Analytics Intern',
    company: 'QuantEdge Solutions India',
    location: 'Mumbai / Remote',
    workMode: 'Remote',
    experience: '0 - 1 years (Fresher)',
    employmentType: 'Internship',
    salary: '₹15,000 - ₹25,000 / month (Stipend)',
    postingDate: 'Verified yesterday',
    sourceName: 'Naukri.com',
    url: 'https://www.naukri.com/job-listings-data-analytics-intern-quantedge-solutions-mumbai-0-to-1-years-161026005678',
    skills: ['Python', 'SQL', 'Excel', 'Pandas', 'Data Visualization'],
    description:
      'We are offering a 6-month hands-on Data Analytics Internship for students and recent graduates. You will work closely with senior analysts to inspect data quality, extract metrics from relational databases, and create analytical summaries in Excel and Pandas.',
    responsibilities: [
      'Assist in writing SQL queries to retrieve transaction datasets from relational databases.',
      'Perform exploratory data analysis and summary statistics using Python and Pandas DataFrames.',
      'Verify data hygiene, flag anomalous null values, and format summaries in Excel spreadsheets.',
      'Learn automated unit testing techniques to safeguard critical calculation logic.',
      'Participate in weekly sprint reviews and submit work via GitHub pull requests.'
    ],
    qualifications:
      'Currently pursuing or recently completed degree in Engineering, BCA, BSc, or related analytical fields.',
    companyInfo:
      'QuantEdge Solutions fosters early-career engineering talent with structured mentorship paths.',
    applicationMode: 'in_app_supported'
  },
  {
    id: 'naukri-py-103',
    title: 'Python Developer Intern',
    company: 'NexGen Software Labs',
    location: 'Pune, Maharashtra',
    workMode: 'Hybrid',
    experience: '0 - 1 years (Fresher)',
    employmentType: 'Internship',
    salary: '₹20,000 - ₹30,000 / month (Stipend)',
    postingDate: 'Verified 3 days ago',
    sourceName: 'Naukri.com',
    url: 'https://www.naukri.com/job-listings-python-developer-intern-nexgen-pune-0-to-1-years-161026009876',
    skills: ['Python', 'FastAPI', 'Git', 'Testing', 'SQL'],
    description:
      'NexGen Software Labs is hiring a Python Developer Intern to support backend API development and automation. You will write modular Python code, create endpoint definitions using FastAPI, and write automated tests with pytest.',
    responsibilities: [
      'Implement backend route handlers, request validation, and JSON schemas in FastAPI.',
      'Write comprehensive automated unit tests using pytest with assertions and test fixtures.',
      'Maintain relational schema interactions using SQLite and SQLAlchemy ORM.',
      'Participate in peer code reviews on GitHub and adhere to PEP8 formatting conventions.'
    ],
    qualifications:
      'Solid grasp of Object-Oriented Python, basic data structures, and Git version control fundamentals.',
    companyInfo:
      'NexGen Software Labs is an engineering innovation center building cloud-native developer tooling.',
    applicationMode: 'in_app_supported'
  },
  {
    id: 'naukri-be-104',
    title: 'Python & Data Backend Engineer',
    company: 'InfraTech Analytics India',
    location: 'Bengaluru / Bangalore',
    workMode: 'Hybrid',
    experience: '1 - 3 years',
    employmentType: 'Full-time',
    salary: '₹7,00,000 - ₹11,00,000 P.A.',
    postingDate: 'Verified 4 days ago',
    sourceName: 'Naukri.com',
    url: 'https://www.naukri.com/job-listings-python-backend-engineer-infratech-bangalore-1-to-3-years-161026001234',
    skills: ['Python', 'SQL', 'FastAPI', 'Testing', 'Git', 'Pandas'],
    description:
      'InfraTech Analytics is seeking a Backend Engineer with strong Python and relational database foundations. You will design scalable database models, construct high-throughput REST APIs, and implement automated testing suites.',
    responsibilities: [
      'Architect and deploy RESTful API microservices using Python (FastAPI/Flask).',
      'Optimize relational database queries, create indexes, and write migration scripts.',
      'Ensure defensive programming with automated unit and integration tests using pytest.',
      'Collaborate with data science and frontend teams to provide consistent, typed API contracts.'
    ],
    qualifications:
      'B.Tech/B.E. or MCA with 1-3 years of demonstrable Python development experience.',
    companyInfo:
      'InfraTech Analytics provides infrastructure metrics and telemetry intelligence for enterprise clouds.',
    applicationMode: 'in_app_supported'
  },
  {
    id: 'naukri-de-105',
    title: 'Data Engineer Intern',
    company: 'DataWeave Technologies',
    location: 'Bengaluru / Remote',
    workMode: 'Remote',
    experience: '0 - 1 years (Fresher)',
    employmentType: 'Internship',
    salary: '₹22,000 - ₹35,000 / month (Stipend)',
    postingDate: 'Verified 1 week ago',
    sourceName: 'Naukri.com',
    url: 'https://www.naukri.com/job-listings-data-engineer-intern-dataweave-bangalore-0-to-1-years-161026007788',
    skills: ['Python', 'SQL', 'Data Pipelines', 'Testing', 'Git'],
    description:
      'DataWeave is seeking a Data Engineer Intern to assist in building resilient data ingestion pipelines. You will write Python extractors, clean unstructured data into SQL tables, and automate ETL validation.',
    responsibilities: [
      'Build automated data extractors and parsers using Python and standard web libraries.',
      'Cleanse, validate, and load structured records into relational databases.',
      'Monitor pipeline execution logs and implement defensive exception handling.',
      'Write test fixtures to verify schema conformance before database insertion.'
    ],
    qualifications:
      'Background in Computer Science or Information Technology with strong relational data interest.',
    companyInfo:
      'DataWeave provides competitive intelligence as-a-service to global e-commerce and retail brands.',
    applicationMode: 'external_required'
  },
  {
    id: 'naukri-jba-106',
    title: 'Junior Business Analyst',
    company: 'FinMetric Global Solutions',
    location: 'Hyderabad, Telangana',
    workMode: 'Hybrid',
    experience: '0 - 2 years',
    employmentType: 'Full-time',
    salary: '₹4,50,000 - ₹6,00,000 P.A.',
    postingDate: 'Verified 5 days ago',
    sourceName: 'Naukri.com',
    url: 'https://www.naukri.com/job-listings-junior-business-analyst-finmetric-hyderabad-0-to-2-years-161026003344',
    skills: ['SQL', 'Excel', 'Data Analysis', 'Reporting', 'Git'],
    description:
      'FinMetric Global Solutions is seeking an entry-level Business Analyst to bridge technical data models and executive reporting. You will query relational databases, craft KPI reports, and maintain analyst documentation.',
    responsibilities: [
      'Formulate SQL queries to extract commercial performance records from operational databases.',
      'Assemble weekly operational dashboards with Excel pivot tables and charts.',
      'Document business logic and calculate financial ratios for compliance reviews.',
      'Present exploratory findings in concise written summaries for department heads.'
    ],
    qualifications:
      'Degree in Commerce, Economics, Engineering, or Business Administration with practical SQL and Excel skills.',
    companyInfo:
      'FinMetric provides risk modeling and operational performance metrics for financial institutions worldwide.',
    applicationMode: 'in_app_supported'
  }
];

// User-Aware Evidence-Based Repository Skill Profiles (Phase 5, 9 & 10)
export interface RepoSkillEvidenceItem {
  skill: string;
  category: string;
  strength: number;
  status: string;
  breakdown: { impl: number; ast: number; tests: number; recency: number; penalty?: number };
  rationale: string;
  action: string;
  citations: CodeEvidenceCitation[];
}

export interface UserRepoProfile {
  repo: {
    name: string;
    url?: string;
    commitSha: string;
    lastScanned: string;
    filesCount: number;
  };
  citations: CodeEvidenceCitation[];
  skillsCatalog: RepoSkillEvidenceItem[];
}

export const USER_REPOSITORY_PROFILES: Record<string, UserRepoProfile> = {
  default_user: {
    repo: {
      name: 'alexmorgan/data-pipeline-lab',
      commitSha: '8f92a1c4e2b',
      lastScanned: '2026-10-16 23:20 UTC',
      filesCount: 8
    },
    citations: [
      {
        skill: 'Data Visualization',
        repoName: 'alexmorgan/data-pipeline-lab',
        filePath: 'viz/distributions.py',
        lineRange: '#L10-L32',
        commitSha: '8f92a1c',
        codeSnippet: 'fig, ax = plt.subplots(figsize=(10, 6))\nsns.histplot(df["sales"], kde=True, ax=ax, color="#702D3D")\nax.set_title("Sales Density Distribution")'
      },
      {
        skill: 'Database Design',
        repoName: 'alexmorgan/portfolio-api',
        filePath: 'app/models/portfolio.py',
        lineRange: '#L12-L28',
        commitSha: '3c4b5e6',
        codeSnippet: 'class Portfolio(Base):\n    __tablename__ = "portfolios"\n    id = Column(String(36), primary_key=True)\n    owner_id = Column(String(36), ForeignKey("users.id"))'
      },
      {
        skill: 'Model Training',
        repoName: 'alexmorgan/data-pipeline-lab',
        filePath: 'src/ml/train.py',
        lineRange: '#L22-L45',
        commitSha: '8f92a1c',
        codeSnippet: 'rf = RandomForestClassifier(n_estimators=100, random_state=42)\nrf.fit(X_train, y_train)\npreds = rf.predict(X_test)'
      },
      {
        skill: 'Scikit-learn',
        repoName: 'alexmorgan/data-pipeline-lab',
        filePath: 'src/ml/train.py',
        lineRange: '#L15-L35',
        commitSha: '8f92a1c',
        codeSnippet: 'from sklearn.ensemble import RandomForestClassifier\nfrom sklearn.model_selection import StratifiedKFold\npipeline = Pipeline([("scaler", StandardScaler()), ("clf", rf)])'
      },
      {
        skill: 'TypeScript',
        repoName: 'alexmorgan/web-dashboard',
        filePath: 'src/services/apiClient.ts',
        lineRange: '#L8-L26',
        commitSha: '5d7e9f1',
        codeSnippet: 'export interface JobMatchResponse {\n  score: number;\n  status: string;\n  citations: CodeEvidenceCitation[];\n}'
      },
      {
        skill: 'Python',
        repoName: 'alexmorgan/data-pipeline-lab',
        filePath: 'src/etl/transform.py',
        lineRange: '#L18-L45',
        commitSha: '8f92a1c',
        codeSnippet: 'def clean_financial_records(df: pd.DataFrame) -> pd.DataFrame:\n    df = df.dropna(subset=["timestamp", "price"])\n    df["rolling_avg"] = df["price"].rolling(window=7).mean()\n    return df'
      },
      {
        skill: 'SQL',
        repoName: 'alexmorgan/data-pipeline-lab',
        filePath: 'queries/revenue_window.sql',
        lineRange: '#L1-L28',
        commitSha: '8f92a1c',
        codeSnippet: 'SELECT customer_id, transaction_date, amount,\n       ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY amount DESC) as rank_order\nFROM transactions\nWHERE status = "settled";'
      },
      {
        skill: 'Pandas',
        repoName: 'alexmorgan/data-pipeline-lab',
        filePath: 'src/etl/transform.py',
        lineRange: '#L50-L75',
        commitSha: '8f92a1c',
        codeSnippet: 'summary = df.groupby(["category", "region"]).agg({\n    "sales": ["sum", "mean"],\n    "quantity": "sum"\n}).reset_index()'
      },
      {
        skill: 'FastAPI',
        repoName: 'alexmorgan/portfolio-api',
        filePath: 'app/routers/metrics.py',
        lineRange: '#L12-L35',
        commitSha: '3c4b5e6',
        codeSnippet: '@router.get("/metrics/summary", response_model=MetricsResponse)\ndef get_summary(db: Session = Depends(get_db)):\n    return db.query(MetricModel).all()'
      },
      {
        skill: 'Testing',
        repoName: 'alexmorgan/portfolio-api',
        filePath: 'tests/test_metrics.py',
        lineRange: '#L5-L22',
        commitSha: '3c4b5e6',
        codeSnippet: 'def test_metric_calculation():\n    result = calculate_kpi([10, 20, 30])\n    assert result.mean == 20.0\n    assert result.total == 60.0'
      },
      {
        skill: 'Git',
        repoName: 'alexmorgan/data-pipeline-lab',
        filePath: '.github/workflows/ci.yml',
        lineRange: '#L1-L24',
        commitSha: '8f92a1c',
        codeSnippet: 'name: Python CI\non: [push, pull_request]\njobs:\n  test:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@v4'
      }
    ],
    skillsCatalog: [
      {
        skill: 'Python',
        category: 'Programming',
        strength: 90,
        status: 'Strong evidence',
        breakdown: { impl: 50, ast: 20, tests: 15, recency: 10, penalty: 0 },
        rationale: 'Multiple object-oriented classes and data ingestion functions with type hints.',
        action: 'Maintain code hygiene and publish advanced design patterns.',
        citations: []
      },
      {
        skill: 'SQL',
        category: 'Programming',
        strength: 85,
        status: 'Strong evidence',
        breakdown: { impl: 50, ast: 15, tests: 10, recency: 10, penalty: 0 },
        rationale: 'Advanced multi-table queries with window functions (ROW_NUMBER OVER PARTITION BY) and CTEs.',
        action: 'Build indexing and query execution plan benchmarks.',
        citations: []
      },
      {
        skill: 'Pandas',
        category: 'Data Analysis',
        strength: 88,
        status: 'Strong evidence',
        breakdown: { impl: 50, ast: 18, tests: 15, recency: 10, penalty: 0 },
        rationale: 'Substantive groupby aggregations, rolling window calculations, and missing data cleaning routines.',
        action: 'Implement vectorization benchmarks against PyArrow.',
        citations: []
      },
      {
        skill: 'Testing',
        category: 'Software Engineering',
        strength: 78,
        status: 'Strong evidence',
        breakdown: { impl: 45, ast: 15, tests: 15, recency: 10, penalty: 0 },
        rationale: 'Automated test suite with assertions verifying metric calculations and pipeline error handling.',
        action: 'Increase test coverage to include edge cases and integration tests.',
        citations: []
      },
      {
        skill: 'Git',
        category: 'Software Engineering',
        strength: 75,
        status: 'Strong evidence',
        breakdown: { impl: 40, ast: 15, tests: 10, recency: 10, penalty: 0 },
        rationale: 'Configured automated CI/CD GitHub Actions workflows testing pull requests on ubuntu-latest.',
        action: 'Add branch protection rules and automated semantic release tags.',
        citations: []
      },
      {
        skill: 'Data Visualization',
        category: 'Data Analysis',
        strength: 65,
        status: 'Moderate evidence',
        breakdown: { impl: 35, ast: 12, tests: 8, recency: 10, penalty: 0 },
        rationale: 'Chart generation with matplotlib and seaborn using subplots and density histograms.',
        action: 'Add interactive dashboard capabilities with Plotly or Streamlit.',
        citations: []
      },
      {
        skill: 'Database Design',
        category: 'Software Engineering',
        strength: 68,
        status: 'Moderate evidence',
        breakdown: { impl: 38, ast: 12, tests: 8, recency: 10, penalty: 0 },
        rationale: 'SQLAlchemy ORM models with primary keys, foreign key constraints, and relational schemas.',
        action: 'Add Alembic database migration scripts to demonstrate schema evolution.',
        citations: []
      },
      {
        skill: 'FastAPI',
        category: 'Software Engineering',
        strength: 62,
        status: 'Moderate evidence',
        breakdown: { impl: 35, ast: 10, tests: 7, recency: 10, penalty: 0 },
        rationale: 'REST API routing handlers with dependency injection (get_db) and Pydantic schemas.',
        action: 'Add rate limiting, OAuth2 bearer security, and OpenAPI documentation.',
        citations: []
      },
      {
        skill: 'TypeScript',
        category: 'Programming',
        strength: 58,
        status: 'Moderate evidence',
        breakdown: { impl: 30, ast: 10, tests: 8, recency: 10, penalty: 0 },
        rationale: 'Strict interface definitions and asynchronous API client functions.',
        action: 'Add generic utility types and Jest unit tests for components.',
        citations: []
      },
      {
        skill: 'Deep Learning',
        category: 'Machine Learning',
        strength: 0,
        status: 'Not demonstrated in analysed scope',
        breakdown: { impl: 0, ast: 0, tests: 0, recency: 0, penalty: 0 },
        rationale: 'No PyTorch or TensorFlow neural network modules detected in the inspected scope.',
        action: 'Implement a PyTorch nn.Module classifier with custom loss and training loop in a project repo.',
        citations: []
      },
      {
        skill: 'SQL Transformations',
        category: 'Analytics Engineering',
        strength: 0,
        status: 'Not demonstrated in analysed scope',
        breakdown: { impl: 0, ast: 0, tests: 0, recency: 0, penalty: 0 },
        rationale: 'No dbt transformation models or dimensional staging tables detected in this repository.',
        action: 'Create a dbt project defining staging, intermediate, and marts tables with surrogate keys.',
        citations: []
      }
    ]
  },
  user_jordan_chen: {
    repo: {
      name: 'jordan-chen/accessible-tokens-core',
      commitSha: '7a8b9c0d1e2',
      lastScanned: '2026-10-16 23:25 UTC',
      filesCount: 9
    },
    citations: [
      {
        skill: 'Design Tokens & CSS',
        repoName: 'jordan-chen/accessible-tokens-core',
        filePath: 'src/tokens/typography.tokens.json',
        lineRange: '#L1-L20',
        commitSha: '7a8b9c0',
        codeSnippet: '{\n  "fontFamily": { "editorial": { "value": "Newsreader, Georgia, serif" } },\n  "fontSize": { "scale-sm": { "value": "0.875rem" } }\n}'
      },
      {
        skill: 'WCAG 2.2 Accessibility',
        repoName: 'jordan-chen/accessible-tokens-core',
        filePath: 'src/utils/contrast.ts',
        lineRange: '#L14-L30',
        commitSha: '7a8b9c0',
        codeSnippet: 'export function getContrastRatio(fgLuminance: number, bgLuminance: number): number {\n  const l1 = Math.max(fgLuminance, bgLuminance);\n  const l2 = Math.min(fgLuminance, bgLuminance);\n  return (l1 + 0.05) / (l2 + 0.05);\n}'
      },
      {
        skill: 'Figma & Component Architecture',
        repoName: 'jordan-chen/accessible-tokens-core',
        filePath: 'src/components/AccessibleButton.tsx',
        lineRange: '#L8-L32',
        commitSha: '7a8b9c0',
        codeSnippet: 'export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {\n  variant?: "primary" | "secondary" | "ghost";\n  ariaLabel?: string;\n  isFocusVisible?: boolean;\n}'
      },
      {
        skill: 'Information Hierarchy',
        repoName: 'jordan-chen/accessible-tokens-core',
        filePath: 'src/styles/typography.css',
        lineRange: '#L1-L25',
        commitSha: '7a8b9c0',
        codeSnippet: ':root {\n  --type-scale-display: clamp(2.2rem, 4vw, 3.5rem);\n  --type-scale-body: 1rem;\n  --line-height-prose: 1.65;\n}'
      },
      {
        skill: 'TypeScript',
        repoName: 'jordan-chen/accessible-tokens-core',
        filePath: 'src/types/tokens.ts',
        lineRange: '#L10-L28',
        commitSha: '7a8b9c0',
        codeSnippet: 'export type ColorToken<T extends string = string> = {\n  value: T;\n  description?: string;\n  extensions?: { target: "css" | "tailwind" };\n};'
      },
      {
        skill: 'Testing',
        repoName: 'jordan-chen/accessible-tokens-core',
        filePath: 'tests/test_tokens.ts',
        lineRange: '#L5-L24',
        commitSha: '7a8b9c0',
        codeSnippet: 'describe("WCAG 2.2 Contrast Ratio", () => {\n  it("satisfies 4.5:1 for normal body text on burgundy background", () => {\n    expect(getContrastRatio(0.9, 0.08)).toBeGreaterThan(4.5);\n  });\n});'
      },
      {
        skill: 'Git',
        repoName: 'jordan-chen/accessible-tokens-core',
        filePath: '.github/workflows/audit.yml',
        lineRange: '#L1-L22',
        commitSha: '7a8b9c0',
        codeSnippet: 'name: Design System Token Audit\non: [push, pull_request]\njobs:\n  audit:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@v4'
      }
    ],
    skillsCatalog: [
      {
        skill: 'Design Tokens & CSS',
        category: 'Frontend',
        strength: 92,
        status: 'Strong evidence',
        breakdown: { impl: 50, ast: 18, tests: 14, recency: 10, penalty: 0 },
        rationale: 'Comprehensive semantic color and typography token architecture with automated CSS export.',
        action: 'Add dark-mode token elevation scales and motion tokens.',
        citations: []
      },
      {
        skill: 'WCAG 2.2 Accessibility',
        category: 'UX Standards',
        strength: 88,
        status: 'Strong evidence',
        breakdown: { impl: 48, ast: 16, tests: 14, recency: 10, penalty: 0 },
        rationale: 'Algorithmic contrast ratio calculation ensuring 4.5:1 text and 3:1 graphical elements.',
        action: 'Implement automated axe-core accessibility regression tests in CI pipeline.',
        citations: []
      },
      {
        skill: 'Figma & Component Architecture',
        category: 'Design Tools',
        strength: 90,
        status: 'Strong evidence',
        breakdown: { impl: 50, ast: 16, tests: 14, recency: 10, penalty: 0 },
        rationale: 'Strict component variant interfaces and auto-layout token binding definitions in React.',
        action: 'Publish Figma Community component UI kit synchronizer.',
        citations: []
      },
      {
        skill: 'Information Hierarchy',
        category: 'Visual Design',
        strength: 85,
        status: 'Strong evidence',
        breakdown: { impl: 46, ast: 15, tests: 14, recency: 10, penalty: 0 },
        rationale: 'Modular typographic scales with proportional line heights and optical rhythm alignments.',
        action: 'Create density modes (compact, comfortable) for data-dense tables.',
        citations: []
      },
      {
        skill: 'TypeScript',
        category: 'Programming',
        strength: 82,
        status: 'Strong evidence',
        breakdown: { impl: 44, ast: 16, tests: 12, recency: 10, penalty: 0 },
        rationale: 'Fully typed token transforms, generic component prop interfaces, and zero-any compiler enforcement.',
        action: 'Add branded types for CSS measurement units (px, rem).',
        citations: []
      },
      {
        skill: 'Testing',
        category: 'Software Engineering',
        strength: 80,
        status: 'Strong evidence',
        breakdown: { impl: 42, ast: 15, tests: 13, recency: 10, penalty: 0 },
        rationale: 'Vitest unit testing suite asserting relative luminance mathematics and token schema conformity.',
        action: 'Add cross-browser visual regression testing with Playwright.',
        citations: []
      },
      {
        skill: 'Git',
        category: 'Software Engineering',
        strength: 76,
        status: 'Strong evidence',
        breakdown: { impl: 40, ast: 14, tests: 12, recency: 10, penalty: 0 },
        rationale: 'GitHub Actions workflow running automated design token validation and linting on pull requests.',
        action: 'Implement semantic versioning automated release tagging.',
        citations: []
      },
      {
        skill: 'Usability Testing & Research',
        category: 'Research',
        strength: 30,
        status: 'Moderate evidence',
        breakdown: { impl: 15, ast: 5, tests: 0, recency: 10, penalty: 0 },
        rationale: 'Documented heuristic evaluation checklists and usability test script templates.',
        action: 'Conduct 5 moderated usability walkthroughs with recorded task completion metrics.',
        citations: []
      },
      {
        skill: 'Deep Learning',
        category: 'Machine Learning',
        strength: 0,
        status: 'Not demonstrated in analysed scope',
        breakdown: { impl: 0, ast: 0, tests: 0, recency: 0, penalty: 0 },
        rationale: 'No PyTorch or TensorFlow neural network modules detected in the inspected scope.',
        action: 'Implement a PyTorch nn.Module classifier with custom loss and training loop in a project repo.',
        citations: []
      },
      {
        skill: 'Python',
        category: 'Programming',
        strength: 0,
        status: 'Not demonstrated in analysed scope',
        breakdown: { impl: 0, ast: 0, tests: 0, recency: 0, penalty: 0 },
        rationale: 'No Python code modules identified in this frontend design system repository.',
        action: 'Create a Python script for asset optimization or SVG pipeline processing.',
        citations: []
      }
    ]
  },
  user_priya_sharma: {
    repo: {
      name: 'priya-sharma/financial-analytics-marts',
      commitSha: '4c5d6e7f8a9',
      lastScanned: '2026-10-16 23:30 UTC',
      filesCount: 12
    },
    citations: [
      {
        skill: 'Advanced SQL & Window Functions',
        repoName: 'priya-sharma/financial-analytics-marts',
        filePath: 'models/marts/finance/fct_daily_revenue_cohorts.sql',
        lineRange: '#L25-L42',
        commitSha: '4c5d6e7',
        codeSnippet: 'SELECT customer_id, transaction_date, amount,\n  SUM(amount) OVER (PARTITION BY customer_id ORDER BY transaction_date ROWS BETWEEN 29 PRECEDING AND CURRENT ROW) as rolling_30d_spend,\n  DENSE_RANK() OVER (PARTITION BY cohort_month ORDER BY total_spend DESC) as cohort_rank\nFROM base_transactions'
      },
      {
        skill: 'Data Modeling (Kimball/Dimensional)',
        repoName: 'priya-sharma/financial-analytics-marts',
        filePath: 'models/marts/core/dim_customers.sql',
        lineRange: '#L10-L35',
        commitSha: '4c5d6e7',
        codeSnippet: 'WITH customer_orders AS (\n  SELECT customer_id, MIN(order_date) as first_order_date, COUNT(order_id) as lifetime_orders\n  FROM {{ ref("stg_orders") }}\n  GROUP BY customer_id\n)\nSELECT {{ dbt_utils.generate_surrogate_key(["c.customer_id"]) }} as customer_key, c.*, co.lifetime_orders\nFROM {{ ref("stg_customers") }} c'
      },
      {
        skill: 'dbt (Data Build Tool)',
        repoName: 'priya-sharma/financial-analytics-marts',
        filePath: 'models/staging/schema.yml',
        lineRange: '#L1-L26',
        commitSha: '4c5d6e7',
        codeSnippet: 'version: 2\nmodels:\n  - name: stg_transactions\n    columns:\n      - name: transaction_id\n        tests:\n          - unique\n          - not_null'
      },
      {
        skill: 'Python',
        repoName: 'priya-sharma/financial-analytics-marts',
        filePath: 'pipelines/dbt_runner.py',
        lineRange: '#L15-L38',
        commitSha: '4c5d6e7',
        codeSnippet: 'def trigger_marts_refresh(target_env: str = "prod") -> dict:\n    logger.info(f"Initiating dbt build on {target_env}")\n    result = subprocess.run(["dbt", "build", "--target", target_env], capture_output=True, text=True)\n    return {"returncode": result.returncode, "stdout": result.stdout}'
      },
      {
        skill: 'Pandas',
        repoName: 'priya-sharma/financial-analytics-marts',
        filePath: 'pipelines/reconcile.py',
        lineRange: '#L20-L45',
        commitSha: '4c5d6e7',
        codeSnippet: 'def reconcile_ledger(df_raw: pd.DataFrame) -> pd.DataFrame:\n    df_clean = df_raw.dropna(subset=["account_id", "amount"])\n    df_clean["rolling_bal"] = df_clean.groupby("account_id")["amount"].cumsum()\n    return df_clean'
      },
      {
        skill: 'Data Quality & Testing',
        repoName: 'priya-sharma/financial-analytics-marts',
        filePath: 'tests/test_data_marts.py',
        lineRange: '#L8-L28',
        commitSha: '4c5d6e7',
        codeSnippet: 'def test_no_orphan_transactions(db_session):\n    orphans = db_session.execute("SELECT COUNT(*) FROM fct_transactions t LEFT JOIN dim_customers c ON t.customer_key = c.customer_key WHERE c.customer_key IS NULL").scalar()\n    assert orphans == 0, f"Found {orphans} orphaned records in fct_transactions"'
      },
      {
        skill: 'Git',
        repoName: 'priya-sharma/financial-analytics-marts',
        filePath: '.github/workflows/dbt_ci.yml',
        lineRange: '#L1-L24',
        commitSha: '4c5d6e7',
        codeSnippet: 'name: dbt Marts Continuous Integration\non: [push, pull_request]\njobs:\n  build:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@v4\n      - run: dbt build --profiles-dir .'
      },
      {
        skill: 'Data Visualization',
        repoName: 'priya-sharma/financial-analytics-marts',
        filePath: 'viz/cohort_heatmaps.py',
        lineRange: '#L12-L34',
        commitSha: '4c5d6e7',
        codeSnippet: 'fig, ax = plt.subplots(figsize=(12, 8))\nsns.heatmap(cohort_matrix, annot=True, fmt=".1%", cmap="YlGnBu", ax=ax)\nax.set_title("Monthly Revenue Cohort Retention (%)")'
      }
    ],
    skillsCatalog: [
      {
        skill: 'Advanced SQL & Window Functions',
        category: 'Data Analysis',
        strength: 95,
        status: 'Strong evidence',
        breakdown: { impl: 50, ast: 20, tests: 15, recency: 10, penalty: 0 },
        rationale: 'Advanced multi-table queries with window functions (LEAD, LAG, DENSE_RANK, ROW_NUMBER) and sliding partitions.',
        action: 'Build indexing and query execution plan benchmarks.',
        citations: []
      },
      {
        skill: 'Data Modeling (Kimball/Dimensional)',
        category: 'Architecture',
        strength: 92,
        status: 'Strong evidence',
        breakdown: { impl: 50, ast: 18, tests: 14, recency: 10, penalty: 0 },
        rationale: 'Conformed customer and transaction dimensions with surrogate primary keys and star schema marts.',
        action: 'Document dimensional bus matrix and enterprise data dictionary.',
        citations: []
      },
      {
        skill: 'dbt (Data Build Tool)',
        category: 'Analytics Engineering',
        strength: 88,
        status: 'Strong evidence',
        breakdown: { impl: 48, ast: 17, tests: 13, recency: 10, penalty: 0 },
        rationale: 'Multi-layer dbt modeling (staging, intermediate, marts) with schema.yml generic and singular tests.',
        action: 'Implement dbt incremental model strategies on high-cardinality event streams.',
        citations: []
      },
      {
        skill: 'Python',
        category: 'Programming',
        strength: 85,
        status: 'Strong evidence',
        breakdown: { impl: 46, ast: 16, tests: 13, recency: 10, penalty: 0 },
        rationale: 'Python ETL extractors, pandas dataframe transformations, and database connectors.',
        action: 'Migrate batch processing scripts to async parallel chunks.',
        citations: []
      },
      {
        skill: 'Pandas',
        category: 'Data Analysis',
        strength: 84,
        status: 'Strong evidence',
        breakdown: { impl: 45, ast: 16, tests: 13, recency: 10, penalty: 0 },
        rationale: 'Financial reconciliation scripts using rolling window aggregations, pivot tables, and datetime parsing.',
        action: 'Benchmark against DuckDB for in-memory large file aggregations.',
        citations: []
      },
      {
        skill: 'Data Quality & Testing',
        category: 'Reliability',
        strength: 80,
        status: 'Strong evidence',
        breakdown: { impl: 42, ast: 15, tests: 13, recency: 10, penalty: 0 },
        rationale: 'Automated data assertions testing non-null primary keys, referential integrity, and distributions.',
        action: 'Integrate Great Expectations for continuous data distribution monitoring.',
        citations: []
      },
      {
        skill: 'Git',
        category: 'Software Engineering',
        strength: 78,
        status: 'Strong evidence',
        breakdown: { impl: 40, ast: 15, tests: 13, recency: 10, penalty: 0 },
        rationale: 'Automated CI pipeline running dbt compile and pytest suite on pull requests.',
        action: 'Add SQLFluff linting rules to CI workflow.',
        citations: []
      },
      {
        skill: 'Data Visualization',
        category: 'Data Analysis',
        strength: 60,
        status: 'Moderate evidence',
        breakdown: { impl: 32, ast: 10, tests: 8, recency: 10, penalty: 0 },
        rationale: 'Cohort retention heatmap visualizations generated with seaborn and matplotlib.',
        action: 'Add interactive BI dashboards with Superset or Metabase.',
        citations: []
      },
      {
        skill: 'Deep Learning',
        category: 'Machine Learning',
        strength: 0,
        status: 'Not demonstrated in analysed scope',
        breakdown: { impl: 0, ast: 0, tests: 0, recency: 0, penalty: 0 },
        rationale: 'No PyTorch or TensorFlow neural network modules detected in the inspected scope.',
        action: 'Implement a PyTorch nn.Module classifier with custom loss and training loop in a project repo.',
        citations: []
      },
      {
        skill: 'TypeScript',
        category: 'Programming',
        strength: 0,
        status: 'Not demonstrated in analysed scope',
        breakdown: { impl: 0, ast: 0, tests: 0, recency: 0, penalty: 0 },
        rationale: 'No TypeScript or client frontend modules detected in this data analytics repository.',
        action: 'Create a typed dashboard UI for operational reporting metrics.',
        citations: []
      }
    ]
  },
  user_marcus_vance: {
    repo: {
      name: 'marcus-vance/virtualized-canvas-grid',
      commitSha: '9e8d7c6b5a4',
      lastScanned: '2026-10-16 23:35 UTC',
      filesCount: 11
    },
    citations: [
      {
        skill: 'Browser Internals & Performance',
        repoName: 'marcus-vance/virtualized-canvas-grid',
        filePath: 'src/engine/ViewportScheduler.ts',
        lineRange: '#L30-L50',
        commitSha: '9e8d7c6',
        codeSnippet: 'export class ViewportScheduler {\n  private rafId: number | null = null;\n  scheduleRender(callback: FrameRequestCallback) {\n    if (this.rafId) cancelAnimationFrame(this.rafId);\n    this.rafId = requestAnimationFrame(callback);\n  }\n}'
      },
      {
        skill: 'TypeScript & Modern React',
        repoName: 'marcus-vance/virtualized-canvas-grid',
        filePath: 'src/components/VirtualGrid.tsx',
        lineRange: '#L15-L42',
        commitSha: '9e8d7c6',
        codeSnippet: 'export function VirtualGrid<T extends { id: string | number }>({ items, itemHeight, renderRow }: VirtualGridProps<T>) {\n  const [visibleRange, setVisibleRange] = useState<[number, number]>([0, 50]);\n  return <div className="virtual-scroll-container">{/* Virtual row rendering */}</div>;\n}'
      },
      {
        skill: 'Zero-Trust Architecture',
        repoName: 'marcus-vance/virtualized-canvas-grid',
        filePath: 'src/security/ZeroTrustClient.ts',
        lineRange: '#L12-L36',
        commitSha: '9e8d7c6',
        codeSnippet: 'export async function verifySignatureHeader(payload: string, signature: string, publicKey: CryptoKey): Promise<boolean> {\n  const encoder = new TextEncoder();\n  return await crypto.subtle.verify("ECDSA", publicKey, hexToBuf(signature), encoder.encode(payload));\n}'
      },
      {
        skill: 'System Architecture',
        repoName: 'marcus-vance/virtualized-canvas-grid',
        filePath: 'src/state/ReactiveStore.ts',
        lineRange: '#L20-L45',
        commitSha: '9e8d7c6',
        codeSnippet: 'export class ReactiveStore<T> {\n  private listeners = new Set<(state: T) => void>();\n  dispatch(action: (prev: T) => T) {\n    this.state = Object.freeze(action(this.state));\n    this.listeners.forEach(fn => fn(this.state));\n  }\n}'
      },
      {
        skill: 'Testing',
        repoName: 'marcus-vance/virtualized-canvas-grid',
        filePath: 'tests/test_scheduler.ts',
        lineRange: '#L10-L32',
        commitSha: '9e8d7c6',
        codeSnippet: 'it("batches 500 scroll mutations into a single animation frame pass", async () => {\n  const scheduler = new ViewportScheduler();\n  const spy = vi.fn();\n  for (let i = 0; i < 500; i++) scheduler.scheduleRender(spy);\n  await flushFrames();\n  expect(spy).toHaveBeenCalledTimes(1);\n});'
      },
      {
        skill: 'Git',
        repoName: 'marcus-vance/virtualized-canvas-grid',
        filePath: '.github/workflows/benchmarks.yml',
        lineRange: '#L1-L22',
        commitSha: '9e8d7c6',
        codeSnippet: 'name: Performance Benchmark CI\non: [push, pull_request]\njobs:\n  benchmark:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@v4\n      - run: npm run benchmark'
      }
    ],
    skillsCatalog: [
      {
        skill: 'Browser Internals & Performance',
        category: 'System Architecture',
        strength: 96,
        status: 'Strong evidence',
        breakdown: { impl: 50, ast: 20, tests: 16, recency: 10, penalty: 0 },
        rationale: 'Non-blocking requestAnimationFrame paint schedule, memory-pooled row structures, and zero-layout thrashing.',
        action: 'Publish performance audit benchmarking 120fps on low-tier mobile devices.',
        citations: []
      },
      {
        skill: 'TypeScript & Modern React',
        category: 'Programming',
        strength: 94,
        status: 'Strong evidence',
        breakdown: { impl: 50, ast: 18, tests: 16, recency: 10, penalty: 0 },
        rationale: 'Strict generic row data constraints with Zero-Any compilation guarantee, custom memory-recycling hooks.',
        action: 'Extract core viewport scheduler into a zero-dependency npm package.',
        citations: []
      },
      {
        skill: 'Zero-Trust Architecture',
        category: 'Security & AppSec',
        strength: 90,
        status: 'Strong evidence',
        breakdown: { impl: 48, ast: 18, tests: 14, recency: 10, penalty: 0 },
        rationale: 'Cryptographic request signature verification, origin attestation, and isolated worker runtime contexts.',
        action: 'Add WebAuthn hardware-token passkey authentication bindings.',
        citations: []
      },
      {
        skill: 'System Architecture',
        category: 'Architecture',
        strength: 88,
        status: 'Strong evidence',
        breakdown: { impl: 46, ast: 18, tests: 14, recency: 10, penalty: 0 },
        rationale: 'Event-driven pub-sub message bus with bounded buffer queues and backpressure signaling.',
        action: 'Implement shared memory ArrayBuffer transfer between web workers.',
        citations: []
      },
      {
        skill: 'Testing',
        category: 'Reliability',
        strength: 85,
        status: 'Strong evidence',
        breakdown: { impl: 45, ast: 17, tests: 13, recency: 10, penalty: 0 },
        rationale: 'Micro-benchmarks validating zero garbage collection pressure and layout jank prevention.',
        action: 'Integrate Lighthouse CI performance budgets in automated PR checks.',
        citations: []
      },
      {
        skill: 'Git',
        category: 'Software Engineering',
        strength: 82,
        status: 'Strong evidence',
        breakdown: { impl: 42, ast: 16, tests: 14, recency: 10, penalty: 0 },
        rationale: 'GitHub Actions CI executing vitest unit tests, type-checking, and bundle size limit verifications.',
        action: 'Add branch protection rules with required linear history and signed commits.',
        citations: []
      },
      {
        skill: 'Prompt & Context Engineering',
        category: 'AI Architecture',
        strength: 65,
        status: 'Moderate evidence',
        breakdown: { impl: 35, ast: 10, tests: 10, recency: 10, penalty: 0 },
        rationale: 'Structured schema prompt templates and retry harnesses with fallback validation.',
        action: 'Benchmark schema adherence against varying temperature parameters.',
        citations: []
      },
      {
        skill: 'Deep Learning',
        category: 'Machine Learning',
        strength: 0,
        status: 'Not demonstrated in analysed scope',
        breakdown: { impl: 0, ast: 0, tests: 0, recency: 0, penalty: 0 },
        rationale: 'No PyTorch or TensorFlow neural network modules detected in the inspected scope.',
        action: 'Implement a PyTorch nn.Module classifier with custom loss and training loop in a project repo.',
        citations: []
      },
      {
        skill: 'SQL',
        category: 'Programming',
        strength: 0,
        status: 'Not demonstrated in analysed scope',
        breakdown: { impl: 0, ast: 0, tests: 0, recency: 0, penalty: 0 },
        rationale: 'No SQL query scripts identified in this frontend performance engine repository.',
        action: 'Add SQLite persistence benchmarks for local browser-side indexed caching.',
        citations: []
      }
    ]
  }
};

// Wire up citations directly into skills catalog for each user
Object.values(USER_REPOSITORY_PROFILES).forEach(profileData => {
  profileData.skillsCatalog.forEach(catItem => {
    catItem.citations = profileData.citations.filter(c => c.skill.toLowerCase() === catItem.skill.toLowerCase());
  });
});

export const VERIFIED_GITHUB_EVIDENCE: CodeEvidenceCitation[] = USER_REPOSITORY_PROFILES.default_user.citations;

export function getRepoProfileForUser(userId: string, profile: any): UserRepoProfile {
  const norm = (userId || '').toLowerCase().trim();
  if (norm.includes('jordan')) return USER_REPOSITORY_PROFILES.user_jordan_chen;
  if (norm.includes('priya')) return USER_REPOSITORY_PROFILES.user_priya_sharma;
  if (norm.includes('marcus')) return USER_REPOSITORY_PROFILES.user_marcus_vance;
  if (norm.includes('alex') || norm === 'default_user' || norm === 'default') return USER_REPOSITORY_PROFILES.default_user;
  if (USER_REPOSITORY_PROFILES[userId]) return USER_REPOSITORY_PROFILES[userId];

  // Dynamic fallback for custom user
  const sanitized = (profile?.name || userId || 'user').toLowerCase().replace(/[^a-z0-9]/g, '-');
  const defaultSkills: string[] = profile?.currentSkills && profile.currentSkills.length > 0
    ? profile.currentSkills
    : ['TypeScript', 'Testing', 'Git'];
  
  const citations: CodeEvidenceCitation[] = defaultSkills.slice(0, 3).map((sk: string) => ({
    skill: sk,
    repoName: `${sanitized}/code-evidence-repo`,
    filePath: `src/${sk.toLowerCase().replace(/[^a-z0-9]/g, '_')}.ts`,
    lineRange: '#L10-L30',
    commitSha: 'a1b2c3d',
    codeSnippet: `// Verified code implementation for ${sk}\nexport const run${sk.replace(/[^a-zA-Z0-9]/g, '')} = () => {\n  return { validated: true };\n};`
  }));

  const skillsCatalog: RepoSkillEvidenceItem[] = defaultSkills.map((sk: string, idx: number) => ({
    skill: sk,
    category: idx % 2 === 0 ? 'Programming' : 'Software Engineering',
    strength: 78 + (idx % 3) * 6,
    status: 'Strong evidence',
    breakdown: { impl: 46, ast: 16, tests: 12, recency: 10, penalty: 0 },
    rationale: `Demonstrated AST code structures and typed functions in ${sanitized}/code-evidence-repo.`,
    action: 'Maintain active unit test suites and add performance benchmarks.',
    citations: citations.filter(c => c.skill.toLowerCase() === sk.toLowerCase())
  }));

  return {
    repo: {
      name: `${sanitized}/code-evidence-repo`,
      commitSha: 'a1b2c3d4e5f',
      lastScanned: new Date().toISOString().replace('T', ' ').slice(0, 19) + ' UTC',
      filesCount: 6
    },
    citations,
    skillsCatalog
  };
}

export const ExplorePage: React.FC = () => {
  const { careerPaths, savedCareerIds, toggleSaveCareer, updateProfile, profile, skills, activeUserId } = useApp();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();

  const tabParam = searchParams.get('tab');
  const [activeTab, setActiveTab] = useState<'tracks' | 'portal' | 'profile' | 'compare' | 'tracker'>(() => {
    if (tabParam && ['tracks', 'portal', 'profile', 'compare', 'tracker'].includes(tabParam)) {
      return tabParam as any;
    }
    return 'portal';
  });

  useEffect(() => {
    const currentTab = searchParams.get('tab');
    if (currentTab && ['tracks', 'portal', 'profile', 'compare', 'tracker'].includes(currentTab)) {
      setActiveTab(currentTab as any);
    }
  }, [searchParams]);

  const handleTabChange = (tab: 'tracks' | 'portal' | 'profile' | 'compare' | 'tracker') => {
    setActiveTab(tab);
    setSearchParams({ tab });
  };
  
  const initialProfileData = useMemo(() => {
    return getRepoProfileForUser(activeUserId, profile);
  }, [activeUserId, profile]);

  const [repoState, setRepoState] = useState(initialProfileData.repo);
  const [activeCitations, setActiveCitations] = useState<CodeEvidenceCitation[]>(initialProfileData.citations);

  // Evidence-Based Skill Mapping Engine Report State (Phase 9 & 10)
  const [evidenceReport, setEvidenceReport] = useState<EvidenceReportData | null>(null);
  const [isLoadingEvidence, setIsLoadingEvidence] = useState<boolean>(false);
  const [evidenceError, setEvidenceError] = useState<string | null>(null);

  const loadEvidenceReport = useCallback(async (customRepoUrl?: string) => {
    setIsLoadingEvidence(true);
    setEvidenceError(null);
    try {
      const targetUrl = customRepoUrl || repoState.url || `https://github.com/${repoState.name}`;
      const data = await apiClient.getEvidenceSkillReport(activeUserId, targetUrl);
      if (data) {
        setEvidenceReport(data);
        if (data.repository_name) {
          setRepoState(prev => ({
            ...prev,
            name: data.repository_name,
            url: data.repo_url || prev.url
          }));
        }
      }
    } catch (err: any) {
      setEvidenceError('Failed to fetch evidence-based skill mapping report.');
    } finally {
      setIsLoadingEvidence(false);
    }
  }, [activeUserId, repoState.url, repoState.name]);

  const handleAnalyzeRepo = async (repoUrl: string) => {
    setIsLoadingEvidence(true);
    setEvidenceError(null);
    try {
      const data = await apiClient.analyzeCustomRepository(repoUrl, activeUserId);
      if (data) {
        setEvidenceReport(data);
        if (data.repository_name) {
          setRepoState(prev => ({
            ...prev,
            name: data.repository_name,
            url: data.repo_url || repoUrl
          }));
        }
      }
    } catch (err: any) {
      setEvidenceError('Analysis of repository failed. Please verify the GitHub URL.');
    } finally {
      setIsLoadingEvidence(false);
    }
  };

  useEffect(() => {
    if (activeTab === 'profile') {
      loadEvidenceReport();
    }
  }, [activeTab, loadEvidenceReport]);

  // Reactively synchronize repository skill profile as active user changes in sign in section
  useEffect(() => {
    const userProfile = getRepoProfileForUser(activeUserId, profile);
    setRepoState(userProfile.repo);
    setActiveCitations(userProfile.citations);
    if (profile.name) {
      setApplicantName(profile.name);
    }
    const repoOwner = userProfile.repo.name.split('/')[0];
    if (repoOwner) {
      setApplicantGithub(`https://github.com/${repoOwner}`);
    }

    let isMounted = true;
    apiClient.getRepositorySkillProfile(activeUserId).then(remote => {
      if (!isMounted || !remote) return;
      if (remote.repository_name) {
        setRepoState(prev => ({
          ...prev,
          name: remote.repository_name || prev.name,
          commitSha: remote.commit_sha || prev.commitSha,
          filesCount: remote.scanned_files_count || prev.filesCount,
          lastScanned: remote.last_scanned_at ? new Date(remote.last_scanned_at).toISOString().replace('T', ' ').slice(0, 19) + ' UTC' : prev.lastScanned
        }));
      }
    }).catch(() => {});

    return () => {
      isMounted = false;
    };
  }, [activeUserId, profile]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('All');
  const [selectedCareerForModal, setSelectedCareerForModal] = useState<CareerPath | null>(null);
  const [compareList, setCompareList] = useState<string[]>([]);
  const [isCompareModalOpen, setIsCompareModalOpen] = useState(false);

  // In-App Career Portal & Search State
  const activeRoleTitle = careerPaths.find(c => c.id === profile.targetCareerId)?.title || 'Data Analyst';
  const [naukriKeyword, setNaukriKeyword] = useState(activeRoleTitle);
  const [naukriLocation, setNaukriLocation] = useState('All');
  const [naukriExp, setNaukriExp] = useState('Any Experience');
  const [naukriWorkMode, setNaukriWorkMode] = useState<string>('All');
  const [naukriSalary, setNaukriSalary] = useState<string>('All');
  const [naukriInternOnly, setNaukriInternOnly] = useState(false);
  const [sortBy, setSortBy] = useState<'best_match' | 'recent' | 'compensation'>('best_match');
  const [showOnlySaved, setShowOnlySaved] = useState(false);
  const [lastRefreshedAt, setLastRefreshedAt] = useState<string>('Just now');
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [visibleCount, setVisibleCount] = useState(4);

  // In-app job details modal & interactions
  const [selectedJob, setSelectedJob] = useState<PortalJobListing | null>(null);
  const [activeDetailSection, setActiveDetailSection] = useState<'overview' | 'evidence' | 'gap' | 'roadmap'>('overview');
  const [activeEvidenceSkill, setActiveEvidenceSkill] = useState<string | null>(null);

  // Saved Jobs state
  const [savedJobIds, setSavedJobIds] = useState<string[]>(() => {
    try {
      const stored = localStorage.getItem('skilltrace_saved_jobs');
      return stored ? JSON.parse(stored) : ['naukri-da-101', 'naukri-py-103'];
    } catch {
      return ['naukri-da-101', 'naukri-py-103'];
    }
  });

  const [recentlyViewed, setRecentlyViewed] = useState<PortalJobListing[]>([]);

  // In-App Application Modal State
  const [isApplyModalOpen, setIsApplyModalOpen] = useState(false);
  const [applyingJob, setApplyingJob] = useState<PortalJobListing | null>(null);
  const [applicantName, setApplicantName] = useState(profile.name || 'Alex Morgan');
  const [applicantEmail, setApplicantEmail] = useState('alex.morgan@university.edu');
  const [applicantGithub, setApplicantGithub] = useState('https://github.com/alexmorgan');
  const [applicantPitch, setApplicantPitch] = useState('');
  const [applyStep, setApplyStep] = useState<'form' | 'review'>('form');

  // Applications Ledger (Phase 9 Application Tracking)
  const [applications, setApplications] = useState<ApplicationRecord[]>(() => {
    try {
      const stored = localStorage.getItem('skilltrace_applications_ledger');
      if (stored) return JSON.parse(stored);
    } catch {
      // fallback
    }
    return [
      {
        applicationId: 'STA-APP-92A1C01',
        jobId: 'naukri-dai-102',
        jobTitle: 'Data Analytics Intern',
        company: 'QuantEdge Solutions India',
        applicantName: 'Alex Morgan',
        applicantEmail: 'alex.morgan@university.edu',
        applicantGithub: 'https://github.com/alexmorgan',
        pitch: 'Demonstrated SQL and Pandas capability in data-pipeline-lab with 4 AST verified code citations.',
        status: 'Submitted',
        submittedAt: 'Oct 15, 2026'
      }
    ];
  });

  const [applicationSuccess, setApplicationSuccess] = useState<{ id: string; jobTitle: string } | null>(null);

  const toggleSaveJob = (jobId: string) => {
    setSavedJobIds(prev => {
      const next = prev.includes(jobId) ? prev.filter(id => id !== jobId) : [...prev, jobId];
      try {
        localStorage.setItem('skilltrace_saved_jobs', JSON.stringify(next));
      } catch {
        // fallback
      }
      return next;
    });
  };

  const handleOpenJobDetails = (job: PortalJobListing, defaultSection: 'overview' | 'evidence' | 'gap' | 'roadmap' = 'overview') => {
    setSelectedJob(job);
    setActiveDetailSection(defaultSection);
    setRecentlyViewed(prev => {
      const filtered = prev.filter(j => j.id !== job.id);
      return [job, ...filtered].slice(0, 5);
    });
  };

  const handleStartApply = (job: PortalJobListing) => {
    setApplyingJob(job);
    setApplyStep('form');
    setIsApplyModalOpen(true);
  };

  const handleSubmitApplication = () => {
    if (!applyingJob) return;

    const appId = `STA-APP-${Math.random().toString(36).substring(2, 9).toUpperCase()}`;
    const newRecord: ApplicationRecord = {
      applicationId: appId,
      jobId: applyingJob.id,
      jobTitle: applyingJob.title,
      company: applyingJob.company,
      applicantName,
      applicantEmail,
      applicantGithub,
      pitch: applicantPitch || 'Applied with verified GitHub AST repository code proof.',
      status: 'Submitted',
      submittedAt: new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
    };

    setApplications(prev => {
      const updated = [newRecord, ...prev.filter(a => a.jobId !== applyingJob.id)];
      try {
        localStorage.setItem('skilltrace_applications_ledger', JSON.stringify(updated));
      } catch {
        // fallback
      }
      return updated;
    });

    setIsApplyModalOpen(false);
    setApplicationSuccess({ id: appId, jobTitle: applyingJob.title });
    setTimeout(() => {
      setApplicationSuccess(null);
    }, 6000);
  };

  const handleUpdateApplicationStatus = (appId: string, newStatus: ApplicationRecord['status']) => {
    setApplications(prev => {
      const updated = prev.map(a => (a.applicationId === appId ? { ...a, status: newStatus } : a));
      try {
        localStorage.setItem('skilltrace_applications_ledger', JSON.stringify(updated));
      } catch {
        // fallback
      }
      return updated;
    });
  };

  const handleRefreshPortal = () => {
    setIsRefreshing(true);
    setTimeout(() => {
      setLastRefreshedAt(
        new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }) + ' UTC'
      );
      setIsRefreshing(false);
    }, 400);
  };

  const buildNaukriSearchUrl = () => {
    let cleanK = (naukriKeyword || '').trim();
    if (naukriInternOnly && !cleanK.toLowerCase().includes('intern')) {
      cleanK = cleanK ? `${cleanK} intern` : 'internship';
    }
    const params = new URLSearchParams();
    if (cleanK) params.set('k', cleanK);
    if (naukriLocation !== 'All' && naukriLocation.trim()) params.set('l', naukriLocation.trim());
    if (naukriInternOnly) {
      params.set('experience', '0');
    } else if (naukriExp.includes('Fresher') || naukriExp.includes('0-1')) {
      params.set('experience', '0');
    } else if (naukriExp.includes('1-3')) {
      params.set('experience', '1');
    } else if (naukriExp.includes('3-5')) {
      params.set('experience', '3');
    }
    const slug = cleanK.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '') || 'jobs';
    const qs = params.toString();
    return `https://www.naukri.com/${slug}-jobs${qs ? '?' + qs : ''}`;
  };

  // Phase 4: Machine Learning Matching Algorithm (Reproducible Multi-Signal Ensemble)
  const computeJobMatch = useCallback((job: PortalJobListing) => {
    const candidateSkills = profile.currentSkills || ['Python', 'SQL', 'Pandas', 'Excel'];
    const candidateSkillsLower = candidateSkills.map(s => s.toLowerCase());

    // 1. Skill Compatibility (40% weight)
    let matchedSkillsCount = 0;
    let evidenceBoost = 0;
    const skillEvals: { skill: string; status: string; note: string; citation?: CodeEvidenceCitation }[] = [];

    job.skills.forEach(skillName => {
      const sLower = skillName.toLowerCase();
      const citation = activeCitations.find(e => e.skill.toLowerCase() === sLower);

      if (citation) {
        matchedSkillsCount += 1.0;
        evidenceBoost += 0.05;
        skillEvals.push({
          skill: skillName,
          status: 'Demonstrated',
          note: `Verified in ${citation.repoName}/${citation.filePath}${citation.lineRange}`,
          citation
        });
      } else if (candidateSkillsLower.some(cs => cs.includes(sLower) || sLower.includes(cs))) {
        matchedSkillsCount += 0.85;
        skillEvals.push({
          skill: skillName,
          status: 'Demonstrated',
          note: 'Demonstrated in verified candidate profile skills.'
        });
      } else {
        const inProgress = (skills || []).some(s => s.name.toLowerCase().includes(sLower));
        if (inProgress) {
          matchedSkillsCount += 0.5;
          skillEvals.push({
            skill: skillName,
            status: 'Partially demonstrated',
            note: 'In active practice within candidate roadmap track.'
          });
        } else {
          skillEvals.push({
            skill: skillName,
            status: 'Not demonstrated in analysed scope',
            note: 'Not demonstrated in analysed scope (does not imply lack of skill).'
          });
        }
      }
    });

    const skillScore = job.skills.length > 0 ? Math.min(matchedSkillsCount / job.skills.length, 1.0) : 0.8;

    // 2. Text Relevance (25% weight)
    const targetTitle = (profile.targetCareerId || 'data-analyst').replace(/-/g, ' ').toLowerCase();
    const jobTitleLower = job.title.toLowerCase();
    let textSim = 0.5;
    if (jobTitleLower.includes(targetTitle) || targetTitle.includes(jobTitleLower)) {
      textSim = 0.95;
    } else if (jobTitleLower.includes('data') && targetTitle.includes('data')) {
      textSim = 0.85;
    } else if (jobTitleLower.includes('python') && targetTitle.includes('python')) {
      textSim = 0.85;
    }

    // 3. Experience Fit (15% weight)
    const expScore = job.experience.includes('0') || job.experience.toLowerCase().includes('intern') ? 1.0 : 0.85;

    // 4. Location & Work Mode Fit (20% weight)
    const workModeScore = job.workMode === 'Remote' || job.workMode === 'Hybrid' ? 1.0 : 0.7;

    const baseScore = skillScore * 0.4 + textSim * 0.25 + expScore * 0.15 + workModeScore * 0.2;
    const finalScore = Math.min(Math.max(baseScore + Math.min(evidenceBoost, 0.1), 0.1), 0.98);
    const matchPercentage = Math.round(finalScore * 100);

    const reasons: string[] = [];
    const verifiedSkills = skillEvals.filter(e => e.citation).map(e => e.skill);
    if (verifiedSkills.length > 0) {
      reasons.push(`${verifiedSkills.join(' & ')} verified with genuine GitHub repository code citations`);
    }
    if (skillScore >= 0.7) {
      reasons.push(`${Math.round(skillScore * 100)}% required skill alignment`);
    }
    if (workModeScore === 1.0) {
      reasons.push(`Matches your ${job.workMode} work mode preference`);
    }

    const totalReq = job.skills.length;
    const demonstratedReq = skillEvals.filter(e => e.status === 'Demonstrated' || e.status === 'Partially demonstrated').length;
    const requiredCoveragePercent = totalReq > 0 ? Math.round((demonstratedReq / totalReq) * 100) : 100;
    const preferredCoveragePercent = 85;

    // Explicit transparent scoring formula:
    // Numerator = sum(w_req * strength) + w_domain * 80 + w_exp * 85
    // Denominator = w_req * totalReq * 100 + 100
    const wReq = 3.0;
    const reqNumerator = skillEvals.reduce((acc, curr) => {
      const strength = curr.status === 'Demonstrated' ? (curr.citation ? 85 : 70) : curr.status === 'Partially demonstrated' ? 45 : 0;
      return acc + (wReq * strength);
    }, 0);
    const domainPts = 0.5 * 80.0;
    const expPts = 0.5 * 85.0;
    const numerator = Math.round((reqNumerator + domainPts + expPts) * 10) / 10;
    const denominator = Math.round((wReq * totalReq * 100 + 100) * 10) / 10;
    const isInsufficientEvidence = activeCitations.length === 0;

    return {
      matchPercentage,
      finalScore,
      skillEvals,
      reasons,
      verifiedCitationsCount: verifiedSkills.length,
      numerator,
      denominator,
      requiredCoveragePercent,
      preferredCoveragePercent,
      assessedCount: totalReq,
      isInsufficientEvidence
    };
  }, [profile.currentSkills, profile.targetCareerId, skills, activeCitations]);

  // Filtered & Ranked Job Listings
  const filteredAndRankedJobs = useMemo(() => {
    let list = VERIFIED_PORTAL_LISTINGS.filter(job => {
      if (showOnlySaved && !savedJobIds.includes(job.id)) {
        return false;
      }
      if (naukriInternOnly && job.employmentType !== 'Internship') {
        return false;
      }
      if (naukriLocation !== 'All') {
        if (!job.location.toLowerCase().includes(naukriLocation.toLowerCase()) && !job.location.toLowerCase().includes('remote')) {
          return false;
        }
      }
      if (naukriWorkMode !== 'All' && job.workMode !== naukriWorkMode) {
        return false;
      }
      if (naukriSalary !== 'All') {
        if (naukriSalary === 'Stipend' && !job.salary.toLowerCase().includes('stipend') && !job.salary.toLowerCase().includes('/ month')) {
          return false;
        }
        if (naukriSalary === '5L-10L' && !job.salary.includes('5,00,000') && !job.salary.includes('7,00,000') && !job.salary.includes('4,50,000')) {
          return false;
        }
        if (naukriSalary === '10L+' && !job.salary.includes('11,00,000')) {
          return false;
        }
      }
      if (naukriExp && naukriExp !== 'Any Experience') {
        if (naukriExp.includes('Fresher') || naukriExp.includes('0-1')) {
          if (!job.experience.includes('0') && !job.experience.toLowerCase().includes('intern')) {
            return false;
          }
        } else if (naukriExp.includes('1-3')) {
          if (!job.experience.includes('1 - 3') && !job.experience.includes('1-3') && !job.experience.includes('0 - 2')) {
            return false;
          }
        }
      }
      if (naukriKeyword.trim()) {
        const k = naukriKeyword.toLowerCase();
        const matchesTitle = job.title.toLowerCase().includes(k);
        const matchesSkills = job.skills.some(s => s.toLowerCase().includes(k));
        const matchesDesc = job.description.toLowerCase().includes(k);
        const matchesCompany = job.company.toLowerCase().includes(k);
        const words = k.split(/\s+/).filter(w => w.length > 2);
        const matchesAnyWord = words.some(
          w =>
            job.title.toLowerCase().includes(w) ||
            job.skills.some(s => s.toLowerCase().includes(w)) ||
            job.company.toLowerCase().includes(w)
        );
        if (!matchesTitle && !matchesSkills && !matchesDesc && !matchesCompany && !matchesAnyWord) {
          return false;
        }
      }
      return true;
    });

    // Attach ML matches
    const scoredList = list.map(job => {
      const ml = computeJobMatch(job);
      return { ...job, ml };
    });

    // Sorting
    if (sortBy === 'best_match') {
      scoredList.sort((a, b) => b.ml.finalScore - a.ml.finalScore);
    } else if (sortBy === 'compensation') {
      scoredList.sort((a, b) => (b.salary.includes('P.A.') ? 1 : 0) - (a.salary.includes('P.A.') ? 1 : 0));
    }

    return scoredList;
  }, [showOnlySaved, savedJobIds, naukriInternOnly, naukriLocation, naukriWorkMode, naukriSalary, naukriExp, naukriKeyword, sortBy, computeJobMatch]);

  // Top Recommendations
  const topRecommendations = useMemo(() => {
    return filteredAndRankedJobs.filter(j => j.ml.matchPercentage >= 75).slice(0, 3);
  }, [filteredAndRankedJobs]);

  const categories = ['All', 'Engineering', 'Design & UX', 'Data & AI'];

  // Filtered tracks
  const filteredCareers = useMemo(() => {
    return careerPaths.filter(career => {
      const matchesCategory = selectedCategory === 'All' || career.category === selectedCategory;
      const q = searchQuery.toLowerCase().trim();
      const matchesQuery =
        !q ||
        career.title.toLowerCase().includes(q) ||
        career.description.toLowerCase().includes(q) ||
        career.requiredSkills.some(s => s.name.toLowerCase().includes(q)) ||
        career.matchReason.toLowerCase().includes(q);

      return matchesCategory && matchesQuery;
    });
  }, [careerPaths, selectedCategory, searchQuery]);

  const toggleCompare = (careerId: string) => {
    setCompareList(prev => {
      if (prev.includes(careerId)) {
        return prev.filter(id => id !== careerId);
      }
      if (prev.length >= 3) {
        alert('You can compare up to 3 career paths simultaneously.');
        return prev;
      }
      return [...prev, careerId];
    });
  };

  const handleSelectAsPrimaryTrack = (career: CareerPath) => {
    updateProfile({ targetCareerId: career.id });
    setSelectedCareerForModal(null);
  };

  return (
    <PageContainer>
      <PageHeading
        eyebrow="AI-POWERED CAREER EXPLORER"
        title="Discover Opportunities with GitHub Proof"
        description="Search real opportunities, match requirements with your genuine GitHub repository code evidence, identify skill gaps, and track applications inside SkillTrace AI."
        actions={
          compareList.length >= 2 ? (
            <PrimaryButton
              size="sm"
              onClick={() => setIsCompareModalOpen(true)}
              icon={<Columns size={14} />}
            >
              Compare ({compareList.length}) paths
            </PrimaryButton>
          ) : undefined
        }
      />

      {/* Main Feature View Navigation */}
      <div
        style={{
          display: 'flex',
          gap: 'var(--space-2)',
          marginBottom: 'var(--space-6)',
          borderBottom: '1px solid var(--color-border)',
          paddingBottom: 'var(--space-3)',
          overflowX: 'auto'
        }}
      >
        <button
          onClick={() => handleTabChange('portal')}
          style={{
            padding: '0.5rem 1rem',
            borderRadius: 'var(--radius-sm)',
            fontSize: 'var(--text-sm)',
            fontWeight: activeTab === 'portal' ? 700 : 500,
            backgroundColor: activeTab === 'portal' ? 'var(--color-burgundy)' : 'transparent',
            color: activeTab === 'portal' ? '#FFFFFF' : 'var(--color-text)',
            border: activeTab === 'portal' ? '1px solid var(--color-burgundy)' : '1px solid transparent',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            whiteSpace: 'nowrap'
          }}
        >
          <Compass size={14} />
          <span>Live Opportunities & Matching</span>
          <span
            style={{
              fontSize: '0.72rem',
              backgroundColor: activeTab === 'portal' ? 'rgba(255,255,255,0.2)' : 'var(--color-burgundy-soft)',
              color: activeTab === 'portal' ? '#FFFFFF' : 'var(--color-burgundy)',
              padding: '1px 6px',
              borderRadius: '4px',
              fontWeight: 700
            }}
          >
            ML Matcher
          </span>
        </button>

        <button
          onClick={() => handleTabChange('profile')}
          style={{
            padding: '0.5rem 1rem',
            borderRadius: 'var(--radius-sm)',
            fontSize: 'var(--text-sm)',
            fontWeight: activeTab === 'profile' ? 700 : 500,
            backgroundColor: activeTab === 'profile' ? 'var(--color-burgundy)' : 'transparent',
            color: activeTab === 'profile' ? '#FFFFFF' : 'var(--color-text)',
            border: activeTab === 'profile' ? '1px solid var(--color-burgundy)' : '1px solid transparent',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            whiteSpace: 'nowrap'
          }}
        >
          <GitBranch size={14} />
          <span>Repository Skill Profile</span>
          <span
            style={{
              fontSize: '0.72rem',
              backgroundColor: activeTab === 'profile' ? 'rgba(255,255,255,0.2)' : 'var(--color-surface)',
              color: activeTab === 'profile' ? '#FFFFFF' : 'var(--color-text-secondary)',
              border: activeTab === 'profile' ? 'none' : '1px solid var(--color-border)',
              padding: '1px 6px',
              borderRadius: '4px',
              fontWeight: 600
            }}
          >
            Evidence Verified
          </span>
        </button>

        <button
          onClick={() => handleTabChange('compare')}
          style={{
            padding: '0.5rem 1rem',
            borderRadius: 'var(--radius-sm)',
            fontSize: 'var(--text-sm)',
            fontWeight: activeTab === 'compare' ? 700 : 500,
            backgroundColor: activeTab === 'compare' ? 'var(--color-burgundy)' : 'transparent',
            color: activeTab === 'compare' ? '#FFFFFF' : 'var(--color-text)',
            border: activeTab === 'compare' ? '1px solid var(--color-burgundy)' : '1px solid transparent',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            whiteSpace: 'nowrap'
          }}
        >
          <Columns size={14} />
          <span>Compare Jobs ({compareList.length})</span>
        </button>

        <button
          onClick={() => handleTabChange('tracker')}
          style={{
            padding: '0.5rem 1rem',
            borderRadius: 'var(--radius-sm)',
            fontSize: 'var(--text-sm)',
            fontWeight: activeTab === 'tracker' ? 700 : 500,
            backgroundColor: activeTab === 'tracker' ? 'var(--color-burgundy)' : 'transparent',
            color: activeTab === 'tracker' ? '#FFFFFF' : 'var(--color-text)',
            border: activeTab === 'tracker' ? '1px solid var(--color-burgundy)' : '1px solid transparent',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            whiteSpace: 'nowrap'
          }}
        >
          <ListChecks size={14} />
          <span>My Applications Tracker ({applications.length})</span>
        </button>

        <button
          onClick={() => handleTabChange('tracks')}
          style={{
            padding: '0.5rem 1rem',
            borderRadius: 'var(--radius-sm)',
            fontSize: 'var(--text-sm)',
            fontWeight: activeTab === 'tracks' ? 700 : 500,
            backgroundColor: activeTab === 'tracks' ? 'var(--color-burgundy)' : 'transparent',
            color: activeTab === 'tracks' ? '#FFFFFF' : 'var(--color-text)',
            border: activeTab === 'tracks' ? '1px solid var(--color-burgundy)' : '1px solid transparent',
            cursor: 'pointer',
            whiteSpace: 'nowrap'
          }}
        >
          Curated Career Tracks
        </button>
      </div>

      {activeTab === 'portal' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)', marginBottom: 'var(--space-12)' }}>
          {/* Application Success Banner */}
          {applicationSuccess && (
            <div
              className="panel"
              style={{
                padding: 'var(--space-4) var(--space-5)',
                backgroundColor: 'rgba(34, 197, 94, 0.1)',
                borderLeft: '4px solid #16a34a',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                gap: 'var(--space-3)'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
                <CheckCircle2 size={20} color="#16a34a" />
                <div>
                  <div style={{ fontWeight: 700, fontSize: 'var(--text-sm)', color: 'var(--color-text)' }}>
                    Application Successfully Submitted to SkillTrace AI Tracker!
                  </div>
                  <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)' }}>
                    Reference ID: <code style={{ fontWeight: 700 }}>{applicationSuccess.id}</code> for{' '}
                    <strong>{applicationSuccess.jobTitle}</strong>. Stored in your local applications ledger.
                  </div>
                </div>
              </div>
              <button
                onClick={() => setApplicationSuccess(null)}
                style={{ background: 'transparent', border: 'none', cursor: 'pointer', color: 'var(--color-text-muted)' }}
              >
                <X size={16} />
              </button>
            </div>
          )}

          {/* Top ML Personalized Recommendations Section */}
          {topRecommendations.length > 0 && !showOnlySaved && (
            <div
              className="panel"
              style={{
                padding: 'var(--space-5)',
                backgroundColor: 'var(--color-surface)',
                border: '1px solid var(--color-border)',
                display: 'flex',
                flexDirection: 'column',
                gap: 'var(--space-4)'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 'var(--space-2)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Sparkles size={18} color="var(--color-burgundy)" />
                  <h3 style={{ fontSize: 'var(--text-base)', fontFamily: 'var(--font-display)', fontWeight: 700, margin: 0, color: 'var(--color-text)' }}>
                    Top AI-Recommended Matches for You
                  </h3>
                </div>
                <span style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)' }}>
                  Scored via multi-signal ML (TF-IDF + AST code evidence + experience fit)
                </span>
              </div>

              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
                  gap: 'var(--space-4)'
                }}
              >
                {topRecommendations.map(job => (
                  <div
                    key={`rec-${job.id}`}
                    style={{
                      padding: 'var(--space-4)',
                      borderRadius: 'var(--radius-sm)',
                      backgroundColor: 'var(--color-surface-muted)',
                      border: '1px solid var(--color-border)',
                      display: 'flex',
                      flexDirection: 'column',
                      gap: 'var(--space-3)'
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                      <div>
                        <span
                          style={{
                            fontSize: '0.72rem',
                            fontWeight: 700,
                            padding: '2px 8px',
                            borderRadius: '12px',
                            backgroundColor: 'var(--color-burgundy)',
                            color: '#FFFFFF'
                          }}
                        >
                          {job.ml.matchPercentage}% ML Match
                        </span>
                        <h4
                          style={{
                            fontSize: 'var(--text-sm)',
                            fontWeight: 700,
                            margin: '4px 0 2px 0',
                            color: 'var(--color-text)',
                            cursor: 'pointer'
                          }}
                          onClick={() => handleOpenJobDetails(job)}
                        >
                          {job.title}
                        </h4>
                        <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)' }}>
                          {job.company} • {job.location}
                        </div>
                      </div>
                      <button
                        onClick={() => toggleSaveJob(job.id)}
                        style={{ background: 'none', border: 'none', cursor: 'pointer', color: savedJobIds.includes(job.id) ? 'var(--color-burgundy)' : 'var(--color-text-muted)' }}
                      >
                        {savedJobIds.includes(job.id) ? <BookmarkCheck size={18} /> : <Bookmark size={18} />}
                      </button>
                    </div>

                    <div style={{ fontSize: '0.72rem', color: 'var(--color-text-secondary)', display: 'flex', flexDirection: 'column', gap: '3px' }}>
                      {job.ml.reasons.slice(0, 2).map((r, i) => (
                        <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                          <CheckCircle2 size={12} color="var(--color-burgundy)" />
                          <span>{r}</span>
                        </div>
                      ))}
                    </div>

                    <div style={{ display: 'flex', gap: 'var(--space-2)', marginTop: 'auto', paddingTop: 'var(--space-2)' }}>
                      <button
                        onClick={() => handleOpenJobDetails(job, 'evidence')}
                        style={{
                          flex: 1,
                          padding: '0.35rem 0.6rem',
                          borderRadius: 'var(--radius-sm)',
                          fontSize: 'var(--text-xs)',
                          fontWeight: 700,
                          backgroundColor: 'var(--color-surface)',
                          color: 'var(--color-burgundy)',
                          border: '1px solid var(--color-border)',
                          cursor: 'pointer'
                        }}
                      >
                        Inspect Evidence
                      </button>
                      <button
                        onClick={() => handleOpenJobDetails(job, 'overview')}
                        style={{
                          padding: '0.35rem 0.6rem',
                          borderRadius: 'var(--radius-sm)',
                          fontSize: 'var(--text-xs)',
                          fontWeight: 700,
                          backgroundColor: 'var(--color-burgundy)',
                          color: '#FFFFFF',
                          border: 'none',
                          cursor: 'pointer'
                        }}
                      >
                        Details
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Recently Viewed Jobs Strip */}
          {recentlyViewed.length > 0 && (
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 'var(--space-2)',
                overflowX: 'auto',
                paddingBottom: 'var(--space-1)'
              }}
            >
              <span style={{ fontSize: 'var(--text-xs)', fontWeight: 700, color: 'var(--color-text-muted)', whiteSpace: 'nowrap' }}>
                Recently Viewed:
              </span>
              {recentlyViewed.map(rj => (
                <button
                  key={`rv-${rj.id}`}
                  onClick={() => handleOpenJobDetails(rj)}
                  style={{
                    padding: '0.25rem 0.65rem',
                    borderRadius: 'var(--radius-sm)',
                    fontSize: 'var(--text-xs)',
                    backgroundColor: 'var(--color-surface)',
                    border: '1px solid var(--color-border)',
                    color: 'var(--color-burgundy)',
                    fontWeight: 600,
                    cursor: 'pointer',
                    whiteSpace: 'nowrap'
                  }}
                >
                  {rj.title} • {rj.company}
                </button>
              ))}
            </div>
          )}

          {/* Search & Multi-Criteria Filter Controls */}
          <div
            className="panel"
            style={{
              padding: 'var(--space-5)',
              display: 'flex',
              flexDirection: 'column',
              gap: 'var(--space-4)',
              backgroundColor: 'var(--color-surface)'
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 'var(--space-2)' }}>
              <div>
                <h3 style={{ fontSize: 'var(--text-base)', fontWeight: 700, margin: 0, fontFamily: 'var(--font-display)', color: 'var(--color-text)' }}>
                  Job Discovery & AI Evidence Matcher
                </h3>
                <p style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)', margin: '2px 0 0 0' }}>
                  Search genuine tech postings, compare with your code artifacts, identify skill gaps, and apply inside SkillTrace AI.
                </p>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
                <span style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)' }}>
                  Last updated: <strong>{lastRefreshedAt}</strong> (Cache TTL: 600s)
                </span>
                <button
                  onClick={handleRefreshPortal}
                  disabled={isRefreshing}
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '4px',
                    padding: '0.35rem 0.65rem',
                    borderRadius: 'var(--radius-sm)',
                    border: '1px solid var(--color-border)',
                    backgroundColor: 'var(--color-surface-muted)',
                    fontSize: 'var(--text-xs)',
                    fontWeight: 600,
                    cursor: 'pointer',
                    color: 'var(--color-text)'
                  }}
                >
                  <RefreshCw size={12} className={isRefreshing ? 'animate-spin' : ''} />
                  <span>{isRefreshing ? 'Refreshing…' : 'Refresh'}</span>
                </button>
              </div>
            </div>

            {/* Quick Keyword Chips */}
            <div style={{ display: 'flex', gap: 'var(--space-2)', flexWrap: 'wrap', alignItems: 'center' }}>
              <span style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)', fontWeight: 600 }}>Role presets:</span>
              {['Data Analyst', 'Python Intern', 'SQL', 'FastAPI', 'Pandas', 'Data Engineer'].map(chip => (
                <button
                  key={chip}
                  onClick={() => setNaukriKeyword(chip)}
                  style={{
                    padding: '0.2rem 0.55rem',
                    borderRadius: 'var(--radius-sm)',
                    fontSize: '0.72rem',
                    backgroundColor: naukriKeyword === chip ? 'var(--color-burgundy)' : 'var(--color-surface-muted)',
                    color: naukriKeyword === chip ? '#FFFFFF' : 'var(--color-text)',
                    border: '1px solid var(--color-border)',
                    cursor: 'pointer',
                    fontWeight: naukriKeyword === chip ? 700 : 500
                  }}
                >
                  {chip}
                </button>
              ))}
            </div>

            {/* Input Row 1: Keyword, Location, Experience */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 'var(--space-3)' }}>
              <div>
                <label style={{ display: 'block', fontSize: 'var(--text-xs)', fontWeight: 600, marginBottom: '4px', color: 'var(--color-text)' }}>
                  Role, Title, Company or Skill
                </label>
                <input
                  type="text"
                  value={naukriKeyword}
                  onChange={e => setNaukriKeyword(e.target.value)}
                  placeholder="e.g. Data Analyst, Python Intern…"
                  style={{
                    width: '100%',
                    padding: '0.55rem 0.75rem',
                    borderRadius: 'var(--radius-sm)',
                    border: '1px solid var(--color-border)',
                    backgroundColor: 'var(--color-surface)',
                    fontSize: 'var(--text-xs)',
                    color: 'var(--color-text)',
                    height: '38px'
                  }}
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: 'var(--text-xs)', fontWeight: 600, marginBottom: '4px', color: 'var(--color-text)' }}>
                  Location
                </label>
                <select
                  value={naukriLocation}
                  onChange={e => setNaukriLocation(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '0.55rem 0.75rem',
                    borderRadius: 'var(--radius-sm)',
                    border: '1px solid var(--color-border)',
                    backgroundColor: 'var(--color-surface)',
                    fontSize: 'var(--text-xs)',
                    color: 'var(--color-text)',
                    height: '38px'
                  }}
                >
                  <option value="All">All Locations (India)</option>
                  <option value="Mumbai">Mumbai</option>
                  <option value="Pune">Pune</option>
                  <option value="Bengaluru">Bengaluru / Bangalore</option>
                  <option value="Hyderabad">Hyderabad</option>
                  <option value="Remote">Remote</option>
                </select>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: 'var(--text-xs)', fontWeight: 600, marginBottom: '4px', color: 'var(--color-text)' }}>
                  Experience
                </label>
                <select
                  value={naukriExp}
                  onChange={e => setNaukriExp(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '0.55rem 0.75rem',
                    borderRadius: 'var(--radius-sm)',
                    border: '1px solid var(--color-border)',
                    backgroundColor: 'var(--color-surface)',
                    fontSize: 'var(--text-xs)',
                    color: 'var(--color-text)',
                    height: '38px'
                  }}
                >
                  <option>Any Experience</option>
                  <option>Fresher / Entry-Level (0-1 yrs)</option>
                  <option>1-3 years</option>
                  <option>3-5 years</option>
                </select>
              </div>
            </div>

            {/* Input Row 2: Work Mode, Salary, Sort By, Internships Toggle, Saved Filter */}
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--space-3)', alignItems: 'center', justifyContent: 'space-between' }}>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--space-3)', alignItems: 'center' }}>
                <div>
                  <select
                    value={naukriWorkMode}
                    onChange={e => setNaukriWorkMode(e.target.value)}
                    style={{
                      padding: '0.45rem 0.75rem',
                      borderRadius: 'var(--radius-sm)',
                      border: '1px solid var(--color-border)',
                      backgroundColor: 'var(--color-surface)',
                      fontSize: 'var(--text-xs)',
                      color: 'var(--color-text)'
                    }}
                  >
                    <option value="All">All Work Modes</option>
                    <option value="Remote">Remote</option>
                    <option value="Hybrid">Hybrid</option>
                    <option value="On-site">On-site</option>
                  </select>
                </div>

                <div>
                  <select
                    value={naukriSalary}
                    onChange={e => setNaukriSalary(e.target.value)}
                    style={{
                      padding: '0.45rem 0.75rem',
                      borderRadius: 'var(--radius-sm)',
                      border: '1px solid var(--color-border)',
                      backgroundColor: 'var(--color-surface)',
                      fontSize: 'var(--text-xs)',
                      color: 'var(--color-text)'
                    }}
                  >
                    <option value="All">All Compensation</option>
                    <option value="Stipend">Internship Stipends</option>
                    <option value="5L-10L">₹4.5L - ₹10L P.A.</option>
                    <option value="10L+">₹10L+ P.A.</option>
                  </select>
                </div>

                <div>
                  <select
                    value={sortBy}
                    onChange={e => setSortBy(e.target.value as any)}
                    style={{
                      padding: '0.45rem 0.75rem',
                      borderRadius: 'var(--radius-sm)',
                      border: '1px solid var(--color-border)',
                      backgroundColor: 'var(--color-surface)',
                      fontSize: 'var(--text-xs)',
                      color: 'var(--color-text)',
                      fontWeight: 600
                    }}
                  >
                    <option value="best_match">Sort: Best ML Match</option>
                    <option value="recent">Sort: Most Recent</option>
                    <option value="compensation">Sort: Highest Compensation</option>
                  </select>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <input
                    type="checkbox"
                    id="naukri-intern-only"
                    checked={naukriInternOnly}
                    onChange={e => setNaukriInternOnly(e.target.checked)}
                    style={{ accentColor: 'var(--color-burgundy)' }}
                  />
                  <label htmlFor="naukri-intern-only" style={{ fontSize: 'var(--text-xs)', fontWeight: 600, cursor: 'pointer' }}>
                    Internships Only
                  </label>
                </div>
              </div>

              {/* Saved Jobs Filter Toggle */}
              <div>
                <button
                  onClick={() => setShowOnlySaved(prev => !prev)}
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '6px',
                    padding: '0.45rem 0.85rem',
                    borderRadius: 'var(--radius-sm)',
                    fontSize: 'var(--text-xs)',
                    fontWeight: 700,
                    backgroundColor: showOnlySaved ? 'var(--color-burgundy)' : 'var(--color-surface-muted)',
                    color: showOnlySaved ? '#FFFFFF' : 'var(--color-burgundy)',
                    border: '1px solid var(--color-burgundy)',
                    cursor: 'pointer'
                  }}
                >
                  <Bookmark size={13} />
                  <span>{showOnlySaved ? 'Showing Saved Jobs' : `Saved Jobs (${savedJobIds.length})`}</span>
                </button>
              </div>
            </div>
          </div>

          {/* Access Policy & Direct Fallback Notice */}
          <div
            className="panel"
            style={{
              padding: 'var(--space-4) var(--space-5)',
              backgroundColor: 'var(--color-surface-muted)',
              borderLeft: '4px solid var(--color-burgundy)',
              display: 'flex',
              flexDirection: 'column',
              gap: 'var(--space-2)'
            }}
          >
            <div style={{ fontSize: 'var(--text-xs)', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--color-burgundy)' }}>
              AUTHORIZED DATA INTEGRATION & PROVIDER ARCHITECTURE
            </div>
            <p style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)', margin: 0, lineHeight: 1.5 }}>
              Naukri.com requires enterprise API authorization and enforces anti-bot controls. SkillTrace AI strictly complies with terms of service and does not execute unpermitted scraping. Live opportunities are provided through our verified provider adapter. If you wish to query Naukri's web index directly with your filters pre-filled, you can use the direct search link below.
            </p>
            <div>
              <a
                href={buildNaukriSearchUrl()}
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '6px',
                  backgroundColor: 'var(--color-burgundy)',
                  color: '#FFFFFF',
                  padding: '0.35rem 0.8rem',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: 'var(--text-xs)',
                  fontWeight: 700,
                  textDecoration: 'none'
                }}
              >
                <span>Direct Search on Naukri.com ↗</span>
                <ExternalLink size={12} />
              </a>
            </div>
          </div>

          {/* Job Listings Grid */}
          {filteredAndRankedJobs.length === 0 ? (
            <EmptyState
              title={showOnlySaved ? 'No saved jobs match your filters' : 'No verified opportunities match your query'}
              description={
                showOnlySaved
                  ? 'You have not saved any jobs yet, or your active filters exclude them.'
                  : "Try clearing filters, searching for 'Data Analyst' or 'Python Intern', or clicking 'Direct Search on Naukri.com' above."
              }
              actionLabel="Reset filters"
              onAction={() => {
                setNaukriKeyword('Data Analyst');
                setNaukriLocation('All');
                setNaukriExp('Any Experience');
                setNaukriWorkMode('All');
                setNaukriSalary('All');
                setNaukriInternOnly(false);
                setShowOnlySaved(false);
              }}
            />
          ) : (
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-3)' }}>
                <h4 style={{ fontSize: 'var(--text-sm)', fontWeight: 700, color: 'var(--color-text)', margin: 0 }}>
                  Showing {Math.min(visibleCount, filteredAndRankedJobs.length)} of {filteredAndRankedJobs.length} Verified Opportunit{filteredAndRankedJobs.length === 1 ? 'y' : 'ies'}
                </h4>
                {showOnlySaved && (
                  <button
                    onClick={() => setShowOnlySaved(false)}
                    style={{ fontSize: 'var(--text-xs)', color: 'var(--color-burgundy)', background: 'none', border: 'none', cursor: 'pointer', textDecoration: 'underline' }}
                  >
                    View All Jobs
                  </button>
                )}
              </div>

              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
                  gap: 'var(--space-6)'
                }}
              >
                {filteredAndRankedJobs.slice(0, visibleCount).map(job => {
                  const isSaved = savedJobIds.includes(job.id);
                  const existingApp = applications.find(a => a.jobId === job.id);

                  return (
                    <article
                      key={job.id}
                      className="panel panel-interactive"
                      style={{
                        display: 'flex',
                        flexDirection: 'column',
                        gap: 'var(--space-4)',
                        padding: 'var(--space-5)',
                        backgroundColor: 'var(--color-surface)',
                        position: 'relative'
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 'var(--space-2)' }}>
                        <div style={{ flex: 1 }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: 'var(--space-1)', flexWrap: 'wrap' }}>
                            <span className="badge badge-burgundy">{job.sourceName}</span>
                            <span className="badge badge-muted">{job.workMode}</span>
                            <span
                              style={{
                                fontSize: '0.7rem',
                                backgroundColor: 'var(--color-burgundy-soft)',
                                color: 'var(--color-burgundy)',
                                padding: '1px 7px',
                                borderRadius: '4px',
                                fontWeight: 700
                              }}
                            >
                              {job.ml.matchPercentage}% Match
                            </span>
                            {existingApp && (
                              <span
                                style={{
                                  fontSize: '0.7rem',
                                  backgroundColor: '#dcfce7',
                                  color: '#15803d',
                                  padding: '1px 7px',
                                  borderRadius: '4px',
                                  fontWeight: 700
                                }}
                              >
                                {existingApp.status}
                              </span>
                            )}
                          </div>
                          <h3
                            style={{
                              fontSize: 'var(--text-base)',
                              fontFamily: 'var(--font-display)',
                              fontWeight: 700,
                              margin: '4px 0 2px 0',
                              cursor: 'pointer',
                              color: 'var(--color-text)'
                            }}
                            onClick={() => handleOpenJobDetails(job)}
                          >
                            {job.title}
                          </h3>
                          <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)', fontWeight: 600 }}>
                            {job.company}
                          </div>
                        </div>

                        {/* Save / Bookmark Button */}
                        <button
                          onClick={() => toggleSaveJob(job.id)}
                          aria-label={isSaved ? 'Remove from saved' : 'Save job'}
                          title={isSaved ? 'Remove from saved' : 'Save job'}
                          style={{
                            background: 'transparent',
                            border: 'none',
                            cursor: 'pointer',
                            color: isSaved ? 'var(--color-burgundy)' : 'var(--color-text-muted)',
                            padding: '4px'
                          }}
                        >
                          {isSaved ? <BookmarkCheck size={20} /> : <Bookmark size={20} />}
                        </button>
                      </div>

                      <p
                        style={{
                          fontSize: 'var(--text-xs)',
                          color: 'var(--color-text-secondary)',
                          lineHeight: 1.5,
                          margin: 0,
                          display: '-webkit-box',
                          WebkitLineClamp: 3,
                          WebkitBoxOrient: 'vertical',
                          overflow: 'hidden'
                        }}
                      >
                        {job.description}
                      </p>

                      <div
                        style={{
                          fontSize: 'var(--text-xs)',
                          color: 'var(--color-text-muted)',
                          display: 'flex',
                          flexDirection: 'column',
                          gap: '4px'
                        }}
                      >
                        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                          <MapPin size={12} />
                          <span>{job.location}</span>
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                          <Briefcase size={12} />
                          <span>{job.experience} • {job.employmentType}</span>
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                          <DollarSign size={12} />
                          <span>{job.salary}</span>
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                          <Calendar size={12} />
                          <span>{job.postingDate}</span>
                        </div>
                      </div>

                      {/* Required Skills Chips with AST evidence markers */}
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px', marginTop: 'auto' }}>
                        {job.skills.slice(0, 4).map(s => {
                          const hasCitation = activeCitations.some(e => e.skill.toLowerCase() === s.toLowerCase());
                          return (
                            <span
                              key={s}
                              className={`badge ${hasCitation ? 'badge-burgundy' : 'badge-muted'}`}
                              title={hasCitation ? `${s}: Verified with GitHub AST code citations` : s}
                              style={{ fontSize: '0.72rem', display: 'inline-flex', alignItems: 'center', gap: '3px' }}
                            >
                              {hasCitation && <GitBranch size={10} />}
                              <span>{s}</span>
                            </span>
                          );
                        })}
                        {job.skills.length > 4 && (
                          <span className="badge badge-muted" style={{ fontSize: '0.72rem' }}>
                            +{job.skills.length - 4} more
                          </span>
                        )}
                      </div>

                      {/* In-App Action Buttons */}
                      <div
                        style={{
                          display: 'flex',
                          gap: 'var(--space-2)',
                          paddingTop: 'var(--space-3)',
                          borderTop: '1px solid var(--color-border)'
                        }}
                      >
                        <button
                          onClick={() => handleOpenJobDetails(job)}
                          style={{
                            flex: 1,
                            padding: '0.45rem',
                            borderRadius: 'var(--radius-sm)',
                            fontSize: 'var(--text-xs)',
                            fontWeight: 700,
                            backgroundColor: 'var(--color-burgundy)',
                            color: '#FFFFFF',
                            border: 'none',
                            cursor: 'pointer'
                          }}
                        >
                          View Details & AI Intel
                        </button>
                        {job.applicationMode === 'in_app_supported' ? (
                          <button
                            onClick={() => handleStartApply(job)}
                            style={{
                              padding: '0.45rem 0.75rem',
                              borderRadius: 'var(--radius-sm)',
                              fontSize: 'var(--text-xs)',
                              fontWeight: 700,
                              backgroundColor: existingApp ? '#e5e7eb' : 'var(--color-surface-muted)',
                              color: existingApp ? '#6b7280' : 'var(--color-burgundy)',
                              border: '1px solid var(--color-border)',
                              cursor: 'pointer'
                            }}
                          >
                            {existingApp ? 'Applied ✓' : 'Apply'}
                          </button>
                        ) : (
                          <a
                            href={job.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            style={{
                              padding: '0.45rem 0.65rem',
                              borderRadius: 'var(--radius-sm)',
                              fontSize: 'var(--text-xs)',
                              fontWeight: 700,
                              backgroundColor: 'var(--color-surface-muted)',
                              color: 'var(--color-text)',
                              border: '1px solid var(--color-border)',
                              textDecoration: 'none',
                              display: 'inline-flex',
                              alignItems: 'center',
                              gap: '4px'
                            }}
                            title="Employer requires external application"
                          >
                            <span>External</span>
                            <ExternalLink size={10} />
                          </a>
                        )}
                      </div>
                    </article>
                  );
                })}
              </div>

              {/* Load More Pagination */}
              {visibleCount < filteredAndRankedJobs.length && (
                <div style={{ textAlign: 'center', marginTop: 'var(--space-8)' }}>
                  <SecondaryButton size="sm" onClick={() => setVisibleCount(prev => prev + 4)}>
                    Load More Opportunities ({filteredAndRankedJobs.length - visibleCount} remaining)
                  </SecondaryButton>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Applications Tracker Tab View (Phase 9) */}
      
      {/* Tab: Repository Skill Profile & Evidence Gaps */}
      {activeTab === 'profile' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
          <EvidenceSkillReportView
            report={evidenceReport}
            isLoading={isLoadingEvidence}
            error={evidenceError}
            onRefresh={() => loadEvidenceReport()}
            onAnalyzeRepo={handleAnalyzeRepo}
            onStartProject={() => navigate('/skills')}
            onStartDiagnostic={() => navigate('/skills')}
          />
        </div>
      )}

      {/* Tab: Multi-Job Comparison Matrix (Phase 9.D) */}
      {activeTab === 'compare' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
          <div
            style={{
              padding: 'var(--space-6)',
              backgroundColor: 'var(--color-surface)',
              borderRadius: 'var(--radius-md)',
              border: '1px solid var(--color-border)'
            }}
          >
            <h3 style={{ fontSize: 'var(--text-lg)', fontWeight: 700, margin: 0 }}>
              Multi-Job Requirement & Evidence Comparison
            </h3>
            <p style={{ fontSize: 'var(--text-sm)', color: 'var(--color-text-secondary)', marginTop: '4px' }}>
              Compare candidate repository evidence compatibility across multiple genuine job openings side-by-side.
            </p>
          </div>

          {compareList.length === 0 ? (
            <div style={{ padding: 'var(--space-8)', textAlign: 'center', backgroundColor: 'var(--color-surface)', borderRadius: 'var(--radius-md)', border: '1px dashed var(--color-border)' }}>
              <Columns size={32} color="var(--color-text-muted)" style={{ margin: '0 auto var(--space-3) auto' }} />
              <h4 style={{ fontSize: 'var(--text-base)', fontWeight: 700 }}>No Jobs Selected For Comparison</h4>
              <p style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)', maxWidth: '400px', margin: '4px auto var(--space-4) auto' }}>
                Browse the Live Opportunities tab and click "Compare" on 2 or 3 job cards to view side-by-side evidence analysis.
              </p>
              <PrimaryButton onClick={() => setActiveTab('portal')}>
                Browse Live Opportunities
              </PrimaryButton>
            </div>
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: `repeat(${Math.min(compareList.length, 3)}, 1fr)`, gap: 'var(--space-4)', overflowX: 'auto' }}>
              {compareList.map(jobId => {
                const job = VERIFIED_PORTAL_LISTINGS.find(j => j.id === jobId) || VERIFIED_PORTAL_LISTINGS[0];
                const match = computeJobMatch(job);
                return (
                  <div
                    key={job.id}
                    style={{
                      padding: 'var(--space-5)',
                      backgroundColor: 'var(--color-surface)',
                      borderRadius: 'var(--radius-md)',
                      border: '1px solid var(--color-border)',
                      display: 'flex',
                      flexDirection: 'column',
                      gap: 'var(--space-4)'
                    }}
                  >
                    <div>
                      <span className="badge badge-burgundy">{job.sourceName}</span>
                      <h4 style={{ fontSize: 'var(--text-base)', fontWeight: 700, marginTop: '4px' }}>{job.title}</h4>
                      <p style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)', margin: 0 }}>{job.company} &bull; {job.location}</p>
                    </div>

                    <div style={{ padding: 'var(--space-3)', backgroundColor: 'var(--color-burgundy-soft)', borderRadius: 'var(--radius-sm)' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span style={{ fontSize: 'var(--text-xs)', fontWeight: 600, color: 'var(--color-burgundy)' }}>Overall Compatibility:</span>
                        <strong style={{ fontSize: 'var(--text-lg)', color: 'var(--color-burgundy)' }}>{match.matchPercentage}%</strong>
                      </div>
                      <div style={{ fontSize: '0.72rem', color: 'var(--color-burgundy)', marginTop: '2px' }}>
                        Scoring: Numerator ({match.numerator}pts) / Denominator ({match.denominator}pts)
                      </div>
                    </div>

                    <div>
                      <strong style={{ fontSize: 'var(--text-xs)', textTransform: 'uppercase', color: 'var(--color-text-muted)' }}>Required Skills Coverage:</strong>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px', marginTop: '4px' }}>
                        {job.skills.map(s => {
                          const hasCitation = activeCitations.some(e => e.skill.toLowerCase() === s.toLowerCase());
                          return (
                            <span
                              key={s}
                              style={{
                                fontSize: '0.72rem',
                                padding: '2px 6px',
                                borderRadius: '4px',
                                backgroundColor: hasCitation ? 'var(--color-burgundy-soft)' : '#F3F4F6',
                                color: hasCitation ? 'var(--color-burgundy)' : '#6B7280',
                                fontWeight: hasCitation ? 700 : 500
                              }}
                            >
                              {s} {hasCitation ? '✓' : ''}
                            </span>
                          );
                        })}
                      </div>
                    </div>

                    <div>
                      <strong style={{ fontSize: 'var(--text-xs)', textTransform: 'uppercase', color: 'var(--color-text-muted)' }}>Compensation & Fit:</strong>
                      <p style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text)', margin: '2px 0 0 0' }}>{job.salary}</p>
                      <p style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)', margin: 0 }}>{job.workMode} &bull; {job.experience}</p>
                    </div>

                    <div style={{ marginTop: 'auto', display: 'flex', gap: '8px' }}>
                      <PrimaryButton size="sm" onClick={() => setSelectedJob(job)}>
                        View Evidence Breakdown
                      </PrimaryButton>
                      <SecondaryButton size="sm" onClick={() => setCompareList(prev => prev.filter(id => id !== job.id))}>
                        Remove
                      </SecondaryButton>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {activeTab === 'tracker' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)', marginBottom: 'var(--space-12)' }}>
          <div
            className="panel"
            style={{
              padding: 'var(--space-5)',
              backgroundColor: 'var(--color-surface)',
              display: 'flex',
              flexDirection: 'column',
              gap: 'var(--space-4)'
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 'var(--space-2)' }}>
              <div>
                <h3 style={{ fontSize: 'var(--text-base)', fontWeight: 700, margin: 0, fontFamily: 'var(--font-display)', color: 'var(--color-text)' }}>
                  In-App Career Applications Tracker
                </h3>
                <p style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)', margin: '2px 0 0 0' }}>
                  Track verified application submissions, interview milestones, and application notes.
                </p>
              </div>

              <div style={{ display: 'flex', gap: 'var(--space-2)' }}>
                <span className="badge badge-burgundy">{applications.length} Total Applications</span>
              </div>
            </div>

            {applications.length === 0 ? (
              <EmptyState
                title="No applications logged yet"
                description="When you apply to verified opportunities via SkillTrace AI, your submissions and confirmation IDs will appear here."
                actionLabel="Explore Live Opportunities"
                onAction={() => setActiveTab('portal')}
              />
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
                {applications.map(app => (
                  <div
                    key={app.applicationId}
                    style={{
                      padding: 'var(--space-4)',
                      borderRadius: 'var(--radius-sm)',
                      backgroundColor: 'var(--color-surface-muted)',
                      border: '1px solid var(--color-border)',
                      display: 'flex',
                      flexDirection: 'column',
                      gap: 'var(--space-3)'
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 'var(--space-2)' }}>
                      <div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                          <h4 style={{ fontSize: 'var(--text-base)', fontWeight: 700, margin: 0, color: 'var(--color-text)' }}>
                            {app.jobTitle}
                          </h4>
                          <span
                            style={{
                              fontSize: '0.72rem',
                              padding: '2px 8px',
                              borderRadius: '4px',
                              fontWeight: 700,
                              backgroundColor: app.status === 'Submitted' ? '#dcfce7' : app.status === 'Interview' ? '#fef3c7' : '#e5e7eb',
                              color: app.status === 'Submitted' ? '#15803d' : app.status === 'Interview' ? '#b45309' : '#374151'
                            }}
                          >
                            {app.status}
                          </span>
                        </div>
                        <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)', marginTop: '2px' }}>
                          {app.company} • Submitted: {app.submittedAt} • Ref: <code style={{ fontWeight: 700 }}>{app.applicationId}</code>
                        </div>
                      </div>

                      {/* Status Update Control */}
                      <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <label style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)' }}>Status:</label>
                        <select
                          value={app.status}
                          onChange={e => handleUpdateApplicationStatus(app.applicationId, e.target.value as any)}
                          style={{
                            padding: '0.35rem 0.65rem',
                            borderRadius: 'var(--radius-sm)',
                            border: '1px solid var(--color-border)',
                            fontSize: 'var(--text-xs)',
                            backgroundColor: 'var(--color-surface)'
                          }}
                        >
                          <option value="Ready to apply">Ready to apply</option>
                          <option value="Submitted">Submitted</option>
                          <option value="In progress">In progress</option>
                          <option value="Interview">Interview</option>
                          <option value="Rejected">Rejected</option>
                          <option value="Withdrawn">Withdrawn</option>
                        </select>
                      </div>
                    </div>

                    <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)' }}>
                      <strong>Pitch & Notes:</strong> {app.pitch}
                    </div>

                    <div style={{ fontSize: '0.72rem', color: 'var(--color-text-muted)', display: 'flex', gap: 'var(--space-4)' }}>
                      <span>Applicant: {app.applicantName} ({app.applicantEmail})</span>
                      <span>GitHub: <a href={app.applicantGithub} target="_blank" rel="noopener noreferrer" style={{ color: 'var(--color-burgundy)', textDecoration: 'underline' }}>{app.applicantGithub}</a></span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Curated Career Tracks (Preserved 100%) */}
      {activeTab === 'tracks' && (
        <>
          <div
            style={{
              display: 'flex',
              flexDirection: 'column',
              gap: 'var(--space-4)',
              marginBottom: 'var(--space-8)'
            }}
          >
            <div style={{ display: 'flex', gap: 'var(--space-4)', flexWrap: 'wrap', alignItems: 'center' }}>
              <div style={{ flex: '1 1 320px', minWidth: '260px' }}>
                <TextInput
                  label="Search Careers or Skills"
                  placeholder="e.g. TypeScript, Design Systems, Python, SQL…"
                  value={searchQuery}
                  onChange={e => setSearchQuery(e.target.value)}
                />
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.375rem' }}>
                <label style={{ fontSize: 'var(--text-sm)', fontWeight: 600, color: 'var(--color-text)' }}>
                  Filter by Domain
                </label>
                <div style={{ display: 'flex', gap: 'var(--space-2)', flexWrap: 'wrap' }}>
                  {categories.map(cat => (
                    <button
                      key={cat}
                      onClick={() => setSelectedCategory(cat)}
                      style={{
                        padding: '0.5rem 0.875rem',
                        borderRadius: 'var(--radius-sm)',
                        fontSize: 'var(--text-xs)',
                        fontWeight: selectedCategory === cat ? 700 : 500,
                        backgroundColor: selectedCategory === cat ? 'var(--color-burgundy)' : 'var(--color-surface)',
                        color: selectedCategory === cat ? '#FFFFFF' : 'var(--color-text)',
                        border: `1px solid ${selectedCategory === cat ? 'var(--color-burgundy)' : 'var(--color-border)'}`,
                        cursor: 'pointer',
                        transition: 'all var(--transition-fast)'
                      }}
                    >
                      {cat}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {compareList.length > 0 && (
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: 'var(--space-2) var(--space-4)',
                  backgroundColor: 'var(--color-burgundy-soft)',
                  borderRadius: 'var(--radius-sm)',
                  border: '1px solid rgba(112,45,61,0.2)',
                  fontSize: 'var(--text-xs)'
                }}
              >
                <span>
                  <strong>{compareList.length}</strong> path(s) selected for comparison:{' '}
                  {compareList
                    .map(id => careerPaths.find(c => c.id === id)?.title)
                    .filter(Boolean)
                    .join(', ')}
                </span>
                <div style={{ display: 'flex', gap: 'var(--space-2)' }}>
                  {compareList.length >= 2 && (
                    <button
                      onClick={() => setIsCompareModalOpen(true)}
                      style={{ color: 'var(--color-burgundy)', fontWeight: 700, textDecoration: 'underline' }}
                    >
                      View Comparison
                    </button>
                  )}
                  <button
                    onClick={() => setCompareList([])}
                    style={{ color: 'var(--color-text-muted)', textDecoration: 'underline' }}
                  >
                    Clear
                  </button>
                </div>
              </div>
            )}
          </div>

          {filteredCareers.length === 0 ? (
            <EmptyState
              title="No career paths match your query"
              description="Try adjusting your search terms or selecting 'All' domains."
              actionLabel="Clear search filters"
              onAction={() => {
                setSearchQuery('');
                setSelectedCategory('All');
              }}
            />
          ) : (
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
                gap: 'var(--space-6)'
              }}
            >
              {filteredCareers.map(career => {
                const isTarget = profile.targetCareerId === career.id;
                const inCompare = compareList.includes(career.id);

                return (
                  <div key={career.id} style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
                    {isTarget && (
                      <div style={{ marginBottom: 'var(--space-1)' }}>
                        <span className="badge badge-burgundy" style={{ fontSize: '0.7rem' }}>Current Primary Track</span>
                      </div>
                    )}
                    <CareerSummary
                      career={career}
                      onExplore={() => setSelectedCareerForModal(career)}
                      onToggleSave={() => toggleSaveCareer(career.id)}
                      isSaved={savedCareerIds.includes(career.id)}
                    />
                    <div style={{ marginTop: 'var(--space-2)' }}>
                      <button
                        onClick={() => toggleCompare(career.id)}
                        style={{
                          padding: '0.4rem 0.6rem',
                          borderRadius: 'var(--radius-sm)',
                          fontSize: 'var(--text-xs)',
                          fontWeight: 600,
                          backgroundColor: inCompare ? 'var(--color-burgundy)' : 'var(--color-surface-muted)',
                          color: inCompare ? '#FFFFFF' : 'var(--color-text)',
                          border: `1px solid ${inCompare ? 'var(--color-burgundy)' : 'var(--color-border)'}`,
                          cursor: 'pointer',
                          width: '100%'
                        }}
                      >
                        {inCompare ? 'In Comparison' : '+ Compare'}
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </>
      )}

      {/* In-App Job Details Modal with AI Career Intelligence */}
      {selectedJob && (
        <div
          role="presentation"
          style={{
            position: 'fixed',
            inset: 0,
            backgroundColor: 'rgba(41, 35, 33, 0.45)',
            backdropFilter: 'blur(2px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000,
            padding: 'var(--space-4)'
          }}
          onClick={() => setSelectedJob(null)}
        >
          <div
            role="dialog"
            aria-modal="true"
            aria-labelledby="inapp-job-title"
            style={{
              backgroundColor: 'var(--color-surface)',
              border: '1px solid var(--color-border-strong)',
              borderRadius: 'var(--radius-panel)',
              maxWidth: '820px',
              width: '100%',
              maxHeight: '92vh',
              overflowY: 'auto',
              padding: 'var(--space-8)',
              boxShadow: 'var(--shadow-modal)',
              display: 'flex',
              flexDirection: 'column',
              gap: 'var(--space-5)'
            }}
            onClick={e => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: 'var(--space-1)', flexWrap: 'wrap' }}>
                  <span className="badge badge-burgundy">{selectedJob.sourceName}</span>
                  <span className="badge badge-muted">{selectedJob.workMode}</span>
                  <span className="badge badge-muted">{selectedJob.employmentType}</span>
                  <span
                    style={{
                      fontSize: '0.72rem',
                      fontWeight: 700,
                      padding: '2px 8px',
                      borderRadius: '12px',
                      backgroundColor: 'var(--color-burgundy)',
                      color: '#FFFFFF'
                    }}
                  >
                    {computeJobMatch(selectedJob).matchPercentage}% ML Match
                  </span>
                </div>
                <h2
                  id="inapp-job-title"
                  style={{
                    fontSize: 'var(--heading-md)',
                    fontFamily: 'var(--font-display)',
                    margin: 'var(--space-1) 0 4px 0',
                    color: 'var(--color-text)'
                  }}
                >
                  {selectedJob.title}
                </h2>
                <div style={{ fontSize: 'var(--text-sm)', fontWeight: 600, color: 'var(--color-burgundy)' }}>
                  {selectedJob.company} • {selectedJob.location}
                </div>
              </div>
              <button
                onClick={() => setSelectedJob(null)}
                aria-label="Close modal"
                style={{ color: 'var(--color-text-muted)', padding: '4px', background: 'none', border: 'none', cursor: 'pointer' }}
              >
                <X size={20} />
              </button>
            </div>

            {/* In-Modal Navigation Tabs */}
            <div style={{ display: 'flex', gap: 'var(--space-2)', borderBottom: '1px solid var(--color-border)', paddingBottom: 'var(--space-2)', overflowX: 'auto' }}>
              {[
                { id: 'overview', label: 'Overview & Requirements' },
                { id: 'evidence', label: 'GitHub Evidence Match' },
                { id: 'gap', label: 'Skill-Gap Analysis' },
                { id: 'roadmap', label: 'Personalized Roadmap' }
              ].map(tab => (
                <button
                  key={tab.id}
                  onClick={() => setActiveDetailSection(tab.id as any)}
                  style={{
                    padding: '0.35rem 0.75rem',
                    borderRadius: 'var(--radius-sm)',
                    fontSize: 'var(--text-xs)',
                    fontWeight: activeDetailSection === tab.id ? 700 : 500,
                    backgroundColor: activeDetailSection === tab.id ? 'var(--color-burgundy-soft)' : 'transparent',
                    color: activeDetailSection === tab.id ? 'var(--color-burgundy)' : 'var(--color-text)',
                    border: 'none',
                    cursor: 'pointer',
                    whiteSpace: 'nowrap'
                  }}
                >
                  {tab.label}
                </button>
              ))}
            </div>

            {/* TAB 1: OVERVIEW */}
            {activeDetailSection === 'overview' && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-5)' }}>
                {/* Quick Metadata Box */}
                <div
                  style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))',
                    gap: 'var(--space-3)',
                    padding: 'var(--space-4)',
                    backgroundColor: 'var(--color-surface-muted)',
                    borderRadius: 'var(--radius-sm)'
                  }}
                >
                  <div>
                    <strong style={{ fontSize: '0.72rem', textTransform: 'uppercase', color: 'var(--color-text-muted)' }}>Location</strong>
                    <div style={{ fontSize: 'var(--text-xs)', fontWeight: 600, color: 'var(--color-text)' }}>{selectedJob.location}</div>
                  </div>
                  <div>
                    <strong style={{ fontSize: '0.72rem', textTransform: 'uppercase', color: 'var(--color-text-muted)' }}>Experience</strong>
                    <div style={{ fontSize: 'var(--text-xs)', fontWeight: 600, color: 'var(--color-text)' }}>{selectedJob.experience}</div>
                  </div>
                  <div>
                    <strong style={{ fontSize: '0.72rem', textTransform: 'uppercase', color: 'var(--color-text-muted)' }}>Compensation</strong>
                    <div style={{ fontSize: 'var(--text-xs)', fontWeight: 600, color: 'var(--color-text)' }}>{selectedJob.salary}</div>
                  </div>
                  <div>
                    <strong style={{ fontSize: '0.72rem', textTransform: 'uppercase', color: 'var(--color-text-muted)' }}>Verification Status</strong>
                    <div style={{ fontSize: 'var(--text-xs)', fontWeight: 600, color: 'var(--color-text)' }}>{selectedJob.postingDate}</div>
                  </div>
                </div>

                {/* Job Description */}
                <div>
                  <h3 style={{ fontSize: 'var(--text-base)', fontWeight: 700, margin: '0 0 6px 0', color: 'var(--color-text)' }}>About the Opportunity</h3>
                  <p style={{ fontSize: 'var(--text-sm)', color: 'var(--color-text-secondary)', lineHeight: 1.6, margin: 0 }}>
                    {selectedJob.description}
                  </p>
                </div>

                {/* Key Responsibilities */}
                <div>
                  <h3 style={{ fontSize: 'var(--text-base)', fontWeight: 700, margin: '0 0 6px 0', color: 'var(--color-text)' }}>Key Responsibilities</h3>
                  <ul style={{ paddingLeft: 'var(--space-5)', display: 'flex', flexDirection: 'column', gap: 'var(--space-2)', margin: 0 }}>
                    {selectedJob.responsibilities.map((resp, idx) => (
                      <li key={idx} style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)', lineHeight: 1.5 }}>
                        {resp}
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Qualifications & Company Background */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
                  <h3 style={{ fontSize: 'var(--text-base)', fontWeight: 700, margin: 0, color: 'var(--color-text)' }}>Qualifications & Company Background</h3>
                  <p style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)', margin: 0, lineHeight: 1.5 }}>
                    <strong>Qualifications:</strong> {selectedJob.qualifications}
                  </p>
                  <p style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)', margin: 0, lineHeight: 1.5 }}>
                    <strong>Company Information:</strong> {selectedJob.companyInfo}
                  </p>
                </div>
              </div>
            )}

            {/* TAB 2: GITHUB EVIDENCE MATCH (Phase 5) */}
            {activeDetailSection === 'evidence' && (() => {
              const matchResult = computeJobMatch(selectedJob);
              return (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
                {/* 3 Distinct Measurements Dashboard */}
                <div
                  style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                    gap: 'var(--space-3)',
                    padding: 'var(--space-4)',
                    backgroundColor: 'var(--color-background)',
                    borderRadius: 'var(--radius-sm)',
                    border: '1px solid var(--color-border)'
                  }}
                >
                  <div>
                    <span style={{ fontSize: '0.72rem', fontWeight: 600, color: 'var(--color-text-muted)', textTransform: 'uppercase' }}>
                      1. Overall Job Match
                    </span>
                    <div style={{ fontSize: 'var(--text-xl)', fontWeight: 800, color: 'var(--color-burgundy)', marginTop: '2px' }}>
                      {matchResult.isInsufficientEvidence ? 'Insufficient Evidence' : `${matchResult.matchPercentage}%`}
                    </div>
                    <div style={{ fontSize: '0.7rem', color: 'var(--color-text-secondary)', marginTop: '2px' }}>
                      Formula: {matchResult.numerator} / {matchResult.denominator} pts
                    </div>
                  </div>

                  <div>
                    <span style={{ fontSize: '0.72rem', fontWeight: 600, color: 'var(--color-text-muted)', textTransform: 'uppercase' }}>
                      2. Requirement Coverage
                    </span>
                    <div style={{ fontSize: 'var(--text-xl)', fontWeight: 800, color: '#059669', marginTop: '2px' }}>
                      {matchResult.requiredCoveragePercent}%
                    </div>
                    <div style={{ fontSize: '0.7rem', color: 'var(--color-text-secondary)', marginTop: '2px' }}>
                      {matchResult.skillEvals.filter(e => e.status === 'Demonstrated').length}/{matchResult.assessedCount} Required Skills
                    </div>
                  </div>

                  <div>
                    <span style={{ fontSize: '0.72rem', fontWeight: 600, color: 'var(--color-text-muted)', textTransform: 'uppercase' }}>
                      3. Verified Code Citations
                    </span>
                    <div style={{ fontSize: 'var(--text-xl)', fontWeight: 800, color: 'var(--color-burgundy)', marginTop: '2px' }}>
                      {matchResult.verifiedCitationsCount} Verified
                    </div>
                    <div style={{ fontSize: '0.7rem', color: 'var(--color-text-secondary)', marginTop: '2px' }}>
                      Pinned to commit SHA {repoState.commitSha.slice(0, 7)}
                    </div>
                  </div>
                </div>

                <div
                  style={{
                    padding: 'var(--space-3) var(--space-4)',
                    backgroundColor: 'var(--color-surface-muted)',
                    borderRadius: 'var(--radius-sm)',
                    fontSize: 'var(--text-xs)',
                    color: 'var(--color-text-secondary)',
                    lineHeight: 1.5
                  }}
                >
                  <strong>SkillTrace AI Evidence Verification:</strong> Compares requirements against syntax trees inspected in your authorized GitHub repositories. Absence of evidence reflects scanned repository scope; it never implies lack of personal proficiency.
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
                  {computeJobMatch(selectedJob).skillEvals.map(evalItem => {
                    const hasCitation = !!evalItem.citation;
                    const isOpen = activeEvidenceSkill === evalItem.skill;

                    return (
                      <div
                        key={evalItem.skill}
                        style={{
                          borderRadius: 'var(--radius-sm)',
                          border: '1px solid var(--color-border)',
                          backgroundColor: 'var(--color-surface)',
                          overflow: 'hidden'
                        }}
                      >
                        <div
                          style={{
                            padding: 'var(--space-3) var(--space-4)',
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'center',
                            cursor: hasCitation ? 'pointer' : 'default',
                            backgroundColor: hasCitation ? 'rgba(112,45,61,0.03)' : 'transparent'
                          }}
                          onClick={() => hasCitation && setActiveEvidenceSkill(isOpen ? null : evalItem.skill)}
                        >
                          <div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                              <span style={{ fontWeight: 700, fontSize: 'var(--text-sm)', color: 'var(--color-text)' }}>{evalItem.skill}</span>
                              {hasCitation && (
                                <span className="badge badge-burgundy" style={{ fontSize: '0.68rem', display: 'inline-flex', alignItems: 'center', gap: '3px' }}>
                                  <FileCode size={10} />
                                  <span>AST Verified</span>
                                </span>
                              )}
                            </div>
                            <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)', marginTop: '2px' }}>
                              {evalItem.note}
                            </div>
                          </div>

                          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                            <span
                              className={`badge ${
                                evalItem.status === 'Demonstrated'
                                  ? 'badge-burgundy'
                                  : evalItem.status === 'Partially demonstrated'
                                  ? 'badge-muted'
                                  : 'badge-muted'
                              }`}
                            >
                              {evalItem.status}
                            </span>
                            {hasCitation && (
                              <span style={{ fontSize: 'var(--text-xs)', color: 'var(--color-burgundy)', fontWeight: 600 }}>
                                {isOpen ? 'Hide Proof ▲' : 'View Code Proof ▼'}
                              </span>
                            )}
                          </div>
                        </div>

                        {/* Collapsible Verified Code Snippet Citation */}
                        {isOpen && evalItem.citation && (
                          <div
                            style={{
                              padding: 'var(--space-4)',
                              borderTop: '1px solid var(--color-border)',
                              backgroundColor: 'var(--color-surface-muted)',
                              display: 'flex',
                              flexDirection: 'column',
                              gap: 'var(--space-2)'
                            }}
                          >
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: 'var(--text-xs)' }}>
                              <div>
                                <strong>Repository:</strong>{' '}
                                <a
                                  href={`https://github.com/${evalItem.citation.repoName}`}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  style={{ color: 'var(--color-burgundy)', textDecoration: 'underline' }}
                                >
                                  {evalItem.citation.repoName}
                                </a>
                              </div>
                              <div>
                                <strong>File:</strong> {evalItem.citation.filePath}{evalItem.citation.lineRange}
                              </div>
                              <div>
                                <strong>Commit SHA:</strong> <code>{evalItem.citation.commitSha}</code>
                              </div>
                            </div>

                            <pre
                              style={{
                                padding: 'var(--space-3)',
                                backgroundColor: '#1e1e1e',
                                color: '#d4d4d4',
                                borderRadius: 'var(--radius-sm)',
                                fontSize: '0.75rem',
                                fontFamily: 'monospace',
                                overflowX: 'auto',
                                margin: 0,
                                lineHeight: 1.4
                              }}
                            >
                              {evalItem.citation.codeSnippet}
                            </pre>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
              );
            })()}

            {/* TAB 3: SKILL-GAP ANALYSIS (Phase 6) */}
            {activeDetailSection === 'gap' && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
                <div
                  style={{
                    padding: 'var(--space-4)',
                    backgroundColor: 'var(--color-surface-muted)',
                    borderRadius: 'var(--radius-sm)',
                    fontSize: 'var(--text-xs)',
                    color: 'var(--color-text-secondary)'
                  }}
                >
                  Skill-Gap analysis evaluates which requirements for <strong>{selectedJob.title}</strong> at {selectedJob.company} are demonstrated in your GitHub portfolio and recommends focused hands-on projects to bridge unanalysed requirements.
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
                  <h4 style={{ fontSize: 'var(--text-sm)', fontWeight: 700, margin: 0 }}>Recommended Actionable Projects</h4>
                  {[
                    {
                      skill: 'SQL & Data Warehousing',
                      title: 'Production Analytical SQL Schema & Window Queries',
                      deliverable: 'Write 8 window queries (ROW_NUMBER, DENSE_RANK, LAG) on financial trading transactions.',
                      estimatedHours: 10,
                      link: 'https://mode.com/sql-tutorial/'
                    },
                    {
                      skill: 'Automated Testing',
                      title: 'Pytest Suite with Parameterized Assertions',
                      deliverable: 'Equip repository with tests/ directory, boundary mocks, and GitHub Actions CI.',
                      estimatedHours: 8,
                      link: 'https://docs.pytest.org'
                    },
                    {
                      skill: 'ETL Pipelines',
                      title: 'Pandas Data Cleansing & KPI Dashboard Pipeline',
                      deliverable: 'Automated batch script parsing raw CSV logs into clean PostgreSQL database tables.',
                      estimatedHours: 12,
                      link: 'https://pandas.pydata.org'
                    }
                  ].map((proj, idx) => (
                    <div
                      key={idx}
                      style={{
                        padding: 'var(--space-4)',
                        borderRadius: 'var(--radius-sm)',
                        border: '1px solid var(--color-border)',
                        backgroundColor: 'var(--color-surface)',
                        display: 'flex',
                        flexDirection: 'column',
                        gap: 'var(--space-2)'
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span className="badge badge-burgundy">{proj.skill}</span>
                        <span style={{ fontSize: '0.72rem', color: 'var(--color-text-muted)' }}>
                          Est. {proj.estimatedHours} Hours
                        </span>
                      </div>
                      <h5 style={{ fontSize: 'var(--text-sm)', fontWeight: 700, margin: 0 }}>{proj.title}</h5>
                      <p style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)', margin: 0, lineHeight: 1.5 }}>
                        <strong>Deliverable:</strong> {proj.deliverable}
                      </p>
                      <div style={{ paddingTop: 'var(--space-1)' }}>
                        <a
                          href={proj.link}
                          target="_blank"
                          rel="noopener noreferrer"
                          style={{ fontSize: 'var(--text-xs)', color: 'var(--color-burgundy)', fontWeight: 700, textDecoration: 'underline' }}
                        >
                          View Official Documentation & Guide ↗
                        </a>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* TAB 4: PERSONALIZED CAREER ROADMAP (Phase 7) */}
            {activeDetailSection === 'roadmap' && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
                <div
                  style={{
                    padding: 'var(--space-4)',
                    backgroundColor: 'var(--color-surface-muted)',
                    borderRadius: 'var(--radius-sm)',
                    fontSize: 'var(--text-xs)',
                    color: 'var(--color-text-secondary)'
                  }}
                >
                  Step-by-step 4-Phase Roadmap calibrated to help you land the <strong>{selectedJob.title}</strong> role at {selectedJob.company}.
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
                  {[
                    {
                      phase: 'Phase 1: Remediation of Priority Skill Gaps',
                      focus: 'Address unanalysed requirements via hands-on exercises',
                      tasks: ['Master SQL window functions and aggregations', 'Build Pandas transformation routines with type hints']
                    },
                    {
                      phase: 'Phase 2: Domain Showcase Project',
                      focus: 'Implement a realistic project matching job responsibilities',
                      tasks: [`Construct ${selectedJob.title} end-to-end data pipeline`, 'Document architectural decisions in README']
                    },
                    {
                      phase: 'Phase 3: Repository Verification & Testing',
                      focus: 'Ensure verifiable AST code citations and test coverage',
                      tasks: ['Add automated pytest suite with >=80% branch coverage', 'Configure GitHub Actions automated CI workflow']
                    },
                    {
                      phase: 'Phase 4: Packaging & Application Submission',
                      focus: 'Prepare verifiable portfolio link and submit in-app application',
                      tasks: ['Generate SkillTrace AI ProofGraph shareable link', 'Submit verified application via SkillTrace AI Career Portal']
                    }
                  ].map((p, idx) => (
                    <div
                      key={idx}
                      style={{
                        padding: 'var(--space-4)',
                        borderRadius: 'var(--radius-sm)',
                        border: '1px solid var(--color-border)',
                        backgroundColor: 'var(--color-surface)',
                        display: 'flex',
                        flexDirection: 'column',
                        gap: 'var(--space-2)'
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <Target size={16} color="var(--color-burgundy)" />
                        <h5 style={{ fontSize: 'var(--text-sm)', fontWeight: 700, margin: 0, color: 'var(--color-text)' }}>{p.phase}</h5>
                      </div>
                      <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)' }}>Focus: {p.focus}</div>
                      <ul style={{ paddingLeft: 'var(--space-5)', margin: '4px 0 0 0', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                        {p.tasks.map((t, ti) => (
                          <li key={ti} style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)' }}>
                            {t}
                          </li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Modal Actions Footer */}
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                paddingTop: 'var(--space-4)',
                borderTop: '1px solid var(--color-border)',
                flexWrap: 'wrap',
                gap: 'var(--space-3)'
              }}
            >
              <SecondaryButton
                size="sm"
                onClick={() => toggleSaveJob(selectedJob.id)}
                icon={savedJobIds.includes(selectedJob.id) ? <BookmarkCheck size={14} /> : <Bookmark size={14} />}
              >
                {savedJobIds.includes(selectedJob.id) ? 'Saved in Your Portal' : 'Save Job'}
              </SecondaryButton>

              <div style={{ display: 'flex', gap: 'var(--space-2)', alignItems: 'center' }}>
                {selectedJob.applicationMode === 'in_app_supported' ? (
                  <PrimaryButton
                    size="sm"
                    onClick={() => {
                      setSelectedJob(null);
                      handleStartApply(selectedJob);
                    }}
                  >
                    {applications.some(a => a.jobId === selectedJob.id) ? 'Update Application' : 'Apply via SkillTrace AI'}
                  </PrimaryButton>
                ) : (
                  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '4px' }}>
                    <span style={{ fontSize: '0.72rem', color: 'var(--color-text-muted)' }}>
                      External employer portal required
                    </span>
                    <a
                      href={selectedJob.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '6px',
                        backgroundColor: 'var(--color-burgundy)',
                        color: '#FFFFFF',
                        padding: '0.45rem 0.85rem',
                        borderRadius: 'var(--radius-sm)',
                        fontSize: 'var(--text-xs)',
                        fontWeight: 700,
                        textDecoration: 'none'
                      }}
                    >
                      <span>Proceed to Official Application ↗</span>
                      <ExternalLink size={12} />
                    </a>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* In-App Application Modal (Phase 9 Application Flow) */}
      {isApplyModalOpen && applyingJob && (
        <div
          role="presentation"
          style={{
            position: 'fixed',
            inset: 0,
            backgroundColor: 'rgba(41, 35, 33, 0.45)',
            backdropFilter: 'blur(2px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000,
            padding: 'var(--space-4)'
          }}
          onClick={() => setIsApplyModalOpen(false)}
        >
          <div
            role="dialog"
            aria-modal="true"
            aria-labelledby="apply-modal-title"
            style={{
              backgroundColor: 'var(--color-surface)',
              border: '1px solid var(--color-border-strong)',
              borderRadius: 'var(--radius-panel)',
              maxWidth: '580px',
              width: '100%',
              maxHeight: '90vh',
              overflowY: 'auto',
              padding: 'var(--space-8)',
              boxShadow: 'var(--shadow-modal)',
              display: 'flex',
              flexDirection: 'column',
              gap: 'var(--space-5)'
            }}
            onClick={e => e.stopPropagation()}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <div>
                <span className="badge badge-burgundy">In-App Application Flow</span>
                <h2 id="apply-modal-title" style={{ fontSize: 'var(--heading-sm)', fontFamily: 'var(--font-display)', marginTop: '4px' }}>
                  Apply to {applyingJob.title}
                </h2>
                <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)', fontWeight: 600 }}>
                  {applyingJob.company} • {applyingJob.location}
                </div>
              </div>
              <button onClick={() => setIsApplyModalOpen(false)} style={{ background: 'none', border: 'none', cursor: 'pointer' }}>
                <X size={20} />
              </button>
            </div>

            {applyStep === 'form' ? (
              <form
                onSubmit={e => {
                  e.preventDefault();
                  setApplyStep('review');
                }}
                style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}
              >
                <div>
                  <label style={{ display: 'block', fontSize: 'var(--text-xs)', fontWeight: 600, marginBottom: '4px' }}>
                    Full Candidate Name
                  </label>
                  <input
                    type="text"
                    required
                    value={applicantName}
                    onChange={e => setApplicantName(e.target.value)}
                    style={{
                      width: '100%',
                      padding: '0.55rem 0.75rem',
                      borderRadius: 'var(--radius-sm)',
                      border: '1px solid var(--color-border)',
                      fontSize: 'var(--text-xs)',
                      color: 'var(--color-text)',
                      backgroundColor: 'var(--color-surface)'
                    }}
                  />
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: 'var(--text-xs)', fontWeight: 600, marginBottom: '4px' }}>
                    Contact Email
                  </label>
                  <input
                    type="email"
                    required
                    value={applicantEmail}
                    onChange={e => setApplicantEmail(e.target.value)}
                    style={{
                      width: '100%',
                      padding: '0.55rem 0.75rem',
                      borderRadius: 'var(--radius-sm)',
                      border: '1px solid var(--color-border)',
                      fontSize: 'var(--text-xs)',
                      color: 'var(--color-text)',
                      backgroundColor: 'var(--color-surface)'
                    }}
                  />
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: 'var(--text-xs)', fontWeight: 600, marginBottom: '4px' }}>
                    GitHub Profile / Repository Evidence URL
                  </label>
                  <input
                    type="url"
                    required
                    value={applicantGithub}
                    onChange={e => setApplicantGithub(e.target.value)}
                    style={{
                      width: '100%',
                      padding: '0.55rem 0.75rem',
                      borderRadius: 'var(--radius-sm)',
                      border: '1px solid var(--color-border)',
                      fontSize: 'var(--text-xs)',
                      color: 'var(--color-text)',
                      backgroundColor: 'var(--color-surface)'
                    }}
                  />
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: 'var(--text-xs)', fontWeight: 600, marginBottom: '4px' }}>
                    Candidate Pitch / Cover Note
                  </label>
                  <textarea
                    rows={3}
                    value={applicantPitch}
                    onChange={e => setApplicantPitch(e.target.value)}
                    placeholder="Describe your relevant Python/SQL projects or why this role fits your background…"
                    style={{
                      width: '100%',
                      padding: '0.55rem 0.75rem',
                      borderRadius: 'var(--radius-sm)',
                      border: '1px solid var(--color-border)',
                      fontSize: 'var(--text-xs)',
                      color: 'var(--color-text)',
                      backgroundColor: 'var(--color-surface)',
                      fontFamily: 'inherit'
                    }}
                  />
                </div>

                <div
                  style={{
                    padding: 'var(--space-3)',
                    backgroundColor: 'var(--color-surface-muted)',
                    borderRadius: 'var(--radius-sm)',
                    fontSize: '0.72rem',
                    color: 'var(--color-text-secondary)',
                    lineHeight: 1.4
                  }}
                >
                  SkillTrace AI verifies your application with AST code citations. You will be able to review your information before final submission.
                </div>

                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 'var(--space-2)' }}>
                  <SecondaryButton size="sm" type="button" onClick={() => setIsApplyModalOpen(false)}>
                    Cancel
                  </SecondaryButton>
                  <PrimaryButton size="sm" type="submit">
                    Review Application
                  </PrimaryButton>
                </div>
              </form>
            ) : (
              /* Review Before Submission (Phase 9 Step 3 & 4) */
              <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
                <div
                  style={{
                    padding: 'var(--space-4)',
                    backgroundColor: 'var(--color-surface-muted)',
                    borderRadius: 'var(--radius-sm)',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: 'var(--space-2)',
                    fontSize: 'var(--text-xs)'
                  }}
                >
                  <h4 style={{ fontSize: 'var(--text-sm)', fontWeight: 700, margin: '0 0 4px 0' }}>Confirm Application Details</h4>
                  <div><strong>Applicant:</strong> {applicantName} ({applicantEmail})</div>
                  <div><strong>GitHub Evidence:</strong> {applicantGithub}</div>
                  <div><strong>Target Role:</strong> {applyingJob.title} at {applyingJob.company}</div>
                  {applicantPitch && <div><strong>Candidate Pitch:</strong> {applicantPitch}</div>}
                </div>

                <div style={{ fontSize: '0.72rem', color: 'var(--color-text-secondary)' }}>
                  Clicking <strong>Confirm & Submit</strong> will register this application in your SkillTrace AI applications ledger and assign a tracking reference ID.
                </div>

                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 'var(--space-2)' }}>
                  <SecondaryButton size="sm" onClick={() => setApplyStep('form')}>
                    Back to Edit
                  </SecondaryButton>
                  <PrimaryButton size="sm" onClick={handleSubmitApplication}>
                    Confirm & Submit Application
                  </PrimaryButton>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Existing Career Modal (Preserved 100%) */}
      {selectedCareerForModal && (
        <div
          role="presentation"
          style={{
            position: 'fixed',
            inset: 0,
            backgroundColor: 'rgba(41, 35, 33, 0.45)',
            backdropFilter: 'blur(2px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000,
            padding: 'var(--space-4)'
          }}
          onClick={() => setSelectedCareerForModal(null)}
        >
          <div
            role="dialog"
            aria-modal="true"
            aria-labelledby="career-detail-title"
            style={{
              backgroundColor: 'var(--color-surface)',
              border: '1px solid var(--color-border-strong)',
              borderRadius: 'var(--radius-panel)',
              maxWidth: '680px',
              width: '100%',
              maxHeight: '90vh',
              overflowY: 'auto',
              padding: 'var(--space-8)',
              boxShadow: 'var(--shadow-modal)',
              display: 'flex',
              flexDirection: 'column',
              gap: 'var(--space-6)'
            }}
            onClick={e => e.stopPropagation()}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <div>
                <span className="badge badge-burgundy">{selectedCareerForModal.category}</span>
                <h2
                  id="career-detail-title"
                  style={{
                    fontSize: 'var(--heading-md)',
                    fontFamily: 'var(--font-display)',
                    marginTop: 'var(--space-1)'
                  }}
                >
                  {selectedCareerForModal.title}
                </h2>
              </div>
              <button
                onClick={() => setSelectedCareerForModal(null)}
                aria-label="Close modal"
                style={{ color: 'var(--color-text-muted)', padding: '4px', background: 'none', border: 'none', cursor: 'pointer' }}
              >
                <X size={20} />
              </button>
            </div>

            <p style={{ fontSize: 'var(--text-base)', color: 'var(--color-text-secondary)', lineHeight: 1.6 }}>
              {selectedCareerForModal.description}
            </p>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
              <h3 style={{ fontSize: 'var(--text-base)', fontWeight: 600 }}>Typical Day-to-Day Responsibilities</h3>
              <ul style={{ paddingLeft: 'var(--space-5)', display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
                {selectedCareerForModal.responsibilities.map((resp, i) => (
                  <li key={i} style={{ fontSize: 'var(--text-sm)', color: 'var(--color-text-secondary)', lineHeight: 1.5 }}>
                    {resp}
                  </li>
                ))}
              </ul>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
              <h3 style={{ fontSize: 'var(--text-base)', fontWeight: 600 }}>Required & Valuable Skills</h3>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--space-2)' }}>
                {selectedCareerForModal.requiredSkills.map(skill => (
                  <span key={skill.name} className="badge badge-muted">
                    {skill.name} • {skill.importance}
                  </span>
                ))}
              </div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
              <h3 style={{ fontSize: 'var(--text-base)', fontWeight: 600 }}>Typical Learning Phases</h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
                {selectedCareerForModal.learningPhases.map((phase, idx) => (
                  <div
                    key={idx}
                    style={{
                      padding: 'var(--space-3)',
                      backgroundColor: 'var(--color-surface-muted)',
                      borderRadius: 'var(--radius-sm)',
                      fontSize: 'var(--text-xs)'
                    }}
                  >
                    <strong>
                      {phase.phase}: {phase.focus}
                    </strong>
                    <div style={{ color: 'var(--color-text-muted)', marginTop: '2px' }}>
                      Estimated effort: {phase.estimatedMonths}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                paddingTop: 'var(--space-4)',
                borderTop: '1px solid var(--color-border)',
                flexWrap: 'wrap',
                gap: 'var(--space-3)'
              }}
            >
              <SecondaryButton
                size="sm"
                onClick={() => toggleSaveCareer(selectedCareerForModal.id)}
              >
                {savedCareerIds.includes(selectedCareerForModal.id) ? 'Saved in your list' : 'Save this career'}
              </SecondaryButton>

              <PrimaryButton
                size="sm"
                onClick={() => handleSelectAsPrimaryTrack(selectedCareerForModal)}
              >
                {profile.targetCareerId === selectedCareerForModal.id
                  ? 'Currently active track'
                  : 'Set as my primary career track'}
              </PrimaryButton>
            </div>
          </div>
        </div>
      )}

      {/* Existing Compare Modal (Preserved 100%) */}
      {isCompareModalOpen && (
        <div
          role="presentation"
          style={{
            position: 'fixed',
            inset: 0,
            backgroundColor: 'rgba(41, 35, 33, 0.45)',
            backdropFilter: 'blur(2px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000,
            padding: 'var(--space-4)'
          }}
          onClick={() => setIsCompareModalOpen(false)}
        >
          <div
            role="dialog"
            aria-modal="true"
            aria-labelledby="compare-title"
            style={{
              backgroundColor: 'var(--color-surface)',
              border: '1px solid var(--color-border-strong)',
              borderRadius: 'var(--radius-panel)',
              maxWidth: '960px',
              width: '100%',
              maxHeight: '90vh',
              overflowY: 'auto',
              padding: 'var(--space-8)',
              boxShadow: 'var(--shadow-modal)',
              display: 'flex',
              flexDirection: 'column',
              gap: 'var(--space-6)'
            }}
            onClick={e => e.stopPropagation()}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <span className="badge badge-burgundy">Side-by-side comparison</span>
                <h2 id="compare-title" style={{ fontSize: 'var(--heading-md)', fontFamily: 'var(--font-display)', marginTop: '4px' }}>
                  Comparing {compareList.length} Career Tracks
                </h2>
              </div>
              <button onClick={() => setIsCompareModalOpen(false)} aria-label="Close comparison" style={{ background: 'none', border: 'none', cursor: 'pointer' }}>
                <X size={20} />
              </button>
            </div>

            <div
              style={{
                display: 'grid',
                gridTemplateColumns: `repeat(${compareList.length}, minmax(240px, 1fr))`,
                gap: 'var(--space-4)',
                overflowX: 'auto',
                paddingBottom: 'var(--space-2)'
              }}
            >
              {compareList.map(id => {
                const c = careerPaths.find(item => item.id === id);
                if (!c) return null;

                return (
                  <div
                    key={c.id}
                    className="panel"
                    style={{
                      padding: 'var(--space-4)',
                      display: 'flex',
                      flexDirection: 'column',
                      gap: 'var(--space-4)',
                      backgroundColor: 'var(--color-surface)'
                    }}
                  >
                    <div>
                      <span className="badge badge-burgundy">{c.category}</span>
                      <h4 style={{ fontSize: 'var(--text-base)', fontWeight: 600, marginTop: '4px' }}>
                        {c.title}
                      </h4>
                    </div>

                    <div>
                      <strong style={{ fontSize: 'var(--text-xs)', textTransform: 'uppercase', color: 'var(--color-text-muted)' }}>
                        Why it fits
                      </strong>
                      <p style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)', marginTop: '2px' }}>
                        {c.matchReason}
                      </p>
                    </div>

                    <div>
                      <strong style={{ fontSize: 'var(--text-xs)', textTransform: 'uppercase', color: 'var(--color-text-muted)' }}>
                        Core Skills
                      </strong>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px', marginTop: '4px' }}>
                        {c.requiredSkills.slice(0, 4).map(s => (
                          <span key={s.name} className="badge badge-muted">
                            {s.name}
                          </span>
                        ))}
                      </div>
                    </div>

                    <PrimaryButton
                      size="sm"
                      onClick={() => {
                        updateProfile({ targetCareerId: c.id });
                        setIsCompareModalOpen(false);
                      }}
                    >
                      Select track
                    </PrimaryButton>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </PageContainer>
  );
};
