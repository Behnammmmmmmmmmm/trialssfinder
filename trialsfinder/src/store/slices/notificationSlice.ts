import { StateCreator } from 'zustand';
import { Notification } from '../../types';
import { notificationsAPI } from '../../api/notifications';
import { AppState } from '../index';

export interface NotificationState {
  notifications: Notification[];
  unreadCount: number;
  fetchNotifications: () => Promise<void>;
  markAsRead: (id: number) => Promise<void>;
}

export const createNotificationSlice: StateCreator<AppState, [], [], NotificationState> = (set, get) => ({
  notifications: [],
  unreadCount: 0,

  fetchNotifications: async () => {
    try {
      const response = await notificationsAPI.list();
      const notifications = response.data;
      const unreadCount = notifications.filter((n: Notification) => !n.is_read).length;
      set({ notifications, unreadCount });
    } catch (error) {
      console.error('Failed to fetch notifications:', error);
    }
  },

  markAsRead: async (id) => {
    // Optimistic update
    const currentNotifications = get().notifications;
    const currentUnreadCount = get().unreadCount;
    
    const updatedNotifications = currentNotifications.map(n => 
      n.id === id ? { ...n, is_read: true } : n
    );
    const updatedUnreadCount = Math.max(0, currentUnreadCount - 1);
    
    set({ 
      notifications: updatedNotifications,
      unreadCount: updatedUnreadCount
    });

    try {
      await notificationsAPI.markRead(id);
    } catch (error) {
      // Revert on error
      set({ 
        notifications: currentNotifications,
        unreadCount: currentUnreadCount
      });
      throw error;
    }
  },
});