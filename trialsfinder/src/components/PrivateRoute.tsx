import React from 'react';
import { Navigate } from 'react-router-dom';

import { useAuth } from '../hooks/useStore';

import { LoadingState } from './LoadingState';

interface PrivateRouteProps {
  children: React.ReactNode;
  userType?: string;
}

export const PrivateRoute: React.FC<PrivateRouteProps> = ({ children, userType }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return <LoadingState fullScreen message="Loading..." />;
  }

  if (!user) {
    return <Navigate to="/login" />;
  }

  if (userType && user.user_type !== userType) {
    return <Navigate to="/" />;
  }

  return <>{children}</>;
};