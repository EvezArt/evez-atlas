/**
 * Notifications Module
 * Handles real-time notifications, alerts, and communication channels
 */

export interface Notification {
  id: string;
  type: 'info' | 'warning' | 'error' | 'success';
  title: string;
  message: string;
  timestamp: number;
  priority: 'low' | 'medium' | 'high' | 'critical';
  channel: 'email' | 'sms' | 'push' | 'webhook';
  metadata?: Record<string, any>;
}

export interface NotificationChannel {
  name: string;
  enabled: boolean;
  endpoint?: string;
}

export class NotificationService {
  private notifications: Notification[] = [];
  private channels: Map<string, NotificationChannel> = new Map();
  private subscribers: Map<string, ((notification: Notification) => void)[]> = new Map();

  constructor() {
    // Initialize default channels
    this.channels.set('email', { name: 'email', enabled: true });
    this.channels.set('sms', { name: 'sms', enabled: true });
    this.channels.set('push', { name: 'push', enabled: true });
    this.channels.set('webhook', { name: 'webhook', enabled: true });
    console.log('[Notifications] Service initialized');
  }

  /**
   * Send a notification through specified channel
   */
  async send(notification: Omit<Notification, 'id' | 'timestamp'>): Promise<string> {
    const fullNotification: Notification = {
      ...notification,
      id: `NOTIF-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      timestamp: Date.now()
    };

    this.notifications.push(fullNotification);
    
    // Emit to subscribers
    const channelSubscribers = this.subscribers.get(notification.channel) || [];
    channelSubscribers.forEach(callback => callback(fullNotification));

    console.log(
      `[Notifications] Sent ${notification.priority} ${notification.type} via ${notification.channel}: ${notification.title}`
    );

    return fullNotification.id;
  }

  /**
   * Subscribe to notifications on a specific channel
   */
  subscribe(channel: string, callback: (notification: Notification) => void): void {
    if (!this.subscribers.has(channel)) {
      this.subscribers.set(channel, []);
    }
    this.subscribers.get(channel)!.push(callback);
    console.log(`[Notifications] New subscriber added to ${channel} channel`);
  }

  /**
   * Configure a notification channel
   */
  configureChannel(channel: string, config: NotificationChannel): void {
    this.channels.set(channel, config);
    console.log(`[Notifications] Channel ${channel} configured`);
  }

  /**
   * Get notification history
   */
  getHistory(filter?: { type?: string; priority?: string; limit?: number }): Notification[] {
    let filtered = [...this.notifications];

    if (filter?.type) {
      filtered = filtered.filter(n => n.type === filter.type);
    }
    if (filter?.priority) {
      filtered = filtered.filter(n => n.priority === filter.priority);
    }
    if (filter?.limit) {
      filtered = filtered.slice(-filter.limit);
    }

    return filtered;
  }

  /**
   * Clear notification history
   */
  clearHistory(): void {
    this.notifications = [];
    console.log('[Notifications] History cleared');
  }
}
