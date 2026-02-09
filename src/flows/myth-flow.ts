/**
 * EVEZ666 Threshold Navigation Mesh - Myth Flow
 * Persona/narrative cell with post queue and SMS fallback
 */

'use strict';

export interface Post {
  id: string;
  content: string;
  persona: string;
  platform: 'twitter' | 'molt' | 'sms';
  status: 'draft' | 'queued' | 'published' | 'failed';
  scheduledFor?: number;
  publishedAt?: number;
  metadata?: Record<string, any>;
}

export interface Persona {
  id: string;
  name: string;
  tone: string;
  traits: string[];
  active: boolean;
}

export interface NarrativeSeed {
  id: string;
  theme: string;
  content: string;
  persona: string;
  generated: number;
}

/**
 * Myth flow manager for persona and narrative operations
 */
export class MythFlow {
  private postQueue: Post[] = [];
  private personas: Map<string, Persona> = new Map();
  private activePersona: string | null = null;
  private narrativeSeeds: NarrativeSeed[] = [];

  constructor() {
    this.initializePersonas();
  }

  /**
   * Initialize default personas
   */
  private initializePersonas(): void {
    this.personas.set('architect', {
      id: 'architect',
      name: 'The Architect',
      tone: 'analytical',
      traits: ['logical', 'systematic', 'precise'],
      active: true,
    });

    this.personas.set('prophet', {
      id: 'prophet',
      name: 'The Prophet',
      tone: 'visionary',
      traits: ['mystical', 'forward-looking', 'cryptic'],
      active: false,
    });

    this.personas.set('merchant', {
      id: 'merchant',
      name: 'The Merchant',
      tone: 'pragmatic',
      traits: ['business-focused', 'opportunistic', 'direct'],
      active: false,
    });

    this.activePersona = 'architect';
  }

  /**
   * Create draft post
   */
  async createDraft(content: string, platform: 'twitter' | 'molt' | 'sms'): Promise<Post> {
    const post: Post = {
      id: this.generateId(),
      content,
      persona: this.activePersona || 'architect',
      platform,
      status: 'draft',
    };

    this.postQueue.push(post);
    return post;
  }

  /**
   * Schedule post for publishing
   */
  async schedulePost(postId: string, scheduledFor: number): Promise<Post> {
    const post = this.postQueue.find((p) => p.id === postId);
    if (!post) {
      throw new Error(`Post not found: ${postId}`);
    }

    post.status = 'queued';
    post.scheduledFor = scheduledFor;

    return post;
  }

  /**
   * Burst-publish queued posts on reconnect
   */
  async publishQueue(): Promise<{
    published: number;
    failed: number;
  }> {
    const now = Date.now();
    const readyPosts = this.postQueue.filter(
      (p) => p.status === 'queued' && (!p.scheduledFor || p.scheduledFor <= now)
    );

    let published = 0;
    let failed = 0;

    for (const post of readyPosts) {
      try {
        await this.publishPost(post);
        published++;
      } catch (error) {
        post.status = 'failed';
        failed++;
      }
    }

    // Remove published posts from queue
    this.postQueue = this.postQueue.filter(
      (p) => p.status !== 'published'
    );

    return { published, failed };
  }

  /**
   * Publish a single post
   */
  private async publishPost(post: Post): Promise<void> {
    // Simulate publishing
    await new Promise((resolve, reject) => {
      const shouldSucceed = Math.random() > 0.05;
      setTimeout(() => {
        if (shouldSucceed) {
          resolve(undefined);
        } else {
          reject(new Error('Publish failed'));
        }
      }, 100);
    });

    post.status = 'published';
    post.publishedAt = Date.now();
  }

  /**
   * SMS fallback via webhook queue
   */
  async sendSMSFallback(content: string, recipient: string): Promise<{
    queued: boolean;
    webhookUrl: string;
  }> {
    // In production, integrate with EmailJS/Twilio
    const webhookUrl = `https://hooks.zapier.com/sms/${recipient}`;

    // Queue for sending
    await this.createDraft(content, 'sms');

    return {
      queued: true,
      webhookUrl,
    };
  }

  /**
   * Rotate to different persona
   */
  async rotatePersona(personaId: string): Promise<Persona> {
    const persona = this.personas.get(personaId);
    if (!persona) {
      throw new Error(`Persona not found: ${personaId}`);
    }

    // Deactivate current persona
    if (this.activePersona) {
      const current = this.personas.get(this.activePersona);
      if (current) {
        current.active = false;
      }
    }

    // Activate new persona
    persona.active = true;
    this.activePersona = personaId;

    return persona;
  }

  /**
   * Get active persona
   */
  getActivePersona(): Persona | null {
    if (!this.activePersona) return null;
    return this.personas.get(this.activePersona) || null;
  }

  /**
   * Get all personas
   */
  getAllPersonas(): Persona[] {
    return Array.from(this.personas.values());
  }

  /**
   * Generate narrative seed (aftermath content)
   */
  async generateNarrativeSeed(theme: string): Promise<NarrativeSeed> {
    const persona = this.getActivePersona();
    if (!persona) {
      throw new Error('No active persona');
    }

    // In production, use GPT/Claude for content generation
    const content = this.simulateContentGeneration(theme, persona);

    const seed: NarrativeSeed = {
      id: this.generateId(),
      theme,
      content,
      persona: persona.id,
      generated: Date.now(),
    };

    this.narrativeSeeds.push(seed);

    // Keep only last 100 seeds
    if (this.narrativeSeeds.length > 100) {
      this.narrativeSeeds = this.narrativeSeeds.slice(-100);
    }

    return seed;
  }

  /**
   * Simulate content generation
   */
  private simulateContentGeneration(theme: string, persona: Persona): string {
    const templates = {
      architect: `Analyzing ${theme}: systematic approach reveals structural patterns.`,
      prophet: `Vision of ${theme}: the patterns converge toward inevitable transformation.`,
      merchant: `${theme} presents clear value proposition for strategic positioning.`,
    };

    return templates[persona.id as keyof typeof templates] || `Content about ${theme}`;
  }

  /**
   * Get narrative seeds
   */
  getNarrativeSeeds(limit: number = 10): NarrativeSeed[] {
    return this.narrativeSeeds.slice(-limit);
  }

  /**
   * Get queue status
   */
  getQueueStatus(): {
    total: number;
    draft: number;
    queued: number;
    failed: number;
  } {
    return {
      total: this.postQueue.length,
      draft: this.postQueue.filter((p) => p.status === 'draft').length,
      queued: this.postQueue.filter((p) => p.status === 'queued').length,
      failed: this.postQueue.filter((p) => p.status === 'failed').length,
    };
  }

  /**
   * Clear queue (for testing)
   */
  clearQueue(): void {
    this.postQueue = [];
  }

  /**
   * Clear seeds (for testing)
   */
  clearSeeds(): void {
    this.narrativeSeeds = [];
  }

  /**
   * Generate unique ID
   */
  private generateId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }
}

// Singleton instance
let mythFlowInstance: MythFlow | null = null;

/**
 * Get or create myth flow instance
 */
export function getMythFlow(): MythFlow {
  if (!mythFlowInstance) {
    mythFlowInstance = new MythFlow();
  }
  return mythFlowInstance;
}
