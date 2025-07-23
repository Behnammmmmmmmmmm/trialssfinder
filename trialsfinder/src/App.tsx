import React, { Suspense, lazy } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ErrorBoundary } from './components/ErrorBoundary';
import { Layout } from './components/Layout';
import { AppProvider } from './context/AppContext';

// Preload critical page
const HomePage = lazy(() => import('./pages/HomePage'));

// Prefetch likely next pages
const LoginPage = lazy(() => import('./pages/LoginPage'));
const SearchResultsPage = lazy(() => import('./pages/SearchResultsPage'));

// Lazy load all other pages with proper chunking
const RegisterPage = lazy(() => import('./pages/RegisterPage'));
const TrialDetailsPage = lazy(() => import('./pages/TrialDetailsPage'));
const UserProfilePage = lazy(() => import('./pages/UserProfilePage'));
const CompanyDashboardPage = lazy(() => import('./pages/CompanyDashboardPage'));
const PrivateRoute = lazy(() => import('./components/PrivateRoute').then(m => ({ default: m.PrivateRoute })));

// Group less-used pages together to reduce chunks
const CreateTrialPage = lazy(() => import('./pages/CreateTrialPage'));
const AnalyticsPage = lazy(() => import('./pages/AnalyticsPage'));
const SubscriptionPage = lazy(() => import('./pages/SubscriptionPage'));

// Group static pages
const AboutPage = lazy(() => import('./pages/AboutPage'));
const ContactPage = lazy(() => import('./pages/ContactPage'));
const FAQPage = lazy(() => import('./pages/FAQPage'));
const TermsPage = lazy(() => import('./pages/TermsPage'));
const PrivacyPage = lazy(() => import('./pages/PrivacyPage'));
const PrivacyDashboard = lazy(() => import('./pages/PrivacyDashboard'));

// Minimal loading component
const PageLoading = () => (
  <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '400px' }}>
    <div className="spinner"></div>
  </div>
);

function App() {
  return (
    <ErrorBoundary>
      <AppProvider>
        <Router>
          <Layout>
            <Suspense fallback={<PageLoading />}>
              <Routes>
                <Route path="/" element={<HomePage />} />
                <Route path="/login" element={<LoginPage />} />
                <Route path="/register" element={<RegisterPage />} />
                <Route path="/trials/:id" element={<TrialDetailsPage />} />
                <Route path="/search" element={<SearchResultsPage />} />
                
                <Route path="/profile" element={
                  <Suspense fallback={<PageLoading />}>
                    <PrivateRoute userType="user">
                      <UserProfilePage />
                    </PrivateRoute>
                  </Suspense>
                } />
                
                <Route path="/dashboard" element={
                  <Suspense fallback={<PageLoading />}>
                    <PrivateRoute userType="company">
                      <CompanyDashboardPage />
                    </PrivateRoute>
                  </Suspense>
                } />
                
                <Route path="/create-trial" element={
                  <Suspense fallback={<PageLoading />}>
                    <PrivateRoute userType="company">
                      <CreateTrialPage />
                    </PrivateRoute>
                  </Suspense>
                } />
                
                <Route path="/analytics" element={
                  <Suspense fallback={<PageLoading />}>
                    <PrivateRoute userType="company">
                      <AnalyticsPage />
                    </PrivateRoute>
                  </Suspense>
                } />
                
                <Route path="/subscription" element={<SubscriptionPage />} />
                <Route path="/about" element={<AboutPage />} />
                <Route path="/contact" element={<ContactPage />} />
                <Route path="/faq" element={<FAQPage />} />
                <Route path="/terms" element={<TermsPage />} />
                <Route path="/privacy" element={<PrivacyPage />} />
                
                <Route path="/privacy-dashboard" element={
                  <Suspense fallback={<PageLoading />}>
                    <PrivateRoute>
                      <PrivacyDashboard />
                    </PrivateRoute>
                  </Suspense>
                } />
              </Routes>
            </Suspense>
          </Layout>
        </Router>
      </AppProvider>
    </ErrorBoundary>
  );
}

export default App;