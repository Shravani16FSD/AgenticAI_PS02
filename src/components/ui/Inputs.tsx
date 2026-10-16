import React, { type InputHTMLAttributes, type SelectHTMLAttributes, useId } from 'react';

interface TextInputProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string;
  hint?: string;
  error?: string;
  required?: boolean;
}

export const TextInput: React.FC<TextInputProps> = ({
  label,
  hint,
  error,
  required,
  id: explicitId,
  disabled,
  style = {},
  className = '',
  ...props
}) => {
  const generatedId = useId();
  const inputId = explicitId || generatedId;
  const hintId = `${inputId}-hint`;
  const errorId = `${inputId}-error`;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.375rem', width: '100%' }}>
      <label
        htmlFor={inputId}
        style={{
          fontSize: 'var(--text-sm)',
          fontWeight: 600,
          color: 'var(--color-text)',
          display: 'flex',
          alignItems: 'center',
          gap: '0.25rem'
        }}
      >
        <span>{label}</span>
        {required && <span style={{ color: 'var(--color-burgundy)', fontSize: '0.75rem' }} aria-hidden="true">*</span>}
      </label>

      {hint && !error && (
        <span id={hintId} style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)', lineHeight: 1.4 }}>
          {hint}
        </span>
      )}

      <input
        id={inputId}
        disabled={disabled}
        aria-invalid={Boolean(error)}
        aria-describedby={error ? errorId : hint ? hintId : undefined}
        style={{
          width: '100%',
          backgroundColor: disabled ? 'var(--color-surface-muted)' : 'var(--color-surface)',
          color: 'var(--color-text)',
          border: `1px solid ${error ? 'var(--color-error)' : 'var(--color-border)'}`,
          borderRadius: 'var(--radius-sm)',
          padding: '0.625rem 0.875rem',
          fontSize: 'var(--text-base)',
          fontFamily: 'var(--font-body)',
          outline: 'none',
          transition: 'border-color var(--transition-fast), box-shadow var(--transition-fast)',
          ...style
        }}
        onFocus={e => {
          if (!error) {
            e.currentTarget.style.borderColor = 'var(--color-focus)';
            e.currentTarget.style.boxShadow = '0 0 0 1px var(--color-focus)';
          }
        }}
        onBlur={e => {
          e.currentTarget.style.borderColor = error ? 'var(--color-error)' : 'var(--color-border)';
          e.currentTarget.style.boxShadow = 'none';
        }}
        className={`text-input ${className}`}
        {...props}
      />

      {error && (
        <span
          id={errorId}
          role="alert"
          style={{
            fontSize: 'var(--text-xs)',
            color: 'var(--color-error)',
            fontWeight: 500,
            display: 'flex',
            alignItems: 'center',
            gap: '0.25rem'
          }}
        >
          {error}
        </span>
      )}
    </div>
  );
};

interface SelectInputProps extends SelectHTMLAttributes<HTMLSelectElement> {
  label: string;
  hint?: string;
  error?: string;
  options: { value: string; label: string }[];
  required?: boolean;
}

export const SelectInput: React.FC<SelectInputProps> = ({
  label,
  hint,
  error,
  options,
  required,
  id: explicitId,
  disabled,
  style = {},
  className = '',
  ...props
}) => {
  const generatedId = useId();
  const selectId = explicitId || generatedId;
  const hintId = `${selectId}-hint`;
  const errorId = `${selectId}-error`;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.375rem', width: '100%' }}>
      <label
        htmlFor={selectId}
        style={{
          fontSize: 'var(--text-sm)',
          fontWeight: 600,
          color: 'var(--color-text)',
          display: 'flex',
          alignItems: 'center',
          gap: '0.25rem'
        }}
      >
        <span>{label}</span>
        {required && <span style={{ color: 'var(--color-burgundy)', fontSize: '0.75rem' }} aria-hidden="true">*</span>}
      </label>

      {hint && !error && (
        <span id={hintId} style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)', lineHeight: 1.4 }}>
          {hint}
        </span>
      )}

      <select
        id={selectId}
        disabled={disabled}
        aria-invalid={Boolean(error)}
        aria-describedby={error ? errorId : hint ? hintId : undefined}
        style={{
          width: '100%',
          backgroundColor: disabled ? 'var(--color-surface-muted)' : 'var(--color-surface)',
          color: 'var(--color-text)',
          border: `1px solid ${error ? 'var(--color-error)' : 'var(--color-border)'}`,
          borderRadius: 'var(--radius-sm)',
          padding: '0.625rem 0.875rem',
          fontSize: 'var(--text-base)',
          fontFamily: 'var(--font-body)',
          outline: 'none',
          cursor: disabled ? 'not-allowed' : 'pointer',
          transition: 'border-color var(--transition-fast)',
          ...style
        }}
        onFocus={e => {
          if (!error) {
            e.currentTarget.style.borderColor = 'var(--color-focus)';
            e.currentTarget.style.boxShadow = '0 0 0 1px var(--color-focus)';
          }
        }}
        onBlur={e => {
          e.currentTarget.style.borderColor = error ? 'var(--color-error)' : 'var(--color-border)';
          e.currentTarget.style.boxShadow = 'none';
        }}
        className={`select-input ${className}`}
        {...props}
      >
        {options.map(opt => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>

      {error && (
        <span
          id={errorId}
          role="alert"
          style={{
            fontSize: 'var(--text-xs)',
            color: 'var(--color-error)',
            fontWeight: 500
          }}
        >
          {error}
        </span>
      )}
    </div>
  );
};
