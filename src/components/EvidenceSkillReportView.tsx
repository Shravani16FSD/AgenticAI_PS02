import React, { useState } from 'react';
import {
  GitBranch,
  FileCode,
  AlertTriangle,
  Sparkles,
  ArrowRight,
  RefreshCw,
  FolderGit2,
  ExternalLink,
  Code2,
  Award,
  HelpCircle
} from 'lucide-react';
import { PrimaryButton, SecondaryButton } from './ui/Buttons';
import type { EvidenceReportData } from '../types/arena';

interface EvidenceSkillReportViewProps {
  report: EvidenceReportData | null;
  isLoading: boolean;
  error: string | null;
  onRefresh: () => void;
  onAnalyzeRepo: (repoUrl: string) => Promise<void>;
  onStartProject: (projectId: string) => void;
  onStartDiagnostic: (diagId: string) => void;
}

export const EvidenceSkillReportView: React.FC<EvidenceSkillReportViewProps> = ({
  report,
  isLoading,
  error,
  onRefresh,
  onAnalyzeRepo,
  onStartProject,
  onStartDiagnostic
}) => {
  const [repoInput, setRepoInput] = useState<string>('');
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [selectedFilter, setSelectedFilter] = useState<'all' | 'High' | 'Medium' | 'Low'>('all');

  const handleSubmitCustomRepo = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!repoInput.trim()) return;
    setIsSubmitting(true);
    try {
      await onAnalyzeRepo(repoInput.trim());
      setRepoInput('');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleQuickLoad = async (repoUrl: string) => {
    setIsSubmitting(true);
    try {
      await onAnalyzeRepo(repoUrl);
    } finally {
      setIsSubmitting(false);
    }
  };

  // Confidence styling helper
  const getConfidenceBadge = (confidence: string) => {
    switch (confidence) {
      case 'High':
        return {
          bg: '#ECFDF5',
          color: '#065F46',
          border: '#A7F3D0',
          label: 'High Evidence'
        };
      case 'Medium':
        return {
          bg: '#EFF6FF',
          color: '#1E40AF',
          border: '#BFDBFE',
          label: 'Medium Evidence'
        };
      default:
        return {
          bg: '#F3F4F6',
          color: '#4B5563',
          border: '#E5E7EB',
          label: 'Low / Unverified'
        };
    }
  };

  // Severity styling helper for skill gaps
  const getSeverityBadge = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'high':
        return { bg: '#FEF2F2', color: '#991B1B', border: '#FECACA', label: 'High Priority Gap' };
      case 'medium':
        return { bg: '#FFFBEB', color: '#92400E', border: '#FDE68A', label: 'Medium Gap' };
      default:
        return { bg: '#F8FAFC', color: '#475569', border: '#E2E8F0', label: 'Improvement Note' };
    }
  };

  const filteredSkills = report?.detected_skills.filter(s => {
    if (selectedFilter === 'all') return true;
    return s.confidence === selectedFilter;
  }) || [];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
      {/* 1. Header Toolbar & Scanner Input */}
      <div
        className="panel"
        style={{
          display: 'flex',
          flexDirection: 'column',
          gap: 'var(--space-4)',
          backgroundColor: 'var(--color-surface)',
          borderRadius: 'var(--radius-panel)',
          border: '1px solid var(--color-border)'
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 'var(--space-3)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div
              style={{
                width: '36px',
                height: '36px',
                borderRadius: '8px',
                backgroundColor: 'var(--color-burgundy-soft)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'var(--color-burgundy)'
              }}
            >
              <FolderGit2 size={20} />
            </div>
            <div>
              <h3 style={{ fontSize: 'var(--text-base)', fontFamily: 'var(--font-display)', fontWeight: 700, margin: 0, color: 'var(--color-text)' }}>
                Evidence-Based Repository Skill Profiler
              </h3>
              <p style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)', margin: 0 }}>
                Translates verified AST nodes, tests, manifests, and documentation into transparent skill indicators.
              </p>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <SecondaryButton
              size="sm"
              onClick={onRefresh}
              icon={<RefreshCw size={13} className={isLoading ? 'spin' : ''} />}
              disabled={isLoading || isSubmitting}
            >
              Re-Scan Repository
            </SecondaryButton>
          </div>
        </div>

        {/* Repository Search / Input Form */}
        <form onSubmit={handleSubmitCustomRepo} style={{ display: 'flex', gap: 'var(--space-2)', flexWrap: 'wrap' }}>
          <div style={{ flex: '1 1 320px', position: 'relative' }}>
            <input
              type="text"
              placeholder="e.g. username/repo-name or https://github.com/..."
              value={repoInput}
              onChange={(e) => setRepoInput(e.target.value)}
              style={{
                width: '100%',
                padding: '9px 12px',
                fontSize: 'var(--text-xs)',
                borderRadius: 'var(--radius-sm)',
                border: '1px solid var(--color-border)',
                backgroundColor: 'var(--color-surface-muted)',
                color: 'var(--color-text)'
              }}
            />
          </div>
          <PrimaryButton
            size="sm"
            type="submit"
            disabled={!repoInput.trim() || isSubmitting || isLoading}
            icon={<ArrowRight size={14} />}
          >
            {isSubmitting ? 'Analyzing...' : 'Analyze Repository'}
          </PrimaryButton>
        </form>

        {/* Quick Sample Selector Chips */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap', fontSize: 'var(--text-xs)' }}>
          <span style={{ color: 'var(--color-text-muted)', fontWeight: 600 }}>Quick Demos:</span>
          <button
            type="button"
            onClick={() => handleQuickLoad('alex-morgan/data-pipeline-lab')}
            style={{
              background: 'none',
              border: '1px solid var(--color-border)',
              borderRadius: '16px',
              padding: '2px 10px',
              fontSize: '0.72rem',
              cursor: 'pointer',
              color: 'var(--color-text)',
              backgroundColor: report?.repository_name?.includes('data-pipeline-lab') ? 'var(--color-burgundy-soft)' : 'transparent',
              borderColor: report?.repository_name?.includes('data-pipeline-lab') ? 'var(--color-burgundy)' : 'var(--color-border)'
            }}
          >
            alex-morgan/data-pipeline-lab (Python / ETL / API)
          </button>
          <button
            type="button"
            onClick={() => handleQuickLoad('jordan-chen/accessible-tokens-core')}
            style={{
              background: 'none',
              border: '1px solid var(--color-border)',
              borderRadius: '16px',
              padding: '2px 10px',
              fontSize: '0.72rem',
              cursor: 'pointer',
              color: 'var(--color-text)',
              backgroundColor: report?.repository_name?.includes('accessible-tokens-core') ? 'var(--color-burgundy-soft)' : 'transparent',
              borderColor: report?.repository_name?.includes('accessible-tokens-core') ? 'var(--color-burgundy)' : 'var(--color-border)'
            }}
          >
            jordan-chen/accessible-tokens-core (TypeScript / UI)
          </button>
        </div>

        {/* Repository Context Strip */}
        {report && (
          <div
            style={{
              padding: 'var(--space-3) var(--space-4)',
              backgroundColor: 'var(--color-surface-muted)',
              borderRadius: 'var(--radius-sm)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              flexWrap: 'wrap',
              gap: 'var(--space-2)',
              fontSize: 'var(--text-xs)'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
              <span style={{ display: 'flex', alignItems: 'center', gap: '5px', fontWeight: 600, color: 'var(--color-text)' }}>
                <GitBranch size={13} color="var(--color-burgundy)" />
                {report.repository_name}
              </span>
              <span style={{ color: 'var(--color-text-muted)' }}>&bull;</span>
              <span style={{ color: 'var(--color-text-secondary)' }}>
                Scanned: <strong>{report.scanned_files_count}</strong> files
              </span>
              <span style={{ color: 'var(--color-text-muted)' }}>&bull;</span>
              <span style={{ color: 'var(--color-text-secondary)', fontFamily: 'monospace' }}>
                SHA: {report.commit_sha.slice(0, 10)}
              </span>
              {report.languages_detected.length > 0 && (
                <>
                  <span style={{ color: 'var(--color-text-muted)' }}>&bull;</span>
                  <span style={{ color: 'var(--color-text-secondary)' }}>
                    Languages: <strong>{report.languages_detected.join(', ')}</strong>
                  </span>
                </>
              )}
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              {report.is_sample_data && (
                <span className="badge badge-muted" style={{ fontSize: '0.65rem' }}>
                  Demo Sandbox Mode
                </span>
              )}
              {report.repo_url && (
                <a
                  href={report.repo_url}
                  target="_blank"
                  rel="noreferrer"
                  style={{ display: 'flex', alignItems: 'center', gap: '4px', color: 'var(--color-burgundy)', textDecoration: 'none', fontWeight: 600 }}
                >
                  View Source <ExternalLink size={11} />
                </a>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Error State */}
      {error && (
        <div
          style={{
            padding: 'var(--space-4)',
            backgroundColor: '#FEF2F2',
            border: '1px solid #EF4444',
            borderRadius: 'var(--radius-sm)',
            color: '#991B1B',
            fontSize: 'var(--text-xs)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: 'var(--space-3)'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <AlertTriangle size={16} />
            <span>{error}</span>
          </div>
          <SecondaryButton size="sm" onClick={onRefresh}>
            Retry
          </SecondaryButton>
        </div>
      )}

      {/* Loading Skeleton */}
      {isLoading && !report && (
        <div className="panel" style={{ textAlign: 'center', padding: 'var(--space-12)' }}>
          <RefreshCw size={24} className="spin" style={{ color: 'var(--color-burgundy)', margin: '0 auto var(--space-3) auto' }} />
          <h4 style={{ fontSize: 'var(--text-sm)', fontWeight: 600, margin: '0 0 4px 0' }}>
            Analyzing Repository Evidence...
          </h4>
          <p style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)', margin: 0 }}>
            Inspecting AST trees, imports, test cases, and configuration files.
          </p>
        </div>
      )}

      {/* Empty State */}
      {!isLoading && !report && !error && (
        <div className="panel" style={{ textAlign: 'center', padding: 'var(--space-12)' }}>
          <HelpCircle size={28} style={{ color: 'var(--color-text-muted)', margin: '0 auto var(--space-3) auto' }} />
          <h4 style={{ fontSize: 'var(--text-base)', fontWeight: 700, margin: '0 0 6px 0' }}>
            No Repository Evidence Available
          </h4>
          <p style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)', maxWidth: '480px', margin: '0 auto var(--space-4) auto' }}>
            Enter a public GitHub repository URL above or click one of the quick demo buttons to scan structured repository evidence.
          </p>
          <PrimaryButton size="sm" onClick={() => handleQuickLoad('alex-morgan/data-pipeline-lab')}>
            Load Sample Repository
          </PrimaryButton>
        </div>
      )}

      {/* Report Content */}
      {report && (
        <>
          {/* 2. AI Executive Synthesis Strip */}
          {report.ai_synthesis && (
            <div
              style={{
                padding: 'var(--space-4) var(--space-5)',
                backgroundColor: 'var(--color-surface)',
                borderRadius: 'var(--radius-panel)',
                border: '1.5px solid var(--color-burgundy)',
                boxShadow: 'var(--shadow-sm)',
                display: 'flex',
                alignItems: 'flex-start',
                gap: 'var(--space-3)'
              }}
            >
              <div
                style={{
                  width: '28px',
                  height: '28px',
                  borderRadius: '6px',
                  backgroundColor: 'var(--color-burgundy-soft)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'var(--color-burgundy)',
                  flexShrink: 0,
                  marginTop: '2px'
                }}
              >
                <Sparkles size={16} />
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                  <span style={{ fontSize: 'var(--text-xs)', fontWeight: 700, color: 'var(--color-burgundy)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                    Evidence-Grounded Executive Synthesis
                  </span>
                  <span style={{ fontSize: '0.65rem', color: 'var(--color-text-muted)' }}>
                    &bull; Based strictly on verified AST & repository artifacts
                  </span>
                </div>
                <p style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text)', lineHeight: 1.65, margin: 0 }}>
                  {report.ai_synthesis}
                </p>
              </div>
            </div>
          )}

          {/* 3. Personalized Next Steps (3 Prioritized Actions) */}
          <section className="panel" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 'var(--space-2)' }}>
              <div>
                <h3 style={{ fontSize: 'var(--text-base)', fontFamily: 'var(--font-display)', fontWeight: 700, margin: 0, color: 'var(--color-text)' }}>
                  Prioritized Recommended Next Steps
                </h3>
                <p style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)', margin: 0 }}>
                  Three targeted actions addressing the repository's primary evidence gaps.
                </p>
              </div>
              <span className="badge badge-burgundy" style={{ fontSize: '0.7rem' }}>
                Action Plan
              </span>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 'var(--space-4)' }}>
              {report.prioritized_actions.map(action => (
                <div
                  key={action.priority}
                  style={{
                    padding: 'var(--space-4)',
                    backgroundColor: 'var(--color-surface)',
                    borderRadius: 'var(--radius-sm)',
                    border: '1px solid var(--color-border)',
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'space-between',
                    gap: 'var(--space-3)'
                  }}
                >
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span
                        style={{
                          fontSize: '0.7rem',
                          fontWeight: 700,
                          padding: '2px 8px',
                          borderRadius: '12px',
                          backgroundColor: action.priority === 1 ? 'var(--color-burgundy-soft)' : 'var(--color-surface-muted)',
                          color: action.priority === 1 ? 'var(--color-burgundy)' : 'var(--color-text-secondary)',
                          textTransform: 'uppercase'
                        }}
                      >
                        Priority #{action.priority} &bull; {action.type.replace('_', ' ')}
                      </span>
                    </div>

                    <h4 style={{ fontSize: 'var(--text-sm)', fontWeight: 700, margin: 0, color: 'var(--color-text)' }}>
                      {action.title}
                    </h4>

                    <p style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)', lineHeight: 1.55, margin: 0 }}>
                      {action.description}
                    </p>
                  </div>

                  <div style={{ paddingTop: 'var(--space-2)', borderTop: '1px solid var(--color-border)' }}>
                    {action.type === 'mini_project' ? (
                      <PrimaryButton
                        size="sm"
                        onClick={() => onStartProject(action.target_id || 'py-data-cleaner-101')}
                        icon={<Code2 size={13} />}
                        style={{ width: '100%', justifyContent: 'center' }}
                      >
                        {action.action_label}
                      </PrimaryButton>
                    ) : action.type === 'verification' ? (
                      <SecondaryButton
                        size="sm"
                        onClick={() => onStartDiagnostic(action.target_id || 'diag-py-101')}
                        icon={<Award size={13} />}
                        style={{ width: '100%', justifyContent: 'center' }}
                      >
                        {action.action_label}
                      </SecondaryButton>
                    ) : (
                      <SecondaryButton
                        size="sm"
                        onClick={() => {
                          const gapEl = document.getElementById('skill-gaps-section');
                          if (gapEl) gapEl.scrollIntoView({ behavior: 'smooth' });
                        }}
                        icon={<ArrowRight size={13} />}
                        style={{ width: '100%', justifyContent: 'center' }}
                      >
                        {action.action_label}
                      </SecondaryButton>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* 4. Detected Skills Profile (Evidence Breakdown) */}
          <section className="panel" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 'var(--space-2)' }}>
              <div>
                <h3 style={{ fontSize: 'var(--text-base)', fontFamily: 'var(--font-display)', fontWeight: 700, margin: 0, color: 'var(--color-text)' }}>
                  Detected Skill Profile
                </h3>
                <p style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)', margin: 0 }}>
                  Showing {filteredSkills.length} skill(s) supported by repository evidence. Confidence reflects evidence depth, not an arbitrary proficiency score.
                </p>
              </div>

              {/* Confidence filter tabs */}
              <div style={{ display: 'flex', gap: '4px' }}>
                {(['all', 'High', 'Medium', 'Low'] as const).map(tier => (
                  <button
                    key={tier}
                    type="button"
                    onClick={() => setSelectedFilter(tier)}
                    style={{
                      padding: '4px 10px',
                      borderRadius: '4px',
                      fontSize: '0.72rem',
                      fontWeight: selectedFilter === tier ? 700 : 500,
                      border: `1px solid ${selectedFilter === tier ? 'var(--color-burgundy)' : 'var(--color-border)'}`,
                      backgroundColor: selectedFilter === tier ? 'var(--color-burgundy-soft)' : 'transparent',
                      color: selectedFilter === tier ? 'var(--color-burgundy)' : 'var(--color-text-secondary)',
                      cursor: 'pointer'
                    }}
                  >
                    {tier === 'all' ? 'All Skills' : `${tier}`}
                  </button>
                ))}
              </div>
            </div>

            {filteredSkills.length === 0 ? (
              <div style={{ padding: 'var(--space-6)', textAlign: 'center', color: 'var(--color-text-muted)', fontSize: 'var(--text-xs)' }}>
                No skills detected matching filter '{selectedFilter}'.
              </div>
            ) : (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: 'var(--space-4)' }}>
                {filteredSkills.map(skill => {
                  const badge = getConfidenceBadge(skill.confidence);

                  return (
                    <div
                      key={skill.skill_name}
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
                      {/* Skill Header */}
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                        <div>
                          <h4 style={{ fontSize: 'var(--text-sm)', fontWeight: 700, margin: '0 0 2px 0', color: 'var(--color-text)' }}>
                            {skill.skill_name}
                          </h4>
                          <span style={{ fontSize: '0.7rem', color: 'var(--color-text-muted)' }}>
                            Verified Repository Evidence
                          </span>
                        </div>
                        <span
                          style={{
                            fontSize: '0.68rem',
                            fontWeight: 700,
                            padding: '2px 8px',
                            borderRadius: '4px',
                            backgroundColor: badge.bg,
                            color: badge.color,
                            border: `1px solid ${badge.border}`,
                            textTransform: 'uppercase'
                          }}
                        >
                          {badge.label}
                        </span>
                      </div>

                      {/* Evidence Summary */}
                      <p style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text)', lineHeight: 1.55, margin: 0 }}>
                        {skill.evidence_summary}
                      </p>

                      {/* Supporting File Paths */}
                      {skill.file_paths.length > 0 && (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                          <span style={{ fontSize: '0.68rem', fontWeight: 600, color: 'var(--color-text-secondary)', textTransform: 'uppercase' }}>
                            Supporting File Paths:
                          </span>
                          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                            {skill.file_paths.map(fp => (
                              <span
                                key={fp}
                                style={{
                                  display: 'inline-flex',
                                  alignItems: 'center',
                                  gap: '4px',
                                  padding: '2px 8px',
                                  borderRadius: '4px',
                                  backgroundColor: 'var(--color-surface-muted)',
                                  border: '1px solid var(--color-border)',
                                  fontFamily: 'monospace',
                                  fontSize: '0.72rem',
                                  color: 'var(--color-text)'
                                }}
                              >
                                <FileCode size={11} color="var(--color-burgundy)" />
                                {fp}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Observed AST Indicators */}
                      {skill.observed_indicators.length > 0 && (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                          <span style={{ fontSize: '0.68rem', fontWeight: 600, color: 'var(--color-text-secondary)', textTransform: 'uppercase' }}>
                            Observed Indicators:
                          </span>
                          <ul style={{ margin: 0, paddingLeft: '16px', fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)', lineHeight: 1.45 }}>
                            {skill.observed_indicators.map((ind, i) => (
                              <li key={i}>{ind}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Missing / Insufficient Evidence Notice */}
                      {skill.missing_evidence && (
                        <div
                          style={{
                            padding: 'var(--space-2) var(--space-3)',
                            backgroundColor: 'var(--color-surface-muted)',
                            borderRadius: 'var(--radius-sm)',
                            borderLeft: '3px solid #D97706',
                            fontSize: 'var(--text-xs)',
                            color: 'var(--color-text-secondary)'
                          }}
                        >
                          <strong style={{ color: '#D97706' }}>Missing Evidence: </strong>
                          {skill.missing_evidence}
                        </div>
                      )}

                      {/* Practical Recommendation */}
                      {skill.recommendation && (
                        <div
                          style={{
                            padding: 'var(--space-2) var(--space-3)',
                            backgroundColor: 'var(--color-burgundy-soft)',
                            borderRadius: 'var(--radius-sm)',
                            borderLeft: '3px solid var(--color-burgundy)',
                            fontSize: 'var(--text-xs)',
                            color: 'var(--color-text)'
                          }}
                        >
                          <strong style={{ color: 'var(--color-burgundy)' }}>Practical Action: </strong>
                          {skill.recommendation}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </section>

          {/* 5. Skill-Gap Analysis */}
          <section id="skill-gaps-section" className="panel" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 'var(--space-2)' }}>
              <div>
                <h3 style={{ fontSize: 'var(--text-base)', fontFamily: 'var(--font-display)', fontWeight: 700, margin: 0, color: 'var(--color-text)' }}>
                  Skill-Gap Analysis & Evidence Gaps
                </h3>
                <p style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)', margin: 0 }}>
                  Areas where repository evidence is missing or limited. These are evidence-gap recommendations, not claims that you lack the skill.
                </p>
              </div>
              <span className="badge badge-warning" style={{ fontSize: '0.7rem' }}>
                {report.skill_gaps.length} Gaps Flagged
              </span>
            </div>

            {report.skill_gaps.length === 0 ? (
              <div style={{ padding: 'var(--space-6)', textAlign: 'center', color: 'var(--color-text-muted)', fontSize: 'var(--text-xs)' }}>
                No significant evidence gaps identified. Your repository demonstrates comprehensive coverage across tests, docs, and architecture.
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
                {report.skill_gaps.map((gap, idx) => {
                  const sBadge = getSeverityBadge(gap.severity);

                  return (
                    <div
                      key={idx}
                      style={{
                        padding: 'var(--space-4)',
                        backgroundColor: 'var(--color-surface)',
                        borderRadius: 'var(--radius-sm)',
                        border: '1px solid var(--color-border)',
                        display: 'flex',
                        flexDirection: 'column',
                        gap: 'var(--space-2)'
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '6px' }}>
                        <h4 style={{ fontSize: 'var(--text-sm)', fontWeight: 700, margin: 0, color: 'var(--color-text)' }}>
                          {gap.area}
                        </h4>
                        <span
                          style={{
                            fontSize: '0.65rem',
                            fontWeight: 700,
                            padding: '2px 8px',
                            borderRadius: '4px',
                            backgroundColor: sBadge.bg,
                            color: sBadge.color,
                            border: `1px solid ${sBadge.border}`,
                            textTransform: 'uppercase'
                          }}
                        >
                          {sBadge.label}
                        </span>
                      </div>

                      <p style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)', margin: 0, lineHeight: 1.5 }}>
                        <strong>Observation: </strong>{gap.observation}
                      </p>

                      <div
                        style={{
                          marginTop: 'var(--space-1)',
                          padding: 'var(--space-2) var(--space-3)',
                          backgroundColor: 'var(--color-surface-muted)',
                          borderRadius: 'var(--radius-sm)',
                          fontSize: 'var(--text-xs)',
                          color: 'var(--color-text)'
                        }}
                      >
                        <strong style={{ color: 'var(--color-burgundy)' }}>Recommendation: </strong>
                        {gap.recommendation}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </section>
        </>
      )}
    </div>
  );
};
