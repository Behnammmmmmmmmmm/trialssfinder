import React, { useCallback } from 'react';
import { useNavigate } from 'react-router-dom';

interface TrialCardProps {
  trial: any;
  featured?: boolean;
  priority?: boolean;
}

const TrialCard: React.FC<TrialCardProps> = ({ trial, featured = false, priority = false }) => {
  const navigate = useNavigate();
  
  const handleClick = useCallback(() => {
    navigate(`/trials/${trial.id}`);
  }, [navigate, trial.id]);
  
  return (
    <article 
      className="card hover:shadow-lg transition-shadow trial-card"
      style={{ minHeight: '320px' }}
      onClick={handleClick}
      role="button"
      tabIndex={0}
      aria-label={`View details for ${trial.title}`}
    >
      <div className="card-body">
        <div className="flex items-start justify-between mb-3">
          <h3 className="text-xl font-semibold">{trial.title}</h3>
          {featured && <span className="badge" data-variant="primary">Featured</span>}
        </div>
        <p className="text-muted mb-4 trial-description">
          {trial.description.substring(0, 150)}...
        </p>
        <div className="flex items-center justify-between text-sm text-muted mb-4">
          <span>📍 {trial.location}</span>
          <span>🏢 {trial.company_name}</span>
        </div>
        <button 
          className="btn w-full" 
          data-variant={featured ? "primary" : "outline"}
          aria-label={`View details for ${trial.title}`}
        >
          View Details
        </button>
      </div>
    </article>
  );
};

export default React.memo(TrialCard);