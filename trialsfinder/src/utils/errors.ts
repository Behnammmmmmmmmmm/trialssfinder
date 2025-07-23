import axios, { AxiosError } from 'axios';

export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, any>;
  request_id?: string;
}

export interface ErrorResponse {
  error: ApiError;
}

export class TrialsFinderError extends Error {
  code: string;
  details?: Record<string, any>;
  request_id?: string;

  constructor(message: string, code: string = 'unknown_error', details?: Record<string, any>) {
    super(message);
    this.name = 'TrialsFinderError';
    this.code = code;
    this.details = details;
  }
}

export const parseError = (error: unknown): TrialsFinderError => {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<ErrorResponse>;
    
    if (axiosError.response?.data?.error) {
      const apiError = axiosError.response.data.error;
      return new TrialsFinderError(
        apiError.message,
        apiError.code,
        apiError.details
      );
    }
    
    if (axiosError.code === 'ECONNABORTED') {
      return new TrialsFinderError('Request timeout', 'timeout_error');
    }
    
    if (axiosError.code === 'ERR_NETWORK') {
      return new TrialsFinderError('Network error', 'network_error');
    }
    
    if (!axiosError.response) {
      return new TrialsFinderError('Network error', 'network_error');
    }
    
    return new TrialsFinderError(axiosError.message || 'Request failed', 'request_error');
  }
  
  if (error instanceof TrialsFinderError) {
    return error;
  }
  
  if (error instanceof Error) {
    return new TrialsFinderError(error.message, 'client_error');
  }
  
  return new TrialsFinderError('An unexpected error occurred', 'unknown_error');
};

export const getErrorMessage = (error: unknown): string => {
  const parsedError = parseError(error);
  
  const errorMessages: Record<string, string> = {
    'network_error': 'Unable to connect to the server. Please check your internet connection.',
    'timeout_error': 'Request took too long. Please try again.',
    'authentication_error': 'Please log in to continue.',
    'permission_error': "You don't have permission to perform this action.",
    'validation_error': 'Please check your input and try again.',
    'not_found': 'The requested resource was not found.',
    'internal_error': 'Something went wrong on our end. Please try again later.',
  };
  
  return errorMessages[parsedError.code] || parsedError.message;
};

// Global error handler
export const handleError = (error: unknown, context: string): void => {
  const parsedError = parseError(error);
  
  // Log to console in development
  if (process.env.NODE_ENV === 'development') {
    console.error(`[${context}] Application Error:`, parsedError);
  }
  
  // You can add your own error logging service here
  // For example, send to your backend logging endpoint
  if (window.logger) {
    window.logger.error('Application error', { error: parsedError, context });
  }
};

// Setup global error handlers
export const setupGlobalErrorHandlers = (): void => {
  window.addEventListener('unhandledrejection', (event) => {
    handleError(event.reason, 'Unhandled Promise Rejection');
    event.preventDefault();
  });
  
  window.addEventListener('error', (event) => {
    handleError(event.error, 'Global Error');
    event.preventDefault();
  });
};