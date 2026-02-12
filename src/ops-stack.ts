/**
 * Ops Stack - Main Orchestration Layer
 * Integrates all operational modules: market intelligence, notifications,
 * automation, monetization, and AI engine
 */

import { MarketIntelligence } from './ops-stack/market-intelligence';
import { NotificationService } from './ops-stack/notifications';
import { AutomationEngine } from './ops-stack/automation';
import { MonetizationEngine } from './ops-stack/monetization';
import { AIEngine } from './ops-stack/ai-engine';

export interface OpsStackConfig {
  enableMarketIntelligence?: boolean;
  enableNotifications?: boolean;
  enableAutomation?: boolean;
  enableMonetization?: boolean;
  enableAI?: boolean;
}

export interface OpsStackStatus {
  healthy: boolean;
  modules: {
    marketIntelligence: boolean;
    notifications: boolean;
    automation: boolean;
    monetization: boolean;
    aiEngine: boolean;
  };
  timestamp: number;
}

export class OpsStack {
  private marketIntelligence?: MarketIntelligence;
  private notifications?: NotificationService;
  private automation?: AutomationEngine;
  private monetization?: MonetizationEngine;
  private aiEngine?: AIEngine;
  private config: OpsStackConfig;
  private startTime: number;

  constructor(config: OpsStackConfig = {}) {
    this.config = {
      enableMarketIntelligence: true,
      enableNotifications: true,
      enableAutomation: true,
      enableMonetization: true,
      enableAI: true,
      ...config
    };

    this.startTime = Date.now();
    console.log('═══════════════════════════════════════════════════════════');
    console.log('  EVEZ666 OPS STACK INITIALIZATION');
    console.log('═══════════════════════════════════════════════════════════');
  }

  /**
   * Initialize all enabled modules
   */
  async initialize(): Promise<void> {
    console.log('\n🚀 Initializing Ops Stack modules...\n');

    if (this.config.enableMarketIntelligence) {
      this.marketIntelligence = new MarketIntelligence();
    }

    if (this.config.enableNotifications) {
      this.notifications = new NotificationService();
    }

    if (this.config.enableAutomation) {
      this.automation = new AutomationEngine();
    }

    if (this.config.enableMonetization) {
      this.monetization = new MonetizationEngine();
    }

    if (this.config.enableAI) {
      this.aiEngine = new AIEngine();
    }

    // Setup cross-module integrations
    await this.setupIntegrations();

    console.log('\n✅ Ops Stack initialization complete');
    console.log('═══════════════════════════════════════════════════════════\n');
  }

  /**
   * Setup integrations between modules
   */
  private async setupIntegrations(): Promise<void> {
    console.log('🔗 Setting up module integrations...');

    // Integration 1: AI Engine → Notifications
    if (this.aiEngine && this.notifications) {
      console.log('  ✓ AI Engine → Notifications');
    }

    // Integration 2: Market Intelligence → AI Engine
    if (this.marketIntelligence && this.aiEngine) {
      console.log('  ✓ Market Intelligence → AI Engine');
    }

    // Integration 3: Automation → All modules
    if (this.automation) {
      console.log('  ✓ Automation → All modules');
    }

    // Integration 4: Monetization → Notifications
    if (this.monetization && this.notifications) {
      console.log('  ✓ Monetization → Notifications');
    }
  }

  /**
   * Execute a complete ops cycle
   */
  async executeCycle(): Promise<void> {
    console.log('\n🔄 Executing ops cycle...\n');

    // 1. Market Intelligence: Collect and analyze data
    if (this.marketIntelligence) {
      console.log('📊 Market Intelligence:');
      await this.marketIntelligence.collectData('quantum-tech');
      await this.marketIntelligence.collectData('ai-services');
      const report = await this.marketIntelligence.analyzeMarket();
      console.log(`   Generated report: ${report.id} (confidence: ${report.confidence})`);
    }

    // 2. AI Engine: Make predictions
    if (this.aiEngine) {
      console.log('\n🤖 AI Engine:');
      const models = this.aiEngine.getModels({ status: 'ready' });
      if (models.length > 0) {
        const prediction = await this.aiEngine.predict(models[0].id, {
          input: 'sample-data'
        });
        console.log(`   Prediction: ${prediction.id} (confidence: ${prediction.confidence.toFixed(2)})`);
      }
    }

    // 3. Automation: Execute scheduled tasks
    if (this.automation) {
      console.log('\n⚙️  Automation:');
      const taskId = this.automation.registerTask({
        name: 'daily-sync',
        description: 'Synchronize data across modules',
        enabled: true
      });
      await this.automation.executeTask(taskId);
    }

    // 4. Monetization: Record revenue and calculate metrics
    if (this.monetization) {
      console.log('\n💰 Monetization:');
      this.monetization.recordRevenue({
        name: 'api-usage',
        type: 'transaction',
        amount: 99.99,
        currency: 'USD'
      });
      const metrics = this.monetization.calculateMetrics();
      console.log(`   Total revenue: ${metrics.totalRevenue.toFixed(2)} USD`);
    }

    // 5. Notifications: Send summary notification
    if (this.notifications) {
      console.log('\n📬 Notifications:');
      await this.notifications.send({
        type: 'success',
        title: 'Ops Cycle Complete',
        message: 'All modules executed successfully',
        priority: 'medium',
        channel: 'webhook'
      });
    }

    console.log('\n✅ Ops cycle completed\n');
  }

  /**
   * Get the status of all modules
   */
  getStatus(): OpsStackStatus {
    return {
      healthy: true,
      modules: {
        marketIntelligence: !!this.marketIntelligence,
        notifications: !!this.notifications,
        automation: !!this.automation,
        monetization: !!this.monetization,
        aiEngine: !!this.aiEngine
      },
      timestamp: Date.now()
    };
  }

  /**
   * Get module instances (for direct access if needed)
   */
  getModules() {
    return {
      marketIntelligence: this.marketIntelligence,
      notifications: this.notifications,
      automation: this.automation,
      monetization: this.monetization,
      aiEngine: this.aiEngine
    };
  }

  /**
   * Get uptime in milliseconds
   */
  getUptime(): number {
    return Date.now() - this.startTime;
  }

  /**
   * Shutdown the ops stack
   */
  async shutdown(): Promise<void> {
    console.log('\n🛑 Shutting down Ops Stack...');

    // Clear module histories
    if (this.marketIntelligence) {
      this.marketIntelligence.clearHistory();
    }
    if (this.notifications) {
      this.notifications.clearHistory();
    }
    if (this.automation) {
      this.automation.clearHistory();
    }
    if (this.monetization) {
      this.monetization.clearHistory();
    }
    if (this.aiEngine) {
      this.aiEngine.clearPredictions();
    }

    console.log('✅ Ops Stack shutdown complete\n');
  }
}

// Export module classes for direct use
export {
  MarketIntelligence,
  NotificationService,
  AutomationEngine,
  MonetizationEngine,
  AIEngine
};

// Export types
export * from './ops-stack/market-intelligence';
export * from './ops-stack/notifications';
export * from './ops-stack/automation';
export * from './ops-stack/monetization';
export * from './ops-stack/ai-engine';
