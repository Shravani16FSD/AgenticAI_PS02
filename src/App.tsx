import React from 'react';
import { BrowserRouter, Routes, Route, Navigate, Link } from 'react-router-dom';
import { AppProvider } from './context/AppContext';
import { AppHeader } from './components/layout/AppHeader';
import { AppFooter } from './components/layout/AppFooter';
import { ToastContainer } from './components/ui/Overlays';
import { LandingPage } from './pages/LandingPage';
import { OnboardingPage } from './pages/OnboardingPage';
import { DashboardPage } from './pages/DashboardPage';
import { CoachPage } from './pages/CoachPage';
import { ExplorePage } from './pages/ExplorePage';
import { RoadmapPage } from './pages/RoadmapPage';
import { SkillsPage } from './pages/SkillsPage';
import { ProfilePage } from './pages/ProfilePage';
import { AuthPage } from './pages/AuthPage';
import { PageContainer } from './components/ui/Typography';
import { PrimaryButton } from './components/ui/Buttons';

// 404 Not Found Page with editorial aesthetic
const NotFoundPage: React.FC = () => {
  return (
    <PageContainer style={{ textAlign: 'center', padding: 'var(--space-16) var(--space-6)' }}>
      <span className="badge badge-burgundy" style={{ marginBottom: 'var(--space-2)' }}>
        Page Not Found
      </span>
      <h1 style={{ fontSize: 'var(--heading-lg)', fontFamily: 'var(--font-display)', margin: 'var(--space-2) 0' }}>
        This path doesn't lead anywhere yet.
      </h1>
      <p style={{ fontSize: 'var(--text-base)', color: 'var(--color-text-secondary)', maxWidth: '480px', margin: '0 auto var(--space-6)' }}>
        The page you are looking for may have moved or doesn't exist. Let's return to familiar territory.
      </p>
      <Link to="/dashboard">
        <PrimaryButton size="md">Return to dashboard</PrimaryButton>
      </Link>
    </PageContainer>
  );
};

export const App: React.FC = () => {
  return (
    <AppProvider>
      <BrowserRouter>
        <div
          style={{
            minHeight: '100vh',
            display: 'flex',
            flexDirection: 'column',
            backgroundColor: 'var(--color-page)',
            color: 'var(--color-text)'
          }}
        >
          {/* Skip link for keyboard accessibility */}
          <a href="#main-content" className="skip-link">
            Skip to main content
          </a>

          {/* Persistent Editorial Header */}
          <AppHeader />

          {/* Application Route Views */}
          <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
            <Routes>
              <Route path="/" element={<LandingPage />} />
              <Route path="/onboarding" element={<OnboardingPage />} />
              <Route path="/dashboard" element={<DashboardPage />} />
              <Route path="/coach" element={<CoachPage />} />
              <Route path="/explore" element={<ExplorePage />} />
              <Route path="/roadmap" element={<RoadmapPage />} />
              <Route path="/skills" element={<SkillsPage />} />
              <Route path="/profile" element={<ProfilePage />} />
              <Route path="/login" element={<AuthPage />} />
              <Route path="/auth" element={<AuthPage />} />
              {/* Backwards compatibility aliases */}
              <Route path="/app" element={<Navigate to="/dashboard" replace />} />
              <Route path="/chat" element={<Navigate to="/coach" replace />} />
              <Route path="*" element={<NotFoundPage />} />
            </Routes>
          </div>

          {/* Persistent Editorial Footer */}
          <AppFooter />

          {/* Notifications live region */}
          <ToastContainer />
        </div>
      </BrowserRouter>
    </AppProvider>
  );
};

export default App;
