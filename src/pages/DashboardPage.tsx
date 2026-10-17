import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowRight, BookOpen, MessageSquare, Compass, Target, Sparkles, Activity, GitBranch } from 'lucide-react';
import { PageContainer, PageHeading } from '../components/ui/Typography';
import { PrimaryButton, SecondaryButton } from '../components/ui/Buttons';
import { ProgressIndicator, StatusLabel } from '../components/ui/FeedbackStates';
import { GoalItem } from '../components/career/CareerSummary';
import { useApp } from '../context/AppContext';
import type { UserProfile } from '../types';

interface UserDashboardConfig {
  hubTitle: string;
  tagline: string;
  interests: string[];
  metrics: Array<{ label: string; value: string; detail: string }>;
  telemetrySource: string;
  tailoredSprint: {
    title: string;
    phase: string;
    estimatedTime: string;
    description: string;
    actionLabel: string;
  };
  exercises: Array<{ title: string; description: string; tag: string }>;
  weeklyFocusQuote: string;
}

const USER_CUSTOM_DASHBOARDS: Record<string, UserDashboardConfig> = {
  default_user: {
    hubTitle: 'Data Engineering & AI Pipelines Hub',
    tagline: 'High-Throughput Stream Ingestion & Vector Infrastructure',
    interests: ['Distributed Systems', 'Data Pipelines', 'PyTorch & MLOps', 'Stream Processing', 'Vector Search'],
    metrics: [
      { label: 'Pipeline Uptime', value: '99.98%', detail: 'Zero dropped stream frames in production' },
      { label: 'Ingestion Throughput', value: '14.8M rec/hr', detail: 'Kafka consumer with async backpressure' },
      { label: 'P99 Inference Latency', value: '12ms', detail: 'FAISS indexed vector embeddings' }
    ],
    telemetrySource: 'alex-morgan/data-pipeline-lab @ 8f92a1c',
    tailoredSprint: {
      title: 'Benchmark Vector Indexing Pipeline for RAG Latency',
      phase: 'Phase 2: High-Scale Ingestion',
      estimatedTime: '3.5 hrs',
      description: 'Implement backpressure-aware batch processing and verify cosine recall over 100k embeddings.',
      actionLabel: 'Open Pipeline Benchmark'
    },
    exercises: [
      {
        title: 'Prompt Evaluation Harness',
        description: 'Write an automated Python script that tests model accuracy and semantic drift across 20 synthetic edge cases.',
        tag: 'ML Engineering'
      },
      {
        title: 'Distributed Stream Transformer',
        description: 'Build a fault-tolerant Kafka consumer with dead-letter queue and idempotency validation.',
        tag: 'Data Architecture'
      }
    ],
    weeklyFocusQuote: '"Optimize for low latency and zero memory leaks. Clean data pipelines build trustworthy AI."'
  },
  user_jordan_chen: {
    hubTitle: 'Design Systems & Accessibility Hub',
    tagline: 'Multi-Brand Tokenization & WCAG 2.2 AAA Architecture',
    interests: ['Design Tokens', 'WCAG 2.2 AAA Accessibility', 'Component Systems', 'Micro-interactions', 'Headless UI'],
    metrics: [
      { label: 'Design Token Coverage', value: '98.4%', detail: 'Automated Style Dictionary multi-theme export' },
      { label: 'WCAG AAA Compliance', value: '100% Pass', detail: 'Zero automated or screen-reader contrast flags' },
      { label: 'Component Adoption', value: '92%', detail: '24 core accessible components active in design system' }
    ],
    telemetrySource: 'jordan-chen/accessible-tokens-core @ 7a8b9c0',
    tailoredSprint: {
      title: 'Complete High-Contrast Theme Matrix & WCAG 2.2 Audit',
      phase: 'Phase 2: Accessible Foundations',
      estimatedTime: '2.5 hrs',
      description: 'Audit semantic focus rings, high-contrast dark mode tokens, and keyboard trap avoidance.',
      actionLabel: 'Launch Token Audit'
    },
    exercises: [
      {
        title: 'Headless Accessible Combobox',
        description: 'Engineer a custom headless combobox adhering to WAI-ARIA 1.2 with roving tabindex and live-region announcements.',
        tag: 'A11y Engineering'
      },
      {
        title: 'Design Token Automation Pipeline',
        description: 'Create a GitHub Actions workflow exporting tokens to CSS custom variables, iOS Swift, and Android XML.',
        tag: 'Design Systems'
      }
    ],
    weeklyFocusQuote: '"Accessibility is not a feature; it is an ergonomic baseline for equitable software."'
  },
  user_priya_sharma: {
    hubTitle: 'Analytics Engineering & Financial Marts Hub',
    tagline: 'Enterprise Dimensional Modeling & dbt Observability',
    interests: ['dbt Core & Modeling', 'Financial Data Marts', 'Snowflake Observability', 'Dimensional Schemas', 'BI Metrics'],
    metrics: [
      { label: 'dbt Model Assertions', value: '42/42 Passing', detail: 'Zero schema drift or unhandled null primary keys' },
      { label: 'Mart Freshness SLA', value: '99.9%', detail: 'Incremental build runs complete under 4 minutes' },
      { label: 'P95 Query Latency', value: '180ms', detail: 'Partitioned columnar cluster for BI dashboards' }
    ],
    telemetrySource: 'priya-sharma/financial-analytics-marts @ 4c5d6e7',
    tailoredSprint: {
      title: 'Deploy Reconciled Financial Ledger Mart with dbt Snapshots',
      phase: 'Phase 2: Dimensional Marts',
      estimatedTime: '4.0 hrs',
      description: 'Implement Type-2 slowly changing dimensions (SCD2) reconciling payment gateway webhooks with general ledgers.',
      actionLabel: 'Run dbt Test Suite'
    },
    exercises: [
      {
        title: 'Financial Reconciliation Mart',
        description: 'Author incremental dbt models reconciling payment gateway logs with bank ledgers with zero discrepancies.',
        tag: 'Data Modeling'
      },
      {
        title: 'Data Observability & Anomaly Monitor',
        description: 'Write custom schema assertion tests detecting volume spikes, null anomalies, and revenue drifts.',
        tag: 'Data Quality'
      }
    ],
    weeklyFocusQuote: '"Data modeling is the foundation of truth. When your schemas are clean, decision-making is effortless."'
  },
  user_marcus_vance: {
    hubTitle: 'High-Performance Graphics & Systems Security Hub',
    tagline: 'Low-Latency Canvas Virtualization & Zero-Trust Sandboxing',
    interests: ['WebGL & WebGPU', 'Virtualized Canvas Grids', 'Memory Safety & WASM', 'Zero-Trust Security', 'Low-Level Graphics'],
    metrics: [
      { label: 'Render Frame Rate', value: '60 FPS Locked', detail: 'Zero stutter with 100,000 virtualized grid nodes' },
      { label: 'Canvas Heap Memory', value: '12.8 MB', detail: 'Aggressive object pooling and zero memory leaks' },
      { label: 'Vulnerability Audit', value: '0 CVEs', detail: 'Zero-trust sandbox and strict Content Security Policy' }
    ],
    telemetrySource: 'marcus-vance/virtualized-canvas-grid @ 9e8d7c6',
    tailoredSprint: {
      title: 'Optimize WebGL Buffer Ring for SIMD Matrix Transforms',
      phase: 'Phase 3: Kernel Engine Optimization',
      estimatedTime: '3.0 hrs',
      description: 'Implement offscreen canvas double-buffering and WebAssembly SIMD operations for viewport transforms.',
      actionLabel: 'Run Frame Benchmark'
    },
    exercises: [
      {
        title: 'Virtualized Canvas Grid Engine',
        description: 'Render 500,000 data cells with 60 FPS viewport scrolling using offscreen canvas and SIMD transforms.',
        tag: 'Systems Graphics'
      },
      {
        title: 'Zero-Trust WASM Sandbox',
        description: 'Build a secure WebAssembly memory harness isolating untrusted user scripts with memory limit guards.',
        tag: 'AppSec & Sandbox'
      }
    ],
    weeklyFocusQuote: '"Precision in memory allocation and frame pacing transforms good applications into world-class software."'
  }
};

const getCustomDashboard = (userId: string, profile: UserProfile): UserDashboardConfig => {
  if (USER_CUSTOM_DASHBOARDS[userId]) {
    return USER_CUSTOM_DASHBOARDS[userId];
  }
  return {
    hubTitle: `${profile.name || 'Personal'} Career Command Center`,
    tagline: profile.studyStatus || 'Professional Growth & Engineering Excellence',
    interests: profile.interests.length > 0 ? profile.interests : ['Software Engineering', 'System Architecture', 'Design'],
    metrics: [
      { label: 'Target Commitment', value: `${profile.weeklyHours || 8} hrs/wk`, detail: 'Active weekly dedication' },
      { label: 'Skill Coverage', value: `${profile.currentSkills.length} Verified`, detail: 'Current tracked competency' },
      { label: 'Roadmap Pace', value: 'On Track', detail: 'Regular milestone progression' }
    ],
    telemetrySource: `${profile.name?.toLowerCase().replace(/\s+/g, '-') || 'user'}/learning-lab`,
    tailoredSprint: {
      title: `Advance Core Milestone for ${profile.targetCareerId.replace(/-/g, ' ')}`,
      phase: 'Current Learning Phase',
      estimatedTime: '3.0 hrs',
      description: 'Focus on primary career goals and master foundational concepts.',
      actionLabel: 'Continue Learning'
    },
    exercises: [
      {
        title: 'Practical Implementation Project',
        description: 'Apply your current core skills in a standalone GitHub repository project.',
        tag: 'Applied Project'
      },
      {
        title: 'Code Quality & Test Harness',
        description: 'Add automated tests and continuous integration to validate software correctness.',
        tag: 'Best Practices'
      }
    ],
    weeklyFocusQuote: '"Small steps count. Look how far you\'ve come."'
  };
};

export const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const {
    profile,
    activeCareer,
    roadmapTasks,
    updateTaskStatus,
    skills,
    completedTasksCount,
    totalTasksCount,
    overallProgressPercent,
    activeUserId
  } = useApp();

  const customDashboard = getCustomDashboard(activeUserId, profile);

  // Find featured "Next Step" task
  const currentNextStep =
    roadmapTasks.find(t => t.status === 'in_progress') ||
    roadmapTasks.find(t => t.status === 'not_started') ||
    roadmapTasks[0];

  const handleToggleGoal = (taskId: string, isCompleted: boolean) => {
    updateTaskStatus(taskId, isCompleted ? 'not_started' : 'completed');
  };

  return (
    <PageContainer>
      {/* 1. Greeting & Editorial Welcome Area */}
      <PageHeading
        eyebrow="NEXORA CAREER DASHBOARD"
        title={`Welcome back${profile.name ? `, ${profile.name}` : ''}. Let's pick up where you left off.`}
        description="Your career plan is personalized to your distinct interests and verified repository code."
        actions={
          <div style={{ display: 'flex', gap: 'var(--space-2)' }}>
            <SecondaryButton
              size="sm"
              onClick={() => navigate('/login')}
              style={{ fontSize: 'var(--text-xs)' }}
            >
              Switch User
            </SecondaryButton>
            <PrimaryButton
              size="sm"
              onClick={() => navigate('/coach')}
              icon={<MessageSquare size={14} />}
            >
              Talk to my mentor
            </PrimaryButton>
          </div>
        }
      />

      {/* 2. Customized User Hub Banner (Unique per User) */}
      <section
        className="panel"
        aria-label="Customized User Domain Command Hub"
        style={{
          backgroundColor: 'var(--color-surface)',
          border: '1px solid var(--color-border)',
          borderRadius: 'var(--radius-md)',
          padding: 'var(--space-4) var(--space-5)',
          marginBottom: 'var(--space-6)',
          display: 'flex',
          flexDirection: 'column',
          gap: 'var(--space-3)'
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 'var(--space-3)' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
              <span className="badge badge-burgundy" style={{ fontSize: '0.6875rem' }}>
                CUSTOMIZED DOMAIN
              </span>
              <h2
                style={{
                  fontSize: 'var(--text-base)',
                  fontFamily: 'var(--font-display)',
                  fontWeight: 600,
                  color: 'var(--color-text)',
                  margin: 0
                }}
              >
                {customDashboard.hubTitle}
              </h2>
            </div>
            <p style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)', margin: '4px 0 0 0' }}>
              {customDashboard.tagline}
            </p>
          </div>

          <div
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px',
              fontSize: 'var(--text-xs)',
              padding: '0.35rem 0.65rem',
              backgroundColor: 'var(--color-surface-muted)',
              borderRadius: 'var(--radius-sm)',
              border: '1px solid var(--color-border)',
              color: 'var(--color-text-secondary)'
            }}
          >
            <GitBranch size={13} style={{ color: 'var(--color-burgundy)' }} />
            <span>Telemetry: <code style={{ color: 'var(--color-text)', fontWeight: 600 }}>{customDashboard.telemetrySource}</code></span>
          </div>
        </div>

        {/* Customized User Interests Pills */}
        <div style={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: '6px', borderTop: '1px solid var(--color-border)', paddingTop: 'var(--space-3)' }}>
          <span style={{ fontSize: '0.6875rem', fontWeight: 700, color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em', marginRight: '4px' }}>
            User Interests:
          </span>
          {customDashboard.interests.map(interest => (
            <span
              key={interest}
              className="badge"
              style={{
                fontSize: '0.6875rem',
                backgroundColor: 'var(--color-burgundy-soft)',
                color: 'var(--color-burgundy)',
                border: '1px solid rgba(112, 45, 61, 0.2)'
              }}
            >
              {interest}
            </span>
          ))}
        </div>
      </section>

      {/* 3. Customized Domain Metrics Cards (Unique per User) */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(3, 1fr)',
          gap: 'var(--space-4)',
          marginBottom: 'var(--space-8)'
        }}
        className="domain-metrics-grid"
      >
        {customDashboard.metrics.map((m, idx) => (
          <div
            key={idx}
            className="panel"
            style={{
              backgroundColor: 'var(--color-surface)',
              border: '1px solid var(--color-border)',
              borderRadius: 'var(--radius-md)',
              padding: 'var(--space-4)',
              display: 'flex',
              flexDirection: 'column',
              gap: '4px'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <span style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)', fontWeight: 500 }}>
                {m.label}
              </span>
              <Activity size={13} style={{ color: 'var(--color-burgundy)' }} />
            </div>
            <p className="tabular-nums" style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--color-text)', margin: '2px 0 0 0' }}>
              {m.value}
            </p>
            <span style={{ fontSize: '0.6875rem', color: 'var(--color-text-muted)', lineHeight: 1.4 }}>
              {m.detail}
            </span>
          </div>
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1.8fr) minmax(0, 1.2fr)', gap: 'var(--space-8)' }} className="dashboard-grid">
        {/* Main Column */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-8)' }}>
          {/* 4. Your Next Step (Featured Prominently) */}
          {currentNextStep && (
            <GoalItem task={currentNextStep} onToggleComplete={handleToggleGoal} />
          )}

          {/* 5. Current Career Direction */}
          {activeCareer && (
            <section
              aria-labelledby="career-direction-title"
              className="panel"
              style={{
                display: 'flex',
                flexDirection: 'column',
                gap: 'var(--space-4)',
                backgroundColor: 'var(--color-surface)'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 'var(--space-2)' }}>
                <div>
                  <span className="badge badge-burgundy" style={{ marginBottom: 'var(--space-1)' }}>
                    TARGET DIRECTION
                  </span>
                  <h3
                    id="career-direction-title"
                    style={{
                      fontSize: 'var(--text-lg)',
                      fontFamily: 'var(--font-display)',
                      fontWeight: 600,
                      color: 'var(--color-text)',
                      marginTop: '4px'
                    }}
                  >
                    {activeCareer.title}
                  </h3>
                </div>

                <SecondaryButton
                  size="sm"
                  onClick={() => navigate('/explore')}
                  icon={<Compass size={14} />}
                >
                  Explore this path
                </SecondaryButton>
              </div>

              <p style={{ fontSize: 'var(--text-sm)', color: 'var(--color-text-secondary)', lineHeight: 1.6 }}>
                {activeCareer.description}
              </p>

              <div
                style={{
                  padding: 'var(--space-3) var(--space-4)',
                  backgroundColor: 'var(--color-surface-muted)',
                  borderLeft: '3px solid var(--color-burgundy)',
                  borderRadius: '0 var(--radius-sm) var(--radius-sm) 0',
                  fontSize: 'var(--text-xs)'
                }}
              >
                <strong style={{ color: 'var(--color-text)' }}>Why it fits: </strong>
                <span style={{ color: 'var(--color-text-secondary)' }}>{activeCareer.matchReason}</span>
              </div>

              <div>
                <span style={{ fontSize: 'var(--text-xs)', fontWeight: 600, color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                  Core skills in progress:
                </span>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--space-2)', marginTop: 'var(--space-2)' }}>
                  {activeCareer.requiredSkills.map(s => (
                    <span key={s.name} className="badge badge-muted">
                      {s.name} • {s.importance}
                    </span>
                  ))}
                </div>
              </div>
            </section>
          )}

          {/* 6. Learning Roadmap Preview */}
          <section
            aria-labelledby="roadmap-preview-title"
            className="panel"
            style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
                <BookOpen size={18} style={{ color: 'var(--color-burgundy)' }} aria-hidden="true" />
                <h3
                  id="roadmap-preview-title"
                  style={{
                    fontSize: 'var(--text-base)',
                    fontFamily: 'var(--font-display)',
                    fontWeight: 600
                  }}
                >
                  Learning Roadmap
                </h3>
              </div>

              <button
                onClick={() => navigate('/roadmap')}
                style={{
                  fontSize: 'var(--text-xs)',
                  color: 'var(--color-burgundy)',
                  fontWeight: 600,
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '4px'
                }}
              >
                <span>View full roadmap</span>
                <ArrowRight size={13} />
              </button>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
              {roadmapTasks.slice(0, 4).map(task => (
                <div
                  key={task.id}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: 'var(--space-3) var(--space-4)',
                    backgroundColor: 'var(--color-surface-muted)',
                    borderRadius: 'var(--radius-sm)',
                    border: '1px solid var(--color-border)',
                    fontSize: 'var(--text-sm)',
                    gap: 'var(--space-3)'
                  }}
                >
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '2px', flex: 1 }}>
                    <span
                      style={{
                        fontWeight: 600,
                        color: 'var(--color-text)',
                        textDecoration: task.status === 'completed' ? 'line-through' : 'none',
                        opacity: task.status === 'completed' ? 0.8 : 1
                      }}
                    >
                      {task.title}
                    </span>
                    <span style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)' }}>
                      {task.phaseName} • Est. {task.estimatedTime}
                    </span>
                  </div>

                  <StatusLabel status={task.status} />
                </div>
              ))}
            </div>
          </section>
        </div>

        {/* Sidebar Column */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
          {/* 7. Progress Overview */}
          <section
            aria-labelledby="progress-overview-title"
            className="panel"
            style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
              <Target size={18} style={{ color: 'var(--color-burgundy)' }} aria-hidden="true" />
              <h3
                id="progress-overview-title"
                style={{
                  fontSize: 'var(--text-base)',
                  fontFamily: 'var(--font-display)',
                  fontWeight: 600
                }}
              >
                Progress Overview
              </h3>
            </div>

            <ProgressIndicator
              value={overallProgressPercent}
              label={`${completedTasksCount} of ${totalTasksCount} milestones achieved`}
            />

            <div
              style={{
                display: 'grid',
                gridTemplateColumns: '1fr 1fr',
                gap: 'var(--space-3)',
                paddingTop: 'var(--space-2)'
              }}
            >
              <div
                style={{
                  padding: 'var(--space-3)',
                  backgroundColor: 'var(--color-surface-muted)',
                  borderRadius: 'var(--radius-sm)',
                  border: '1px solid var(--color-border)'
                }}
              >
                <span style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)' }}>Skills Practiced</span>
                <p className="tabular-nums" style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--color-text)', marginTop: '2px' }}>
                  {skills.length}
                </p>
              </div>

              <div
                style={{
                  padding: 'var(--space-3)',
                  backgroundColor: 'var(--color-surface-muted)',
                  borderRadius: 'var(--radius-sm)',
                  border: '1px solid var(--color-border)'
                }}
              >
                <span style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)' }}>Weekly Target</span>
                <p className="tabular-nums" style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--color-burgundy)', marginTop: '2px' }}>
                  {profile.weeklyHours || 8} hrs/wk
                </p>
              </div>
            </div>

            <p style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)', fontStyle: 'italic', borderTop: '1px solid var(--color-border)', paddingTop: 'var(--space-2)' }}>
              {customDashboard.weeklyFocusQuote}
            </p>
          </section>

          {/* 8. NEXORA AI Career Mentor Preview */}
          <section
            aria-labelledby="coach-preview-title"
            className="panel"
            style={{
              backgroundColor: 'var(--color-burgundy-soft)',
              border: '1px solid rgba(112, 45, 61, 0.2)',
              display: 'flex',
              flexDirection: 'column',
              gap: 'var(--space-3)'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
              <Sparkles size={16} style={{ color: 'var(--color-burgundy)' }} aria-hidden="true" />
              <h3
                id="coach-preview-title"
                style={{
                  fontSize: 'var(--text-sm)',
                  fontWeight: 700,
                  textTransform: 'uppercase',
                  letterSpacing: '0.04em',
                  color: 'var(--color-burgundy)'
                }}
              >
                NEXORA AI CAREER MENTOR
              </h3>
            </div>

            <p style={{ fontSize: 'var(--text-sm)', color: 'var(--color-text)', lineHeight: 1.5 }}>
              Not sure which skill to learn next or preparing for an interview? Let's work it out together.
            </p>

            <PrimaryButton
              size="sm"
              onClick={() => navigate('/coach')}
              icon={<MessageSquare size={14} />}
            >
              Talk to my career coach
            </PrimaryButton>
          </section>

          {/* 9. Recommended Discovery Opportunities (Tailored to User Interests) */}
          <section
            aria-labelledby="discovery-title"
            className="panel"
            style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
              <Compass size={16} style={{ color: 'var(--color-burgundy)' }} aria-hidden="true" />
              <h3
                id="discovery-title"
                style={{
                  fontSize: 'var(--text-sm)',
                  fontWeight: 600,
                  color: 'var(--color-text)'
                }}
              >
                Curated Practical Exercises
              </h3>
            </div>

            <p style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)', lineHeight: 1.5 }}>
              Genuine, open-source projects tailored to your specific discipline to prove competence to hiring teams:
            </p>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
              {customDashboard.exercises.map(exercise => (
                <div
                  key={exercise.title}
                  style={{
                    padding: 'var(--space-3)',
                    backgroundColor: 'var(--color-surface-muted)',
                    borderRadius: 'var(--radius-sm)',
                    fontSize: 'var(--text-xs)',
                    border: '1px solid var(--color-border)'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '2px' }}>
                    <strong style={{ color: 'var(--color-text)' }}>{exercise.title}</strong>
                    <span className="badge badge-burgundy" style={{ fontSize: '0.625rem' }}>
                      {exercise.tag}
                    </span>
                  </div>
                  <p style={{ color: 'var(--color-text-secondary)', margin: 0, lineHeight: 1.4 }}>
                    {exercise.description}
                  </p>
                </div>
              ))}
            </div>
          </section>
        </div>
      </div>

      <style>{`
        @media (max-width: 900px) {
          .dashboard-grid {
            grid-template-columns: 1fr !important;
            gap: var(--space-6) !important;
          }
          .domain-metrics-grid {
            grid-template-columns: 1fr !important;
          }
        }
      `}</style>
    </PageContainer>
  );
};
