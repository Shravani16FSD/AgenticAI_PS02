import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Compass, BookOpen, CheckSquare, MessageSquare, LayoutDashboard, Menu, X, User } from 'lucide-react';
import { useApp } from '../../context/AppContext';

export const AppHeader: React.FC = () => {
  const location = useLocation();
  const { profile } = useApp();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);


  // Close on Escape key
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && mobileMenuOpen) {
        setMobileMenuOpen(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [mobileMenuOpen]);

  const navItems = [
    { label: 'Dashboard', path: '/dashboard', icon: <LayoutDashboard size={16} /> },
    { label: 'Explore Careers', path: '/explore', icon: <Compass size={16} /> },
    { label: 'My Roadmap', path: '/roadmap', icon: <BookOpen size={16} /> },
    { label: 'Skills & Progress', path: '/skills', icon: <CheckSquare size={16} /> },
    { label: 'Career Coach', path: '/coach', icon: <MessageSquare size={16} /> },
  ];

  const isActive = (path: string) => {
    if (path === '/dashboard' && (location.pathname === '/dashboard' || location.pathname === '/app')) return true;
    return location.pathname === path;
  };

  return (
    <>
      <header
        style={{
          height: 'var(--header-height)',
          backgroundColor: 'var(--color-surface)',
          borderBottom: '1px solid var(--color-border)',
          position: 'sticky',
          top: 0,
          zIndex: 100,
          display: 'flex',
          alignItems: 'center',
          padding: '0 var(--space-6)',
          width: '100%',
          boxSizing: 'border-box'
        }}
      >
        <div
          style={{
            maxWidth: 'var(--content-max)',
            margin: '0 auto',
            width: '100%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: 'var(--space-6)'
          }}
        >
          {/* Brand Logo & Editorial Title */}
          <Link
            to="/"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 'var(--space-3)',
              textDecoration: 'none',
              color: 'var(--color-text)'
            }}
            aria-label="NEXORA — Home"
          >
            <div
              style={{
                width: '32px',
                height: '32px',
                backgroundColor: 'var(--color-burgundy)',
                color: '#FFFFFF',
                borderRadius: 'var(--radius-sm)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontFamily: 'var(--font-display)',
                fontWeight: 700,
                fontSize: '1.15rem'
              }}
            >
              N
            </div>
            <div style={{ display: 'flex', flexDirection: 'column' }}>
              <span
                style={{
                  fontFamily: 'var(--font-display)',
                  fontWeight: 600,
                  fontSize: '1.25rem',
                  letterSpacing: '-0.02em',
                  lineHeight: 1
                }}
              >
                NEXORA
              </span>
              <span
                style={{
                  fontSize: '0.6875rem',
                  letterSpacing: '0.06em',
                  textTransform: 'uppercase',
                  color: 'var(--color-text-muted)',
                  marginTop: '2px'
                }}
              >
                AI Career Mentor
              </span>
            </div>
          </Link>

          {/* Desktop Navigation */}
          <nav
            aria-label="Main Navigation"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 'var(--space-1)'
            }}
            className="desktop-nav"
          >
            {navItems.map(item => {
              const active = isActive(item.path);
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  aria-current={active ? 'page' : undefined}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.4rem',
                    padding: '0.5rem 0.875rem',
                    borderRadius: 'var(--radius-sm)',
                    fontSize: 'var(--text-sm)',
                    fontWeight: active ? 600 : 500,
                    textDecoration: 'none',
                    color: active ? 'var(--color-burgundy)' : 'var(--color-text)',
                    backgroundColor: active ? 'var(--color-burgundy-soft)' : 'transparent',
                    borderBottom: active ? '2px solid var(--color-burgundy)' : '2px solid transparent',
                    transition: 'background-color var(--transition-fast), color var(--transition-fast)'
                  }}
                  onMouseEnter={e => {
                    if (!active) {
                      e.currentTarget.style.backgroundColor = 'var(--color-surface-muted)';
                    }
                  }}
                  onMouseLeave={e => {
                    if (!active) {
                      e.currentTarget.style.backgroundColor = 'transparent';
                    }
                  }}
                >
                  <span aria-hidden="true" style={{ color: active ? 'var(--color-burgundy)' : 'var(--color-text-secondary)' }}>
                    {item.icon}
                  </span>
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </nav>

          {/* Profile & CTA on the right */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 'var(--space-3)'
            }}
          >
            <Link
              to="/login"
              aria-label="Sign in or switch account dashboard"
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.4rem',
                textDecoration: 'none',
                padding: '0.375rem 0.625rem',
                borderRadius: 'var(--radius-sm)',
                border: '1px solid var(--color-burgundy)',
                backgroundColor: 'var(--color-burgundy-soft)',
                color: 'var(--color-burgundy)',
                fontSize: 'var(--text-xs)',
                fontWeight: 600,
                transition: 'background-color var(--transition-fast)'
              }}
              className="signin-header-link"
            >
              <span>Sign In</span>
            </Link>

            <Link
              to="/profile"
              aria-label="Profile and preferences"
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                textDecoration: 'none',
                padding: '0.375rem 0.75rem',
                borderRadius: 'var(--radius-sm)',
                border: '1px solid var(--color-border)',
                backgroundColor: 'var(--color-surface)',
                color: 'var(--color-text)',
                fontSize: 'var(--text-xs)',
                fontWeight: 600,
                transition: 'border-color var(--transition-fast)'
              }}
              className="profile-link"
            >
              <User size={14} style={{ color: 'var(--color-burgundy)' }} aria-hidden="true" />
              <span>{profile.name || 'My Profile'}</span>
            </Link>

            {/* Mobile menu trigger */}
            <button
              onClick={() => setMobileMenuOpen(prev => !prev)}
              aria-label={mobileMenuOpen ? 'Close navigation menu' : 'Open navigation menu'}
              aria-expanded={mobileMenuOpen}
              className="mobile-menu-btn"
              style={{
                display: 'none',
                padding: '0.5rem',
                borderRadius: 'var(--radius-sm)',
                border: '1px solid var(--color-border)',
                color: 'var(--color-text)',
                backgroundColor: 'var(--color-surface)'
              }}
            >
              {mobileMenuOpen ? <X size={20} /> : <Menu size={20} />}
            </button>
          </div>
        </div>
      </header>

      {/* Mobile Drawer Navigation */}
      {mobileMenuOpen && (
        <div
          role="dialog"
          aria-modal="true"
          aria-label="Mobile Navigation"
          style={{
            position: 'fixed',
            inset: 0,
            top: 'var(--header-height)',
            backgroundColor: 'var(--color-surface)',
            zIndex: 99,
            display: 'flex',
            flexDirection: 'column',
            padding: 'var(--space-6)',
            borderTop: '1px solid var(--color-border)',
            gap: 'var(--space-2)'
          }}
        >
          {navItems.map(item => {
            const active = isActive(item.path);
            return (
              <Link
                key={item.path}
                to={item.path}
                onClick={() => setMobileMenuOpen(false)}
                aria-current={active ? 'page' : undefined}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 'var(--space-3)',
                  padding: 'var(--space-4)',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: 'var(--text-base)',
                  fontWeight: active ? 600 : 500,
                  textDecoration: 'none',
                  color: active ? 'var(--color-burgundy)' : 'var(--color-text)',
                  backgroundColor: active ? 'var(--color-burgundy-soft)' : 'transparent',
                  borderLeft: active ? '3px solid var(--color-burgundy)' : '3px solid transparent'
                }}
              >
                <span aria-hidden="true">{item.icon}</span>
                <span>{item.label}</span>
              </Link>
            );
          })}

          <div style={{ marginTop: 'auto', paddingTop: 'var(--space-4)', borderTop: '1px solid var(--color-border)' }}>
            <Link
              to="/profile"
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 'var(--space-3)',
                padding: 'var(--space-3)',
                textDecoration: 'none',
                color: 'var(--color-text)',
                fontWeight: 600,
                fontSize: 'var(--text-sm)'
              }}
            >
              <User size={18} style={{ color: 'var(--color-burgundy)' }} />
              <span>Signed in as {profile.name}</span>
            </Link>
          </div>
        </div>
      )}

      {/* Media query helpers in CSS */}
      <style>{`
        @media (max-width: 860px) {
          .desktop-nav {
            display: none !important;
          }
          .mobile-menu-btn {
            display: flex !important;
          }
        }
      `}</style>
    </>
  );
};
