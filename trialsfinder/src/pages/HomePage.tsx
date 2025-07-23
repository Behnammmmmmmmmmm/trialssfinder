import React, { useEffect, useState, useCallback, useMemo, lazy, Suspense } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useTrials, useAuth } from '../hooks/useStore';
import { LoadingState } from '../components/LoadingState';

// Lazy load heavy components
const TrialCard = lazy(() => import('../components/TrialCard'));

// Debounce without lodash
const debounce = (func: Function, delay: number) => {
  let timeoutId: NodeJS.Timeout;
  return (...args: any[]) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func(...args), delay);
  };
};

// Simple card skeleton
const CardSkeleton = () => (
  <div className="card" style={{ minHeight: '320px' }}>
    <div className="card-body">
      <div className="skeleton h-6 w-3/4 mb-3"></div>
      <div className="skeleton h-4 w-full mb-2"></div>
      <div className="skeleton h-4 w-5/6 mb-4"></div>
      <div className="skeleton h-10 w-full"></div>
    </div>
  </div>
);

// Hero section as separate component
const HeroSection = React.memo(() => {
  const [searchQuery, setSearchQuery] = useState('');
  const navigate = useNavigate();

  const debouncedSearch = useMemo(
    () =>
      debounce((query: string) => {
        if (query.length > 2) {
          navigate(`/search?q=${encodeURIComponent(query)}`);
        }
      }, 500),
    [navigate]
  );

  const handleSearchChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const value = e.target.value;
      setSearchQuery(value);
      debouncedSearch(value);
    },
    [debouncedSearch]
  );

  return (
    <div className="text-center mb-12">
      <h1 className="text-5xl font-bold mb-6 text-primary">Find Your Perfect Trial</h1>
      <p className="text-xl text-muted mb-8">
        Discover free trials for the tools and services your business needs
      </p>
      <div className="max-w-full mx-auto mb-8" style={{ maxWidth: '600px' }}>
        <div className="relative">
          <label htmlFor="search-trials" className="sr-only">
            Search trials
          </label>
          <input
            id="search-trials"
            type="search"
            value={searchQuery}
            onChange={handleSearchChange}
            placeholder="Search trials..."
            className="form-control form-control-lg px-6"
            style={{ paddingLeft: '3rem' }}
            aria-label="Search for clinical trials"
            autoComplete="off"
          />
          <span className="search-icon" aria-hidden="true">
            🔍
          </span>
        </div>
      </div>
      <Link to="/search" className="btn" data-variant="outline" data-size="lg">
        Browse All Trials
      </Link>
    </div>
  );
});

HeroSection.displayName = 'HeroSection';

const HomePage: React.FC = () => {
  const { trials, fetchTrials, loadingTrials } = useTrials();
  const { mockMode } = useAuth();
  const [visibleTrials, setVisibleTrials] = useState(6);
  const [initialLoad, setInitialLoad] = useState(true);

  useEffect(() => {
    // Fetch only what's needed initially
    const loadInitialData = async () => {
      if (!mockMode) {
        // Only fetch if not in mock mode
        await fetchTrials({ page_size: 12 });
      }
      setInitialLoad(false);
    };
    loadInitialData();
  }, [fetchTrials, mockMode]);

  const trialsArray = useMemo(() => (Array.isArray(trials) ? trials : []), [trials]);

  const { featuredTrials, latestTrials } = useMemo(() => {
    const featured: any[] = [];
    const latest: any[] = [];

    trialsArray.forEach((trial) => {
      if (trial.is_featured) {
        featured.push(trial);
      } else {
        latest.push(trial);
      }
    });

    return {
      featuredTrials: featured.slice(0, visibleTrials),
      latestTrials: latest.slice(0, visibleTrials),
    };
  }, [trialsArray, visibleTrials]);

  // Load more trials on scroll
  useEffect(() => {
    const handleScroll = () => {
      if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 1000) {
        setVisibleTrials((prev) => Math.min(prev + 6, trialsArray.length));
      }
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, [trialsArray.length]);

  if (loadingTrials && initialLoad) {
    return <LoadingState fullScreen message="Loading trials..." />;
  }

  return (
    <div className="container py-8">
      <HeroSection />

      {mockMode && (
        <div className="alert mb-4" data-variant="warning">
          <p className="font-semibold">Development Mode</p>
          <p className="text-sm">Backend is not available. Using mock data.</p>
        </div>
      )}

      {featuredTrials.length > 0 && (
        <section className="mb-12">
          <h2 className="text-3xl font-semibold mb-6">Featured Free Trials</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {featuredTrials.map((trial, index) => (
              <Suspense key={trial.id} fallback={<CardSkeleton />}>
                <TrialCard trial={trial} featured={true} priority={index < 3} />
              </Suspense>
            ))}
          </div>
        </section>
      )}

      {latestTrials.length > 0 && (
        <section className="mb-12">
          <h2 className="text-3xl font-semibold mb-6">Latest Free Trials</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {latestTrials.map((trial) => (
              <Suspense key={trial.id} fallback={<CardSkeleton />}>
                <TrialCard trial={trial} featured={false} priority={false} />
              </Suspense>
            ))}
          </div>
        </section>
      )}

      {trialsArray.length === 0 && !loadingTrials && (
        <div className="text-center py-12">
          <div className="text-6xl mb-4" aria-hidden="true">
            🔍
          </div>
          <p className="text-xl text-muted">No trials available at the moment</p>
          <p className="text-lg text-muted">Check back soon for new opportunities!</p>
        </div>
      )}
    </div>
  );
};

export default HomePage;