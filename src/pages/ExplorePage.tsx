import React, { useState, useMemo } from 'react';
import { Columns, X } from 'lucide-react';
import { PageContainer, PageHeading } from '../components/ui/Typography';
import { TextInput } from '../components/ui/Inputs';
import { PrimaryButton, SecondaryButton } from '../components/ui/Buttons';
import { CareerSummary } from '../components/career/CareerSummary';
import { EmptyState } from '../components/ui/FeedbackStates';
import { useApp } from '../context/AppContext';
import type { CareerPath } from '../types';

export const ExplorePage: React.FC = () => {
  const { careerPaths, savedCareerIds, toggleSaveCareer, updateProfile, profile } = useApp();

  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('All');
  const [selectedCareerForModal, setSelectedCareerForModal] = useState<CareerPath | null>(null);
  const [compareList, setCompareList] = useState<string[]>([]);
  const [isCompareModalOpen, setIsCompareModalOpen] = useState(false);

  const categories = ['All', 'Engineering', 'Design & UX', 'Data & AI'];

  // Filtered careers
  const filteredCareers = useMemo(() => {
    return careerPaths.filter(career => {
      const matchesCategory = selectedCategory === 'All' || career.category === selectedCategory;
      const q = searchQuery.toLowerCase().trim();
      const matchesQuery =
        !q ||
        career.title.toLowerCase().includes(q) ||
        career.description.toLowerCase().includes(q) ||
        career.requiredSkills.some(s => s.name.toLowerCase().includes(q)) ||
        career.matchReason.toLowerCase().includes(q);

      return matchesCategory && matchesQuery;
    });
  }, [careerPaths, selectedCategory, searchQuery]);

  const toggleCompare = (careerId: string) => {
    setCompareList(prev => {
      if (prev.includes(careerId)) {
        return prev.filter(id => id !== careerId);
      }
      if (prev.length >= 3) {
        alert('You can compare up to 3 career paths simultaneously.');
        return prev;
      }
      return [...prev, careerId];
    });
  };

  const handleSelectAsPrimaryTrack = (career: CareerPath) => {
    updateProfile({ targetCareerId: career.id });
    setSelectedCareerForModal(null);
  };

  return (
    <PageContainer>
      <PageHeading
        eyebrow="CAREER DISCOVERY"
        title="Explore what could fit you."
        description="You don't have to choose forever. Start by learning what each path actually involves on a day-to-day basis."
        actions={
          compareList.length >= 2 ? (
            <PrimaryButton
              size="sm"
              onClick={() => setIsCompareModalOpen(true)}
              icon={<Columns size={14} />}
            >
              Compare ({compareList.length}) paths
            </PrimaryButton>
          ) : undefined
        }
      />

      {/* Search & Category Filter Controls */}
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          gap: 'var(--space-4)',
          marginBottom: 'var(--space-8)'
        }}
      >
        <div style={{ display: 'flex', gap: 'var(--space-4)', flexWrap: 'wrap', alignItems: 'center' }}>
          <div style={{ flex: '1 1 320px', minWidth: '260px' }}>
            <TextInput
              label="Search Careers or Skills"
              placeholder="e.g. TypeScript, Design Systems, Python, SQL…"
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
            />
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.375rem' }}>
            <label style={{ fontSize: 'var(--text-sm)', fontWeight: 600, color: 'var(--color-text)' }}>
              Filter by Domain
            </label>
            <div style={{ display: 'flex', gap: 'var(--space-2)', flexWrap: 'wrap' }}>
              {categories.map(cat => (
                <button
                  key={cat}
                  onClick={() => setSelectedCategory(cat)}
                  style={{
                    padding: '0.5rem 0.875rem',
                    borderRadius: 'var(--radius-sm)',
                    fontSize: 'var(--text-xs)',
                    fontWeight: selectedCategory === cat ? 700 : 500,
                    backgroundColor: selectedCategory === cat ? 'var(--color-burgundy)' : 'var(--color-surface)',
                    color: selectedCategory === cat ? '#FFFFFF' : 'var(--color-text)',
                    border: `1px solid ${selectedCategory === cat ? 'var(--color-burgundy)' : 'var(--color-border)'}`,
                    cursor: 'pointer',
                    transition: 'all var(--transition-fast)'
                  }}
                >
                  {cat}
                </button>
              ))}
            </div>
          </div>
        </div>

        {compareList.length > 0 && (
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              padding: 'var(--space-2) var(--space-4)',
              backgroundColor: 'var(--color-burgundy-soft)',
              borderRadius: 'var(--radius-sm)',
              border: '1px solid rgba(112,45,61,0.2)',
              fontSize: 'var(--text-xs)'
            }}
          >
            <span>
              <strong>{compareList.length}</strong> path(s) selected for comparison:{' '}
              {compareList
                .map(id => careerPaths.find(c => c.id === id)?.title)
                .filter(Boolean)
                .join(', ')}
            </span>
            <div style={{ display: 'flex', gap: 'var(--space-2)' }}>
              {compareList.length >= 2 && (
                <button
                  onClick={() => setIsCompareModalOpen(true)}
                  style={{ color: 'var(--color-burgundy)', fontWeight: 700, textDecoration: 'underline' }}
                >
                  View Comparison
                </button>
              )}
              <button
                onClick={() => setCompareList([])}
                style={{ color: 'var(--color-text-muted)', textDecoration: 'underline' }}
              >
                Clear
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Careers Grid */}
      {filteredCareers.length === 0 ? (
        <EmptyState
          title="No career paths match your query"
          description="Try adjusting your search terms or selecting 'All' domains."
          actionLabel="Clear search filters"
          onAction={() => {
            setSearchQuery('');
            setSelectedCategory('All');
          }}
        />
      ) : (
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
            gap: 'var(--space-6)'
          }}
        >
          {filteredCareers.map(career => {
            const isTarget = profile.targetCareerId === career.id;
            const inCompare = compareList.includes(career.id);

            return (
              <div key={career.id} style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
                <CareerSummary
                  career={career}
                  isSaved={savedCareerIds.includes(career.id)}
                  onToggleSave={toggleSaveCareer}
                  onExplore={() => setSelectedCareerForModal(career)}
                />

                <div
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: 'var(--space-2) var(--space-3)',
                    backgroundColor: 'var(--color-surface-muted)',
                    borderRadius: '0 0 var(--radius-sm) var(--radius-sm)',
                    border: '1px solid var(--color-border)',
                    borderTop: 'none',
                    fontSize: 'var(--text-xs)'
                  }}
                >
                  <label style={{ display: 'flex', alignItems: 'center', gap: '4px', cursor: 'pointer' }}>
                    <input
                      type="checkbox"
                      checked={inCompare}
                      onChange={() => toggleCompare(career.id)}
                      style={{ accentColor: 'var(--color-burgundy)' }}
                    />
                    <span>Compare</span>
                  </label>

                  {isTarget && (
                    <span style={{ color: 'var(--color-burgundy)', fontWeight: 700 }}>
                      ✓ Your active target
                    </span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Deep Career Detail Modal */}
      {selectedCareerForModal && (
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
          onClick={() => setSelectedCareerForModal(null)}
        >
          <div
            role="dialog"
            aria-modal="true"
            aria-labelledby="career-detail-title"
            style={{
              backgroundColor: 'var(--color-surface)',
              border: '1px solid var(--color-border-strong)',
              borderRadius: 'var(--radius-panel)',
              maxWidth: '680px',
              width: '100%',
              maxHeight: '90vh',
              overflowY: 'auto',
              padding: 'var(--space-8)',
              boxShadow: 'var(--shadow-modal)',
              display: 'flex',
              flexDirection: 'column',
              gap: 'var(--space-6)'
            }}
            onClick={e => e.stopPropagation()}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <div>
                <span className="badge badge-burgundy">{selectedCareerForModal.category}</span>
                <h2
                  id="career-detail-title"
                  style={{
                    fontSize: 'var(--heading-md)',
                    fontFamily: 'var(--font-display)',
                    marginTop: 'var(--space-1)'
                  }}
                >
                  {selectedCareerForModal.title}
                </h2>
              </div>
              <button
                onClick={() => setSelectedCareerForModal(null)}
                aria-label="Close modal"
                style={{ color: 'var(--color-text-muted)', padding: '4px' }}
              >
                <X size={20} />
              </button>
            </div>

            <p style={{ fontSize: 'var(--text-base)', color: 'var(--color-text-secondary)', lineHeight: 1.6 }}>
              {selectedCareerForModal.description}
            </p>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
              <h3 style={{ fontSize: 'var(--text-base)', fontWeight: 600 }}>Typical Day-to-Day Responsibilities</h3>
              <ul style={{ paddingLeft: 'var(--space-5)', display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
                {selectedCareerForModal.responsibilities.map((resp, i) => (
                  <li key={i} style={{ fontSize: 'var(--text-sm)', color: 'var(--color-text-secondary)', lineHeight: 1.5 }}>
                    {resp}
                  </li>
                ))}
              </ul>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
              <h3 style={{ fontSize: 'var(--text-base)', fontWeight: 600 }}>Required & Valuable Skills</h3>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--space-2)' }}>
                {selectedCareerForModal.requiredSkills.map(skill => (
                  <span key={skill.name} className="badge badge-muted">
                    {skill.name} • {skill.importance}
                  </span>
                ))}
              </div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
              <h3 style={{ fontSize: 'var(--text-base)', fontWeight: 600 }}>Typical Learning Phases</h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
                {selectedCareerForModal.learningPhases.map((phase, idx) => (
                  <div
                    key={idx}
                    style={{
                      padding: 'var(--space-3)',
                      backgroundColor: 'var(--color-surface-muted)',
                      borderRadius: 'var(--radius-sm)',
                      fontSize: 'var(--text-xs)'
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontWeight: 600 }}>
                      <span>{phase.phase}</span>
                      <span style={{ color: 'var(--color-text-muted)' }}>{phase.estimatedMonths}</span>
                    </div>
                    <p style={{ color: 'var(--color-text-secondary)', marginTop: '2px' }}>{phase.focus}</p>
                  </div>
                ))}
              </div>
            </div>

            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                paddingTop: 'var(--space-4)',
                borderTop: '1px solid var(--color-border)',
                flexWrap: 'wrap',
                gap: 'var(--space-3)'
              }}
            >
              <SecondaryButton
                size="sm"
                onClick={() => toggleSaveCareer(selectedCareerForModal.id)}
              >
                {savedCareerIds.includes(selectedCareerForModal.id) ? 'Saved in your list' : 'Save this career'}
              </SecondaryButton>

              <PrimaryButton
                size="sm"
                onClick={() => handleSelectAsPrimaryTrack(selectedCareerForModal)}
              >
                {profile.targetCareerId === selectedCareerForModal.id
                  ? 'Currently active track'
                  : 'Set as my primary career track'}
              </PrimaryButton>
            </div>
          </div>
        </div>
      )}

      {/* Compare Modal */}
      {isCompareModalOpen && (
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
          onClick={() => setIsCompareModalOpen(false)}
        >
          <div
            role="dialog"
            aria-modal="true"
            aria-labelledby="compare-title"
            style={{
              backgroundColor: 'var(--color-surface)',
              border: '1px solid var(--color-border-strong)',
              borderRadius: 'var(--radius-panel)',
              maxWidth: '960px',
              width: '100%',
              maxHeight: '90vh',
              overflowY: 'auto',
              padding: 'var(--space-8)',
              boxShadow: 'var(--shadow-modal)',
              display: 'flex',
              flexDirection: 'column',
              gap: 'var(--space-6)'
            }}
            onClick={e => e.stopPropagation()}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <span className="badge badge-burgundy">Side-by-side comparison</span>
                <h2 id="compare-title" style={{ fontSize: 'var(--heading-md)', fontFamily: 'var(--font-display)', marginTop: '4px' }}>
                  Comparing {compareList.length} Career Tracks
                </h2>
              </div>
              <button onClick={() => setIsCompareModalOpen(false)} aria-label="Close comparison">
                <X size={20} />
              </button>
            </div>

            <div
              style={{
                display: 'grid',
                gridTemplateColumns: `repeat(${compareList.length}, minmax(240px, 1fr))`,
                gap: 'var(--space-4)',
                overflowX: 'auto',
                paddingBottom: 'var(--space-2)'
              }}
            >
              {compareList.map(id => {
                const c = careerPaths.find(item => item.id === id);
                if (!c) return null;

                return (
                  <div
                    key={c.id}
                    className="panel"
                    style={{
                      padding: 'var(--space-4)',
                      display: 'flex',
                      flexDirection: 'column',
                      gap: 'var(--space-4)',
                      backgroundColor: 'var(--color-surface)'
                    }}
                  >
                    <div>
                      <span className="badge badge-burgundy">{c.category}</span>
                      <h4 style={{ fontSize: 'var(--text-base)', fontWeight: 600, marginTop: '4px' }}>
                        {c.title}
                      </h4>
                    </div>

                    <div>
                      <strong style={{ fontSize: 'var(--text-xs)', textTransform: 'uppercase', color: 'var(--color-text-muted)' }}>
                        Why it fits
                      </strong>
                      <p style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)', marginTop: '2px' }}>
                        {c.matchReason}
                      </p>
                    </div>

                    <div>
                      <strong style={{ fontSize: 'var(--text-xs)', textTransform: 'uppercase', color: 'var(--color-text-muted)' }}>
                        Core Skills
                      </strong>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px', marginTop: '4px' }}>
                        {c.requiredSkills.slice(0, 4).map(s => (
                          <span key={s.name} className="badge badge-muted">
                            {s.name}
                          </span>
                        ))}
                      </div>
                    </div>

                    <PrimaryButton
                      size="sm"
                      onClick={() => {
                        updateProfile({ targetCareerId: c.id });
                        setIsCompareModalOpen(false);
                      }}
                    >
                      Select track
                    </PrimaryButton>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </PageContainer>
  );
};
