import React, { useState } from 'react';
import { Plus, Calendar, Check, X } from 'lucide-react';
import { PageContainer, PageHeading } from '../components/ui/Typography';
import { PrimaryButton, SecondaryButton } from '../components/ui/Buttons';
import { TextInput, SelectInput } from '../components/ui/Inputs';
import { ProgressIndicator } from '../components/ui/FeedbackStates';
import { useApp } from '../context/AppContext';
import type { SkillProficiency, SkillProgress } from '../types';

export const SkillsPage: React.FC = () => {
  const { skills, updateSkill, addSkill, profile, roadmapTasks } = useApp();

  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [practiceModalSkill, setPracticeModalSkill] = useState<SkillProgress | null>(null);
  const [practiceHours, setPracticeHours] = useState('1');

  // New Skill form state
  const [newSkillName, setNewSkillName] = useState('');
  const [newCategory, setNewCategory] = useState('Frontend');
  const [newTargetHours, setNewTargetHours] = useState('30');
  const [formError, setFormError] = useState('');

  // Weekly consistency data (grounded in profile weekly hours)
  const weeklyDays = [
    { day: 'Mon', hours: 1.5, completed: true },
    { day: 'Tue', hours: 2.0, completed: true },
    { day: 'Wed', hours: 0, completed: false },
    { day: 'Thu', hours: 2.5, completed: true },
    { day: 'Fri', hours: 1.0, completed: true },
    { day: 'Sat', hours: 0, completed: false },
    { day: 'Sun', hours: 0, completed: false }
  ];

  const totalHoursPracticed = skills.reduce((sum, s) => sum + s.hoursSpent, 0);

  const handleCreateSkill = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newSkillName.trim()) {
      setFormError('Skill name is required.');
      return;
    }

    addSkill({
      name: newSkillName.trim(),
      category: newCategory,
      status: 'learning',
      hoursSpent: 0,
      targetHours: Number(newTargetHours) || 30,
      lastPracticed: 'Just added'
    });

    setNewSkillName('');
    setFormError('');
    setIsAddModalOpen(false);
  };

  const handleLogPractice = (e: React.FormEvent) => {
    e.preventDefault();
    if (!practiceModalSkill) return;

    const added = Number(practiceHours) || 1;
    const newHours = practiceModalSkill.hoursSpent + added;
    const newStatus: SkillProficiency =
      newHours >= practiceModalSkill.targetHours
        ? 'proficient'
        : newHours >= practiceModalSkill.targetHours / 2
        ? 'practicing'
        : 'learning';

    updateSkill(practiceModalSkill.id, {
      hoursSpent: newHours,
      status: newStatus,
      lastPracticed: 'Today'
    });

    setPracticeModalSkill(null);
    setPracticeHours('1');
  };

  return (
    <PageContainer>
      <PageHeading
        eyebrow="SKILLS & PROGRESS"
        title="Quiet, transparent tracking."
        description="Every number comes from your actual practice. Small, consistent investments compound into deep competence."
        actions={
          <PrimaryButton
            size="sm"
            onClick={() => setIsAddModalOpen(true)}
            icon={<Plus size={14} />}
          >
            Track new skill
          </PrimaryButton>
        }
      />

      {/* Top Level Metrics Cards */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
          gap: 'var(--space-4)',
          marginBottom: 'var(--space-8)'
        }}
      >
        <div className="panel" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-1)' }}>
          <span style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            Total Practice Logged
          </span>
          <span className="tabular-nums" style={{ fontSize: '1.75rem', fontFamily: 'var(--font-display)', fontWeight: 700, color: 'var(--color-burgundy)' }}>
            {totalHoursPracticed} hrs
          </span>
          <span style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)' }}>
            Across {skills.length} tracked disciplines
          </span>
        </div>

        <div className="panel" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-1)' }}>
          <span style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            Weekly Cadence
          </span>
          <span className="tabular-nums" style={{ fontSize: '1.75rem', fontFamily: 'var(--font-display)', fontWeight: 700, color: 'var(--color-text)' }}>
            7.0 / {profile.weeklyHours || 8} hrs
          </span>
          <span style={{ fontSize: 'var(--text-xs)', color: 'var(--color-success)', fontWeight: 600 }}>
            On track this week
          </span>
        </div>

        <div className="panel" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-1)' }}>
          <span style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            Proficient Skills
          </span>
          <span className="tabular-nums" style={{ fontSize: '1.75rem', fontFamily: 'var(--font-display)', fontWeight: 700, color: 'var(--color-text)' }}>
            {skills.filter(s => s.status === 'proficient').length} of {skills.length}
          </span>
          <span style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)' }}>
            {skills.filter(s => s.status === 'practicing').length} actively practicing
          </span>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1.8fr) minmax(0, 1.2fr)', gap: 'var(--space-8)' }} className="skills-grid">
        {/* Skills List */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
          <h3 style={{ fontSize: 'var(--text-base)', fontFamily: 'var(--font-display)', fontWeight: 600 }}>
            Skills Under Active Development
          </h3>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
            {skills.map(skill => {
              const percent = Math.min(100, Math.round((skill.hoursSpent / skill.targetHours) * 100));
              const statusBadge = {
                learning: { label: 'Learning foundations', color: 'var(--color-warning)', bg: 'var(--color-warning-bg)' },
                practicing: { label: 'Practicing & building', color: 'var(--color-burgundy)', bg: 'var(--color-burgundy-soft)' },
                proficient: { label: 'Comfortable / Proficient', color: 'var(--color-success)', bg: 'var(--color-success-bg)' }
              }[skill.status];

              return (
                <div
                  key={skill.id}
                  className="panel panel-interactive"
                  style={{
                    padding: 'var(--space-4) var(--space-5)',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: 'var(--space-3)',
                    backgroundColor: 'var(--color-surface)'
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 'var(--space-2)' }}>
                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
                        <h4 style={{ fontSize: 'var(--text-base)', fontWeight: 600, color: 'var(--color-text)' }}>
                          {skill.name}
                        </h4>
                        <span className="badge badge-muted">{skill.category}</span>
                      </div>
                      <span style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)', marginTop: '2px', display: 'block' }}>
                        Last practiced: {skill.lastPracticed}
                      </span>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
                      <span
                        style={{
                          fontSize: 'var(--text-xs)',
                          fontWeight: 600,
                          padding: '2px 8px',
                          borderRadius: 'var(--radius-sm)',
                          color: statusBadge.color,
                          backgroundColor: statusBadge.bg,
                          border: `1px solid ${statusBadge.color}25`
                        }}
                      >
                        {statusBadge.label}
                      </span>

                      <SecondaryButton
                        size="sm"
                        onClick={() => setPracticeModalSkill(skill)}
                        style={{ fontSize: 'var(--text-xs)', padding: '4px 8px' }}
                      >
                        Log practice
                      </SecondaryButton>
                    </div>
                  </div>

                  <ProgressIndicator
                    value={percent}
                    label={`${skill.hoursSpent} of ${skill.targetHours} target hours logged`}
                    size="sm"
                  />
                </div>
              );
            })}
          </div>
        </div>

        {/* Weekly Consistency & Reflection */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
          <section className="panel" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
              <Calendar size={18} style={{ color: 'var(--color-burgundy)' }} />
              <h3 style={{ fontSize: 'var(--text-base)', fontFamily: 'var(--font-display)', fontWeight: 600 }}>
                Weekly Consistency Tracker
              </h3>
            </div>

            <p style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)', lineHeight: 1.5 }}>
              4 to 5 deliberate sessions each week produce superior retention compared to infrequent cramming sessions.
            </p>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: 'var(--space-2)', textAlign: 'center' }}>
              {weeklyDays.map(d => (
                <div
                  key={d.day}
                  style={{
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    gap: '4px',
                    padding: 'var(--space-2) 0',
                    backgroundColor: d.completed ? 'var(--color-success-bg)' : 'var(--color-surface-muted)',
                    borderRadius: 'var(--radius-sm)',
                    border: `1px solid ${d.completed ? 'rgba(40,98,71,0.25)' : 'var(--color-border)'}`
                  }}
                >
                  <span style={{ fontSize: 'var(--text-xs)', fontWeight: 600, color: 'var(--color-text-muted)' }}>
                    {d.day}
                  </span>
                  <span className="tabular-nums" style={{ fontSize: 'var(--text-xs)', fontWeight: 700, color: d.completed ? 'var(--color-success)' : 'var(--color-text-secondary)' }}>
                    {d.hours > 0 ? `${d.hours}h` : '—'}
                  </span>
                </div>
              ))}
            </div>

            <div
              style={{
                padding: 'var(--space-3)',
                backgroundColor: 'var(--color-surface-muted)',
                borderRadius: 'var(--radius-sm)',
                fontSize: 'var(--text-xs)',
                color: 'var(--color-text-secondary)'
              }}
            >
              <strong>Weekly insight:</strong> You completed your Thursday session focusing on structured validation. Keep up the rhythm!
            </div>
          </section>

          <section className="panel" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
            <h3 style={{ fontSize: 'var(--text-base)', fontFamily: 'var(--font-display)', fontWeight: 600 }}>
              Recent Milestones Completed
            </h3>

            {roadmapTasks.filter(t => t.status === 'completed').length === 0 ? (
              <p style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)' }}>
                No milestones completed yet. Check off your next step on the dashboard!
              </p>
            ) : (
              roadmapTasks.filter(t => t.status === 'completed').slice(0, 3).map(task => (
                <div
                  key={task.id}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 'var(--space-2)',
                    fontSize: 'var(--text-xs)',
                    color: 'var(--color-text)'
                  }}
                >
                  <Check size={14} style={{ color: 'var(--color-success)', flexShrink: 0 }} />
                  <span>{task.title}</span>
                </div>
              ))
            )}
          </section>
        </div>
      </div>

      {/* Log Practice Hours Modal */}
      {practiceModalSkill && (
        <div
          role="presentation"
          style={{
            position: 'fixed',
            inset: 0,
            backgroundColor: 'rgba(41, 35, 33, 0.45)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000,
            padding: 'var(--space-4)'
          }}
          onClick={() => setPracticeModalSkill(null)}
        >
          <div
            role="dialog"
            aria-modal="true"
            aria-labelledby="practice-modal-title"
            style={{
              backgroundColor: 'var(--color-surface)',
              border: '1px solid var(--color-border-strong)',
              borderRadius: 'var(--radius-panel)',
              maxWidth: '440px',
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
              <h3 id="practice-modal-title" style={{ fontSize: 'var(--text-lg)', fontFamily: 'var(--font-display)', fontWeight: 600 }}>
                Log Practice: {practiceModalSkill.name}
              </h3>
              <button onClick={() => setPracticeModalSkill(null)} aria-label="Close modal">
                <X size={18} />
              </button>
            </div>

            <form onSubmit={handleLogPractice} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
              <TextInput
                label="Hours spent in this session"
                type="number"
                min="0.25"
                max="12"
                step="0.25"
                value={practiceHours}
                onChange={e => setPracticeHours(e.target.value)}
                hint="e.g. 1.5 hours of code exercises or reading documentation."
                required
              />

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 'var(--space-3)', marginTop: 'var(--space-3)' }}>
                <SecondaryButton type="button" onClick={() => setPracticeModalSkill(null)} size="sm">
                  Cancel
                </SecondaryButton>
                <PrimaryButton type="submit" size="sm">
                  Save practice time
                </PrimaryButton>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Add New Skill Modal */}
      {isAddModalOpen && (
        <div
          role="presentation"
          style={{
            position: 'fixed',
            inset: 0,
            backgroundColor: 'rgba(41, 35, 33, 0.45)',
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
            aria-labelledby="add-skill-title"
            style={{
              backgroundColor: 'var(--color-surface)',
              border: '1px solid var(--color-border-strong)',
              borderRadius: 'var(--radius-panel)',
              maxWidth: '480px',
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
              <h3 id="add-skill-title" style={{ fontSize: 'var(--text-lg)', fontFamily: 'var(--font-display)', fontWeight: 600 }}>
                Track a New Skill
              </h3>
              <button onClick={() => setIsAddModalOpen(false)} aria-label="Close modal">
                <X size={18} />
              </button>
            </div>

            <form onSubmit={handleCreateSkill} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
              <TextInput
                label="Skill Name"
                placeholder="e.g. Docker & Containers / Vector Embeddings"
                value={newSkillName}
                onChange={e => setNewSkillName(e.target.value)}
                error={formError}
                required
              />

              <SelectInput
                label="Category"
                value={newCategory}
                onChange={e => setNewCategory(e.target.value)}
                options={[
                  { value: 'Frontend', label: 'Frontend & UI' },
                  { value: 'Backend', label: 'Backend & APIs' },
                  { value: 'AI Systems', label: 'AI & Data Systems' },
                  { value: 'Design & UX', label: 'Design & Accessibility' },
                  { value: 'Platform & DevOps', label: 'Platform & DevOps' }
                ]}
              />

              <TextInput
                label="Target Practice Hours for Baseline Fluency"
                type="number"
                min="5"
                max="200"
                value={newTargetHours}
                onChange={e => setNewTargetHours(e.target.value)}
                hint="Typically 25 to 50 hours delivers functional working independence."
              />

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 'var(--space-3)', marginTop: 'var(--space-3)' }}>
                <SecondaryButton type="button" onClick={() => setIsAddModalOpen(false)} size="sm">
                  Cancel
                </SecondaryButton>
                <PrimaryButton type="submit" size="sm">
                  Start tracking
                </PrimaryButton>
              </div>
            </form>
          </div>
        </div>
      )}

      <style>{`
        @media (max-width: 860px) {
          .skills-grid {
            grid-template-columns: 1fr !important;
          }
        }
      `}</style>
    </PageContainer>
  );
};
