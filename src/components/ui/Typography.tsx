import React, { type ReactNode } from 'react';

interface PageHeadingProps {
  eyebrow?: string;
  title: string;
  description?: string;
  actions?: ReactNode;
  level?: 1 | 2;
}

export const PageHeading: React.FC<PageHeadingProps> = ({
  eyebrow,
  title,
  description,
  actions,
  level = 1
}) => {
  const HeadingTag = level === 1 ? 'h1' : 'h2';

  return (
    <header
      style={{
        display: 'flex',
        flexDirection: 'row',
        alignItems: 'flex-start',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: 'var(--space-4)',
        marginBottom: 'var(--space-8)',
        borderBottom: '1px solid var(--color-border)',
        paddingBottom: 'var(--space-6)'
      }}
    >
      <div style={{ maxWidth: '780px', display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
        {eyebrow && (
          <span
            style={{
              fontSize: 'var(--text-xs)',
              fontWeight: 700,
              letterSpacing: '0.08em',
              textTransform: 'uppercase',
              color: 'var(--color-burgundy)'
            }}
          >
            {eyebrow}
          </span>
        )}
        <HeadingTag
          style={{
            fontSize: level === 1 ? 'var(--heading-lg)' : 'var(--heading-md)',
            fontFamily: 'var(--font-display)',
            fontWeight: 600,
            lineHeight: 1.2,
            color: 'var(--color-text)',
            letterSpacing: '-0.02em'
          }}
        >
          {title}
        </HeadingTag>
        {description && (
          <p
            style={{
              fontSize: 'var(--text-base)',
              color: 'var(--color-text-secondary)',
              lineHeight: 1.6,
              marginTop: 'var(--space-1)'
            }}
          >
            {description}
          </p>
        )}
      </div>

      {actions && (
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)', marginTop: 'var(--space-2)' }}>
          {actions}
        </div>
      )}
    </header>
  );
};

interface SectionDividerProps {
  label?: string;
}

export const SectionDivider: React.FC<SectionDividerProps> = ({ label }) => {
  if (!label) {
    return <hr className="divider" aria-hidden="true" />;
  }

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: 'var(--space-4)',
        margin: 'var(--space-8) 0',
        width: '100%'
      }}
      aria-hidden="true"
    >
      <div style={{ flex: 1, height: '1px', backgroundColor: 'var(--color-border)' }} />
      <span
        style={{
          fontSize: 'var(--text-xs)',
          fontWeight: 600,
          textTransform: 'uppercase',
          letterSpacing: '0.06em',
          color: 'var(--color-text-muted)'
        }}
      >
        {label}
      </span>
      <div style={{ flex: 1, height: '1px', backgroundColor: 'var(--color-border)' }} />
    </div>
  );
};

export const PageContainer: React.FC<{ children: ReactNode; className?: string; style?: React.CSSProperties }> = ({
  children,
  className = '',
  style = {}
}) => {
  return (
    <main
      id="main-content"
      className={`page-container ${className}`}
      style={{
        maxWidth: 'var(--content-max)',
        margin: '0 auto',
        padding: 'var(--space-8) var(--space-6)',
        width: '100%',
        boxSizing: 'border-box',
        ...style
      }}
    >
      {children}
    </main>
  );
};
