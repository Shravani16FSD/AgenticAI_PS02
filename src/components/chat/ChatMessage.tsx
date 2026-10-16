import React, { useState } from 'react';
import { Copy, Check, Sparkles, User } from 'lucide-react';
import { marked } from 'marked';
import DOMPurify from 'dompurify';
import type { ChatMessage as ChatMessageType } from '../../types';

interface ChatMessageProps {
  message: ChatMessageType;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const [copied, setCopied] = useState(false);
  const isAssistant = message.sender === 'assistant';

  const handleCopy = () => {
    navigator.clipboard.writeText(message.text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Safe markdown conversion
  const renderSafeMarkdown = (content: string) => {
    try {
      const rawHtml = marked.parse(content, { gfm: true, breaks: true }) as string;
      const sanitized = DOMPurify.sanitize(rawHtml);
      return { __html: sanitized };
    } catch {
      return { __html: content.replace(/\n/g, '<br/>') };
    }
  };

  const formattedTime = new Intl.DateTimeFormat('en-US', {
    hour: 'numeric',
    minute: 'numeric',
    hour12: true
  }).format(new Date(message.timestamp));

  return (
    <article
      aria-label={`${isAssistant ? 'Career Coach' : 'You'} said:`}
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: isAssistant ? 'flex-start' : 'flex-end',
        gap: 'var(--space-1)',
        width: '100%',
        maxWidth: '820px',
        margin: '0 auto'
      }}
    >
      {/* Sender Eyebrow */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 'var(--space-2)',
          fontSize: 'var(--text-xs)',
          color: 'var(--color-text-muted)',
          padding: '0 var(--space-2)'
        }}
      >
        {isAssistant ? (
          <>
            <Sparkles size={13} style={{ color: 'var(--color-burgundy)' }} aria-hidden="true" />
            <span style={{ fontWeight: 600, color: 'var(--color-text)' }}>Career Mentor</span>
          </>
        ) : (
          <>
            <span style={{ fontWeight: 600 }}>You</span>
            <User size={13} aria-hidden="true" />
          </>
        )}
        <span>•</span>
        <span>{formattedTime}</span>
      </div>

      {/* Message Body */}
      <div
        style={{
          width: '100%',
          backgroundColor: isAssistant ? 'var(--color-surface)' : 'var(--color-surface-muted)',
          border: `1px solid ${isAssistant ? 'var(--color-border)' : 'var(--color-border-strong)'}`,
          borderRadius: 'var(--radius-panel)',
          padding: 'var(--space-5) var(--space-6)',
          position: 'relative',
          boxSizing: 'border-box'
        }}
      >
        <div
          className="chat-markdown-content"
          dangerouslySetInnerHTML={renderSafeMarkdown(message.text)}
          style={{
            fontSize: 'var(--text-base)',
            color: 'var(--color-text)',
            lineHeight: 1.65,
            wordBreak: 'break-word'
          }}
        />

        {isAssistant && message.text && (
          <div
            style={{
              display: 'flex',
              justifyContent: 'flex-end',
              marginTop: 'var(--space-3)',
              paddingTop: 'var(--space-2)',
              borderTop: '1px solid var(--color-surface-muted)'
            }}
          >
            <button
              onClick={handleCopy}
              aria-label={copied ? 'Copied to clipboard' : 'Copy response to clipboard'}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '4px',
                fontSize: 'var(--text-xs)',
                color: 'var(--color-text-muted)',
                padding: '2px 6px',
                borderRadius: 'var(--radius-sm)',
                transition: 'color var(--transition-fast)'
              }}
            >
              {copied ? (
                <>
                  <Check size={13} style={{ color: 'var(--color-success)' }} />
                  <span style={{ color: 'var(--color-success)' }}>Copied</span>
                </>
              ) : (
                <>
                  <Copy size={13} />
                  <span>Copy</span>
                </>
              )}
            </button>
          </div>
        )}
      </div>

      <style>{`
        .chat-markdown-content h1,
        .chat-markdown-content h2,
        .chat-markdown-content h3,
        .chat-markdown-content h4 {
          font-family: var(--font-display);
          font-weight: 600;
          color: var(--color-text);
          margin-top: 1rem;
          margin-bottom: 0.5rem;
          line-height: 1.3;
        }
        .chat-markdown-content h1:first-child,
        .chat-markdown-content h2:first-child,
        .chat-markdown-content h3:first-child {
          margin-top: 0;
        }
        .chat-markdown-content h3 {
          font-size: 1.15rem;
        }
        .chat-markdown-content h4 {
          font-size: 1rem;
        }
        .chat-markdown-content p {
          margin-bottom: 0.75rem;
        }
        .chat-markdown-content p:last-child {
          margin-bottom: 0;
        }
        .chat-markdown-content ul,
        .chat-markdown-content ol {
          margin: 0.5rem 0 0.75rem 1.25rem;
          padding-left: 0.5rem;
        }
        .chat-markdown-content li {
          margin-bottom: 0.375rem;
        }
        .chat-markdown-content strong {
          font-weight: 600;
          color: var(--color-text);
        }
        .chat-markdown-content code {
          background-color: var(--color-surface-muted);
          padding: 2px 6px;
          border-radius: var(--radius-sm);
          font-size: 0.875em;
          border: 1px solid var(--color-border);
        }
      `}</style>
    </article>
  );
};
