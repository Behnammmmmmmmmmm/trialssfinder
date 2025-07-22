import React, { Suspense, lazy } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import * as Sentry from '@sentry/react';
import { ErrorBoundary } from './components/ErrorBoundary';
import { Layout } from './components/Layout';
import { AppProvider } from './context/AppContext';

// Create Sentry-enhanced router
const SentryRoutes = Sentry.withSentryRouting(Routes);

// Preload critical page
const HomePage = lazy(() => 
  import(/* webpackPreload: true, webpackChunkName: "home" */ './pages/HomePage')
);

// Prefetch likely next pages
const LoginPage = lazy(() => 
  import(/* webpackPrefetch: true, webpackChunkName: "login" */ './pages/LoginPage')
);
const SearchResultsPage = lazy(() => 
  import(/* webpackPrefetch: true, webpackChunkName: "search" */ './pages/SearchResultsPage')
);

// Lazy load all other pages with proper chunking
const RegisterPage = lazy(() => 
  import(/* webpackChunkName: "register" */ './pages/RegisterPage')
);
const TrialDetailsPage = lazy(() => 
  import(/* webpackChunkName: "trial-details" */ './pages/TrialDetailsPage')
);
const UserProfilePage = lazy(() => 
  import(/* webpackChunkName: "profile" */ './pages/UserProfilePage')
);
const CompanyDashboardPage = lazy(() => 
  import(/* webpackChunkName: "dashboard" */ './pages/CompanyDashboardPage')
);
const PrivateRoute = lazy(() => 
  import(/* webpackChunkName: "private-route" */ './components/PrivateRoute').then(m => ({ default: m.PrivateRoute }))
);

// Group less-used pages together to reduce chunks
const CreateTrialPage = lazy(() => 
  import(/* webpackChunkName: "company-features" */ './pages/CreateTrialPage')
);
const AnalyticsPage = lazy(() => 
  import(/* webpackChunkName: "company-features" */ './pages/AnalyticsPage')
);
const SubscriptionPage = lazy(() => 
  import(/* webpackChunkName: "company-features" */ './pages/SubscriptionPage')
);

// Group static pages
const AboutPage = lazy(() => 
  import(/* webpackChunkName: "static-pages" */ './pages/AboutPage')
);
const ContactPage = lazy(() => 
  import(/* webpackChunkName: "static-pages" */ './pages/ContactPage')
);
const FAQPage = lazy(() => 
  import(/* webpackChunkName: "static-pages" */ './pages/FAQPage')
);
const TermsPage = lazy(() => 
  import(/* webpackChunkName: "static-pages" */ './pages/TermsPage')
);
const PrivacyPage = lazy(() => 
  import(/* webpackChunkName: "static-pages" */ './pages/PrivacyPage')
);
const PrivacyDashboard = lazy(() => 
  import(/* webpackChunkName: "privacy-dashboard" */ './pages/PrivacyDashboard')
);

// Minimal loading component
const PageLoading = () => (
  <div style={{ 
    display: 'flex', 
    justifyContent: 'center', 
    alignItems: 'center', 
    minHeight: '400px' 
  }}>
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
              <SentryRoutes>
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
              </SentryRoutes>
            </Suspense>
          </Layout>
        </Router>
      </AppProvider>
    </ErrorBoundary>
  );
}

export default Sentry.withProfiler(App);