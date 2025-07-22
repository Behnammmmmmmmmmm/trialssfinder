import { StateCreator } from 'zustand';
import { Trial, Industry } from '../../types';
import { trialsAPI } from '../../api/trials';
import { AppState } from '../index';

export interface TrialsState {
  trials: Trial[];
  favoriteTrials: number[];
  selectedIndustries: number[];
  industries: Industry[];
  loadingTrials: boolean;
  toggleFavorite: (trialId: number) => Promise<void>;
  loadFavorites: () => Promise<void>;
  updateIndustries: (industries: number[]) => Promise<void>;
  fetchTrials: (params?: any) => Promise<void>;
  fetchIndustries: () => Promise<void>;
}

export const createTrialsSlice: StateCreator<AppState, [], [], TrialsState> = (set, get) => ({
  trials: [],
  favoriteTrials: [],
  selectedIndustries: [],
  industries: [],
  loadingTrials: false,

  toggleFavorite: async (trialId) => {
    const { favoriteTrials, trials } = get();
    const isFavorited = favoriteTrials.includes(trialId);
    
    // Optimistic update
    const updatedFavorites = isFavorited 
      ? favoriteTrials.filter(id => id !== trialId)
      : [...favoriteTrials, trialId];
      
    const updatedTrials = trials.map(t => 
      t.id === trialId ? { ...t, is_favorited: !isFavorited } : t
    );
    
    set({
      favoriteTrials: updatedFavorites,
      trials: updatedTrials
    });

    try {
      await trialsAPI.toggleFavorite(trialId);
    } catch (error) {
      // Revert on error
      set({
        favoriteTrials: favoriteTrials,
        trials: trials
      });
      throw error;
    }
  },

  loadFavorites: async () => {
    try {
      const response = await trialsAPI.getFavorites();
      const favoriteIds = response.data.map((fav: any) => fav.trial.id);
      set({ favoriteTrials: favoriteIds });
    } catch (error) {
      // Only log in non-test environments
      if (process.env.NODE_ENV !== 'test') {
        console.error('Failed to load favorites:', error);
      }
    }
  },

  updateIndustries: async (industries) => {
    set({ selectedIndustries: industries });
    try {
      await trialsAPI.followIndustries(industries);
    } catch (error) {
      throw error;
    }
  },

  fetchTrials: async (params) => {
    set({ loadingTrials: true });
    try {
      const response = await trialsAPI.list(params);
      // Handle paginated response
      const trialsData = response.data.results || response.data;
      // Ensure we always have an array
      const trials = Array.isArray(trialsData) ? trialsData : [];
      set({ trials, loadingTrials: false });
    } catch (error) {
      set({ trials: [], loadingTrials: false });
      // Only log in non-test environments
      if (process.env.NODE_ENV !== 'test') {
        console.error('Failed to fetch trials:', error);
      }
    }
  },

  fetchIndustries: async () => {
    try {
      const response = await trialsAPI.getIndustries();
      set({ industries: response.data });
    } catch (error) {
      // Only log in non-test environments
      if (process.env.NODE_ENV !== 'test') {
        console.error('Failed to load industries:', error);
      }
    }
  },
});