/**
 * EVEZ666 Threshold Navigation Mesh - Wealth Flow
 * Revenue cell with offline simulation and failover processor switching
 */

'use strict';

export interface RevenueEvent {
  id: string;
  amount: number;
  currency: string;
  processor: 'stripe' | 'local-sim';
  status: 'pending' | 'completed' | 'failed';
  timestamp: number;
  metadata?: Record<string, any>;
}

export interface PayoutCalculation {
  gross: number;
  fees: number;
  net: number;
  processor: string;
  cached: boolean;
  calculatedAt: number;
}

export interface ProcessorHealth {
  processor: string;
  available: boolean;
  latency: number;
  lastCheck: number;
}

/**
 * Wealth flow manager for revenue operations
 */
export class WealthFlow {
  private revenueQueue: RevenueEvent[] = [];
  private payoutCache: Map<string, PayoutCalculation> = new Map();
  private processorHealth: Map<string, ProcessorHealth> = new Map();
  private activeProcessor: 'stripe' | 'local-sim' = 'stripe';

  constructor() {
    this.initializeProcessors();
  }

  /**
   * Initialize processor health tracking
   */
  private initializeProcessors(): void {
    this.processorHealth.set('stripe', {
      processor: 'stripe',
      available: true,
      latency: 0,
      lastCheck: Date.now(),
    });

    this.processorHealth.set('local-sim', {
      processor: 'local-sim',
      available: true,
      latency: 0,
      lastCheck: Date.now(),
    });
  }

  /**
   * Process revenue event with automatic failover
   */
  async processRevenue(event: RevenueEvent): Promise<RevenueEvent> {
    // Try active processor first
    try {
      const result = await this.processWithProcessor(event, this.activeProcessor);
      return result;
    } catch (error) {
      console.warn(`[WealthFlow] Processor ${this.activeProcessor} failed, switching to failover`);
      
      // Switch to local simulation
      this.activeProcessor = 'local-sim';
      const result = await this.processWithProcessor(event, 'local-sim');
      return result;
    }
  }

  /**
   * Process with specific processor
   */
  private async processWithProcessor(
    event: RevenueEvent,
    processor: 'stripe' | 'local-sim'
  ): Promise<RevenueEvent> {
    const startTime = Date.now();

    if (processor === 'stripe') {
      // Simulate Stripe API call
      await this.simulateStripeProcessing();
      const latency = Date.now() - startTime;
      this.updateProcessorHealth('stripe', true, latency);
      
      return {
        ...event,
        processor: 'stripe',
        status: 'completed',
      };
    } else {
      // Local simulation (always succeeds, offline-capable)
      const latency = Date.now() - startTime;
      this.updateProcessorHealth('local-sim', true, latency);
      
      return {
        ...event,
        processor: 'local-sim',
        status: 'completed',
      };
    }
  }

  /**
   * Calculate payout with caching
   */
  async calculatePayout(
    amount: number,
    processor: string = 'stripe'
  ): Promise<PayoutCalculation> {
    const cacheKey = `${processor}:${amount}`;
    
    // Check cache first
    const cached = this.payoutCache.get(cacheKey);
    if (cached && Date.now() - cached.calculatedAt < 3600000) { // 1 hour cache
      return { ...cached, cached: true };
    }

    // Calculate new payout
    const fees = this.calculateFees(amount, processor);
    const net = amount - fees;

    const calculation: PayoutCalculation = {
      gross: amount,
      fees,
      net,
      processor,
      cached: false,
      calculatedAt: Date.now(),
    };

    // Cache the calculation
    this.payoutCache.set(cacheKey, calculation);

    return calculation;
  }

  /**
   * Calculate processor fees
   */
  private calculateFees(amount: number, processor: string): number {
    if (processor === 'stripe') {
      // Stripe: 2.9% + $0.30
      return amount * 0.029 + 0.30;
    } else {
      // Local sim: no fees
      return 0;
    }
  }

  /**
   * Simulate Stripe processing
   */
  private async simulateStripeProcessing(): Promise<void> {
    return new Promise((resolve, reject) => {
      // Simulate 95% success rate
      const shouldSucceed = Math.random() > 0.05;
      const delay = Math.random() * 200 + 100; // 100-300ms

      setTimeout(() => {
        if (shouldSucceed) {
          resolve();
        } else {
          reject(new Error('Stripe processing failed'));
        }
      }, delay);
    });
  }

  /**
   * Update processor health
   */
  private updateProcessorHealth(
    processor: string,
    available: boolean,
    latency: number
  ): void {
    this.processorHealth.set(processor, {
      processor,
      available,
      latency,
      lastCheck: Date.now(),
    });
  }

  /**
   * Get processor health status
   */
  getProcessorHealth(): ProcessorHealth[] {
    return Array.from(this.processorHealth.values());
  }

  /**
   * Get active processor
   */
  getActiveProcessor(): string {
    return this.activeProcessor;
  }

  /**
   * Cell slicing: partition revenue streams
   */
  partitionRevenueStreams(events: RevenueEvent[]): {
    digital: RevenueEvent[];
    service: RevenueEvent[];
    tool: RevenueEvent[];
  } {
    return {
      digital: events.filter((e) => e.metadata?.type === 'digital'),
      service: events.filter((e) => e.metadata?.type === 'service'),
      tool: events.filter((e) => e.metadata?.type === 'tool'),
    };
  }

  /**
   * Queue revenue event for later processing
   */
  queueRevenue(event: RevenueEvent): void {
    this.revenueQueue.push(event);
  }

  /**
   * Process queued revenue events
   */
  async processQueue(): Promise<{ processed: number; failed: number }> {
    let processed = 0;
    let failed = 0;

    const queue = [...this.revenueQueue];
    this.revenueQueue = [];

    for (const event of queue) {
      try {
        await this.processRevenue(event);
        processed++;
      } catch (error) {
        failed++;
        this.revenueQueue.push(event); // Re-queue failed events
      }
    }

    return { processed, failed };
  }

  /**
   * Get queue status
   */
  getQueueStatus(): {
    length: number;
    totalAmount: number;
  } {
    const totalAmount = this.revenueQueue.reduce(
      (sum, event) => sum + event.amount,
      0
    );

    return {
      length: this.revenueQueue.length,
      totalAmount,
    };
  }

  /**
   * Clear cache (for testing)
   */
  clearCache(): void {
    this.payoutCache.clear();
  }
}

// Singleton instance
let wealthFlowInstance: WealthFlow | null = null;

/**
 * Get or create wealth flow instance
 */
export function getWealthFlow(): WealthFlow {
  if (!wealthFlowInstance) {
    wealthFlowInstance = new WealthFlow();
  }
  return wealthFlowInstance;
}
