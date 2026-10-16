import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, ArrowRight, Check, Sparkles } from 'lucide-react';
import { PageContainer } from '../components/ui/Typography';
import { PrimaryButton, SecondaryButton } from '../components/ui/Buttons';
import { TextInput, SelectInput } from '../components/ui/Inputs';
import { ProgressIndicator } from '../components/ui/FeedbackStates';
import { useApp } from '../context/AppContext';

export const OnboardingPage: React.FC = () => {
  const navigate = useNavigate();
  const { profile, updateProfile, careerPaths } = useApp();

  const [step, setStep] = useState(1);
  const totalSteps = 5;

  // Local form state
  const [name, setName] = useState(profile.name || '');
  const [studyStatus, setStudyStatus] = useState(profile.studyStatus || '');
  const [selectedInterests, setSelectedInterests] = useState<string[]>(profile.interests || []);
  const [primaryGoal, setPrimaryGoal] = useState(profile.primaryGoal || '');
  const [targetCareerId, setTargetCareerId] = useState(profile.targetCareerId || 'ai-product-engineer');
  const [selectedSkills, setSelectedSkills] = useState<string[]>(profile.currentSkills || []);
  const [weeklyHours, setWeeklyHours] = useState(profile.weeklyHours || 8);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const interestOptions = [
    'Artificial Intelligence & LLMs',
    'Human-Computer Interaction (HCI)',
    'Frontend & Web Systems',
    'Data Analytics & SQL',
    'Cloud Architecture & DevOps',
    'Design Systems & Typography',
    'User Research & Usability'
  ];

  const skillOptions = [
    'Python',
    'JavaScript / TypeScript',
    'React',
    'SQL',
    'HTML & CSS',
    'Figma & UI Design',
    'Git & Version Control',
    'Linux / Command Line'
  ];

  const toggleInterest = (interest: string) => {
    setSelectedInterests(prev =>
      prev.includes(interest) ? prev.filter(i => i !== interest) : [...prev, interest]
    );
  };

  const toggleSkill = (skill: string) => {
    setSelectedSkills(prev =>
      prev.includes(skill) ? prev.filter(s => s !== skill) : [...prev, skill]
    );
  };

  const handleNext = () => {
    // Validate current step
    const newErrors: Record<string, string> = {};

    if (step === 1) {
      if (!name.trim()) newErrors.name = 'Please provide your name so we know how to address you.';
      if (!studyStatus.trim()) newErrors.studyStatus = 'Please share your current study or work focus.';
    }

    if (step === 2) {
      if (selectedInterests.length === 0) {
        newErrors.interests = 'Please select at least one area of interest.';
      }
    }

    if (step === 3) {
      if (!primaryGoal.trim()) {
        newErrors.primaryGoal = 'Please summarize what you are aiming to achieve.';
      }
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    setErrors({});

    if (step < totalSteps) {
      setStep(prev => prev + 1);
    } else {
      // Save and complete onboarding
      updateProfile({
        name,
        studyStatus,
        interests: selectedInterests,
        primaryGoal,
        targetCareerId,
        currentSkills: selectedSkills,
        weeklyHours,
        onboardingCompleted: true
      });
      navigate('/dashboard');
    }
  };

  const handleBack = () => {
    if (step > 1) {
      setStep(prev => prev - 1);
    } else {
      navigate('/');
    }
  };

  const handleSkip = () => {
    updateProfile({
      onboardingCompleted: true
    });
    navigate('/dashboard');
  };

  return (
    <PageContainer style={{ maxWidth: '680px', minHeight: '80vh', display: 'flex', flexDirection: 'column' }}>
      {/* Step Header */}
      <div style={{ marginBottom: 'var(--space-6)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-3)' }}>
          <span style={{ fontSize: 'var(--text-xs)', fontWeight: 700, letterSpacing: '0.08em', textTransform: 'uppercase', color: 'var(--color-burgundy)' }}>
            Step {step} of {totalSteps}
          </span>
          <button
            onClick={handleSkip}
            style={{
              fontSize: 'var(--text-xs)',
              color: 'var(--color-text-secondary)',
              textDecoration: 'underline',
              cursor: 'pointer'
            }}
          >
            Skip for now
          </button>
        </div>

        <ProgressIndicator value={(step / totalSteps) * 100} showPercentage={false} size="sm" />
      </div>

      {/* Main Step Content Card */}
      <div
        className="panel"
        style={{
          padding: 'var(--space-8)',
          display: 'flex',
          flexDirection: 'column',
          gap: 'var(--space-6)',
          backgroundColor: 'var(--color-surface)',
          boxShadow: 'var(--shadow-subtle)'
        }}
      >
        {/* Step 1: Study & Identity */}
        {step === 1 && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
            <div>
              <span className="badge badge-burgundy" style={{ marginBottom: 'var(--space-2)' }}>
                Let's start with you
              </span>
              <h2 style={{ fontSize: 'var(--heading-md)', fontFamily: 'var(--font-display)', color: 'var(--color-text)' }}>
                What are you studying or working on?
              </h2>
              <p style={{ fontSize: 'var(--text-sm)', color: 'var(--color-text-secondary)', marginTop: '4px' }}>
                No need to have everything figured out. Your answers help us calibrate technical depth and examples.
              </p>
            </div>

            <TextInput
              label="Your Name or Preferred Handle"
              value={name}
              onChange={e => setName(e.target.value)}
              placeholder="e.g. Alex Morgan"
              error={errors.name}
              required
            />

            <TextInput
              label="Current Study Status or Role"
              value={studyStatus}
              onChange={e => setStudyStatus(e.target.value)}
              placeholder="e.g. 3rd year Computer Science student / Self-taught developer"
              hint="This tells us how to pace your fundamentals and project scopes."
              error={errors.studyStatus}
              required
            />
          </div>
        )}

        {/* Step 2: Interests */}
        {step === 2 && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
            <div>
              <span className="badge badge-burgundy" style={{ marginBottom: 'var(--space-2)' }}>
                Areas of curiosity
              </span>
              <h2 style={{ fontSize: 'var(--heading-md)', fontFamily: 'var(--font-display)', color: 'var(--color-text)' }}>
                Which areas interest you most right now?
              </h2>
              <p style={{ fontSize: 'var(--text-sm)', color: 'var(--color-text-secondary)', marginTop: '4px' }}>
                Select as many as you like. You can always change this later.
              </p>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))', gap: 'var(--space-2)' }}>
              {interestOptions.map(interest => {
                const selected = selectedInterests.includes(interest);
                return (
                  <button
                    key={interest}
                    type="button"
                    onClick={() => toggleInterest(interest)}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      padding: 'var(--space-3) var(--space-4)',
                      borderRadius: 'var(--radius-sm)',
                      border: `1px solid ${selected ? 'var(--color-burgundy)' : 'var(--color-border)'}`,
                      backgroundColor: selected ? 'var(--color-burgundy-soft)' : 'var(--color-surface)',
                      color: selected ? 'var(--color-burgundy)' : 'var(--color-text)',
                      fontWeight: selected ? 600 : 500,
                      fontSize: 'var(--text-sm)',
                      cursor: 'pointer',
                      textAlign: 'left',
                      transition: 'border-color var(--transition-fast), background-color var(--transition-fast)'
                    }}
                  >
                    <span>{interest}</span>
                    {selected && <Check size={16} />}
                  </button>
                );
              })}
            </div>

            {errors.interests && (
              <span style={{ fontSize: 'var(--text-xs)', color: 'var(--color-error)' }} role="alert">
                {errors.interests}
              </span>
            )}
          </div>
        )}

        {/* Step 3: Goals & Target Career */}
        {step === 3 && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
            <div>
              <span className="badge badge-burgundy" style={{ marginBottom: 'var(--space-2)' }}>
                Your Ambition
              </span>
              <h2 style={{ fontSize: 'var(--heading-md)', fontFamily: 'var(--font-display)', color: 'var(--color-text)' }}>
                What are you trying to achieve?
              </h2>
              <p style={{ fontSize: 'var(--text-sm)', color: 'var(--color-text-secondary)', marginTop: '4px' }}>
                We'll frame your roadmap toward a tangible, near-term milestone.
              </p>
            </div>

            <TextInput
              label="Primary Career Goal (Next 6 to 12 months)"
              value={primaryGoal}
              onChange={e => setPrimaryGoal(e.target.value)}
              placeholder="e.g. Prepare for summer internships / Build a standout portfolio project"
              error={errors.primaryGoal}
              required
            />

            <SelectInput
              label="Preferred Starting Career Track"
              value={targetCareerId}
              onChange={e => setTargetCareerId(e.target.value)}
              options={careerPaths.map(c => ({ value: c.id, label: `${c.title} (${c.category})` }))}
              hint="You can explore other paths anytime in the Explore section."
            />
          </div>
        )}

        {/* Step 4: Existing Skills */}
        {step === 4 && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
            <div>
              <span className="badge badge-burgundy" style={{ marginBottom: 'var(--space-2)' }}>
                Starting Baseline
              </span>
              <h2 style={{ fontSize: 'var(--heading-md)', fontFamily: 'var(--font-display)', color: 'var(--color-text)' }}>
                What skills do you already feel comfortable with?
              </h2>
              <p style={{ fontSize: 'var(--text-sm)', color: 'var(--color-text-secondary)', marginTop: '4px' }}>
                We won't make you repeat things you already know well.
              </p>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))', gap: 'var(--space-2)' }}>
              {skillOptions.map(skill => {
                const selected = selectedSkills.includes(skill);
                return (
                  <button
                    key={skill}
                    type="button"
                    onClick={() => toggleSkill(skill)}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      padding: 'var(--space-3) var(--space-4)',
                      borderRadius: 'var(--radius-sm)',
                      border: `1px solid ${selected ? 'var(--color-burgundy)' : 'var(--color-border)'}`,
                      backgroundColor: selected ? 'var(--color-burgundy-soft)' : 'var(--color-surface)',
                      color: selected ? 'var(--color-burgundy)' : 'var(--color-text)',
                      fontWeight: selected ? 600 : 500,
                      fontSize: 'var(--text-sm)',
                      cursor: 'pointer',
                      textAlign: 'left'
                    }}
                  >
                    <span>{skill}</span>
                    {selected && <Check size={16} />}
                  </button>
                );
              })}
            </div>
          </div>
        )}

        {/* Step 5: Weekly Commitment */}
        {step === 5 && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
            <div>
              <span className="badge badge-burgundy" style={{ marginBottom: 'var(--space-2)' }}>
                Realistic Pacing
              </span>
              <h2 style={{ fontSize: 'var(--heading-md)', fontFamily: 'var(--font-display)', color: 'var(--color-text)' }}>
                How much time can you spend each week?
              </h2>
              <p style={{ fontSize: 'var(--text-sm)', color: 'var(--color-text-secondary)', marginTop: '4px' }}>
                Honest consistency beats intense burnout. Even 4–8 hours a week compounds quickly.
              </p>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)', marginTop: 'var(--space-2)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: 'var(--text-base)', fontWeight: 600 }}>Weekly commitment</span>
                <span className="tabular-nums" style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--color-burgundy)' }}>
                  {weeklyHours} hours / week
                </span>
              </div>

              <input
                type="range"
                min={2}
                max={25}
                step={1}
                value={weeklyHours}
                onChange={e => setWeeklyHours(Number(e.target.value))}
                aria-label="Weekly hours slider"
                style={{
                  accentColor: 'var(--color-burgundy)',
                  width: '100%',
                  cursor: 'pointer'
                }}
              />

              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)' }}>
                <span>Light (2–4 hrs)</span>
                <span>Steady (6–10 hrs)</span>
                <span>Dedicated (15+ hrs)</span>
              </div>

              <div
                style={{
                  padding: 'var(--space-4)',
                  backgroundColor: 'var(--color-surface-muted)',
                  borderRadius: 'var(--radius-sm)',
                  borderLeft: '3px solid var(--color-burgundy)',
                  fontSize: 'var(--text-xs)',
                  color: 'var(--color-text-secondary)'
                }}
              >
                With <strong>{weeklyHours} hours per week</strong>, you can comfortably master your core foundations and complete your first portfolio milestone in approximately 8 to 12 weeks.
              </div>
            </div>
          </div>
        )}

        {/* Flow Controls */}
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            paddingTop: 'var(--space-4)',
            borderTop: '1px solid var(--color-border)',
            marginTop: 'var(--space-2)'
          }}
        >
          <SecondaryButton
            size="md"
            onClick={handleBack}
            icon={<ArrowLeft size={16} />}
          >
            {step === 1 ? 'Cancel' : 'Back'}
          </SecondaryButton>

          <PrimaryButton
            size="md"
            onClick={handleNext}
            icon={step === totalSteps ? <Sparkles size={16} /> : <ArrowRight size={16} />}
            iconPosition="right"
          >
            {step === totalSteps ? 'Complete & view dashboard' : 'Continue'}
          </PrimaryButton>
        </div>
      </div>
    </PageContainer>
  );
};
