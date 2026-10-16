import React, { useState, useRef, useEffect, type KeyboardEvent } from 'react';
import { Send, Square, Sparkles } from 'lucide-react';
import { PrimaryButton, SecondaryButton } from '../ui/Buttons';

interface ChatComposerProps {
  onSendMessage: (message: string) => void;
  onCancelGeneration?: () => void;
  isGenerating?: boolean;
  statusMessage?: string;
  disabled?: boolean;
}

export const ChatComposer: React.FC<ChatComposerProps> = ({
  onSendMessage,
  onCancelGeneration,
  isGenerating = false,
  statusMessage,
  disabled = false
}) => {
  const [text, setText] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea up to 160px
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      const scrollHeight = textareaRef.current.scrollHeight;
      textareaRef.current.style.height = `${Math.min(scrollHeight, 160)}px`;
    }
  }, [text]);

  const handleSubmit = () => {
    const trimmed = text.trim();
    if (!trimmed || isGenerating || disabled) return;
    onSendMessage(trimmed);
    setText('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: 'var(--space-2)',
        width: '100%',
        maxWidth: '820px',
        margin: '0 auto'
      }}
    >
      {/* Honest AI status indicator */}
      {isGenerating && statusMessage && (
        <div
          role="status"
          aria-live="polite"
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: 'var(--space-2)',
            fontSize: 'var(--text-xs)',
            color: 'var(--color-text-secondary)',
            backgroundColor: 'var(--color-burgundy-soft)',
            border: '1px solid rgba(112,45,61,0.15)',
            padding: 'var(--space-2) var(--space-4)',
            borderRadius: 'var(--radius-sm)'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
            <span
              style={{
                width: '6px',
                height: '6px',
                borderRadius: '50%',
                backgroundColor: 'var(--color-burgundy)',
                display: 'inline-block',
                animation: 'pulse 1.5s infinite'
              }}
              aria-hidden="true"
            />
            <span>{statusMessage}</span>
          </div>

          {onCancelGeneration && (
            <button
              onClick={onCancelGeneration}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '4px',
                fontSize: 'var(--text-xs)',
                color: 'var(--color-burgundy)',
                fontWeight: 600,
                cursor: 'pointer'
              }}
            >
              <Square size={12} fill="currentColor" />
              <span>Stop response</span>
            </button>
          )}
        </div>
      )}

      {/* Main Composer Box */}
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          backgroundColor: 'var(--color-surface)',
          border: '1px solid var(--color-border-strong)',
          borderRadius: 'var(--radius-panel)',
          padding: 'var(--space-3) var(--space-4)',
          boxShadow: 'var(--shadow-subtle)',
          transition: 'border-color var(--transition-fast)'
        }}
        onFocus={() => {
          const el = document.getElementById('chat-composer-box');
          if (el) el.style.borderColor = 'var(--color-focus)';
        }}
      >
        <label htmlFor="chat-textarea" className="sr-only" style={{ position: 'absolute', width: '1px', height: '1px', overflow: 'hidden', clip: 'rect(0,0,0,0)' }}>
          Tell your career coach what you are thinking about
        </label>

        <textarea
          id="chat-textarea"
          ref={textareaRef}
          value={text}
          onChange={e => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={disabled || isGenerating}
          placeholder="Tell me what you're thinking about..."
          rows={2}
          style={{
            width: '100%',
            backgroundColor: 'transparent',
            border: 'none',
            outline: 'none',
            fontSize: 'var(--text-base)',
            fontFamily: 'var(--font-body)',
            color: 'var(--color-text)',
            lineHeight: 1.5,
            resize: 'none',
            minHeight: '48px',
            maxHeight: '160px',
            boxSizing: 'border-box'
          }}
        />

        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            borderTop: '1px solid var(--color-surface-muted)',
            paddingTop: 'var(--space-2)',
            marginTop: 'var(--space-1)'
          }}
        >
          <span style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)' }}>
            Press <strong>Enter</strong> to send, <strong>Shift+Enter</strong> for newline
          </span>

          <PrimaryButton
            size="sm"
            onClick={handleSubmit}
            disabled={!text.trim() || isGenerating || disabled}
            icon={<Send size={14} />}
            iconPosition="right"
            aria-label="Send message to career coach"
          >
            Send
          </PrimaryButton>
        </div>
      </div>
    </div>
  );
};

interface SuggestedPromptProps {
  prompts: string[];
  onSelectPrompt: (prompt: string) => void;
  disabled?: boolean;
}

export const SuggestedPrompts: React.FC<SuggestedPromptProps> = ({
  prompts,
  onSelectPrompt,
  disabled = false
}) => {
  return (
    <div
      style={{
        display: 'flex',
        flexWrap: 'wrap',
        gap: 'var(--space-2)',
        width: '100%',
        maxWidth: '820px',
        margin: '0 auto'
      }}
    >
      {prompts.map((prompt, idx) => (
        <SecondaryButton
          key={idx}
          size="sm"
          disabled={disabled}
          onClick={() => onSelectPrompt(prompt)}
          icon={<Sparkles size={12} style={{ color: 'var(--color-burgundy)' }} />}
          style={{
            textAlign: 'left',
            borderRadius: 'var(--radius-sm)',
            fontSize: 'var(--text-xs)',
            backgroundColor: 'var(--color-surface)',
            border: '1px solid var(--color-border)'
          }}
        >
          {prompt}
        </SecondaryButton>
      ))}
    </div>
  );
};
