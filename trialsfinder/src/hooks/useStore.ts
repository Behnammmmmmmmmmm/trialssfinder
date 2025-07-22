import { useStore as useZustandStore } from '../store';

// Selectors with manual shallow comparison
export const useAuth = () => {
  const user = useZustandStore((state) => state.user);
  const loading = useZustandStore((state) => state.loading);
  const mockMode = useZustandStore((state) => state.mockMode);
  const login = useZustandStore((state) => state.login);
  const register = useZustandStore((state) => state.register);
  const logout = useZustandStore((state) => state.logout);
  const loadUser = useZustandStore((state) => state.loadUser);
  
  return { user, loading, mockMode, login, register, logout, loadUser };
};

export const useTrials = () => {
  const trials = useZustandStore((state) => state.trials);
  const favoriteTrials = useZustandStore((state) => state.favoriteTrials);
  const loadingTrials = useZustandStore((state) => state.loadingTrials);
  const toggleFavorite = useZustandStore((state) => state.toggleFavorite);
  const fetchTrials = useZustandStore((state) => state.fetchTrials);
  
  return { trials, favoriteTrials, loadingTrials, toggleFavorite, fetchTrials };
};

export const useNotifications = () => {
  const notifications = useZustandStore((state) => state.notifications);
  const unreadCount = useZustandStore((state) => state.unreadCount);
  const fetchNotifications = useZustandStore((state) => state.fetchNotifications);
  const markAsRead = useZustandStore((state) => state.markAsRead);
  
  return { notifications, unreadCount, fetchNotifications, markAsRead };
};

export const useUI = () => {
  const sidebarOpen = useZustandStore((state) => state.sidebarOpen);
  const theme = useZustandStore((state) => state.theme);
  const loadingStates = useZustandStore((state) => state.loadingStates);
  const toggleSidebar = useZustandStore((state) => state.toggleSidebar);
  const setTheme = useZustandStore((state) => state.setTheme);
  const setLoadingState = useZustandStore((state) => state.setLoadingState);
  
  return { sidebarOpen, theme, loadingStates, toggleSidebar, setTheme, setLoading: setLoadingState };
};