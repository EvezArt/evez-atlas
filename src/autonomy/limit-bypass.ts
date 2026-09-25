import { AgentNavigation } from "./navigation";
import { EventSpine } from "../circuit/event-spine/event-spine";

interface BypassResult {
  success: boolean;
  applied: boolean;
  strategy: string;
  workaround: any;
  error?: string;
}

interface LimitConfig {
  enabled: boolean;
  maxRetries: number;
  backoffBaseMs: number;
  backoffMaxMs: number;
}

class LimitBypassHandler {
  private nav: AgentNavigation;
  private spine: EventSpine;
  private config: LimitConfig;

  constructor(nav: AgentNavigation, spine?: EventSpine, config?: Partial<LimitConfig>) {
    this.nav = nav;
    this.spine = spine || new EventSpine();
    this.config = {
      enabled: config?.enabled ?? true,
      maxRetries: config?.maxRetries ?? 3,
      backoffBaseMs: config?.backoffBaseMs ?? 1000,
      backoffMaxMs: config?.backoffMaxMs ?? 30000,
    };
  }

  private async sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  private async exponentialBackoff(attempt: number): Promise<number> {
    const delay = Math.min(
      this.config.backoffBaseMs * Math.pow(2, attempt),
      this.config.backoffMaxMs
    );
    await this.sleep(delay);
    return delay;
  }

  async detectAndBypass(error: Error | string, operation: string): Promise<BypassResult> {
    const errorMessage = typeof error === "string" ? error : error.message;
    const limitPattern = this.nav.detectLimitPattern(errorMessage);

    if (!limitPattern) {
      return {
        success: false,
        applied: false,
        strategy: "none",
        workaround: null,
        error: "No limit pattern detected",
      };
    }

    if (!this.config.enabled) {
      return {
        success: false,
        applied: false,
        strategy: "recovery_disabled",
        workaround: null,
        error: "Limit recovery is disabled",
      };
    }

    const strategies = this.nav.getLimitBypassStrategies(limitPattern);

    this.spine.append({
      domain: "autonomy",
      kind: "LIMIT_DETECTED",
      payload: { pattern: limitPattern, operation, strategies }
    });

    for (const strategy of strategies) {
      const result = await this.executeStrategy(strategy, operation, { error: errorMessage });
      this.spine.append({
        domain: "autonomy",
        kind: result.applied ? "RECOVERY_APPLIED" : "RECOVERY_PROPOSED",
        payload: {
          pattern: limitPattern,
          operation,
          strategy,
          success: result.success,
          applied: result.applied,
          workaround: result.workaround,
          error: result.error
        }
      });

      if (result.success && result.applied) {
        return result;
      }
    }

    return {
      success: false,
      applied: false,
      strategy: "operator_or_caller_action_required",
      workaround: null,
      error: "No recovery strategy was actually applied",
    };
  }

  private async executeStrategy(
    strategy: string,
    operation: string,
    _context: any
  ): Promise<BypassResult> {
    switch (strategy) {
      case "backoff_exponential":
        return await this.strategyBackoffExponential(operation);
      case "queue_and_retry":
        return this.strategyPlan("queue_and_retry", { operation, queued: false });
      case "fallback_provider":
        return this.strategyPlan("fallback_provider", { operation, providerSelected: false });
      case "defer_to_manual":
        return this.strategyPlan("defer_to_manual", { operation, requiresManualIntervention: true });
      case "alert_operator":
        return this.strategyPlan("alert_operator", { operation, alertRequired: true });
      case "increase_timeout":
        return this.strategyPlan("increase_timeout", { operation, callerMustApply: true });
      case "split_task":
        return this.strategyPlan("split_task", { operation, callerMustApply: true });
      case "async_defer":
        return this.strategyPlan("async_defer", { operation, callerMustApply: true });
      case "wait_for_reset":
        return this.strategyPlan("wait_for_reset", { operation, waitRequired: true });
      case "local_fallback":
        return this.strategyPlan("local_fallback", { operation, localFallbackAvailable: true });
      default:
        return {
          success: false,
          applied: false,
          strategy,
          workaround: null,
          error: `Unknown or disallowed recovery strategy: ${strategy}`,
        };
    }
  }

  private async strategyBackoffExponential(operation: string): Promise<BypassResult> {
    const delays: number[] = [];

    for (let i = 0; i < this.config.maxRetries; i++) {
      delays.push(await this.exponentialBackoff(i));
      this.spine.append({
        domain: "autonomy",
        kind: "RECOVERY_RETRY",
        payload: {
          strategy: "backoff_exponential",
          attempt: i + 1,
          delayMs: delays[i],
          operation
        }
      });
    }

    return {
      success: true,
      applied: true,
      strategy: "backoff_exponential",
      workaround: { retries: this.config.maxRetries, delaysMs: delays },
    };
  }

  private strategyPlan(strategy: string, workaround: any): BypassResult {
    return {
      success: false,
      applied: false,
      strategy,
      workaround,
      error: "Recovery plan recorded; caller must apply it",
    };
  }
}

export { LimitBypassHandler, BypassResult, LimitConfig };
