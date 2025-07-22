import { create } from 'zustand';
import { devtools, persist, subscribeWithSelector } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';

import { AuthState, createAuthSlice } from './slices/authSlice';
import { NotificationState, createNotificationSlice } from './slices/notificationSlice';
import { TrialsState, createTrialsSlice } from './slices/trialsSlice';
import { UIState, createUISlice } from './slices/uiSlice';

export interface AppState extends AuthState, TrialsState, UIState, NotificationState {
  clearLoadingStates: () => void;
}

export const useStore = create<AppState>()(
  devtools(
    persist(
      subscribeWithSelector(
        immer((set, get, api) => ({
          ...createAuthSlice(set, get, api),
          ...createTrialsSlice(set, get, api),
          ...createUISlice(set, get, api),
          ...createNotificationSlice(set, get, api),
          clearLoadingStates: () => set((state) => {
            state.loadingStates = {};
          }),
        }))
      ),
      {
        name: 'trialssfinder-store',
        partialize: (state) => ({
          user: state.user,
          favoriteTrials: state.favoriteTrials,
          selectedIndustries: state.selectedIndustries,
        }),
      }
    ),
    { name: 'TrialsFinder' }
  )
);