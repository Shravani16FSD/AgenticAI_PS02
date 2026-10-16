import React, { useState } from 'react';
import { Plus, BookOpen, X } from 'lucide-react';
import { PageContainer, PageHeading } from '../components/ui/Typography';
import { PrimaryButton, SecondaryButton } from '../components/ui/Buttons';
import { TextInput, SelectInput } from '../components/ui/Inputs';
import { ProgressIndicator } from '../components/ui/FeedbackStates';
import { RoadmapTimeline } from '../components/roadmap/RoadmapTimeline';
import { EmptyState } from '../components/ui/FeedbackStates';
import { useApp } from '../context/AppContext';
import type { TaskStatus } from '../types';

export const RoadmapPage: React.FC = () => {
  const {
    roadmapTasks,
    updateTaskStatus,
    addTask,
    deleteTask,
    activeCareer,
    completedTasksCount,
    totalTasksCount,
    overallProgressPercent
  } = useApp();

  const [statusFilter, setStatusFilter] = useState<'all' | TaskStatus>('all');
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);

  // New task form state
  const [newTitle, setNewTitle] = useState('');
  const [newDescription, setNewDescription] = useState('');
  const [newSkill, setNewSkill] = useState('');
  const [newPhaseId, setNewPhaseId] = useState('2');
  const [newEstimatedTime, setNewEstimatedTime] = useState('2 hours');
  const [newResourceName, setNewResourceName] = useState('');
  const [newResourceUrl, setNewResourceUrl] = useState('');
  const [formError, setFormError] = useState('');

  const phaseNames: Record<number, string> = {
    1: 'Phase 1: Foundations',
    2: 'Phase 2: Core Skills',
    3: 'Phase 3: Applied Projects',
    4: 'Phase 4: Portfolio & Practical Experience',
    5: 'Phase 5: Internship & Job Preparation'
  };

  const handleCreateTask = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle.trim()) {
      setFormError('Please provide a milestone title.');
      return;
    }

    const pId = Number(newPhaseId);
    addTask({
      phaseId: pId,
      phaseName: phaseNames[pId] || `Phase ${pId}`,
      title: newTitle.trim(),
      description: newDescription.trim() || 'Custom milestone added to your roadmap.',
      skill: newSkill.trim() || 'General Engineering',
      estimatedTime: newEstimatedTime.trim() || '1 hour',
      status: 'not_started',
      resourceName: newResourceName.trim() || undefined,
      resourceUrl: newResourceUrl.trim() || undefined
    });

    // Reset and close
    setNewTitle('');
    setNewDescription('');
    setNewSkill('');
    setNewResourceName('');
    setNewResourceUrl('');
    setFormError('');
    setIsAddModalOpen(false);
  };

  const filteredTasks = roadmapTasks.filter(task => {
    if (statusFilter === 'all') return true;
    return task.status === statusFilter;
  });

  return (
    <PageContainer>
      <PageHeading
        eyebrow="LEARNING ROADMAP"
        title="Your personalized sequence."
        description={`A structured path tailored for ${activeCareer?.title || 'your chosen career'}. Take one achievable step at a time.`}
        actions={
          <PrimaryButton
            size="sm"
            onClick={() => setIsAddModalOpen(true)}
            icon={<Plus size={14} />}
          >
            Add milestone
          </PrimaryButton>
        }
      />

      {/* Progress & Filters Strip */}
      <div
        className="panel"
        style={{
          display: 'flex',
          flexDirection: 'column',
          gap: 'var(--space-4)',
          marginBottom: 'var(--space-8)',
          backgroundColor: 'var(--color-surface)'
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 'var(--space-3)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
            <BookOpen size={18} style={{ color: 'var(--color-burgundy)' }} aria-hidden="true" />
            <span style={{ fontSize: 'var(--text-sm)', fontWeight: 600 }}>
              Milestones: {completedTasksCount} of {totalTasksCount} completed
            </span>
          </div>

          {/* Filter Pills */}
          <div style={{ display: 'flex', gap: 'var(--space-2)', flexWrap: 'wrap' }}>
            {(['all', 'not_started', 'in_progress', 'completed'] as const).map(statusKey => {
              const label = {
                all: 'All Milestones',
                not_started: 'Not Started',
                in_progress: 'In Progress',
                completed: 'Completed'
              }[statusKey];

              const isSelected = statusFilter === statusKey;

              return (
                <button
                  key={statusKey}
                  onClick={() => setStatusFilter(statusKey)}
                  style={{
                    padding: '0.375rem 0.75rem',
                    borderRadius: 'var(--radius-sm)',
                    fontSize: 'var(--text-xs)',
                    fontWeight: isSelected ? 700 : 500,
                    backgroundColor: isSelected ? 'var(--color-burgundy-soft)' : 'transparent',
                    color: isSelected ? 'var(--color-burgundy)' : 'var(--color-text-secondary)',
                    border: `1px solid ${isSelected ? 'var(--color-burgundy)' : 'var(--color-border)'}`,
                    cursor: 'pointer'
                  }}
                >
                  {label}
                </button>
              );
            })}
          </div>
        </div>

        <ProgressIndicator value={overallProgressPercent} size="sm" showPercentage={true} />
      </div>

      {/* Timeline view */}
      {filteredTasks.length === 0 ? (
        <EmptyState
          title="No tasks match the selected filter"
          description="Try switching the filter to 'All Milestones' to see your complete curriculum."
          actionLabel="Show all milestones"
          onAction={() => setStatusFilter('all')}
        />
      ) : (
        <RoadmapTimeline
          tasks={filteredTasks}
          onStatusChange={updateTaskStatus}
          onDeleteTask={deleteTask}
          interactive={true}
        />
      )}

      {/* Add Custom Milestone Modal */}
      {isAddModalOpen && (
        <div
          role="presentation"
          style={{
            position: 'fixed',
            inset: 0,
            backgroundColor: 'rgba(41, 35, 33, 0.45)',
            backdropFilter: 'blur(2px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000,
            padding: 'var(--space-4)'
          }}
          onClick={() => setIsAddModalOpen(false)}
        >
          <div
            role="dialog"
            aria-modal="true"
            aria-labelledby="add-task-title"
            style={{
              backgroundColor: 'var(--color-surface)',
              border: '1px solid var(--color-border-strong)',
              borderRadius: 'var(--radius-panel)',
              maxWidth: '540px',
              width: '100%',
              padding: 'var(--space-6)',
              boxShadow: 'var(--shadow-modal)',
              display: 'flex',
              flexDirection: 'column',
              gap: 'var(--space-4)'
            }}
            onClick={e => e.stopPropagation()}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h3 id="add-task-title" style={{ fontSize: 'var(--text-lg)', fontFamily: 'var(--font-display)', fontWeight: 600 }}>
                Add Custom Milestone
              </h3>
              <button onClick={() => setIsAddModalOpen(false)} aria-label="Close modal">
                <X size={18} />
              </button>
            </div>

            <form onSubmit={handleCreateTask} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
              <TextInput
                label="Milestone Title"
                placeholder="e.g. Build interactive feedback modal with keyboard traps"
                value={newTitle}
                onChange={e => setNewTitle(e.target.value)}
                error={formError}
                required
              />

              <TextInput
                label="Description & Learning Objective"
                placeholder="Why does this matter and what are you practicing?"
                value={newDescription}
                onChange={e => setNewDescription(e.target.value)}
              />

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-3)' }}>
                <SelectInput
                  label="Phase"
                  value={newPhaseId}
                  onChange={e => setNewPhaseId(e.target.value)}
                  options={[
                    { value: '1', label: '1. Foundations' },
                    { value: '2', label: '2. Core Skills' },
                    { value: '3', label: '3. Applied Projects' },
                    { value: '4', label: '4. Portfolio & Systems' },
                    { value: '5', label: '5. Interview Prep' }
                  ]}
                />

                <TextInput
                  label="Estimated Time"
                  placeholder="e.g. 45 mins / 3 hours"
                  value={newEstimatedTime}
                  onChange={e => setNewEstimatedTime(e.target.value)}
                />
              </div>

              <TextInput
                label="Associated Skill"
                placeholder="e.g. WCAG Accessibility / React Hooks"
                value={newSkill}
                onChange={e => setNewSkill(e.target.value)}
              />

              <TextInput
                label="Verified Resource Name (Optional)"
                placeholder="e.g. MDN Web Docs: Dialog Element"
                value={newResourceName}
                onChange={e => setNewResourceName(e.target.value)}
              />

              <TextInput
                label="Resource URL (Optional)"
                placeholder="https://..."
                value={newResourceUrl}
                onChange={e => setNewResourceUrl(e.target.value)}
              />

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 'var(--space-3)', marginTop: 'var(--space-3)' }}>
                <SecondaryButton type="button" onClick={() => setIsAddModalOpen(false)} size="sm">
                  Cancel
                </SecondaryButton>
                <PrimaryButton type="submit" size="sm">
                  Save to roadmap
                </PrimaryButton>
              </div>
            </form>
          </div>
        </div>
      )}
    </PageContainer>
  );
};
