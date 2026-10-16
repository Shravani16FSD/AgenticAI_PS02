import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowRight, Compass, BookOpen, MessageSquare, Sparkles } from 'lucide-react';
import { PageContainer } from '../components/ui/Typography';
import { PrimaryButton, SecondaryButton } from '../components/ui/Buttons';
import { useApp } from '../context/AppContext';

export const LandingPage: React.FC = () => {
  const navigate = useNavigate();
  const { profile, activeCareer, roadmapTasks } = useApp();

  return (
    <div>
      {/* Editorial Hero Section */}
      <section
        style={{
          borderBottom: '1px solid var(--color-border)',
          backgroundColor: 'var(--color-surface)',
          padding: 'var(--space-16) var(--space-6) var(--space-20)',
          position: 'relative'
        }}
      >
        <div
          style={{
            maxWidth: 'var(--content-max)',
            margin: '0 auto',
            display: 'grid',
            gridTemplateColumns: 'minmax(320px, 1.15fr) minmax(300px, 0.85fr)',
            gap: 'var(--space-12)',
            alignItems: 'center'
          }}
          className="hero-grid"
        >
          {/* Left Column: Editorial Headline & Messaging */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
              <span
                style={{
                  fontSize: 'var(--text-xs)',
                  fontWeight: 700,
                  letterSpacing: '0.1em',
                  textTransform: 'uppercase',
                  color: 'var(--color-burgundy)',
                  backgroundColor: 'var(--color-burgundy-soft)',
                  padding: '4px 10px',
                  borderRadius: 'var(--radius-sm)'
                }}
              >
                YOUR PERSONAL CAREER COMPANION
              </span>
            </div>

            <h1
              style={{
                fontFamily: 'var(--font-display)',
                fontSize: 'var(--heading-xl)',
                lineHeight: 1.15,
                fontWeight: 600,
                color: 'var(--color-text)',
                letterSpacing: '-0.025em'
              }}
            >
              Your next chapter starts here.
            </h1>

            <p
              style={{
                fontSize: 'var(--text-lg)',
                color: 'var(--color-text-secondary)',
                lineHeight: 1.6,
                maxWidth: '560px'
              }}
            >
              You have interests, ambitions, and a lot of possible directions. Let's turn them into a plan you can actually follow.
            </p>

            <div
              style={{
                display: 'flex',
                flexWrap: 'wrap',
                gap: 'var(--space-3)',
                marginTop: 'var(--space-4)'
              }}
            >
              <PrimaryButton
                size="lg"
                onClick={() => navigate(profile.onboardingCompleted ? '/dashboard' : '/onboarding')}
                icon={<ArrowRight size={16} />}
                iconPosition="right"
              >
                {profile.onboardingCompleted ? 'Explore my career path' : 'Start my career journey'}
              </PrimaryButton>

              <SecondaryButton
                size="lg"
                onClick={() => navigate('/coach')}
                icon={<MessageSquare size={16} />}
              >
                Talk to my career coach
              </SecondaryButton>
            </div>

            <span
              style={{
                fontSize: 'var(--text-xs)',
                color: 'var(--color-text-muted)',
                fontStyle: 'italic',
                marginTop: 'var(--space-2)'
              }}
            >
              Start with where you are. Build from there.
            </span>
          </div>

          {/* Right Column: Authentic Product Preview (No generic fake illustrations) */}
          <div
            className="panel"
            style={{
              padding: 'var(--space-6)',
              backgroundColor: 'var(--color-page)',
              border: '1px solid var(--color-border-strong)',
              boxShadow: 'var(--shadow-dropdown)',
              display: 'flex',
              flexDirection: 'column',
              gap: 'var(--space-4)'
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span className="badge badge-burgundy">Current Focus</span>
              <span style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)' }}>
                Target: {activeCareer?.title || 'AI Product Engineer'}
              </span>
            </div>

            <div
              style={{
                backgroundColor: 'var(--color-surface)',
                padding: 'var(--space-4)',
                borderRadius: 'var(--radius-md)',
                border: '1px solid var(--color-border)'
              }}
            >
              <span style={{ fontSize: 'var(--text-xs)', color: 'var(--color-burgundy)', fontWeight: 700, textTransform: 'uppercase' }}>
                Your Next Step Today
              </span>
              <h4 style={{ fontSize: 'var(--text-base)', fontWeight: 600, color: 'var(--color-text)', marginTop: '4px' }}>
                Spend 25 minutes practicing Python fundamentals & structured outputs
              </h4>
              <p style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)', marginTop: '4px' }}>
                Understanding schema validation with Pydantic ensures models return reliable JSON.
              </p>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
              <span style={{ fontSize: 'var(--text-xs)', fontWeight: 600, color: 'var(--color-text-secondary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                Roadmap Snapshot
              </span>

              {roadmapTasks.slice(0, 3).map((task, idx) => (
                <div
                  key={task.id}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: 'var(--space-2) var(--space-3)',
                    backgroundColor: 'var(--color-surface)',
                    borderRadius: 'var(--radius-sm)',
                    border: '1px solid var(--color-border)',
                    fontSize: 'var(--text-xs)'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
                    <span
                      style={{
                        width: '18px',
                        height: '18px',
                        borderRadius: '50%',
                        backgroundColor: task.status === 'completed' ? 'var(--color-success-bg)' : 'var(--color-surface-muted)',
                        color: task.status === 'completed' ? 'var(--color-success)' : 'var(--color-text-muted)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontWeight: 700,
                        fontSize: '10px'
                      }}
                    >
                      {idx + 1}
                    </span>
                    <span style={{ fontWeight: 500, color: 'var(--color-text)', textDecoration: task.status === 'completed' ? 'line-through' : 'none' }}>
                      {task.title.substring(0, 42)}…
                    </span>
                  </div>
                  <span
                    style={{
                      color: task.status === 'completed' ? 'var(--color-success)' : 'var(--color-text-secondary)',
                      fontWeight: 600,
                      textTransform: 'capitalize'
                    }}
                  >
                    {task.status.replace('_', ' ')}
                  </span>
                </div>
              ))}
            </div>

            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 'var(--space-2)',
                paddingTop: 'var(--space-3)',
                borderTop: '1px solid var(--color-border)',
                fontSize: 'var(--text-xs)',
                color: 'var(--color-text-muted)'
              }}
            >
              <Sparkles size={14} style={{ color: 'var(--color-burgundy)' }} />
              <span>Personalized for your 8-hour weekly pace.</span>
            </div>
          </div>
        </div>
      </section>

      {/* Value Pillars Section */}
      <section style={{ padding: 'var(--space-16) var(--space-6)' }}>
        <PageContainer>
          <div style={{ textAlign: 'center', maxWidth: '640px', margin: '0 auto var(--space-12)' }}>
            <span style={{ fontSize: 'var(--text-xs)', fontWeight: 700, letterSpacing: '0.08em', textTransform: 'uppercase', color: 'var(--color-burgundy)' }}>
              THE PHILOSOPHY
            </span>
            <h2 style={{ fontSize: 'var(--heading-lg)', fontFamily: 'var(--font-display)', marginTop: 'var(--space-2)' }}>
              Career planning designed for human clarity, not algorithmic noise.
            </h2>
          </div>

          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
              gap: 'var(--space-6)'
            }}
          >
            <div className="panel" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
              <div
                style={{
                  width: '36px',
                  height: '36px',
                  borderRadius: 'var(--radius-sm)',
                  backgroundColor: 'var(--color-burgundy-soft)',
                  color: 'var(--color-burgundy)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}
              >
                <Compass size={20} />
              </div>
              <h3 style={{ fontSize: 'var(--text-base)', fontWeight: 600 }}>Explore with context</h3>
              <p style={{ fontSize: 'var(--text-sm)', color: 'var(--color-text-secondary)', lineHeight: 1.6 }}>
                Understand what engineers, designers, and researchers actually do each day. We clarify responsibilities, required skills, and realistic entry points without hype.
              </p>
            </div>

            <div className="panel" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
              <div
                style={{
                  width: '36px',
                  height: '36px',
                  borderRadius: 'var(--radius-sm)',
                  backgroundColor: 'var(--color-burgundy-soft)',
                  color: 'var(--color-burgundy)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}
              >
                <BookOpen size={20} />
              </div>
              <h3 style={{ fontSize: 'var(--text-base)', fontWeight: 600 }}>Sequenced, achievable roadmaps</h3>
              <p style={{ fontSize: 'var(--text-sm)', color: 'var(--color-text-secondary)', lineHeight: 1.6 }}>
                Break complex ambitions into sequential phases: Foundations, Core Skills, Applied Projects, and Interview Readiness. Every task has a defined time estimate.
              </p>
            </div>

            <div className="panel" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
              <div
                style={{
                  width: '36px',
                  height: '36px',
                  borderRadius: 'var(--radius-sm)',
                  backgroundColor: 'var(--color-burgundy-soft)',
                  color: 'var(--color-burgundy)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}
              >
                <MessageSquare size={20} />
              </div>
              <h3 style={{ fontSize: 'var(--text-base)', fontWeight: 600 }}>Supportive AI mentor</h3>
              <p style={{ fontSize: 'var(--text-sm)', color: 'var(--color-text-secondary)', lineHeight: 1.6 }}>
                Bring genuine dilemmas, interview preparation questions, or schedule planning. Your coach responds with reasoned advice and actionable next steps.
              </p>
            </div>
          </div>
        </PageContainer>
      </section>

      {/* How It Works Editorial Section */}
      <section
        style={{
          backgroundColor: 'var(--color-surface)',
          borderTop: '1px solid var(--color-border)',
          borderBottom: '1px solid var(--color-border)',
          padding: 'var(--space-16) var(--space-6)'
        }}
      >
        <PageContainer>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-8)' }}>
            <div>
              <span style={{ fontSize: 'var(--text-xs)', fontWeight: 700, letterSpacing: '0.08em', textTransform: 'uppercase', color: 'var(--color-burgundy)' }}>
                HOW IT WORKS
              </span>
              <h2 style={{ fontSize: 'var(--heading-lg)', fontFamily: 'var(--font-display)', marginTop: 'var(--space-2)' }}>
                Three simple steps to build your momentum.
              </h2>
            </div>

            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
                gap: 'var(--space-8)'
              }}
            >
              <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
                <span style={{ fontFamily: 'var(--font-display)', fontSize: '2.5rem', color: 'var(--color-burgundy)', lineHeight: 1, fontWeight: 700 }}>
                  01
                </span>
                <h3 style={{ fontSize: 'var(--text-base)', fontWeight: 600 }}>Reflect on your interests & strengths</h3>
                <p style={{ fontSize: 'var(--text-sm)', color: 'var(--color-text-secondary)', lineHeight: 1.6 }}>
                  Complete a 3-minute onboarding that assesses where you are right now, what you study, and how much time you can realistically commit each week.
                </p>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
                <span style={{ fontFamily: 'var(--font-display)', fontSize: '2.5rem', color: 'var(--color-burgundy)', lineHeight: 1, fontWeight: 700 }}>
                  02
                </span>
                <h3 style={{ fontSize: 'var(--text-base)', fontWeight: 600 }}>Receive a structured roadmap</h3>
                <p style={{ fontSize: 'var(--text-sm)', color: 'var(--color-text-secondary)', lineHeight: 1.6 }}>
                  Get an ordered sequence of verified educational material, hands-on tasks, and project milestones tailored to your target career.
                </p>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
                <span style={{ fontFamily: 'var(--font-display)', fontSize: '2.5rem', color: 'var(--color-burgundy)', lineHeight: 1, fontWeight: 700 }}>
                  03
                </span>
                <h3 style={{ fontSize: 'var(--text-base)', fontWeight: 600 }}>Execute with continuous guidance</h3>
                <p style={{ fontSize: 'var(--text-sm)', color: 'var(--color-text-secondary)', lineHeight: 1.6 }}>
                  Focus on one achievable next step at a time. Consult your AI mentor whenever you need advice, code feedback, or interview roleplay.
                </p>
              </div>
            </div>
          </div>
        </PageContainer>
      </section>

      {/* Final Warm Call to Action */}
      <section style={{ padding: 'var(--space-16) var(--space-6) var(--space-20)', textAlign: 'center' }}>
        <div
          style={{
            maxWidth: '680px',
            margin: '0 auto',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: 'var(--space-4)'
          }}
        >
          <h2 style={{ fontSize: 'var(--heading-lg)', fontFamily: 'var(--font-display)' }}>
            Start with where you are. Build from there.
          </h2>
          <p style={{ fontSize: 'var(--text-base)', color: 'var(--color-text-secondary)', lineHeight: 1.6 }}>
            Let's make sense of your options and find a next step that feels right for you. No pressure to have everything figured out today.
          </p>

          <div style={{ display: 'flex', gap: 'var(--space-3)', marginTop: 'var(--space-4)', flexWrap: 'wrap', justifyContent: 'center' }}>
            <PrimaryButton size="lg" onClick={() => navigate('/onboarding')} icon={<ArrowRight size={16} />} iconPosition="right">
              Start my career journey
            </PrimaryButton>
            <SecondaryButton size="lg" onClick={() => navigate('/coach')}>
              Meet your career coach
            </SecondaryButton>
          </div>
        </div>
      </section>

      <style>{`
        @media (max-width: 860px) {
          .hero-grid {
            grid-template-columns: 1fr !important;
            gap: var(--space-8) !important;
          }
        }
      `}</style>
    </div>
  );
};
