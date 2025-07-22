import { StateCreator } from 'zustand';
import { AppState } from '../index';

export interface UIState {
  sidebarOpen: boolean;
  theme: 'light' | 'dark';
  loadingStates: Record<string, boolean>;
  toggleSidebar: () => void;
  setTheme: (theme: 'light' | 'dark') => void;
  setLoadingState: (key: string, loading: boolean) => void;
  clearLoadingStates: () => void;
}

export const createUISlice: StateCreator<AppState, [], [], UIState> = (set) => ({
  sidebarOpen: false,
  theme: 'light',
  loadingStates: {},

  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  
  setTheme: (theme) => set({ theme }),
  
  setLoadingState: (key, loading) => {
    set((state) => ({
      loadingStates: {
        ...state.loadingStates,
        [key]: loading
      }
    }));
  },
  
  clearLoadingStates: () => set({ loadingStates: {} }),
});