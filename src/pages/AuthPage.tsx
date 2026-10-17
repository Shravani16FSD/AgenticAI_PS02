import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { ArrowRight, ShieldCheck, Sparkles, CheckCircle2, Lock, ArrowLeft } from 'lucide-react';
import { PageContainer, PageHeading } from '../components/ui/Typography';
import { PrimaryButton, SecondaryButton } from '../components/ui/Buttons';
import { TextInput } from '../components/ui/Inputs';
import { useApp } from '../context/AppContext';

export const AuthPage: React.FC = () => {
  const navigate = useNavigate();
  const { availableUsers, activeUserId, loginUser, isLoggedIn } = useApp();

  const [authMode, setAuthMode] = useState<'signin' | 'register'>('signin');
  const [usernameInput, setUsernameInput] = useState('');
  const [passwordInput, setPasswordInput] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [selectedPersonaId, setSelectedPersonaId] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handlePersonaLogin = async (userId: string) => {
    setSelectedPersonaId(userId);
    setErrorMsg(null);
    try {
      const ok = await loginUser(userId);
      if (ok) {
        navigate('/dashboard');
      }
    } catch {
      setErrorMsg('Failed to sign in. Please try again.');
    } finally {
      setSelectedPersonaId(null);
    }
  };

  const handleManualSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!usernameInput.trim()) {
      setErrorMsg('Please enter a username or user ID.');
      return;
    }

    setIsSubmitting(true);
    setErrorMsg(null);
    try {
      const ok = await loginUser(usernameInput.trim());
      if (ok) {
        navigate('/dashboard');
      } else {
        setErrorMsg(`User '${usernameInput}' not recognized. Try one of the seeded personas below or quick login.`);
      }
    } catch {
      setErrorMsg('Could not establish connection to authentication service.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <PageContainer style={{ maxWidth: '1060px', paddingBottom: 'var(--space-16)' }}>
      {/* Return home link */}
      <div style={{ marginBottom: 'var(--space-4)' }}>
        <Link
          to="/"
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            fontSize: 'var(--text-xs)',
            color: 'var(--color-burgundy)',
            fontWeight: 600,
            textDecoration: 'none'
          }}
        >
          <ArrowLeft size={13} />
          <span>Back to Home</span>
        </Link>
      </div>

      <PageHeading
        eyebrow="NEXORA AUTHENTICATION & ACCESS PORTAL"
        title="Sign In to Your Career Dashboard"
        description="Choose a personalized persona below for instant access, or authenticate with your account credentials. Each profile features tailor-made widgets, distinct interests, and verified skill telemetry."
        actions={
          isLoggedIn && (
            <SecondaryButton
              size="sm"
              onClick={() => navigate('/dashboard')}
              icon={<ArrowRight size={14} />}
              iconPosition="right"
            >
              Continue as active user
            </SecondaryButton>
          )
        }
      />

      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'minmax(0, 1.4fr) minmax(0, 1fr)',
          gap: 'var(--space-8)',
          marginTop: 'var(--space-4)'
        }}
        className="auth-grid"
      >
        {/* Left Column: 1-Click Fast Persona Entry */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-5)' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
              <Sparkles size={18} style={{ color: 'var(--color-burgundy)' }} />
              <h2
                style={{
                  fontSize: 'var(--text-lg)',
                  fontFamily: 'var(--font-display)',
                  fontWeight: 600,
                  color: 'var(--color-text)',
                  margin: 0
                }}
              >
                1-Click Persona Sign-In
              </h2>
            </div>
            <span className="badge badge-burgundy" style={{ fontSize: '0.6875rem' }}>
              Custom Dashboards Enabled
            </span>
          </div>

          <p style={{ fontSize: 'var(--text-sm)', color: 'var(--color-text-secondary)', lineHeight: 1.5, margin: 0 }}>
            Select an engineering persona to load their customized metrics, dedicated GitHub repository evidence, and domain-specific roadmap:
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
            {availableUsers.map(user => {
              const isCurrent = activeUserId === user.id && isLoggedIn;
              const isPending = selectedPersonaId === user.id;

              return (
                <div
                  key={user.id}
                  className="panel"
                  style={{
                    backgroundColor: isCurrent ? 'var(--color-burgundy-soft)' : 'var(--color-surface)',
                    border: isCurrent ? '1.5px solid var(--color-burgundy)' : '1px solid var(--color-border)',
                    borderRadius: 'var(--radius-md)',
                    padding: 'var(--space-4)',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: 'var(--space-3)',
                    transition: 'all var(--transition-fast)'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 'var(--space-3)' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
                      <div
                        style={{
                          width: '42px',
                          height: '42px',
                          borderRadius: '50%',
                          backgroundColor: isCurrent ? 'var(--color-burgundy)' : 'var(--color-surface-muted)',
                          color: isCurrent ? '#FFFFFF' : 'var(--color-burgundy)',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          fontWeight: 700,
                          fontSize: 'var(--text-sm)',
                          border: '1px solid var(--color-border)',
                          flexShrink: 0
                        }}
                      >
                        {user.avatarInitials || user.name.slice(0, 2).toUpperCase()}
                      </div>

                      <div style={{ display: 'flex', flexDirection: 'column' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
                          <span style={{ fontWeight: 600, fontSize: 'var(--text-base)', color: 'var(--color-text)' }}>
                            {user.name}
                          </span>
                          {isCurrent && (
                            <span className="badge badge-success" style={{ fontSize: '0.625rem' }}>
                              Current Active Session
                            </span>
                          )}
                        </div>
                        <span style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)', marginTop: '2px' }}>
                          {user.role || user.study_status}
                        </span>
                      </div>
                    </div>

                    <PrimaryButton
                      size="sm"
                      disabled={isPending}
                      onClick={() => handlePersonaLogin(user.id)}
                      icon={isPending ? undefined : <ArrowRight size={13} />}
                      iconPosition="right"
                      style={{ fontSize: 'var(--text-xs)', flexShrink: 0 }}
                    >
                      {isPending ? 'Logging in...' : isCurrent ? 'Re-enter' : 'Sign in as ' + user.name.split(' ')[0]}
                    </PrimaryButton>
                  </div>

                  {/* Interests preview pills */}
                  {user.interests && user.interests.length > 0 && (
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', paddingTop: 'var(--space-1)' }}>
                      <span style={{ fontSize: '0.6875rem', fontWeight: 600, color: 'var(--color-text-muted)', alignSelf: 'center', marginRight: '4px' }}>
                        INTERESTS:
                      </span>
                      {user.interests.map(interest => (
                        <span
                          key={interest}
                          className="badge badge-muted"
                          style={{
                            fontSize: '0.6875rem',
                            backgroundColor: 'var(--color-surface-muted)',
                            border: '1px solid var(--color-border)',
                            color: 'var(--color-text)'
                          }}
                        >
                          {interest}
                        </span>
                      ))}
                    </div>
                  )}

                  {user.primary_goal && (
                    <p style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)', margin: 0, fontStyle: 'italic' }}>
                      "{user.primary_goal}"
                    </p>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Right Column: Custom Sign-In Form & Security Highlights */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
          <section
            className="panel"
            aria-labelledby="auth-form-title"
            style={{
              backgroundColor: 'var(--color-surface)',
              border: '1px solid var(--color-border)',
              borderRadius: 'var(--radius-md)',
              padding: 'var(--space-6)'
            }}
          >
            {/* Tab switch between Sign In and Register */}
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: '1fr 1fr',
                backgroundColor: 'var(--color-surface-muted)',
                borderRadius: 'var(--radius-sm)',
                padding: '3px',
                marginBottom: 'var(--space-5)'
              }}
            >
              <button
                type="button"
                onClick={() => setAuthMode('signin')}
                style={{
                  padding: '0.45rem',
                  fontSize: 'var(--text-xs)',
                  fontWeight: 600,
                  borderRadius: 'var(--radius-sm)',
                  backgroundColor: authMode === 'signin' ? 'var(--color-surface)' : 'transparent',
                  color: authMode === 'signin' ? 'var(--color-burgundy)' : 'var(--color-text-secondary)',
                  border: authMode === 'signin' ? '1px solid var(--color-border)' : 'none',
                  cursor: 'pointer',
                  transition: 'all var(--transition-fast)'
                }}
              >
                Sign In
              </button>
              <button
                type="button"
                onClick={() => setAuthMode('register')}
                style={{
                  padding: '0.45rem',
                  fontSize: 'var(--text-xs)',
                  fontWeight: 600,
                  borderRadius: 'var(--radius-sm)',
                  backgroundColor: authMode === 'register' ? 'var(--color-surface)' : 'transparent',
                  color: authMode === 'register' ? 'var(--color-burgundy)' : 'var(--color-text-secondary)',
                  border: authMode === 'register' ? '1px solid var(--color-border)' : 'none',
                  cursor: 'pointer',
                  transition: 'all var(--transition-fast)'
                }}
              >
                New Account
              </button>
            </div>

            <h3
              id="auth-form-title"
              style={{
                fontSize: 'var(--text-base)',
                fontFamily: 'var(--font-display)',
                fontWeight: 600,
                color: 'var(--color-text)',
                margin: '0 0 var(--space-2) 0'
              }}
            >
              {authMode === 'signin' ? 'Sign In with Credentials' : 'Create NEXORA Profile'}
            </h3>

            <p style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)', margin: '0 0 var(--space-4) 0', lineHeight: 1.5 }}>
              Enter your registered username or user ID. For quick testing, you may type any persona ID (e.g. <code>alex_morgan</code> or <code>jordan_chen</code>).
            </p>

            {errorMsg && (
              <div
                style={{
                  padding: 'var(--space-3)',
                  backgroundColor: 'var(--color-error-bg)',
                  color: 'var(--color-error)',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: 'var(--text-xs)',
                  marginBottom: 'var(--space-4)',
                  border: '1px solid rgba(165, 44, 50, 0.2)'
                }}
              >
                {errorMsg}
              </div>
            )}

            <form onSubmit={handleManualSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
              <TextInput
                label="Username / User ID"
                value={usernameInput}
                onChange={e => setUsernameInput(e.target.value)}
                placeholder="e.g. alex_morgan or jordan_chen"
                required
              />

              {/* Quick suggestion tags */}
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px', marginTop: '-4px' }}>
                <span style={{ fontSize: '0.6875rem', color: 'var(--color-text-muted)' }}>Quick IDs:</span>
                {['default_user', 'user_jordan_chen', 'user_priya_sharma', 'user_marcus_vance'].map(id => (
                  <button
                    key={id}
                    type="button"
                    onClick={() => setUsernameInput(id)}
                    style={{
                      fontSize: '0.6875rem',
                      background: 'none',
                      border: 'none',
                      color: 'var(--color-burgundy)',
                      textDecoration: 'underline',
                      cursor: 'pointer',
                      padding: 0
                    }}
                  >
                    {id}
                  </button>
                ))}
              </div>

              <TextInput
                label="Password"
                type="password"
                value={passwordInput}
                onChange={e => setPasswordInput(e.target.value)}
                placeholder="••••••••••••"
              />

              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: 'var(--text-xs)' }}>
                <label style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--color-text-secondary)', cursor: 'pointer' }}>
                  <input type="checkbox" defaultChecked style={{ accentColor: 'var(--color-burgundy)' }} />
                  <span>Stay signed in on this browser</span>
                </label>
              </div>

              <PrimaryButton
                type="submit"
                size="md"
                disabled={isSubmitting}
                icon={<Lock size={14} />}
                style={{ width: '100%', justifyContent: 'center', marginTop: 'var(--space-2)' }}
              >
                {isSubmitting ? 'Authenticating...' : authMode === 'signin' ? 'Sign In to NEXORA' : 'Create & Access Dashboard'}
              </PrimaryButton>
            </form>
          </section>

          {/* Security & Personalization Highlights */}
          <section
            className="panel"
            style={{
              backgroundColor: 'var(--color-surface-muted)',
              border: '1px solid var(--color-border)',
              borderRadius: 'var(--radius-md)',
              padding: 'var(--space-4)',
              display: 'flex',
              flexDirection: 'column',
              gap: 'var(--space-3)'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
              <ShieldCheck size={16} style={{ color: 'var(--color-burgundy)' }} />
              <span style={{ fontSize: 'var(--text-xs)', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.04em', color: 'var(--color-text)' }}>
                NEXORA Architecture
              </span>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)', fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)' }}>
              <div style={{ display: 'flex', alignItems: 'flex-start', gap: '8px' }}>
                <CheckCircle2 size={14} style={{ color: 'var(--color-success)', flexShrink: 0, marginTop: '2px' }} />
                <span>
                  <strong style={{ color: 'var(--color-text)' }}>Customized User Dashboards:</strong> Telemetry metrics, active goals, and skill progress automatically adapt to your domain.
                </span>
              </div>
              <div style={{ display: 'flex', alignItems: 'flex-start', gap: '8px' }}>
                <CheckCircle2 size={14} style={{ color: 'var(--color-success)', flexShrink: 0, marginTop: '2px' }} />
                <span>
                  <strong style={{ color: 'var(--color-text)' }}>AST Code Telemetry:</strong> Codebase commits and syntax trees are verified in real time without mocks.
                </span>
              </div>
              <div style={{ display: 'flex', alignItems: 'flex-start', gap: '8px' }}>
                <CheckCircle2 size={14} style={{ color: 'var(--color-success)', flexShrink: 0, marginTop: '2px' }} />
                <span>
                  <strong style={{ color: 'var(--color-text)' }}>One-Click Account Switching:</strong> Effortlessly explore how different senior roles are evaluated.
                </span>
              </div>
            </div>
          </section>
        </div>
      </div>

      <style>{`
        @media (max-width: 860px) {
          .auth-grid {
            grid-template-columns: 1fr !important;
          }
        }
      `}</style>
    </PageContainer>
  );
};
