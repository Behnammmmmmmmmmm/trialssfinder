import React, { createContext, useContext, useReducer, ReactNode } from 'react';
import { User, Trial, Notification } from '../types';

interface AppState {
  user: User | null;
  trials: Trial[];
  notifications: Notification[];
  loading: Record<string, boolean>;
  errors: Record<string, string>;
}

type AppAction =
  | { type: 'SET_USER'; payload: User | null }
  | { type: 'SET_TRIALS'; payload: Trial[] }
  | { type: 'ADD_TRIAL'; payload: Trial }
  | { type: 'UPDATE_TRIAL'; payload: { id: number; trial: Partial<Trial> } }
  | { type: 'SET_NOTIFICATIONS'; payload: Notification[] }
  | { type: 'MARK_NOTIFICATION_READ'; payload: number }
  | { type: 'SET_LOADING'; payload: { key: string; value: boolean } }
  | { type: 'SET_ERROR'; payload: { key: string; error: string | null } }
  | { type: 'CLEAR_ERRORS' };

const initialState: AppState = {
  user: null,
  trials: [],
  notifications: [],
  loading: {},
  errors: {}
};

function appReducer(state: AppState, action: AppAction): AppState {
  switch (action.type) {
    case 'SET_USER':
      return { ...state, user: action.payload };
    
    case 'SET_TRIALS':
      return { ...state, trials: action.payload };
    
    case 'ADD_TRIAL':
      return { ...state, trials: [...state.trials, action.payload] };
    
    case 'UPDATE_TRIAL':
      return {
        ...state,
        trials: state.trials.map(trial =>
          trial.id === action.payload.id
            ? { ...trial, ...action.payload.trial }
            : trial
        )
      };
    
    case 'SET_NOTIFICATIONS':
      return { ...state, notifications: action.payload };
    
    case 'MARK_NOTIFICATION_READ':
      return {
        ...state,
        notifications: state.notifications.map(notif =>
          notif.id === action.payload
            ? { ...notif, is_read: true }
            : notif
        )
      };
    
    case 'SET_LOADING':
      return {
        ...state,
        loading: {
          ...state.loading,
          [action.payload.key]: action.payload.value
        }
      };
    
    case 'SET_ERROR':
      return {
        ...state,
        errors: action.payload.error
          ? { ...state.errors, [action.payload.key]: action.payload.error }
          : Object.fromEntries(
              Object.entries(state.errors).filter(([key]) => key !== action.payload.key)
            )
      };
    
    case 'CLEAR_ERRORS':
      return { ...state, errors: {} };
    
    default:
      return state;
  }
}

const AppContext = createContext<{
  state: AppState;
  dispatch: React.Dispatch<AppAction>;
} | null>(null);

export const AppProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(appReducer, initialState);

  return (
    <AppContext.Provider value={{ state, dispatch }}>
      {children}
    </AppContext.Provider>
  );
};

export function useAppContext() {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useAppContext must be used within AppProvider');
  }
  return context;
}

// Selector hooks
export function useUser() {
  const { state } = useAppContext();
  return state.user;
}

export function useTrials() {
  const { state, dispatch } = useAppContext();
  return {
    trials: state.trials,
    setTrials: (trials: Trial[]) => dispatch({ type: 'SET_TRIALS', payload: trials }),
    addTrial: (trial: Trial) => dispatch({ type: 'ADD_TRIAL', payload: trial }),
    updateTrial: (id: number, trial: Partial<Trial>) => 
      dispatch({ type: 'UPDATE_TRIAL', payload: { id, trial } })
  };
}

export function useLoading(key: string) {
  const { state, dispatch } = useAppContext();
  return {
    isLoading: state.loading[key] || false,
    setLoading: (value: boolean) => 
      dispatch({ type: 'SET_LOADING', payload: { key, value } })
  };
}

export function useError(key: string) {
  const { state, dispatch } = useAppContext();
  return {
    error: state.errors[key] || null,
    setError: (error: string | null) => 
      dispatch({ type: 'SET_ERROR', payload: { key, error } })
  };
}

export default AppProvider;