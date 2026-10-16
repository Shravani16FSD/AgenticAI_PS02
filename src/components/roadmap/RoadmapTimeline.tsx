import React from 'react';
import { CheckCircle2, Circle, Clock, ExternalLink, Trash2 } from 'lucide-react';
import type { RoadmapTask, TaskStatus } from '../../types';
import { StatusLabel } from '../ui/FeedbackStates';

interface RoadmapTimelineProps {
  tasks: RoadmapTask[];
  onStatusChange: (taskId: string, status: TaskStatus) => void;
  onDeleteTask?: (taskId: string) => void;
  interactive?: boolean;
}

export const RoadmapTimeline: React.FC<RoadmapTimelineProps> = ({
  tasks,
  onStatusChange,
  onDeleteTask,
  interactive = true
}) => {
  // Group tasks by Phase
  const phases = [1, 2, 3, 4, 5];

  const getPhaseName = (phaseNum: number) => {
    const found = tasks.find(t => t.phaseId === phaseNum);
    if (found) return found.phaseName;
    const defaults = [
      'Phase 1: Foundations',
      'Phase 2: Core Skills',
      'Phase 3: Applied Projects',
      'Phase 4: Portfolio & Systems',
      'Phase 5: Job & Internship Readiness'
    ];
    return defaults[phaseNum - 1] || `Phase ${phaseNum}`;
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-8)' }}>
      {phases.map(phaseNum => {
        const phaseTasks = tasks.filter(t => t.phaseId === phaseNum);
        if (phaseTasks.length === 0) return null;

        const allPhaseCompleted = phaseTasks.every(t => t.status === 'completed');

        return (
          <section
            key={phaseNum}
            aria-labelledby={`phase-title-${phaseNum}`}
            style={{
              display: 'flex',
              flexDirection: 'column',
              gap: 'var(--space-4)',
              position: 'relative'
            }}
          >
            {/* Phase Header */}
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                paddingBottom: 'var(--space-2)',
                borderBottom: '1px solid var(--color-border)'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
                <div
                  style={{
                    width: '28px',
                    height: '28px',
                    borderRadius: '50%',
                    backgroundColor: allPhaseCompleted ? 'var(--color-success-bg)' : 'var(--color-burgundy-soft)',
                    color: allPhaseCompleted ? 'var(--color-success)' : 'var(--color-burgundy)',
                    border: `1px solid ${allPhaseCompleted ? 'rgba(40,98,71,0.2)' : 'rgba(112,45,61,0.2)'}`,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: 'var(--text-xs)',
                    fontWeight: 700
                  }}
                  aria-hidden="true"
                >
                  {allPhaseCompleted ? <CheckCircle2 size={16} /> : phaseNum}
                </div>
                <h3
                  id={`phase-title-${phaseNum}`}
                  style={{
                    fontSize: 'var(--text-base)',
                    fontFamily: 'var(--font-display)',
                    fontWeight: 600,
                    color: 'var(--color-text)'
                  }}
                >
                  {getPhaseName(phaseNum)}
                </h3>
              </div>

              <span style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)' }}>
                {phaseTasks.filter(t => t.status === 'completed').length} of {phaseTasks.length} done
              </span>
            </div>

            {/* Task list in this phase */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)', paddingLeft: 'var(--space-2)' }}>
              {phaseTasks.map(task => {
                const isCompleted = task.status === 'completed';

                return (
                  <div
                    key={task.id}
                    className="panel panel-interactive"
                    style={{
                      padding: 'var(--space-4) var(--space-5)',
                      backgroundColor: isCompleted ? 'var(--color-surface)' : 'var(--color-surface)',
                      borderLeft: isCompleted
                        ? '3px solid var(--color-success)'
                        : task.status === 'in_progress'
                        ? '3px solid var(--color-warning)'
                        : '3px solid var(--color-border)',
                      display: 'flex',
                      flexDirection: 'column',
                      gap: 'var(--space-3)'
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 'var(--space-3)' }}>
                      <div style={{ display: 'flex', alignItems: 'flex-start', gap: 'var(--space-3)', flex: 1 }}>
                        {interactive && (
                          <button
                            onClick={() => {
                              const nextStatus: TaskStatus =
                                task.status === 'completed'
                                  ? 'not_started'
                                  : task.status === 'not_started'
                                  ? 'in_progress'
                                  : 'completed';
                              onStatusChange(task.id, nextStatus);
                            }}
                            title={`Status: ${task.status}. Click to advance.`}
                            aria-label={`Toggle task status for ${task.title}. Current status: ${task.status}`}
                            style={{
                              marginTop: '2px',
                              color: isCompleted
                                ? 'var(--color-success)'
                                : task.status === 'in_progress'
                                ? 'var(--color-warning)'
                                : 'var(--color-border-strong)',
                              cursor: 'pointer',
                              display: 'flex',
                              padding: '2px',
                              borderRadius: 'var(--radius-sm)'
                            }}
                          >
                            {isCompleted ? (
                              <CheckCircle2 size={20} />
                            ) : task.status === 'in_progress' ? (
                              <Clock size={20} />
                            ) : (
                              <Circle size={20} />
                            )}
                          </button>
                        )}

                        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                          <h4
                            style={{
                              fontSize: 'var(--text-base)',
                              fontWeight: 600,
                              color: 'var(--color-text)',
                              textDecoration: isCompleted ? 'line-through' : 'none',
                              opacity: isCompleted ? 0.8 : 1
                            }}
                          >
                            {task.title}
                          </h4>
                          <p style={{ fontSize: 'var(--text-sm)', color: 'var(--color-text-secondary)', lineHeight: 1.5 }}>
                            {task.description}
                          </p>
                        </div>
                      </div>

                      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
                        <StatusLabel status={task.status} />
                        {onDeleteTask && (
                          <button
                            onClick={() => onDeleteTask(task.id)}
                            aria-label={`Delete task: ${task.title}`}
                            style={{
                              padding: '4px',
                              color: 'var(--color-text-muted)',
                              borderRadius: 'var(--radius-sm)',
                              display: 'flex'
                            }}
                          >
                            <Trash2 size={14} />
                          </button>
                        )}
                      </div>
                    </div>

                    <div
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        flexWrap: 'wrap',
                        gap: 'var(--space-3)',
                        fontSize: 'var(--text-xs)',
                        paddingTop: 'var(--space-2)',
                        borderTop: '1px solid var(--color-surface-muted)'
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)', flexWrap: 'wrap' }}>
                        <span className="badge badge-muted">Skill: {task.skill}</span>
                        <span style={{ color: 'var(--color-text-secondary)' }}>Est. {task.estimatedTime}</span>
                      </div>

                      {task.resourceName && (
                        <a
                          href={task.resourceUrl || '#'}
                          target="_blank"
                          rel="noopener noreferrer"
                          style={{
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '4px',
                            color: 'var(--color-burgundy)',
                            fontWeight: 600,
                            textDecoration: 'none'
                          }}
                        >
                          <span>{task.resourceName}</span>
                          <ExternalLink size={12} aria-hidden="true" />
                        </a>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </section>
        );
      })}
    </div>
  );
};
