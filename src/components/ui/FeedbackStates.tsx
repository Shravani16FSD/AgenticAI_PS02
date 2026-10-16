import React, { type ReactNode } from 'react';
import { AlertCircle, CheckCircle2, Clock, HelpCircle, Loader2 } from 'lucide-react';
import type { TaskStatus } from '../../types';
import { PrimaryButton, SecondaryButton } from './Buttons';

// Status Label
interface StatusLabelProps {
  status: TaskStatus;
}

export const StatusLabel: React.FC<StatusLabelProps> = ({ status }) => {
  const config = {
    not_started: {
      label: 'Not started',
      color: 'var(--color-text-secondary)',
      bg: 'var(--color-surface-muted)',
      borderColor: 'var(--color-border)',
      icon: <HelpCircle size={13} aria-hidden="true" />
    },
    in_progress: {
      label: 'In progress',
      color: 'var(--color-warning)',
      bg: 'var(--color-warning-bg)',
      borderColor: 'rgba(128, 84, 0, 0.25)',
      icon: <Clock size={13} aria-hidden="true" />
    },
    completed: {
      label: 'Completed',
      color: 'var(--color-success)',
      bg: 'var(--color-success-bg)',
      borderColor: 'rgba(40, 98, 71, 0.25)',
      icon: <CheckCircle2 size={13} aria-hidden="true" />
    }
  }[status];

  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '0.375rem',
        padding: '0.25rem 0.625rem',
        borderRadius: 'var(--radius-sm)',
        fontSize: 'var(--text-xs)',
        fontWeight: 600,
        color: config.color,
        backgroundColor: config.bg,
        border: `1px solid ${config.borderColor}`,
        letterSpacing: '0.01em',
        lineHeight: 1
      }}
    >
      {config.icon}
      <span>{config.label}</span>
    </span>
  );
};

// Progress Indicator
interface ProgressIndicatorProps {
  value: number; // 0 - 100
  label?: string;
  size?: 'sm' | 'md';
  showPercentage?: boolean;
}

export const ProgressIndicator: React.FC<ProgressIndicatorProps> = ({
  value,
  label,
  size = 'md',
  showPercentage = true
}) => {
  const clampedValue = Math.min(100, Math.max(0, Math.round(value)));
  const height = size === 'sm' ? '6px' : '8px';

  return (
    <div style={{ width: '100%', display: 'flex', flexDirection: 'column', gap: '0.375rem' }}>
      {(label || showPercentage) && (
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: 'var(--text-xs)' }}>
          {label && <span style={{ color: 'var(--color-text-secondary)', fontWeight: 500 }}>{label}</span>}
          {showPercentage && (
            <span className="tabular-nums" style={{ color: 'var(--color-burgundy)', fontWeight: 700, marginLeft: 'auto' }}>
              {clampedValue}%
            </span>
          )}
        </div>
      )}
      <div
        role="progressbar"
        aria-valuenow={clampedValue}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label={label || 'Progress'}
        style={{
          width: '100%',
          height,
          backgroundColor: 'var(--color-surface-muted)',
          border: '1px solid var(--color-border)',
          borderRadius: 'var(--radius-sm)',
          overflow: 'hidden'
        }}
      >
        <div
          style={{
            height: '100%',
            width: `${clampedValue}%`,
            backgroundColor: 'var(--color-burgundy)',
            borderRadius: 'calc(var(--radius-sm) - 1px)',
            transition: 'width 300ms ease'
          }}
        />
      </div>
    </div>
  );
};

// Empty State
interface EmptyStateProps {
  title: string;
  description: string;
  actionLabel?: string;
  onAction?: () => void;
  icon?: ReactNode;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  title,
  description,
  actionLabel,
  onAction,
  icon
}) => {
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: 'var(--space-10) var(--space-6)',
        backgroundColor: 'var(--color-surface)',
        border: '1px dashed var(--color-border-strong)',
        borderRadius: 'var(--radius-panel)',
        textAlign: 'center',
        gap: 'var(--space-4)',
        maxWidth: '560px',
        margin: '0 auto'
      }}
    >
      {icon && (
        <div
          style={{
            color: 'var(--color-burgundy)',
            backgroundColor: 'var(--color-burgundy-soft)',
            padding: 'var(--space-3)',
            borderRadius: 'var(--radius-md)'
          }}
          aria-hidden="true"
        >
          {icon}
        </div>
      )}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.375rem' }}>
        <h3 style={{ fontSize: 'var(--text-lg)', fontWeight: 600, color: 'var(--color-text)' }}>
          {title}
        </h3>
        <p style={{ fontSize: 'var(--text-sm)', color: 'var(--color-text-secondary)', maxWidth: '440px' }}>
          {description}
        </p>
      </div>
      {actionLabel && onAction && (
        <PrimaryButton onClick={onAction} size="sm">
          {actionLabel}
        </PrimaryButton>
      )}
    </div>
  );
};

// Error State
interface ErrorStateProps {
  title?: string;
  message: string;
  onRetry?: () => void;
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  title = 'Something didn\'t work as expected',
  message,
  onRetry
}) => {
  return (
    <div
      role="alert"
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: 'var(--space-8) var(--space-6)',
        backgroundColor: 'var(--color-error-bg)',
        border: '1px solid rgba(165, 44, 50, 0.25)',
        borderRadius: 'var(--radius-panel)',
        textAlign: 'center',
        gap: 'var(--space-3)',
        maxWidth: '560px',
        margin: 'var(--space-6) auto'
      }}
    >
      <AlertCircle size={28} style={{ color: 'var(--color-error)' }} aria-hidden="true" />
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
        <h4 style={{ fontSize: 'var(--text-base)', fontWeight: 600, color: 'var(--color-error)' }}>
          {title}
        </h4>
        <p style={{ fontSize: 'var(--text-sm)', color: 'var(--color-text)' }}>
          {message}
        </p>
      </div>
      {onRetry && (
        <SecondaryButton onClick={onRetry} size="sm" style={{ marginTop: 'var(--space-2)' }}>
          Try again
        </SecondaryButton>
      )}
    </div>
  );
};

// Loading State
interface LoadingStateProps {
  message?: string;
  minHeight?: string;
}

export const LoadingState: React.FC<LoadingStateProps> = ({
  message = 'Loading content…',
  minHeight = '240px'
}) => {
  return (
    <div
      aria-live="polite"
      aria-busy="true"
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight,
        gap: 'var(--space-3)',
        color: 'var(--color-text-secondary)'
      }}
    >
      <Loader2 size={24} style={{ color: 'var(--color-burgundy)', animation: 'spin 1s linear infinite' }} aria-hidden="true" />
      <span style={{ fontSize: 'var(--text-sm)', fontWeight: 500 }}>{message}</span>
    </div>
  );
};
