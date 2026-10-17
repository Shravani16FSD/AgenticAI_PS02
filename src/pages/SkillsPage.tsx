import React, { useState, useEffect, useCallback } from 'react';
import {
  Award,
  Play,
  RotateCcw,
  CheckCircle2,
  XCircle,
  AlertCircle,
  Code2,
  Terminal,
  Lightbulb,
  ArrowRight,
  Sparkles,
  Check,
  Unlock,
  ShieldCheck
} from 'lucide-react';
import { PageContainer, PageHeading } from '../components/ui/Typography';
import { PrimaryButton, SecondaryButton } from '../components/ui/Buttons';
import { ProgressIndicator } from '../components/ui/FeedbackStates';
import { useApp } from '../context/AppContext';
import { apiClient } from '../services/apiClient';
import type {
  ArenaDashboardData,
  DiagnosticAssessmentData,
  DiagnosticSubmitResult,
  MiniProjectData,
  ProjectRunResult,
  ProjectSubmitResult,
  AdaptiveChallengeRec
} from '../types/arena';

type ArenaViewMode = 'dashboard' | 'diagnostic' | 'project';

const FALLBACK_DIAGNOSTIC: DiagnosticAssessmentData = {
  id: 'diag-py-101',
  career_id: 'ai-product-engineer',
  skill_name: 'Python Fundamentals',
  title: 'Python Architecture & Fundamentals Diagnostic',
  difficulty: 'beginner',
  time_limit_mins: 15,
  questions: [
    {
      id: 'q1',
      type: 'mcq',
      skill_tag: 'Python Architecture',
      text: 'In Python, what is the output of calling a function twice if it defines `def append_to(element, target=[]): target.append(element); return target` when called with append_to(1) then append_to(2)?',
      options: ['[1, 2]', '[2]', 'TypeError: mutable default argument', 'None']
    },
    {
      id: 'q2',
      type: 'mcq',
      skill_tag: 'Comprehensions',
      text: 'Predict the value of `result` after executing:\nitems = [("cpu", 80), ("ram", 45), ("disk", 92)]\nresult = {k: v for k, v in items if v > 50}',
      options: ["{'cpu': 80, 'disk': 92}", "{'ram': 45}", "{80: 'cpu', 92: 'disk'}", '[(cpu, 80), (disk, 92)]']
    },
    {
      id: 'q3',
      type: 'short_answer',
      skill_tag: 'Slicing & Memory',
      text: 'What Python slicing syntax reverses a sequence `nums` without creating an in-place mutation? (e.g. nums[::-1])'
    }
  ]
};

const FALLBACK_PROJECT: MiniProjectData = {
  id: 'py-data-cleaner-101',
  career_id: 'ai-product-engineer',
  skill_name: 'Python Fundamentals',
  difficulty: 'beginner',
  title: 'Trading Log Ingestion & Data Cleaner',
  tagline: 'Build a resilient data ingestion function to sanitize messy financial transaction records.',
  description: `### Objective
Implement the function \`clean_and_aggregate_transactions(records: list[dict]) -> dict\`.

### Requirements
1. **Drop Invalid Records**: Any transaction missing \`'amount'\`, \`'symbol'\`, or \`'timestamp'\` must be omitted. If \`'amount'\` is negative or 0, omit it.
2. **Normalize Symbols**: Convert all symbols to uppercase string (e.g. \`'aapl'\` -> \`'AAPL'\`).
3. **Aggregate Summary**:
   - \`'total_volume'\`: Sum of valid amounts (float rounded to 2 decimal places).
   - \`'symbol_counts'\`: Dictionary mapping each uppercase symbol to its count of valid transactions.
   - \`'valid_transactions'\`: Count of processed valid items.
4. If \`records\` is empty or contains no valid transactions, return:
   \`{'total_volume': 0.0, 'symbol_counts': {}, 'valid_transactions': 0}\`.`,
  sample_data: `[
  {"symbol": "aapl", "amount": 150.50, "timestamp": "2025-01-15T10:00:00Z"},
  {"symbol": "GOOG", "amount": -20.00, "timestamp": "2025-01-15T10:01:00Z"},
  {"symbol": "msft", "amount": 210.25, "timestamp": "2025-01-15T10:02:00Z"},
  {"amount": 100.0}
]`,
  starter_code: `def clean_and_aggregate_transactions(records: list[dict]) -> dict:
    """
    Clean and aggregate financial transaction records.
    """
    # TODO: Implement sanitization and rollup logic
    return {
        "total_volume": 0.0,
        "symbol_counts": {},
        "valid_transactions": 0
    }
`,
  public_test_cases: [
    {
      name: "Empty transactions list returns zeros",
      function_name: "clean_and_aggregate_transactions",
      expected: "{'total_volume': 0.0, 'symbol_counts': {}, 'valid_transactions': 0}"
    },
    {
      name: "Filters negative amounts and normalizes lowercase symbols",
      function_name: "clean_and_aggregate_transactions",
      expected: "{'total_volume': 150.5, 'symbol_counts': {'AAPL': 1}, 'valid_transactions': 1}"
    }
  ],
  hints: [
    "Check that all required keys ('amount', 'symbol', 'timestamp') exist and 'amount' > 0 before proceeding.",
    "Use str(symbol).strip().upper() to ensure uniform uppercase formatting for dictionary keys.",
    "Use round(total_volume, 2) when returning the aggregate total volume."
  ],
  rubric: [
    { criterion: "Correctness", weight: "60%", description: "Passes all edge cases, negative amount filters, and empty list checks" },
    { criterion: "Code Structure", weight: "20%", description: "Clean control flow, safe dictionary access, no redundant loops" },
    { criterion: "Hint Efficiency", weight: "20%", description: "Completed with minimal hint reliance" }
  ]
};

export const SkillsPage: React.FC = () => {
  const { profile, activeUserId } = useApp();

  // Mode state
  const [viewMode, setViewMode] = useState<ArenaViewMode>('dashboard');
  const [catalog, setCatalog] = useState<{ diagnostics: any[]; projects: any[] }>({
    diagnostics: [
      { id: 'diag-py-101', title: 'Python Architecture & Fundamentals Diagnostic', skill_name: 'Python Fundamentals', difficulty: 'beginner', time_limit_mins: 15, question_count: 5 },
      { id: 'diag-data-101', title: 'Data Engineering & Pipeline Diagnostic', skill_name: 'Data Analysis & SQL', difficulty: 'beginner', time_limit_mins: 15, question_count: 4 }
    ],
    projects: [
      { id: 'py-data-cleaner-101', title: 'Trading Log Ingestion & Data Cleaner', skill_name: 'Python Fundamentals', difficulty: 'beginner', hints_count: 4, public_tests_count: 2 },
      { id: 'py-metrics-aggregator-201', title: 'Event Stream Metrics & Cohort Aggregator', skill_name: 'Data Analysis & SQL', difficulty: 'intermediate', hints_count: 3, public_tests_count: 1 }
    ]
  });

  // Dashboard Data State
  const [dashboardData, setDashboardData] = useState<ArenaDashboardData | null>(null);
  const [isLoadingDashboard, setIsLoadingDashboard] = useState<boolean>(true);
  const [dashboardError, setDashboardError] = useState<string | null>(null);

  // Diagnostic State
  const [diagnostic, setDiagnostic] = useState<DiagnosticAssessmentData | null>(null);
  const [diagAnswers, setDiagAnswers] = useState<Record<string, string>>({});
  const [isSubmittingDiag, setIsSubmittingDiag] = useState<boolean>(false);
  const [diagResult, setDiagResult] = useState<DiagnosticSubmitResult | null>(null);
  const [diagError, setDiagError] = useState<string | null>(null);

  // In-Browser Project Workspace State
  const [project, setProject] = useState<MiniProjectData | null>(null);
  const [userCode, setUserCode] = useState<string>('');
  const [unlockedHintsCount, setUnlockedHintsCount] = useState<number>(0);
  const [activeWorkspaceTab, setActiveWorkspaceTab] = useState<'instructions' | 'sample_data' | 'hints'>('instructions');

  // Execution & Submission State
  const [isRunningSandbox, setIsRunningSandbox] = useState<boolean>(false);
  const [isSubmittingProject, setIsSubmittingProject] = useState<boolean>(false);
  const [sandboxResult, setSandboxResult] = useState<ProjectRunResult | null>(null);
  const [submissionResult, setSubmissionResult] = useState<ProjectSubmitResult | null>(null);
  const [workspaceError, setWorkspaceError] = useState<string | null>(null);

  // 1. Fetch Dashboard & Catalog
  const loadDashboardAndCatalog = useCallback(async () => {
    setIsLoadingDashboard(true);
    setDashboardError(null);
    try {
      const [dash, cat] = await Promise.all([
        apiClient.getArenaDashboard(),
        apiClient.getArenaCatalog(profile.targetCareerId)
      ]);

      if (dash) {
        setDashboardData(dash);
      }
      if (cat && cat.diagnostics && cat.diagnostics.length > 0) {
        setCatalog(cat);
      }
    } catch (err: any) {
      setDashboardError('Unable to sync with evaluation server. Verify the backend is running on port 8000.');
    } finally {
      setIsLoadingDashboard(false);
    }
  }, [profile.targetCareerId]);

  useEffect(() => {
    loadDashboardAndCatalog();
  }, [loadDashboardAndCatalog, activeUserId]);

  // 2. Launch Diagnostic
  const handleStartDiagnostic = async (diagId: string) => {
    setDiagResult(null);
    setDiagAnswers({});
    setDiagError(null);
    setViewMode('diagnostic');

    try {
      const data = await apiClient.getDiagnosticAssessment(diagId);
      if (data) {
        setDiagnostic(data);
      } else {
        setDiagnostic(FALLBACK_DIAGNOSTIC);
      }
    } catch (err: any) {
      setDiagnostic(FALLBACK_DIAGNOSTIC);
    }
  };

  // 3. Submit Diagnostic
  const handleSubmitDiagnostic = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!diagnostic) return;

    setIsSubmittingDiag(true);
    setDiagError(null);
    try {
      const res = await apiClient.submitDiagnosticAssessment(diagnostic.id, diagAnswers);
      if (res) {
        setDiagResult(res);
        // Refresh dashboard background data
        apiClient.getArenaDashboard().then(d => { if (d) setDashboardData(d); }).catch(() => {});
      } else {
        setDiagError('Submission could not be recorded.');
      }
    } catch (err: any) {
      setDiagError('Diagnostic submission failed. Please try again.');
    } finally {
      setIsSubmittingDiag(false);
    }
  };

  // 4. Launch Project Workspace
  const handleStartProject = async (projId: string) => {
    setSandboxResult(null);
    setSubmissionResult(null);
    setWorkspaceError(null);
    setUnlockedHintsCount(0);
    setActiveWorkspaceTab('instructions');
    setViewMode('project');

    try {
      const data = await apiClient.getProjectDefinition(projId);
      if (data) {
        setProject(data);
        setUserCode(data.starter_code || '');
      } else {
        setProject(FALLBACK_PROJECT);
        setUserCode(FALLBACK_PROJECT.starter_code || '');
      }
    } catch (err: any) {
      setProject(FALLBACK_PROJECT);
      setUserCode(FALLBACK_PROJECT.starter_code || '');
    }
  };

  // 5. Run Public Test Cases in Sandbox (Dry Run)
  const handleRunCodeSandbox = async () => {
    if (!project) return;
    setIsRunningSandbox(true);
    setWorkspaceError(null);
    try {
      const res = await apiClient.runProjectTest(project.id, userCode);
      if (res) {
        setSandboxResult(res);
      } else {
        setWorkspaceError('Sandbox execution returned no response.');
      }
    } catch (err: any) {
      setWorkspaceError('Sandbox runner failed to respond.');
    } finally {
      setIsRunningSandbox(false);
    }
  };

  // 6. Submit Project for Evaluation (Public + Hidden tests + Rubric)
  const handleSubmitProjectEvaluation = async () => {
    if (!project) return;
    setIsSubmittingProject(true);
    setWorkspaceError(null);
    try {
      const res = await apiClient.submitProject(project.id, userCode, unlockedHintsCount);
      if (res) {
        setSubmissionResult(res);
        setSandboxResult({
          success: res.status === 'passed',
          status: res.status,
          score: res.score,
          tests_passed: res.tests_passed,
          tests_total: res.tests_total,
          test_results: res.test_results,
          output: res.execution_output,
          error: '',
          execution_time_ms: res.execution_time_ms
        });
        // Refresh dashboard data
        apiClient.getArenaDashboard().then(d => { if (d) setDashboardData(d); }).catch(() => {});
      } else {
        setWorkspaceError('Evaluation engine did not return a verdict.');
      }
    } catch (err: any) {
      setWorkspaceError('Project evaluation failed. Please retry.');
    } finally {
      setIsSubmittingProject(false);
    }
  };

  // 7. Handle Adaptive Action Button click
  const handleAdaptiveAction = (rec: AdaptiveChallengeRec) => {
    if (rec.action_type === 'diagnostic') {
      handleStartDiagnostic(rec.recommended_id);
    } else {
      handleStartProject(rec.recommended_id);
    }
  };

  // Determine active adaptive recommendation
  const adaptiveRec = dashboardData?.adaptive_recommendation;

  return (
    <PageContainer>
      {/* Editorial Header */}
      <PageHeading
        eyebrow="SKILLPROOF ARENA & PROGRESS"
        title="Evidence-grounded skill mastery."
        description="Mastery is proven through verified code execution and diagnostic rigor — never through passive time or uninspected stubs."
        actions={
          <div style={{ display: 'flex', gap: 'var(--space-2)' }}>
            <SecondaryButton
              size="sm"
              onClick={() => {
                setViewMode('dashboard');
                loadDashboardAndCatalog();
              }}
              style={{
                backgroundColor: viewMode === 'dashboard' ? 'var(--color-surface-muted)' : 'transparent',
                fontWeight: viewMode === 'dashboard' ? 700 : 500
              }}
            >
              Arena Dashboard
            </SecondaryButton>
            <SecondaryButton
              size="sm"
              onClick={() => handleStartDiagnostic(catalog.diagnostics[0]?.id || 'diag-py-101')}
              style={{
                backgroundColor: viewMode === 'diagnostic' ? 'var(--color-surface-muted)' : 'transparent',
                fontWeight: viewMode === 'diagnostic' ? 700 : 500
              }}
            >
              Take Diagnostic
            </SecondaryButton>
            <PrimaryButton
              size="sm"
              onClick={() => handleStartProject(catalog.projects[0]?.id || 'py-data-cleaner-101')}
              icon={<Code2 size={14} />}
            >
              Launch Mini-Project
            </PrimaryButton>
          </div>
        }
      />

      {/* Mode 1: Main Evidence Dashboard */}
      {viewMode === 'dashboard' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
          {dashboardError && (
            <div style={{ padding: 'var(--space-3)', backgroundColor: '#FEF2F2', border: '1px solid #EF4444', color: '#991B1B', borderRadius: 'var(--radius-sm)', fontSize: 'var(--text-xs)' }}>
              {dashboardError}
            </div>
          )}

          {isLoadingDashboard && !dashboardData && (
            <div style={{ padding: 'var(--space-8)', textAlign: 'center', color: 'var(--color-text-secondary)', fontSize: 'var(--text-xs)' }}>
              Loading SkillProof Arena records...
            </div>
          )}
          {/* Dynamic Adaptive Challenge Banner (Feature C) */}
          {adaptiveRec && (
            <div
              style={{
                padding: 'var(--space-6)',
                backgroundColor: 'var(--color-surface)',
                borderRadius: 'var(--radius-panel)',
                border: '1.5px solid var(--color-burgundy)',
                boxShadow: 'var(--shadow-sm)',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                flexWrap: 'wrap',
                gap: 'var(--space-4)',
                position: 'relative',
                overflow: 'hidden'
              }}
            >
              <div style={{ maxWidth: '680px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
                  <span className="badge badge-burgundy" style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <Sparkles size={12} />
                    ADAPTIVE NEXT CHALLENGE
                  </span>
                  <span style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                    Target: {adaptiveRec.skill_name}
                  </span>
                </div>
                <h3 style={{ fontSize: 'var(--text-lg)', fontFamily: 'var(--font-display)', fontWeight: 700, margin: '0 0 6px 0', color: 'var(--color-text)' }}>
                  {adaptiveRec.target_title}
                </h3>
                <p style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)', lineHeight: 1.6, margin: 0 }}>
                  {adaptiveRec.reason}
                </p>
              </div>

              <PrimaryButton
                size="md"
                onClick={() => handleAdaptiveAction(adaptiveRec)}
                icon={<ArrowRight size={16} />}
              >
                {adaptiveRec.action_type === 'project' ? 'Enter Project Workspace' : 'Start Diagnostic'}
              </PrimaryButton>
            </div>
          )}

          {/* KPI Summary Strip */}
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
              gap: 'var(--space-4)'
            }}
          >
            <div className="panel" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-1)' }}>
              <span style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                Verified Skill Competencies
              </span>
              <span className="tabular-nums" style={{ fontSize: '1.75rem', fontFamily: 'var(--font-display)', fontWeight: 700, color: 'var(--color-burgundy)' }}>
                {dashboardData?.demonstrated_skills?.length || 0} Skills
              </span>
              <span style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)' }}>
                Proven through tests & code assertions
              </span>
            </div>

            <div className="panel" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-1)' }}>
              <span style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                Skills Needing Practice
              </span>
              <span className="tabular-nums" style={{ fontSize: '1.75rem', fontFamily: 'var(--font-display)', fontWeight: 700, color: '#D97706' }}>
                {dashboardData?.skills_to_practice?.length || 0} Identified
              </span>
              <span style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)' }}>
                Flagged from failed boundary tests
              </span>
            </div>

            <div className="panel" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-1)' }}>
              <span style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                Completed Evaluations
              </span>
              <span className="tabular-nums" style={{ fontSize: '1.75rem', fontFamily: 'var(--font-display)', fontWeight: 700, color: 'var(--color-text)' }}>
                {(dashboardData?.diagnostic_history?.length || 0) + (dashboardData?.project_history?.length || 0)} Attempts
              </span>
              <span style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)' }}>
                {dashboardData?.project_history?.length || 0} practical projects evaluated
              </span>
            </div>

            <div className="panel" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-1)' }}>
              <span style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                Study Time (Secondary)
              </span>
              <span className="tabular-nums" style={{ fontSize: '1.75rem', fontFamily: 'var(--font-display)', fontWeight: 700, color: 'var(--color-text)' }}>
                {dashboardData?.study_time_hours || 0} hrs
              </span>
              <span style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)' }}>
                Secondary contextual indicator
              </span>
            </div>
          </div>

          {/* Evidence-Based Mastery Records (Feature E) */}
          <section className="panel" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Award size={18} color="var(--color-burgundy)" />
                <h3 style={{ fontSize: 'var(--text-base)', fontFamily: 'var(--font-display)', fontWeight: 700, margin: 0 }}>
                  Demonstrated Skill Mastery Evidence
                </h3>
              </div>
              <span style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)' }}>
                Requires dual confirmation (conceptual diagnostic + practical code)
              </span>
            </div>

            {(!dashboardData?.mastery_records || dashboardData.mastery_records.length === 0) ? (
              <div style={{ padding: 'var(--space-6)', textAlign: 'center', color: 'var(--color-text-secondary)', fontSize: 'var(--text-xs)' }}>
                No verified skill records established yet. Complete a diagnostic assessment or mini-project to generate evidence.
              </div>
            ) : (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 'var(--space-4)' }}>
                {dashboardData.mastery_records.map(record => {
                  const levelColors = {
                    novice: { bg: '#F3F4F6', color: '#4B5563', label: 'Novice' },
                    competent: { bg: '#EFF6FF', color: '#2563EB', label: 'Competent' },
                    proficient: { bg: 'var(--color-burgundy-soft)', color: 'var(--color-burgundy)', label: 'Proficient' },
                    advanced: { bg: '#ECFDF5', color: '#059669', label: 'Advanced Mastery' }
                  }[record.mastery_level] || { bg: '#F3F4F6', color: '#4B5563', label: record.mastery_level };

                  return (
                    <div
                      key={record.id}
                      style={{
                        padding: 'var(--space-4)',
                        backgroundColor: 'var(--color-surface)',
                        borderRadius: 'var(--radius-sm)',
                        border: '1px solid var(--color-border)',
                        display: 'flex',
                        flexDirection: 'column',
                        gap: 'var(--space-3)'
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                        <div>
                          <h4 style={{ fontSize: 'var(--text-sm)', fontWeight: 700, margin: 0, color: 'var(--color-text)' }}>
                            {record.skill_name}
                          </h4>
                          <span style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)' }}>
                            {record.category}
                          </span>
                        </div>
                        <span
                          style={{
                            fontSize: '0.7rem',
                            fontWeight: 700,
                            padding: '2px 8px',
                            borderRadius: '4px',
                            backgroundColor: levelColors.bg,
                            color: levelColors.color,
                            textTransform: 'uppercase'
                          }}
                        >
                          {levelColors.label}
                        </span>
                      </div>

                      <ProgressIndicator
                        value={record.mastery_score}
                        label={`Evidence Score: ${record.mastery_score}%`}
                        size="sm"
                      />

                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)', borderTop: '1px solid var(--color-border)', paddingTop: 'var(--space-2)' }}>
                        <span>
                          Diagnostic: <strong>{record.diagnostic_score !== null && record.diagnostic_score !== undefined ? `${record.diagnostic_score}%` : '—'}</strong>
                        </span>
                        <span>
                          Practical: <strong>{record.practical_score !== null && record.practical_score !== undefined ? `${record.practical_score}%` : '—'}</strong>
                        </span>
                        <span>
                          Evidence count: <strong>{record.evidence_count}</strong>
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </section>

          {/* Two-Column Log: Diagnostics vs Projects */}
          <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1fr) minmax(0, 1fr)', gap: 'var(--space-6)' }} className="arena-grid">
            {/* Diagnostic Assessment History */}
            <section className="panel" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h3 style={{ fontSize: 'var(--text-sm)', fontFamily: 'var(--font-display)', fontWeight: 700, margin: 0 }}>
                  Diagnostic Attempt History
                </h3>
                <SecondaryButton size="sm" onClick={() => handleStartDiagnostic(catalog.diagnostics[0]?.id || 'diag-py-101')}>
                  New Test
                </SecondaryButton>
              </div>

              {(!dashboardData?.diagnostic_history || dashboardData.diagnostic_history.length === 0) ? (
                <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)', padding: 'var(--space-4) 0' }}>
                  No diagnostics logged yet. Take a 15-minute diagnostic to establish your baseline score.
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
                  {dashboardData.diagnostic_history.map(item => (
                    <div
                      key={item.id}
                      style={{
                        padding: 'var(--space-3)',
                        backgroundColor: 'var(--color-surface-muted)',
                        borderRadius: 'var(--radius-sm)',
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        fontSize: 'var(--text-xs)'
                      }}
                    >
                      <div>
                        <div style={{ fontWeight: 600, color: 'var(--color-text)' }}>
                          {item.skill_name}
                        </div>
                        <span style={{ color: 'var(--color-text-muted)' }}>
                          {item.correct_count} / {item.total_questions} correct &bull; {item.difficulty}
                        </span>
                      </div>
                      <div style={{ textAlign: 'right' }}>
                        <span style={{ fontWeight: 700, color: item.passed ? 'var(--color-success)' : 'var(--color-danger, #EF4444)' }}>
                          {item.score}%
                        </span>
                        <div style={{ fontSize: '0.65rem', color: 'var(--color-text-muted)' }}>
                          {item.passed ? 'Passed' : 'Needs practice'}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </section>

            {/* Practical Project Submissions */}
            <section className="panel" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h3 style={{ fontSize: 'var(--text-sm)', fontFamily: 'var(--font-display)', fontWeight: 700, margin: 0 }}>
                  Practical Project Submissions
                </h3>
                <SecondaryButton size="sm" onClick={() => handleStartProject(catalog.projects[0]?.id || 'py-data-cleaner-101')}>
                  Open Project
                </SecondaryButton>
              </div>

              {(!dashboardData?.project_history || dashboardData.project_history.length === 0) ? (
                <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)', padding: 'var(--space-4) 0' }}>
                  No project attempts evaluated yet. Complete a hands-on project to prove execution capability.
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
                  {dashboardData.project_history.map(item => (
                    <div
                      key={item.id}
                      style={{
                        padding: 'var(--space-3)',
                        backgroundColor: 'var(--color-surface-muted)',
                        borderRadius: 'var(--radius-sm)',
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        fontSize: 'var(--text-xs)'
                      }}
                    >
                      <div>
                        <div style={{ fontWeight: 600, color: 'var(--color-text)' }}>
                          {item.skill_name} Project
                        </div>
                        <span style={{ color: 'var(--color-text-muted)' }}>
                          Tests: {item.tests_passed} / {item.tests_total} &bull; {item.hints_used} hint(s)
                        </span>
                      </div>
                      <div style={{ textAlign: 'right' }}>
                        <span style={{ fontWeight: 700, color: item.status === 'passed' ? 'var(--color-success)' : 'var(--color-danger, #EF4444)' }}>
                          {item.score}%
                        </span>
                        <div style={{ fontSize: '0.65rem', color: 'var(--color-text-muted)' }}>
                          {item.status.toUpperCase()}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </section>
          </div>

          {/* Demonstrated Skills vs Gaps Breakdown */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-6)' }} className="arena-grid">
            <div className="panel">
              <h4 style={{ fontSize: 'var(--text-xs)', fontWeight: 700, textTransform: 'uppercase', color: 'var(--color-success)', marginBottom: 'var(--space-3)' }}>
                Demonstrated Skills & Concepts
              </h4>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                {(!dashboardData?.demonstrated_skills || dashboardData.demonstrated_skills.length === 0) ? (
                  <span style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)' }}>None logged yet.</span>
                ) : (
                  dashboardData.demonstrated_skills.map(s => (
                    <span key={s} className="badge badge-success" style={{ fontSize: '0.75rem' }}>
                      <Check size={11} style={{ marginRight: '4px' }} />
                      {s}
                    </span>
                  ))
                )}
              </div>
            </div>

            <div className="panel">
              <h4 style={{ fontSize: 'var(--text-xs)', fontWeight: 700, textTransform: 'uppercase', color: '#D97706', marginBottom: 'var(--space-3)' }}>
                Targeted Practice Gaps
              </h4>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                {(!dashboardData?.skills_to_practice || dashboardData.skills_to_practice.length === 0) ? (
                  <span style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)' }}>No current weaknesses identified.</span>
                ) : (
                  dashboardData.skills_to_practice.map(s => (
                    <span key={s} className="badge badge-warning" style={{ fontSize: '0.75rem' }}>
                      <AlertCircle size={11} style={{ marginRight: '4px' }} />
                      {s}
                    </span>
                  ))
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Mode 2: Diagnostic Assessment Interface (Feature A) */}
      {viewMode === 'diagnostic' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 'var(--space-3)' }}>
            <div>
              <span className="badge badge-burgundy">DIAGNOSTIC ASSESSMENT</span>
              <h2 style={{ fontSize: 'var(--text-xl)', fontFamily: 'var(--font-display)', fontWeight: 700, margin: '4px 0' }}>
                {diagnostic?.title || 'Diagnostic Evaluation'}
              </h2>
              <span style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)' }}>
                Skill: <strong>{diagnostic?.skill_name}</strong> &bull; Level: <strong>{diagnostic?.difficulty}</strong> &bull; Time: <strong>{diagnostic?.time_limit_mins || 15} mins</strong>
              </span>
            </div>

            <div style={{ display: 'flex', gap: '8px' }}>
              <SecondaryButton size="sm" onClick={() => setViewMode('dashboard')}>
                Exit to Dashboard
              </SecondaryButton>
            </div>
          </div>

          {diagError && (
            <div style={{ padding: 'var(--space-3)', backgroundColor: '#FEF2F2', border: '1px solid #EF4444', color: '#991B1B', borderRadius: 'var(--radius-sm)', fontSize: 'var(--text-xs)' }}>
              {diagError}
            </div>
          )}

          {/* Diagnostic Question Forms or Results */}
          {!diagResult ? (
            <form onSubmit={handleSubmitDiagnostic} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
              {diagnostic?.questions.map((q, idx) => (
                <div
                  key={q.id}
                  className="panel"
                  style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <span style={{ fontSize: 'var(--text-xs)', fontWeight: 700, color: 'var(--color-burgundy)', textTransform: 'uppercase' }}>
                      Question {idx + 1} of {diagnostic.questions.length} &bull; {q.skill_tag}
                    </span>
                    <span className="badge badge-muted" style={{ fontSize: '0.65rem' }}>
                      {q.type.toUpperCase()}
                    </span>
                  </div>

                  <p style={{ fontSize: 'var(--text-sm)', fontWeight: 600, color: 'var(--color-text)', margin: 0, whiteSpace: 'pre-line' }}>
                    {q.text}
                  </p>

                  {/* MCQ Options */}
                  {q.type === 'mcq' && q.options && (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginTop: 'var(--space-2)' }}>
                      {q.options.map(opt => {
                        const isSelected = diagAnswers[q.id] === opt;
                        return (
                          <label
                            key={opt}
                            style={{
                              display: 'flex',
                              alignItems: 'center',
                              gap: '10px',
                              padding: '10px 14px',
                              borderRadius: 'var(--radius-sm)',
                              border: `1.5px solid ${isSelected ? 'var(--color-burgundy)' : 'var(--color-border)'}`,
                              backgroundColor: isSelected ? 'var(--color-burgundy-soft)' : 'var(--color-surface)',
                              cursor: 'pointer',
                              fontSize: 'var(--text-xs)',
                              color: 'var(--color-text)'
                            }}
                          >
                            <input
                              type="radio"
                              name={q.id}
                              value={opt}
                              checked={isSelected}
                              onChange={() => setDiagAnswers(prev => ({ ...prev, [q.id]: opt }))}
                              style={{ accentColor: 'var(--color-burgundy)' }}
                            />
                            <span>{opt}</span>
                          </label>
                        );
                      })}
                    </div>
                  )}

                  {/* Short Answer / Code Snippet input */}
                  {q.type !== 'mcq' && (
                    <input
                      type="text"
                      placeholder="Type your concise answer..."
                      value={diagAnswers[q.id] || ''}
                      onChange={e => setDiagAnswers(prev => ({ ...prev, [q.id]: e.target.value }))}
                      style={{
                        padding: '0.6rem 0.8rem',
                        fontSize: 'var(--text-xs)',
                        borderRadius: 'var(--radius-sm)',
                        border: '1px solid var(--color-border)',
                        backgroundColor: 'var(--color-background)',
                        color: 'var(--color-text)',
                        marginTop: 'var(--space-2)',
                        outline: 'none'
                      }}
                    />
                  )}
                </div>
              ))}

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 'var(--space-3)' }}>
                <SecondaryButton type="button" onClick={() => setViewMode('dashboard')}>
                  Cancel
                </SecondaryButton>
                <PrimaryButton type="submit" disabled={isSubmittingDiag}>
                  {isSubmittingDiag ? 'Scoring Answers...' : 'Submit Diagnostic for Evaluation'}
                </PrimaryButton>
              </div>
            </form>
          ) : (
            /* Diagnostic Result View */
            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
              <div
                className="panel"
                style={{
                  padding: 'var(--space-6)',
                  textAlign: 'center',
                  backgroundColor: diagResult.passed ? 'var(--color-success-bg)' : '#FEF2F2',
                  border: `1.5px solid ${diagResult.passed ? 'var(--color-success)' : '#EF4444'}`
                }}
              >
                <span style={{ fontSize: 'var(--text-xs)', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                  {diagResult.passed ? 'Diagnostic Benchmark Satisfied' : 'Foundational Practice Required'}
                </span>
                <div style={{ fontSize: '3rem', fontFamily: 'var(--font-display)', fontWeight: 800, margin: '8px 0', color: diagResult.passed ? 'var(--color-success)' : '#DC2626' }}>
                  {diagResult.score}%
                </div>
                <p style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)', maxWidth: '520px', margin: '0 auto' }}>
                  {diagResult.correct_count} of {diagResult.total_questions} questions verified correctly. Confidence level evaluated as <strong>{diagResult.confidence_level}</strong>.
                </p>

                <div style={{ display: 'flex', justifyContent: 'center', gap: 'var(--space-3)', marginTop: 'var(--space-4)' }}>
                  <SecondaryButton size="sm" onClick={() => setViewMode('dashboard')}>
                    Return to Dashboard
                  </SecondaryButton>
                  <PrimaryButton size="sm" onClick={() => handleStartProject('py-data-cleaner-101')}>
                    Proceed to Practical Mini-Project
                  </PrimaryButton>
                </div>
              </div>

              {/* Question Feedback Breakdown */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
                <h3 style={{ fontSize: 'var(--text-sm)', fontWeight: 700 }}>Question-by-Question Review</h3>
                {diagResult.question_results.map((res, i) => (
                  <div
                    key={res.question_id}
                    style={{
                      padding: 'var(--space-4)',
                      borderRadius: 'var(--radius-sm)',
                      backgroundColor: 'var(--color-surface)',
                      border: `1px solid ${res.is_correct ? 'var(--color-border)' : '#FCA5A5'}`
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '4px' }}>
                      {res.is_correct ? (
                        <CheckCircle2 size={16} color="var(--color-success)" />
                      ) : (
                        <XCircle size={16} color="#DC2626" />
                      )}
                      <span style={{ fontWeight: 600, fontSize: 'var(--text-xs)' }}>
                        Question {i + 1}: {res.is_correct ? 'Correct' : 'Incorrect'}
                      </span>
                    </div>
                    <p style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text)', margin: '4px 0' }}>
                      {res.question_text}
                    </p>
                    <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)', marginTop: '4px' }}>
                      Your answer: <code>{res.user_answer || '(Blank)'}</code> &bull; Correct: <strong>{res.correct_answer}</strong>
                    </div>
                    {res.explanation && (
                      <div style={{ marginTop: '6px', fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)', backgroundColor: 'var(--color-surface-muted)', padding: '6px 10px', borderRadius: '4px' }}>
                        <strong>Rationale:</strong> {res.explanation}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Mode 3: In-Browser Mini-Project Workspace (Feature B & D) */}
      {viewMode === 'project' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
          {/* Workspace Top Toolbar */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 'var(--space-3)', paddingBottom: 'var(--space-3)', borderBottom: '1px solid var(--color-border)' }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span className="badge badge-burgundy" style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                  <Terminal size={12} />
                  PRACTICAL MINI-PROJECT WORKBENCH
                </span>
                <span className="badge badge-muted" style={{ textTransform: 'uppercase' }}>
                  {project?.difficulty || 'Beginner'}
                </span>
              </div>
              <h2 style={{ fontSize: 'var(--text-lg)', fontFamily: 'var(--font-display)', fontWeight: 700, margin: '2px 0' }}>
                {project?.title || 'Interactive Project Evaluation'}
              </h2>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
              <SecondaryButton
                size="sm"
                onClick={() => setUserCode(project?.starter_code || '')}
                icon={<RotateCcw size={13} />}
                disabled={isRunningSandbox || isSubmittingProject}
              >
                Reset Code
              </SecondaryButton>

              <SecondaryButton
                size="sm"
                onClick={handleRunCodeSandbox}
                disabled={isRunningSandbox || isSubmittingProject}
                icon={<Play size={13} />}
              >
                {isRunningSandbox ? 'Running Sandbox...' : 'Run Public Tests'}
              </SecondaryButton>

              <PrimaryButton
                size="sm"
                onClick={handleSubmitProjectEvaluation}
                disabled={isRunningSandbox || isSubmittingProject}
                icon={<CheckCircle2 size={13} />}
              >
                {isSubmittingProject ? 'Evaluating Rubrics...' : 'Submit for Evaluation'}
              </PrimaryButton>

              <SecondaryButton size="sm" onClick={() => setViewMode('dashboard')}>
                Exit
              </SecondaryButton>
            </div>
          </div>

          {workspaceError && (
            <div style={{ padding: 'var(--space-3)', backgroundColor: '#FEF2F2', border: '1px solid #EF4444', color: '#991B1B', borderRadius: 'var(--radius-sm)', fontSize: 'var(--text-xs)' }}>
              {workspaceError}
            </div>
          )}

          {/* Workbench Grid Layout: Left Specs vs Right Code & Console */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.35fr', gap: 'var(--space-4)', minHeight: '620px' }} className="arena-grid">
            {/* Left Panel: Instructions, Sample Data & Progressive Hints */}
            <div
              style={{
                display: 'flex',
                flexDirection: 'column',
                backgroundColor: 'var(--color-surface)',
                borderRadius: 'var(--radius-panel)',
                border: '1px solid var(--color-border)',
                overflow: 'hidden'
              }}
            >
              {/* Left Sub-tabs */}
              <div style={{ display: 'flex', borderBottom: '1px solid var(--color-border)', backgroundColor: 'var(--color-surface-muted)' }}>
                <button
                  type="button"
                  onClick={() => setActiveWorkspaceTab('instructions')}
                  style={{
                    padding: '10px 16px',
                    fontSize: 'var(--text-xs)',
                    fontWeight: 600,
                    border: 'none',
                    borderBottom: activeWorkspaceTab === 'instructions' ? '2px solid var(--color-burgundy)' : '2px solid transparent',
                    backgroundColor: activeWorkspaceTab === 'instructions' ? 'var(--color-surface)' : 'transparent',
                    color: activeWorkspaceTab === 'instructions' ? 'var(--color-burgundy)' : 'var(--color-text-secondary)',
                    cursor: 'pointer'
                  }}
                >
                  Instructions & Spec
                </button>
                <button
                  type="button"
                  onClick={() => setActiveWorkspaceTab('sample_data')}
                  style={{
                    padding: '10px 16px',
                    fontSize: 'var(--text-xs)',
                    fontWeight: 600,
                    border: 'none',
                    borderBottom: activeWorkspaceTab === 'sample_data' ? '2px solid var(--color-burgundy)' : '2px solid transparent',
                    backgroundColor: activeWorkspaceTab === 'sample_data' ? 'var(--color-surface)' : 'transparent',
                    color: activeWorkspaceTab === 'sample_data' ? 'var(--color-burgundy)' : 'var(--color-text-secondary)',
                    cursor: 'pointer'
                  }}
                >
                  Sample Dataset
                </button>
                <button
                  type="button"
                  onClick={() => setActiveWorkspaceTab('hints')}
                  style={{
                    padding: '10px 16px',
                    fontSize: 'var(--text-xs)',
                    fontWeight: 600,
                    border: 'none',
                    borderBottom: activeWorkspaceTab === 'hints' ? '2px solid var(--color-burgundy)' : '2px solid transparent',
                    backgroundColor: activeWorkspaceTab === 'hints' ? 'var(--color-surface)' : 'transparent',
                    color: activeWorkspaceTab === 'hints' ? 'var(--color-burgundy)' : 'var(--color-text-secondary)',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px'
                  }}
                >
                  <Lightbulb size={12} />
                  <span>Hints ({unlockedHintsCount}/{project?.hints?.length || 0})</span>
                </button>
              </div>

              {/* Tab Contents */}
              <div style={{ padding: 'var(--space-4)', overflowY: 'auto', flex: 1, fontSize: 'var(--text-xs)', lineHeight: 1.6 }}>
                {activeWorkspaceTab === 'instructions' && (
                  <div style={{ whiteSpace: 'pre-line', color: 'var(--color-text)' }}>
                    {project?.description}
                  </div>
                )}

                {activeWorkspaceTab === 'sample_data' && (
                  <div>
                    <span style={{ fontWeight: 600, color: 'var(--color-text-secondary)', display: 'block', marginBottom: '8px' }}>
                      Mock Ingestion Payload:
                    </span>
                    <pre
                      style={{
                        padding: 'var(--space-3)',
                        backgroundColor: 'var(--color-background)',
                        borderRadius: 'var(--radius-sm)',
                        fontFamily: 'monospace',
                        fontSize: '0.75rem',
                        overflowX: 'auto',
                        border: '1px solid var(--color-border)'
                      }}
                    >
                      {project?.sample_data || 'No sample data for this challenge.'}
                    </pre>
                  </div>
                )}

                {activeWorkspaceTab === 'hints' && (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span style={{ fontWeight: 600 }}>Progressive Hints</span>
                      {project && unlockedHintsCount < (project.hints?.length || 0) && (
                        <SecondaryButton
                          size="sm"
                          onClick={() => setUnlockedHintsCount(prev => prev + 1)}
                          icon={<Unlock size={12} />}
                          style={{ fontSize: '0.7rem', padding: '3px 8px' }}
                        >
                          Unlock Next Hint (-12% Rubric Penalty)
                        </SecondaryButton>
                      )}
                    </div>

                    {unlockedHintsCount === 0 ? (
                      <div style={{ padding: 'var(--space-4)', textAlign: 'center', color: 'var(--color-text-muted)' }}>
                        No hints unlocked. Solving challenges without hints awards full rubric points for independent problem solving.
                      </div>
                    ) : (
                      project?.hints.slice(0, unlockedHintsCount).map((h, i) => (
                        <div
                          key={i}
                          style={{
                            padding: 'var(--space-3)',
                            backgroundColor: 'var(--color-surface-muted)',
                            borderRadius: 'var(--radius-sm)',
                            borderLeft: '3px solid var(--color-burgundy)'
                          }}
                        >
                          <span style={{ fontWeight: 700, color: 'var(--color-burgundy)' }}>Hint #{i + 1}: </span>
                          <span>{h}</span>
                        </div>
                      ))
                    )}
                  </div>
                )}
              </div>
            </div>

            {/* Right Panel: Code Editor & Sandboxed Terminal Console */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
              {/* Code Editor Header */}
              <div
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  flex: 1,
                  backgroundColor: 'var(--color-surface)',
                  borderRadius: 'var(--radius-panel)',
                  border: '1px solid var(--color-border)',
                  overflow: 'hidden'
                }}
              >
                <div style={{ padding: '8px 14px', backgroundColor: 'var(--color-surface-muted)', borderBottom: '1px solid var(--color-border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontFamily: 'monospace', fontSize: 'var(--text-xs)', fontWeight: 600 }}>
                    solution.py (Python 3.10+ Isolated Sandbox)
                  </span>
                  <span style={{ fontSize: '0.7rem', color: 'var(--color-text-muted)', display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <ShieldCheck size={13} color="var(--color-success)" />
                    Sandboxed Runtime Active
                  </span>
                </div>

                <textarea
                  value={userCode}
                  onChange={e => setUserCode(e.target.value)}
                  placeholder="# Write your implementation here..."
                  spellCheck={false}
                  style={{
                    flex: 1,
                    minHeight: '260px',
                    padding: 'var(--space-3)',
                    fontFamily: '"SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace',
                    fontSize: '0.82rem',
                    lineHeight: 1.5,
                    border: 'none',
                    outline: 'none',
                    resize: 'none',
                    backgroundColor: '#1E1E1E',
                    color: '#D4D4D4'
                  }}
                />
              </div>

              {/* Sandboxed Test Console / Output Drawer */}
              <div
                style={{
                  height: '240px',
                  backgroundColor: 'var(--color-surface)',
                  borderRadius: 'var(--radius-panel)',
                  border: '1px solid var(--color-border)',
                  display: 'flex',
                  flexDirection: 'column',
                  overflow: 'hidden'
                }}
              >
                <div style={{ padding: '6px 12px', backgroundColor: 'var(--color-surface-muted)', borderBottom: '1px solid var(--color-border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <Terminal size={14} color="var(--color-burgundy)" />
                    <span style={{ fontSize: 'var(--text-xs)', fontWeight: 600 }}>Console & Test Suite</span>
                  </div>

                  {sandboxResult && (
                    <span
                      style={{
                        fontSize: '0.7rem',
                        fontWeight: 700,
                        color: sandboxResult.success ? 'var(--color-success)' : '#DC2626'
                      }}
                    >
                      {sandboxResult.tests_passed} / {sandboxResult.tests_total} Passed ({sandboxResult.execution_time_ms} ms)
                    </span>
                  )}
                </div>

                <div style={{ flex: 1, overflowY: 'auto', padding: 'var(--space-3)', fontSize: '0.75rem', fontFamily: 'monospace' }}>
                  {!sandboxResult ? (
                    <div style={{ color: 'var(--color-text-muted)', padding: 'var(--space-2)' }}>
                      Click <strong>"Run Public Tests"</strong> to execute your code against test cases in the isolated Python sandbox.
                    </div>
                  ) : (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                      {sandboxResult.output && (
                        <div style={{ padding: '6px', backgroundColor: '#F8F9FA', borderRadius: '4px', whiteSpace: 'pre-line', border: '1px solid var(--color-border)' }}>
                          <strong>Stdout:</strong>\n{sandboxResult.output}
                        </div>
                      )}

                      {sandboxResult.error && (
                        <div style={{ padding: '6px', backgroundColor: '#FEF2F2', color: '#991B1B', borderRadius: '4px', whiteSpace: 'pre-line' }}>
                          <strong>Error:</strong> {sandboxResult.error}
                        </div>
                      )}

                      {sandboxResult.test_results?.map((t, idx) => (
                        <div
                          key={idx}
                          style={{
                            padding: '6px 10px',
                            borderRadius: '4px',
                            backgroundColor: t.passed ? 'rgba(5, 150, 105, 0.08)' : 'rgba(220, 38, 38, 0.08)',
                            border: `1px solid ${t.passed ? '#10B981' : '#F87171'}`,
                            display: 'flex',
                            flexDirection: 'column',
                            gap: '2px'
                          }}
                        >
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <span style={{ fontWeight: 600, color: t.passed ? '#065F46' : '#991B1B' }}>
                              {t.passed ? '✓' : '✗'} {t.name}
                            </span>
                            <span style={{ fontSize: '0.65rem', color: 'var(--color-text-muted)' }}>
                              {t.execution_time_ms} ms
                            </span>
                          </div>
                          {t.error && (
                            <span style={{ color: '#DC2626', fontSize: '0.7rem' }}>
                              {t.error}
                            </span>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Submission Evaluation Report Modal (Feature D) */}
          {submissionResult && (
            <div
              style={{
                position: 'fixed',
                inset: 0,
                backgroundColor: 'rgba(28, 25, 23, 0.65)',
                backdropFilter: 'blur(3px)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                zIndex: 1000,
                padding: 'var(--space-4)'
              }}
            >
              <div
                style={{
                  backgroundColor: 'var(--color-surface)',
                  borderRadius: 'var(--radius-panel)',
                  border: '1.5px solid var(--color-border-strong)',
                  maxWidth: '680px',
                  width: '100%',
                  maxHeight: '90vh',
                  overflowY: 'auto',
                  padding: 'var(--space-6)',
                  boxShadow: 'var(--shadow-modal)',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: 'var(--space-4)'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <div>
                    <span className="badge badge-burgundy">OFFICIAL EVALUATION VERDICT</span>
                    <h3 style={{ fontSize: 'var(--text-xl)', fontFamily: 'var(--font-display)', fontWeight: 800, margin: '4px 0' }}>
                      {submissionResult.status === 'passed' ? 'Project Benchmark Satisfied' : 'Project Needs Further Refinement'}
                    </h3>
                  </div>
                  <button
                    onClick={() => setSubmissionResult(null)}
                    style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: '1.2rem' }}
                  >
                    ✕
                  </button>
                </div>

                {/* Score Header */}
                <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-4)', padding: 'var(--space-3) var(--space-4)', backgroundColor: 'var(--color-surface-muted)', borderRadius: 'var(--radius-sm)' }}>
                  <div style={{ fontSize: '2.5rem', fontWeight: 800, fontFamily: 'var(--font-display)', color: submissionResult.score >= 70 ? 'var(--color-success)' : '#DC2626' }}>
                    {submissionResult.score}%
                  </div>
                  <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)' }}>
                    <div>Tests Verified: <strong>{submissionResult.tests_passed} / {submissionResult.tests_total}</strong> assertions passed</div>
                    <div>Execution Runtime: <strong>{submissionResult.execution_time_ms} ms</strong> in isolated sandbox</div>
                  </div>
                </div>

                {/* Rubric Breakdown */}
                <div>
                  <h4 style={{ fontSize: 'var(--text-xs)', fontWeight: 700, textTransform: 'uppercase', marginBottom: '8px' }}>
                    Transparent Rubric Evaluation
                  </h4>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                    {submissionResult.rubric_evaluation?.map((r, i) => (
                      <div
                        key={i}
                        style={{
                          padding: '8px 12px',
                          borderRadius: '4px',
                          border: '1px solid var(--color-border)',
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center',
                          fontSize: 'var(--text-xs)'
                        }}
                      >
                        <div>
                          <strong>{r.criterion}</strong> ({r.weight})
                          <div style={{ color: 'var(--color-text-muted)', fontSize: '0.7rem' }}>{r.detail}</div>
                        </div>
                        <span style={{ fontWeight: 700, color: r.passed ? 'var(--color-success)' : '#DC2626' }}>
                          {r.score}%
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Mentor Feedback & AI distinction */}
                <div style={{ padding: 'var(--space-3)', backgroundColor: 'var(--color-burgundy-soft)', borderRadius: 'var(--radius-sm)', fontSize: 'var(--text-xs)' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontWeight: 700, color: 'var(--color-burgundy)', marginBottom: '4px' }}>
                    <Sparkles size={13} />
                    <span>{submissionResult.feedback?.has_ai_mentor_review ? 'Qualitative AI Mentor Review' : 'Automated Diagnostic Feedback'}</span>
                  </div>
                  <p style={{ margin: 0, lineHeight: 1.5 }}>
                    {submissionResult.feedback?.summary}
                  </p>
                </div>

                {/* Adaptive Next Step */}
                {submissionResult.adaptive_next_challenge && (
                  <div style={{ padding: 'var(--space-3)', border: '1px dashed var(--color-burgundy)', borderRadius: 'var(--radius-sm)', fontSize: 'var(--text-xs)' }}>
                    <strong>Next Adaptive Step:</strong> {submissionResult.adaptive_next_challenge.target_title} ({submissionResult.adaptive_next_challenge.difficulty})
                    <p style={{ margin: '4px 0 0 0', color: 'var(--color-text-secondary)' }}>
                      {submissionResult.adaptive_next_challenge.reason}
                    </p>
                  </div>
                )}

                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 'var(--space-2)' }}>
                  <SecondaryButton size="sm" onClick={() => setSubmissionResult(null)}>
                    Continue Editing Code
                  </SecondaryButton>
                  <PrimaryButton
                    size="sm"
                    onClick={() => {
                      setSubmissionResult(null);
                      setViewMode('dashboard');
                    }}
                  >
                    Return to Arena Dashboard
                  </PrimaryButton>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      <style>{`
        @media (max-width: 860px) {
          .arena-grid {
            grid-template-columns: 1fr !important;
          }
        }
      `}</style>
    </PageContainer>
  );
};

export default SkillsPage;
