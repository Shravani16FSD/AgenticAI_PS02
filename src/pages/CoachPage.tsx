import React, { useState, useRef, useEffect } from 'react';
import { Sparkles, Trash2 } from 'lucide-react';
import { PageContainer, PageHeading } from '../components/ui/Typography';
import { SecondaryButton } from '../components/ui/Buttons';
import { ChatMessage } from '../components/chat/ChatMessage';
import { ChatComposer, SuggestedPrompts } from '../components/chat/ChatComposer';
import { ConfirmationDialog } from '../components/ui/Overlays';
import { useApp } from '../context/AppContext';
import { aiService } from '../services/aiService';
import type { ChatMessage as ChatMessageType } from '../types';

export const CoachPage: React.FC = () => {
  const {
    profile,
    activeCareer,
    roadmapTasks,
    skills,
    chatMessages,
    addChatMessage,
    updateChatMessage,
    clearChat
  } = useApp();

  const [isGenerating, setIsGenerating] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string>('');
  const [isClearDialogOpen, setIsClearDialogOpen] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const defaultPrompts = [
    'Help me choose a career direction.',
    'What should I learn to become an AI engineer?',
    'Can you help me prepare for an internship?',
    'Let\'s make a realistic weekly learning plan.'
  ];

  // Auto-scroll to bottom of conversation
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [chatMessages, isGenerating, statusMessage]);

  const handleSendMessage = async (text: string) => {
    const userMsgId = `msg-user-${Date.now()}`;
    const userMsg: ChatMessageType = {
      id: userMsgId,
      sender: 'user',
      text,
      timestamp: Date.now(),
      status: 'delivered'
    };
    addChatMessage(userMsg);

    // Prepare placeholder assistant message
    const assistantMsgId = `msg-assistant-${Date.now()}`;
    const assistantMsg: ChatMessageType = {
      id: assistantMsgId,
      sender: 'assistant',
      text: '',
      timestamp: Date.now(),
      status: 'thinking'
    };
    addChatMessage(assistantMsg);

    setIsGenerating(true);
    setStatusMessage('Thinking through your question…');

    let currentAccumulated = '';

    await aiService.sendMessage(
      text,
      {
        profile,
        activeCareer,
        currentTasks: roadmapTasks,
        skills,
        conversationHistory: chatMessages.map(m => ({ sender: m.sender, text: m.text }))
      },
      {
        onStatusChange: status => {
          setStatusMessage(status);
        },
        onChunk: chunk => {
          currentAccumulated += chunk;
          updateChatMessage(assistantMsgId, {
            text: currentAccumulated,
            status: 'thinking'
          });
        },
        onError: error => {
          setIsGenerating(false);
          setStatusMessage('');
          updateChatMessage(assistantMsgId, {
            text: currentAccumulated ? `${currentAccumulated}\n\n*[${error.message}]*` : error.message,
            status: 'error'
          });
        },
        onDone: (fullText, followUps) => {
          setIsGenerating(false);
          setStatusMessage('');
          updateChatMessage(assistantMsgId, {
            text: fullText,
            status: 'delivered',
            suggestedActions: followUps
          });
        }
      }
    );
  };

  const handleCancelGeneration = () => {
    aiService.cancelCurrentRequest();
    setIsGenerating(false);
    setStatusMessage('');
  };

  // Find latest message suggested actions if any
  const latestAssistantMessage = [...chatMessages].reverse().find(m => m.sender === 'assistant');
  const availablePrompts =
    latestAssistantMessage?.suggestedActions && latestAssistantMessage.suggestedActions.length > 0
      ? latestAssistantMessage.suggestedActions
      : defaultPrompts;

  return (
    <PageContainer style={{ maxWidth: '1160px', paddingBottom: 'var(--space-12)' }}>
      <PageHeading
        eyebrow="AI CAREER MENTOR"
        title="Let's talk about your future."
        description="You can bring a specific question, a career decision, or just a feeling that you're not sure where to begin."
        actions={
          <SecondaryButton
            size="sm"
            onClick={() => setIsClearDialogOpen(true)}
            icon={<Trash2 size={14} />}
          >
            Clear conversation
          </SecondaryButton>
        }
      />

      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1fr) 280px', gap: 'var(--space-8)' }} className="coach-layout">
        {/* Main Conversation Stream */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)', minHeight: '60vh' }}>
          {/* Welcome Intro Header when conversation is fresh */}
          {chatMessages.length <= 1 && (
            <div
              className="panel"
              style={{
                backgroundColor: 'var(--color-surface)',
                border: '1px solid var(--color-border)',
                padding: 'var(--space-6)',
                display: 'flex',
                flexDirection: 'column',
                gap: 'var(--space-3)'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
                <Sparkles size={18} style={{ color: 'var(--color-burgundy)' }} />
                <h3 style={{ fontSize: 'var(--text-base)', fontWeight: 600 }}>
                  How your career mentor works
                </h3>
              </div>
              <p style={{ fontSize: 'var(--text-sm)', color: 'var(--color-text-secondary)', lineHeight: 1.6 }}>
                Every answer is grounded in your active roadmap and goals. We believe in direct answers, brief reasoning, practical next steps, and realistic weekly learning plans.
              </p>
            </div>
          )}

          {/* Messages List */}
          <div
            role="log"
            aria-live="polite"
            aria-label="Conversation history"
            style={{
              display: 'flex',
              flexDirection: 'column',
              gap: 'var(--space-6)',
              flex: 1
            }}
          >
            {chatMessages.map(msg => (
              <ChatMessage key={msg.id} message={msg} />
            ))}
            <div ref={messagesEndRef} />
          </div>

          {/* Suggested Prompts Pill Cards */}
          <div style={{ marginTop: 'var(--space-2)' }}>
            <span style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)', display: 'block', marginBottom: 'var(--space-2)' }}>
              Suggested inquiries:
            </span>
            <SuggestedPrompts
              prompts={availablePrompts}
              onSelectPrompt={handleSendMessage}
              disabled={isGenerating}
            />
          </div>

          {/* Composer Box */}
          <div style={{ position: 'sticky', bottom: 'var(--space-4)', zIndex: 10 }}>
            <ChatComposer
              onSendMessage={handleSendMessage}
              onCancelGeneration={handleCancelGeneration}
              isGenerating={isGenerating}
              statusMessage={statusMessage}
              disabled={isGenerating}
            />
          </div>
        </div>

        {/* Context Sidebar */}
        <aside
          aria-label="Your coaching context"
          className="coach-sidebar"
          style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}
        >
          <div className="panel" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
            <span style={{ fontSize: 'var(--text-xs)', fontWeight: 700, textTransform: 'uppercase', color: 'var(--color-burgundy)', letterSpacing: '0.04em' }}>
              ACTIVE CONTEXT
            </span>

            <div>
              <span style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)' }}>Target Direction</span>
              <p style={{ fontSize: 'var(--text-sm)', fontWeight: 600, color: 'var(--color-text)', marginTop: '2px' }}>
                {activeCareer?.title || 'AI Product Engineer'}
              </p>
            </div>

            <div>
              <span style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)' }}>Stated Goal</span>
              <p style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)', marginTop: '2px', lineHeight: 1.4 }}>
                {profile.primaryGoal}
              </p>
            </div>

            <div>
              <span style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)' }}>Weekly Commitment</span>
              <p style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)', marginTop: '2px' }}>
                {profile.weeklyHours || 8} hours per week
              </p>
            </div>
          </div>

          <div className="panel" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
            <span style={{ fontSize: 'var(--text-xs)', fontWeight: 700, textTransform: 'uppercase', color: 'var(--color-text-secondary)', letterSpacing: '0.04em' }}>
              CURRENT ROADMAP FOCUS
            </span>

            {roadmapTasks.filter(t => t.status === 'in_progress' || t.status === 'not_started').slice(0, 2).map(task => (
              <div
                key={task.id}
                style={{
                  padding: 'var(--space-2) var(--space-3)',
                  backgroundColor: 'var(--color-surface-muted)',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: 'var(--text-xs)',
                  border: '1px solid var(--color-border)'
                }}
              >
                <strong style={{ color: 'var(--color-text)' }}>{task.title}</strong>
                <p style={{ color: 'var(--color-text-muted)', marginTop: '2px' }}>
                  {task.skill} • {task.estimatedTime}
                </p>
              </div>
            ))}
          </div>

          <div
            style={{
              padding: 'var(--space-4)',
              backgroundColor: 'var(--color-surface-muted)',
              borderRadius: 'var(--radius-panel)',
              border: '1px solid var(--color-border)',
              fontSize: 'var(--text-xs)',
              color: 'var(--color-text-secondary)',
              lineHeight: 1.5
            }}
          >
            <strong>Note on privacy & honest AI:</strong>
            <p style={{ marginTop: '4px' }}>
              Your career mentor does not invent credentials or claim guaranteed placements. Real momentum comes from consistent deliberate practice.
            </p>
          </div>
        </aside>
      </div>

      {/* Clear conversation confirmation modal */}
      <ConfirmationDialog
        isOpen={isClearDialogOpen}
        title="Clear conversation history?"
        message="This will reset your conversation with the career coach. Your saved careers, skills, and roadmap tasks will remain intact."
        confirmLabel="Clear conversation"
        isDestructive={true}
        onConfirm={() => {
          clearChat();
          setIsClearDialogOpen(false);
        }}
        onCancel={() => setIsClearDialogOpen(false)}
      />

      <style>{`
        @media (max-width: 860px) {
          .coach-layout {
            grid-template-columns: 1fr !important;
          }
          .coach-sidebar {
            order: 2;
          }
        }
      `}</style>
    </PageContainer>
  );
};
