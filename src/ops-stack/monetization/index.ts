/**
 * Monetization Module
 * Handles revenue tracking, billing, subscriptions, and financial metrics
 */

export interface RevenueStream {
  id: string;
  name: string;
  type: 'subscription' | 'transaction' | 'licensing' | 'advertising';
  amount: number;
  currency: string;
  timestamp: number;
  metadata?: Record<string, any>;
}

export interface Subscription {
  id: string;
  customerId: string;
  plan: string;
  status: 'active' | 'inactive' | 'suspended' | 'cancelled';
  startDate: number;
  endDate?: number;
  amount: number;
  currency: string;
  billingCycle: 'monthly' | 'quarterly' | 'yearly';
}

export interface FinancialMetrics {
  totalRevenue: number;
  activeSubscriptions: number;
  averageRevenuePerUser: number;
  churnRate: number;
  lifetimeValue: number;
  timestamp: number;
}

export class MonetizationEngine {
  private revenueStreams: RevenueStream[] = [];
  private subscriptions: Map<string, Subscription> = new Map();
  private metricsHistory: FinancialMetrics[] = [];

  constructor() {
    console.log('[Monetization] Engine initialized');
  }

  /**
   * Record a revenue event
   */
  recordRevenue(revenue: Omit<RevenueStream, 'id' | 'timestamp'>): string {
    const revenueId = `REV-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    const fullRevenue: RevenueStream = {
      ...revenue,
      id: revenueId,
      timestamp: Date.now()
    };

    this.revenueStreams.push(fullRevenue);
    console.log(
      `[Monetization] Revenue recorded: ${revenue.type} - ${revenue.currency} ${revenue.amount}`
    );
    return revenueId;
  }

  /**
   * Create a new subscription
   */
  createSubscription(subscription: Omit<Subscription, 'id'>): string {
    const subscriptionId = `SUB-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    const fullSubscription: Subscription = {
      ...subscription,
      id: subscriptionId
    };

    this.subscriptions.set(subscriptionId, fullSubscription);
    console.log(
      `[Monetization] Subscription created: ${subscription.plan} for customer ${subscription.customerId}`
    );
    return subscriptionId;
  }

  /**
   * Update subscription status
   */
  updateSubscriptionStatus(subscriptionId: string, status: Subscription['status']): boolean {
    const subscription = this.subscriptions.get(subscriptionId);
    if (!subscription) {
      console.error(`[Monetization] Subscription not found: ${subscriptionId}`);
      return false;
    }

    subscription.status = status;
    if (status === 'cancelled') {
      subscription.endDate = Date.now();
    }

    console.log(`[Monetization] Subscription ${subscriptionId} status updated to ${status}`);
    return true;
  }

  /**
   * Calculate and record financial metrics
   */
  calculateMetrics(): FinancialMetrics {
    const activeSubscriptions = Array.from(this.subscriptions.values()).filter(
      sub => sub.status === 'active'
    );

    const totalRevenue = this.revenueStreams.reduce((sum, rev) => sum + rev.amount, 0);
    const activeSubCount = activeSubscriptions.length;
    const totalCustomers = new Set(activeSubscriptions.map(sub => sub.customerId)).size;

    const metrics: FinancialMetrics = {
      totalRevenue,
      activeSubscriptions: activeSubCount,
      averageRevenuePerUser: totalCustomers > 0 ? totalRevenue / totalCustomers : 0,
      churnRate: this.calculateChurnRate(),
      lifetimeValue: this.calculateLifetimeValue(),
      timestamp: Date.now()
    };

    this.metricsHistory.push(metrics);
    console.log(`[Monetization] Metrics calculated: Revenue ${totalRevenue}, Active subs ${activeSubCount}`);
    return metrics;
  }

  /**
   * Calculate churn rate
   */
  private calculateChurnRate(): number {
    const totalSubs = this.subscriptions.size;
    if (totalSubs === 0) return 0;

    const cancelledSubs = Array.from(this.subscriptions.values()).filter(
      sub => sub.status === 'cancelled'
    ).length;

    return (cancelledSubs / totalSubs) * 100;
  }

  /**
   * Calculate average lifetime value
   */
  private calculateLifetimeValue(): number {
    const activeSubscriptions = Array.from(this.subscriptions.values()).filter(
      sub => sub.status === 'active'
    );

    if (activeSubscriptions.length === 0) return 0;

    const avgSubscriptionValue = activeSubscriptions.reduce(
      (sum, sub) => sum + sub.amount,
      0
    ) / activeSubscriptions.length;

    // Simplified LTV calculation (assumes 24 month average lifetime)
    return avgSubscriptionValue * 24;
  }

  /**
   * Get revenue history
   */
  getRevenueHistory(filter?: { type?: string; limit?: number }): RevenueStream[] {
    let filtered = [...this.revenueStreams];

    if (filter?.type) {
      filtered = filtered.filter(rev => rev.type === filter.type);
    }
    if (filter?.limit) {
      filtered = filtered.slice(-filter.limit);
    }

    return filtered;
  }

  /**
   * Get active subscriptions
   */
  getActiveSubscriptions(): Subscription[] {
    return Array.from(this.subscriptions.values()).filter(sub => sub.status === 'active');
  }

  /**
   * Get metrics history
   */
  getMetricsHistory(limit?: number): FinancialMetrics[] {
    if (limit) {
      return this.metricsHistory.slice(-limit);
    }
    return [...this.metricsHistory];
  }

  /**
   * Clear historical data
   */
  clearHistory(): void {
    this.revenueStreams = [];
    this.metricsHistory = [];
    console.log('[Monetization] History cleared');
  }
}
