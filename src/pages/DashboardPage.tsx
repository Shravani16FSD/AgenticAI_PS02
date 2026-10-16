import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowRight, BookOpen, MessageSquare, Compass, Target, Sparkles } from 'lucide-react';
import { PageContainer, PageHeading } from '../components/ui/Typography';
import { PrimaryButton, SecondaryButton } from '../components/ui/Buttons';
import { ProgressIndicator, StatusLabel } from '../components/ui/FeedbackStates';
import { GoalItem } from '../components/career/CareerSummary';
import { useApp } from '../context/AppContext';

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
    overallProgressPercent
  } = useApp();

  // Find featured "Next Step" task (first in_progress task or first not_started task)
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
        eyebrow="CAREER DASHBOARD"
        title={`Welcome back${profile.name ? `, ${profile.name}` : ''}. Let's pick up where you left off.`}
        description="Your career plan is a work in progress. Here's what you can focus on today."
        actions={
          <PrimaryButton
            size="sm"
            onClick={() => navigate('/coach')}
            icon={<MessageSquare size={14} />}
          >
            Talk to my career coach
          </PrimaryButton>
        }
      />

      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1.8fr) minmax(0, 1.2fr)', gap: 'var(--space-8)' }} className="dashboard-grid">
        {/* Main Column */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-8)' }}>
          {/* 2. Your Next Step (Featured Prominently) */}
          {currentNextStep && (
            <GoalItem task={currentNextStep} onToggleComplete={handleToggleGoal} />
          )}

          {/* 3. Current Career Direction */}
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

          {/* 4. Learning Roadmap Preview */}
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
          {/* 5. Progress Overview */}
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
              "Small steps count. Look how far you've come."
            </p>
          </section>

          {/* 6. Career Coach Preview */}
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
                AI CAREER MENTOR
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

          {/* 7. Recommended Discovery Opportunities (Authentic & Clearly Labeled) */}
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
              Genuine, open-source projects and design challenges you can build to prove competence to hiring teams:
            </p>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
              <div
                style={{
                  padding: 'var(--space-3)',
                  backgroundColor: 'var(--color-surface-muted)',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: 'var(--text-xs)',
                  border: '1px solid var(--color-border)'
                }}
              >
                <strong style={{ color: 'var(--color-text)' }}>Prompt Evaluation Harness</strong>
                <p style={{ color: 'var(--color-text-secondary)', marginTop: '2px' }}>
                  Write an automated Python script that tests model accuracy across 20 synthetic edge cases.
                </p>
              </div>

              <div
                style={{
                  padding: 'var(--space-3)',
                  backgroundColor: 'var(--color-surface-muted)',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: 'var(--text-xs)',
                  border: '1px solid var(--color-border)'
                }}
              >
                <strong style={{ color: 'var(--color-text)' }}>Accessible Design Audit</strong>
                <p style={{ color: 'var(--color-text-secondary)', marginTop: '2px' }}>
                  Audit a public open-source web application for WCAG 2.2 AA contrast and submit a PR.
                </p>
              </div>
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
        }
      `}</style>
    </PageContainer>
  );
};
