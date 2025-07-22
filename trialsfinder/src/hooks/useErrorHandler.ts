import { useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from './useStore';
import { parseError, handleError, TrialsFinderError } from '../utils/errors';

interface ErrorHandlerOptions {
  showToast?: boolean;
  fallbackMessage?: string;
  redirectTo?: string;
  onError?: (error: TrialsFinderError) => void;
}

export const useErrorHandler = () => {
  const navigate = useNavigate();
  const { logout } = useAuth();

  const handleApiError = useCallback(
    (error: unknown, options: ErrorHandlerOptions = {}) => {
      const parsedError = parseError(error);
      
      // Log the error
      handleError(error, 'API Error');

      // Handle authentication errors
      if (parsedError.code === 'authentication_error') {
        logout();
        navigate('/login');
        return;
      }

      // Handle specific error codes
      if (parsedError.code === 'not_found' && options.redirectTo) {
        navigate(options.redirectTo);
        return;
      }

      // Call custom error handler if provided
      if (options.onError) {
        options.onError(parsedError);
      }

      // Show toast notification if needed
      if (options.showToast) {
        // You can integrate with your toast library here
        console.error(parsedError.message);
      }
    },
    [navigate, logout]
  );

  return { handleApiError };
};