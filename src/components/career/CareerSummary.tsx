import React from 'react';
import { Bookmark, BookmarkCheck, ArrowRight, CheckCircle2, ExternalLink } from 'lucide-react';
import type { CareerPath, RoadmapTask } from '../../types';
import { PrimaryButton, SecondaryButton } from '../ui/Buttons';

interface CareerSummaryProps {
  career: CareerPath;
  onExplore: (careerId: string) => void;
  isSaved?: boolean;
  onToggleSave?: (careerId: string) => void;
  compact?: boolean;
}

export const CareerSummary: React.FC<CareerSummaryProps> = ({
  career,
  onExplore,
  isSaved = false,
  onToggleSave,
  compact = false
}) => {
  return (
    <article
      className="panel panel-interactive"
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: 'var(--space-4)',
        position: 'relative',
        height: '100%',
        boxSizing: 'border-box'
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 'var(--space-3)' }}>
        <div>
          <span className="badge badge-burgundy" style={{ marginBottom: 'var(--space-2)' }}>
            {career.category}
          </span>
          <h3
            style={{
              fontSize: 'var(--text-lg)',
              fontFamily: 'var(--font-display)',
              fontWeight: 600,
              color: 'var(--color-text)',
              marginTop: 'var(--space-1)'
            }}
          >
            {career.title}
          </h3>
        </div>

        {onToggleSave && (
          <button
            onClick={() => onToggleSave(career.id)}
            aria-label={isSaved ? `Remove ${career.title} from saved` : `Save ${career.title}`}
            title={isSaved ? 'Saved to your paths' : 'Save career'}
            style={{
              padding: '0.375rem',
              borderRadius: 'var(--radius-sm)',
              color: isSaved ? 'var(--color-burgundy)' : 'var(--color-text-muted)',
              backgroundColor: isSaved ? 'var(--color-burgundy-soft)' : 'transparent',
              border: `1px solid ${isSaved ? 'rgba(112,45,61,0.2)' : 'var(--color-border)'}`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
          >
            {isSaved ? <BookmarkCheck size={16} /> : <Bookmark size={16} />}
          </button>
        )}
      </div>

      <p style={{ fontSize: 'var(--text-sm)', color: 'var(--color-text-secondary)', lineHeight: 1.5, flex: 1 }}>
        {career.tagline}
      </p>

      {/* Rationale note */}
      <div
        style={{
          padding: 'var(--space-3)',
          backgroundColor: 'var(--color-surface-muted)',
          borderLeft: '2px solid var(--color-burgundy)',
          borderRadius: '0 var(--radius-sm) var(--radius-sm) 0'
        }}
      >
        <span style={{ fontSize: 'var(--text-xs)', fontWeight: 600, color: 'var(--color-text)' }}>
          Why it may fit:
        </span>
        <p style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)', marginTop: '2px' }}>
          {career.matchReason}
        </p>
      </div>

      {/* Key Skills */}
      {!compact && (
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--space-1)', marginTop: 'var(--space-1)' }}>
          {career.requiredSkills.slice(0, 4).map(skill => (
            <span key={skill.name} className="badge badge-muted">
              {skill.name}
            </span>
          ))}
          {career.requiredSkills.length > 4 && (
            <span style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)', alignSelf: 'center', marginLeft: '4px' }}>
              +{career.requiredSkills.length - 4} more
            </span>
          )}
        </div>
      )}

      <div style={{ marginTop: 'auto', paddingTop: 'var(--space-3)', borderTop: '1px solid var(--color-border)' }}>
        <SecondaryButton
          onClick={() => onExplore(career.id)}
          size="sm"
          fullWidth
          icon={<ArrowRight size={14} />}
          iconPosition="right"
        >
          Explore this path
        </SecondaryButton>
      </div>
    </article>
  );
};

interface GoalItemProps {
  task: RoadmapTask;
  onToggleComplete: (taskId: string, isCompleted: boolean) => void;
}

export const GoalItem: React.FC<GoalItemProps> = ({ task, onToggleComplete }) => {
  const isDone = task.status === 'completed';

  return (
    <section
      aria-label="Your next step"
      className="panel"
      style={{
        borderLeft: '4px solid var(--color-burgundy)',
        backgroundColor: 'var(--color-surface)',
        display: 'flex',
        flexDirection: 'column',
        gap: 'var(--space-4)',
        boxShadow: 'var(--shadow-subtle)'
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 'var(--space-2)' }}>
        <span
          style={{
            fontSize: 'var(--text-xs)',
            fontWeight: 700,
            letterSpacing: '0.08em',
            textTransform: 'uppercase',
            color: 'var(--color-burgundy)'
          }}
        >
          YOUR NEXT STEP
        </span>
        <span
          style={{
            fontSize: 'var(--text-xs)',
            color: 'var(--color-text-secondary)',
            backgroundColor: 'var(--color-surface-muted)',
            padding: '2px 8px',
            borderRadius: 'var(--radius-sm)',
            border: '1px solid var(--color-border)'
          }}
        >
          Estimated {task.estimatedTime}
        </span>
      </div>

      <div>
        <h3
          style={{
            fontSize: 'var(--text-lg)',
            fontFamily: 'var(--font-display)',
            fontWeight: 600,
            color: 'var(--color-text)',
            marginBottom: 'var(--space-1)'
          }}
        >
          {task.title}
        </h3>
        <p style={{ fontSize: 'var(--text-sm)', color: 'var(--color-text-secondary)', lineHeight: 1.6 }}>
          {task.description}
        </p>
      </div>

      {task.resourceName && (
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', fontSize: 'var(--text-xs)' }}>
          <span style={{ color: 'var(--color-text-muted)' }}>Verified Resource:</span>
          <a
            href={task.resourceUrl || '#'}
            target="_blank"
            rel="noopener noreferrer"
            style={{ display: 'inline-flex', alignItems: 'center', gap: '3px', fontWeight: 600 }}
          >
            {task.resourceName}
            <ExternalLink size={12} aria-hidden="true" />
          </a>
        </div>
      )}

      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 'var(--space-3)', paddingTop: 'var(--space-2)', borderTop: '1px solid var(--color-border)' }}>
        <span style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)' }}>
          Skill focus: <strong>{task.skill}</strong>
        </span>

        <PrimaryButton
          size="sm"
          onClick={() => onToggleComplete(task.id, isDone)}
          style={{
            backgroundColor: isDone ? 'var(--color-success)' : 'var(--color-burgundy)',
          }}
          icon={<CheckCircle2 size={15} />}
        >
          {isDone ? 'Marked as completed' : 'Mark completed'}
        </PrimaryButton>
      </div>
    </section>
  );
};
