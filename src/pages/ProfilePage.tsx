import React, { useState } from 'react';
import { Download, RotateCcw, Bookmark, Check, Trash2 } from 'lucide-react';
import { PageContainer, PageHeading } from '../components/ui/Typography';
import { PrimaryButton, SecondaryButton } from '../components/ui/Buttons';
import { TextInput, SelectInput } from '../components/ui/Inputs';
import { ConfirmationDialog } from '../components/ui/Overlays';
import { useApp } from '../context/AppContext';

export const ProfilePage: React.FC = () => {
  const {
    profile,
    updateProfile,
    resetAllData,
    careerPaths,
    savedCareerIds,
    toggleSaveCareer,
    roadmapTasks,
    skills,
    overallProgressPercent
  } = useApp();

  const [name, setName] = useState(profile.name || '');
  const [studyStatus, setStudyStatus] = useState(profile.studyStatus || '');
  const [primaryGoal, setPrimaryGoal] = useState(profile.primaryGoal || '');
  const [targetCareerId, setTargetCareerId] = useState(profile.targetCareerId || 'ai-product-engineer');
  const [weeklyHours, setWeeklyHours] = useState(profile.weeklyHours || 8);
  const [isResetDialogOpen, setIsResetDialogOpen] = useState(false);

  const handleSaveProfile = (e: React.FormEvent) => {
    e.preventDefault();
    updateProfile({
      name: name.trim(),
      studyStatus: studyStatus.trim(),
      primaryGoal: primaryGoal.trim(),
      targetCareerId,
      weeklyHours
    });
  };

  const handleExportPlan = () => {
    const activeCareer = careerPaths.find(c => c.id === profile.targetCareerId);
    const planText = `# ${profile.name || 'My'} Career Plan — Chapter Mentor
Date: ${new Date().toLocaleDateString()}
Status: ${profile.studyStatus}
Target Role: ${activeCareer?.title || 'Technology'}
Weekly Commitment: ${profile.weeklyHours} hours/week
Overall Roadmap Progress: ${overallProgressPercent}%

## Primary Goal
${profile.primaryGoal}

## Interests
${profile.interests.map(i => `- ${i}`).join('\n')}

## Core Roadmap Milestones
${roadmapTasks
  .map(
    t =>
      `[${t.status === 'completed' ? 'x' : ' '}] ${t.title} (${t.phaseName}) - Est. ${t.estimatedTime}${
        t.resourceName ? ` | Resource: ${t.resourceName}` : ''
      }`
  )
  .join('\n')}

## Tracked Skills
${skills.map(s => `- ${s.name}: ${s.hoursSpent}/${s.targetHours} hours logged (${s.status})`).join('\n')}
`;

    const blob = new Blob([planText], { type: 'text/markdown;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `career-plan-${(profile.name || 'user').toLowerCase().replace(/\s+/g, '-')}.md`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const savedCareers = careerPaths.filter(c => savedCareerIds.includes(c.id));

  return (
    <PageContainer style={{ maxWidth: '880px' }}>
      <PageHeading
        eyebrow="ACCOUNT & PREFERENCES"
        title="Your Profile & Plan Settings"
        description="Update your baseline context, export your learning plan, or adjust your weekly commitment."
        actions={
          <SecondaryButton
            size="sm"
            onClick={handleExportPlan}
            icon={<Download size={14} />}
          >
            Export plan (.md)
          </SecondaryButton>
        }
      />

      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-8)' }}>
        {/* Profile Settings Form */}
        <section className="panel" aria-labelledby="profile-settings-title" style={{ backgroundColor: 'var(--color-surface)' }}>
          <h3 id="profile-settings-title" style={{ fontSize: 'var(--text-lg)', fontFamily: 'var(--font-display)', fontWeight: 600, marginBottom: 'var(--space-4)' }}>
            Personal Career Profile
          </h3>

          <form onSubmit={handleSaveProfile} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-4)' }} className="profile-form-grid">
              <TextInput
                label="Full Name or Preferred Name"
                value={name}
                onChange={e => setName(e.target.value)}
                required
              />

              <TextInput
                label="Study Status or Background"
                value={studyStatus}
                onChange={e => setStudyStatus(e.target.value)}
                hint="Used to frame technical advice."
                required
              />
            </div>

            <TextInput
              label="Primary Goal (Next 6–12 months)"
              value={primaryGoal}
              onChange={e => setPrimaryGoal(e.target.value)}
              required
            />

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-4)' }} className="profile-form-grid">
              <SelectInput
                label="Primary Target Career Track"
                value={targetCareerId}
                onChange={e => setTargetCareerId(e.target.value)}
                options={careerPaths.map(c => ({ value: c.id, label: `${c.title} (${c.category})` }))}
              />

              <TextInput
                label="Target Weekly Hours"
                type="number"
                min="2"
                max="30"
                value={weeklyHours}
                onChange={e => setWeeklyHours(Number(e.target.value))}
                hint="Calibrates the pacing of your roadmap."
              />
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', paddingTop: 'var(--space-3)', borderTop: '1px solid var(--color-border)' }}>
              <PrimaryButton type="submit" size="sm" icon={<Check size={14} />}>
                Save preferences
              </PrimaryButton>
            </div>
          </form>
        </section>

        {/* Saved Careers List */}
        <section className="panel" aria-labelledby="saved-careers-title" style={{ backgroundColor: 'var(--color-surface)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', marginBottom: 'var(--space-4)' }}>
            <Bookmark size={18} style={{ color: 'var(--color-burgundy)' }} />
            <h3 id="saved-careers-title" style={{ fontSize: 'var(--text-lg)', fontFamily: 'var(--font-display)', fontWeight: 600 }}>
              Saved Career Paths ({savedCareers.length})
            </h3>
          </div>

          {savedCareers.length === 0 ? (
            <p style={{ fontSize: 'var(--text-sm)', color: 'var(--color-text-secondary)' }}>
              You haven't saved any careers yet. Explore a few paths and keep the ones that interest you.
            </p>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
              {savedCareers.map(c => (
                <div
                  key={c.id}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: 'var(--space-3) var(--space-4)',
                    backgroundColor: 'var(--color-surface-muted)',
                    borderRadius: 'var(--radius-sm)',
                    border: '1px solid var(--color-border)'
                  }}
                >
                  <div style={{ display: 'flex', flexDirection: 'column' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
                      <strong style={{ fontSize: 'var(--text-sm)', color: 'var(--color-text)' }}>
                        {c.title}
                      </strong>
                      <span className="badge badge-burgundy">{c.category}</span>
                    </div>
                    <span style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)', marginTop: '2px' }}>
                      {c.tagline}
                    </span>
                  </div>

                  <button
                    onClick={() => toggleSaveCareer(c.id)}
                    aria-label={`Remove ${c.title} from saved`}
                    title="Remove from saved"
                    style={{
                      color: 'var(--color-text-muted)',
                      padding: '4px',
                      borderRadius: 'var(--radius-sm)',
                      display: 'flex'
                    }}
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              ))}
            </div>
          )}
        </section>

        {/* Data Reset & Storage Management */}
        <section
          className="panel"
          aria-labelledby="danger-title"
          style={{
            backgroundColor: 'var(--color-surface)',
            border: '1px solid rgba(165, 44, 50, 0.25)',
            display: 'flex',
            flexDirection: 'column',
            gap: 'var(--space-3)'
          }}
        >
          <h3 id="danger-title" style={{ fontSize: 'var(--text-base)', fontWeight: 600, color: 'var(--color-error)' }}>
            Reset & Clear Application Data
          </h3>
          <p style={{ fontSize: 'var(--text-sm)', color: 'var(--color-text-secondary)', lineHeight: 1.5 }}>
            Reset your roadmap tasks, tracked skills, chat history, and personal preferences back to original initial defaults.
          </p>

          <div>
            <SecondaryButton
              size="sm"
              onClick={() => setIsResetDialogOpen(true)}
              icon={<RotateCcw size={14} style={{ color: 'var(--color-error)' }} />}
              style={{ color: 'var(--color-error)', borderColor: 'rgba(165, 44, 50, 0.3)' }}
            >
              Reset to initial defaults
            </SecondaryButton>
          </div>
        </section>
      </div>

      <ConfirmationDialog
        isOpen={isResetDialogOpen}
        title="Reset all application data?"
        message="This will clear your customized roadmap tasks, logged skill practice hours, conversation history, and profile back to sample defaults. This action cannot be undone."
        confirmLabel="Reset everything"
        isDestructive={true}
        onConfirm={() => {
          resetAllData();
          setIsResetDialogOpen(false);
          setName('Alex Morgan');
          setStudyStatus('Third-year CS & HCI Student');
          setPrimaryGoal('Secure a Summer 2027 AI Product Engineering Internship');
          setTargetCareerId('ai-product-engineer');
          setWeeklyHours(8);
        }}
        onCancel={() => setIsResetDialogOpen(false)}
      />

      <style>{`
        @media (max-width: 640px) {
          .profile-form-grid {
            grid-template-columns: 1fr !important;
          }
        }
      `}</style>
    </PageContainer>
  );
};
