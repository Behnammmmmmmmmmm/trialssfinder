import React, { useEffect, useState, useCallback } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { Trial, Industry } from '../types';
import { trialsAPI } from '../api/trials';

export const SearchResultsPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const [trials, setTrials] = useState<Trial[]>([]);
  const [industries, setIndustries] = useState<Industry[]>([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    industry: '',
    location: ''
  });

  const searchTrials = useCallback(async () => {
    setLoading(true);
    try {
      const params = {
        search: searchParams.get('q') || '',
        ...filters
      };
      const response = await trialsAPI.list(params);
      const trialsData = response.data.results || response.data;
      setTrials(Array.isArray(trialsData) ? trialsData : []);
    } catch (error) {
      console.error('Failed to search trials:', error);
      setTrials([]);
    } finally {
      setLoading(false);
    }
  }, [searchParams, filters]);

  useEffect(() => {
    loadIndustries();
    searchTrials();
  }, [searchParams, searchTrials]);

  const loadIndustries = async () => {
    try {
      const response = await trialsAPI.getIndustries();
      setIndustries(response.data);
    } catch (error) {
      console.error('Failed to load industries:', error);
    }
  };

  const handleFilterChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFilters({ ...filters, [e.target.name]: e.target.value });
  };

  const applyFilters = () => {
    searchTrials();
  };

  const searchQuery = searchParams.get('q') || '';

  return (
    <div className="container py-8">
      <h1 className="text-3xl font-bold mb-6">
        Search Results {searchQuery && `for "${searchQuery}"`}
      </h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        <div className="lg:col-span-1">
          <div className="card">
            <div className="card-header">
              <h3 className="text-lg font-semibold">Filters</h3>
            </div>
            <div className="card-body">
              <div className="form-group">
                <label className="form-label">Industry</label>
                <select 
                  name="industry" 
                  value={filters.industry} 
                  onChange={handleFilterChange}
                  className="form-control"
                >
                  <option value="">All Industries</option>
                  {industries.map(industry => (
                    <option key={industry.id} value={industry.id}>
                      {industry.name}
                    </option>
                  ))}
                </select>
              </div>
              
              <div className="form-group">
                <label className="form-label">Location</label>
                <input
                  type="text"
                  name="location"
                  value={filters.location}
                  onChange={handleFilterChange}
                  placeholder="Enter location"
                  className="form-control"
                />
              </div>
              
              <button 
                onClick={applyFilters}
                className="btn w-full"
                data-variant="primary"
              >
                Apply Filters
              </button>
            </div>
          </div>
        </div>
        
        <div className="lg:col-span-3">
          {loading ? (
            <div className="flex justify-center py-12">
              <div className="spinner" data-size="lg"></div>
            </div>
          ) : trials.length === 0 ? (
            <div className="card">
              <div className="card-body text-center py-12">
                <div className="text-6xl mb-4">🔍</div>
                <h2 className="text-xl font-semibold mb-2">No Results Found</h2>
                <p className="text-muted mb-6">
                  Try adjusting your search terms or filters
                </p>
                <Link to="/" className="btn" data-variant="primary">
                  Browse All Trials
                </Link>
              </div>
            </div>
          ) : (
            <>
              <p className="text-muted mb-4">
                Found {trials.length} trial{trials.length !== 1 ? 's' : ''}
              </p>
              <div className="space-y-4">
                {trials.map(trial => (
                  <div key={trial.id} className="card hover:shadow-lg transition-shadow">
                    <div className="card-body">
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <h3 className="text-xl font-semibold mb-2">{trial.title}</h3>
                          <p className="text-muted mb-3">{trial.description}</p>
                          <div className="flex items-center gap-4 text-sm text-muted">
                            <span>🏢 {trial.company_name}</span>
                            <span>🏭 {trial.industry_name}</span>
                            <span>📍 {trial.location}</span>
                          </div>
                        </div>
                        <Link 
                          to={`/trials/${trial.id}`}
                          className="btn ml-4"
                          data-variant="outline"
                        >
                          View Details
                        </Link>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default SearchResultsPage;