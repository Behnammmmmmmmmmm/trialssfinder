import React from 'react';

interface LoadingStateProps {
  size?: 'sm' | 'md' | 'lg';
  fullScreen?: boolean;
  message?: string;
}

export const LoadingState: React.FC<LoadingStateProps> = ({ 
  size = 'md', 
  fullScreen = false,
  message = 'Loading...'
}) => {
  const content = (
    <div className="flex flex-col items-center justify-center">
      <div className="spinner" data-size={size}></div>
      <p className="mt-4 text-muted">{message}</p>
    </div>
  );

  if (fullScreen) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        {content}
      </div>
    );
  }

  return content;
};

export const LoadingSkeleton: React.FC<{ count?: number }> = ({ count = 3 }) => {
  return (
    <div className="space-y-4">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="card">
          <div className="card-body">
            <div className="skeleton h-6 w-3/4 mb-3"></div>
            <div className="skeleton h-4 w-full mb-2"></div>
            <div className="skeleton h-4 w-5/6"></div>
          </div>
        </div>
      ))}
    </div>
  );
};