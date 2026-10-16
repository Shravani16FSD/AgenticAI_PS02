import React, { type ButtonHTMLAttributes, type ReactNode } from 'react';
import { Loader2 } from 'lucide-react';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;
  isLoading?: boolean;
  icon?: ReactNode;
  iconPosition?: 'left' | 'right';
  size?: 'sm' | 'md' | 'lg';
  fullWidth?: boolean;
}

export const PrimaryButton: React.FC<ButtonProps> = ({
  children,
  isLoading = false,
  icon,
  iconPosition = 'left',
  size = 'md',
  fullWidth = false,
  disabled,
  className = '',
  style = {},
  ...props
}) => {
  const sizeStyles = {
    sm: { padding: '0.375rem 0.75rem', fontSize: 'var(--text-xs)', height: '32px' },
    md: { padding: '0.625rem 1.25rem', fontSize: 'var(--text-sm)', height: '40px' },
    lg: { padding: '0.75rem 1.75rem', fontSize: 'var(--text-base)', height: '48px' },
  }[size];

  return (
    <button
      disabled={disabled || isLoading}
      aria-busy={isLoading}
      style={{
        display: fullWidth ? 'flex' : 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '0.5rem',
        backgroundColor: disabled ? 'var(--color-border)' : 'var(--color-burgundy)',
        color: disabled ? 'var(--color-text-muted)' : '#FFFFFF',
        border: '1px solid transparent',
        borderRadius: 'var(--radius-sm)',
        fontWeight: 600,
        letterSpacing: '0.01em',
        cursor: disabled || isLoading ? 'not-allowed' : 'pointer',
        transition: 'background-color var(--transition-fast), border-color var(--transition-fast), transform 100ms ease',
        width: fullWidth ? '100%' : 'auto',
        ...sizeStyles,
        ...style
      }}
      onMouseEnter={e => {
        if (!disabled && !isLoading) {
          e.currentTarget.style.backgroundColor = 'var(--color-burgundy-hover)';
        }
      }}
      onMouseLeave={e => {
        if (!disabled && !isLoading) {
          e.currentTarget.style.backgroundColor = 'var(--color-burgundy)';
        }
      }}
      className={`primary-button ${className}`}
      {...props}
    >
      {isLoading ? (
        <>
          <Loader2 size={16} className="animate-spin" aria-hidden="true" style={{ animation: 'spin 1s linear infinite' }} />
          <span>Please wait…</span>
        </>
      ) : (
        <>
          {icon && iconPosition === 'left' && <span aria-hidden="true">{icon}</span>}
          <span>{children}</span>
          {icon && iconPosition === 'right' && <span aria-hidden="true">{icon}</span>}
        </>
      )}
    </button>
  );
};

export const SecondaryButton: React.FC<ButtonProps> = ({
  children,
  isLoading = false,
  icon,
  iconPosition = 'left',
  size = 'md',
  fullWidth = false,
  disabled,
  className = '',
  style = {},
  ...props
}) => {
  const sizeStyles = {
    sm: { padding: '0.375rem 0.75rem', fontSize: 'var(--text-xs)', height: '32px' },
    md: { padding: '0.625rem 1.25rem', fontSize: 'var(--text-sm)', height: '40px' },
    lg: { padding: '0.75rem 1.75rem', fontSize: 'var(--text-base)', height: '48px' },
  }[size];

  return (
    <button
      disabled={disabled || isLoading}
      aria-busy={isLoading}
      style={{
        display: fullWidth ? 'flex' : 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '0.5rem',
        backgroundColor: 'var(--color-surface)',
        color: disabled ? 'var(--color-text-muted)' : 'var(--color-text)',
        border: '1px solid var(--color-border)',
        borderRadius: 'var(--radius-sm)',
        fontWeight: 500,
        cursor: disabled || isLoading ? 'not-allowed' : 'pointer',
        transition: 'background-color var(--transition-fast), border-color var(--transition-fast)',
        width: fullWidth ? '100%' : 'auto',
        ...sizeStyles,
        ...style
      }}
      onMouseEnter={e => {
        if (!disabled && !isLoading) {
          e.currentTarget.style.backgroundColor = 'var(--color-surface-muted)';
          e.currentTarget.style.borderColor = 'var(--color-border-strong)';
        }
      }}
      onMouseLeave={e => {
        if (!disabled && !isLoading) {
          e.currentTarget.style.backgroundColor = 'var(--color-surface)';
          e.currentTarget.style.borderColor = 'var(--color-border)';
        }
      }}
      className={`secondary-button ${className}`}
      {...props}
    >
      {isLoading ? (
        <>
          <Loader2 size={16} style={{ animation: 'spin 1s linear infinite' }} aria-hidden="true" />
          <span>Loading…</span>
        </>
      ) : (
        <>
          {icon && iconPosition === 'left' && <span aria-hidden="true">{icon}</span>}
          <span>{children}</span>
          {icon && iconPosition === 'right' && <span aria-hidden="true">{icon}</span>}
        </>
      )}
    </button>
  );
};
