/**
 * Tests for Resource Flows
 */

import { WealthFlow, getWealthFlow } from '../flows/wealth-flow';
import { InfoFlow, getInfoFlow } from '../flows/info-flow';
import { MythFlow, getMythFlow } from '../flows/myth-flow';
import { CircuitAuditBridge, getCircuitAuditBridge } from '../flows/circuit-audit-bridge';

describe('WealthFlow', () => {
  let flow: WealthFlow;

  beforeEach(() => {
    flow = new WealthFlow();
  });

  describe('processRevenue', () => {
    it('should process revenue event', async () => {
      const event = {
        id: 'test-1',
        amount: 100,
        currency: 'USD',
        processor: 'stripe' as const,
        status: 'pending' as const,
        timestamp: Date.now(),
      };

      const result = await flow.processRevenue(event);

      expect(result.status).toBe('completed');
      expect(['stripe', 'local-sim']).toContain(result.processor);
    });

    it('should failover to local sim on processor failure', async () => {
      // Process multiple events to trigger failover
      const events = [];
      for (let i = 0; i < 20; i++) {
        const event = {
          id: `test-${i}`,
          amount: 100,
          currency: 'USD',
          processor: 'stripe' as const,
          status: 'pending' as const,
          timestamp: Date.now(),
        };
        events.push(flow.processRevenue(event));
      }

      const results = await Promise.all(events);
      const localSims = results.filter(r => r.processor === 'local-sim');

      // Some should fail over to local sim
      expect(localSims.length).toBeGreaterThan(0);
    });
  });

  describe('calculatePayout', () => {
    it('should calculate payout with fees', async () => {
      const payout = await flow.calculatePayout(1000, 'stripe');

      expect(payout.gross).toBe(1000);
      expect(payout.fees).toBeGreaterThan(0);
      expect(payout.net).toBeLessThan(1000);
      expect(payout.cached).toBe(false);
    });

    it('should return cached payout', async () => {
      const payout1 = await flow.calculatePayout(1000, 'stripe');
      const payout2 = await flow.calculatePayout(1000, 'stripe');

      expect(payout2.cached).toBe(true);
      expect(payout2.net).toBe(payout1.net);
    });

    it('should calculate zero fees for local sim', async () => {
      const payout = await flow.calculatePayout(1000, 'local-sim');

      expect(payout.fees).toBe(0);
      expect(payout.net).toBe(1000);
    });
  });

  describe('queue operations', () => {
    it('should queue and process revenue events', async () => {
      const event = {
        id: 'test-1',
        amount: 100,
        currency: 'USD',
        processor: 'stripe' as const,
        status: 'pending' as const,
        timestamp: Date.now(),
      };

      flow.queueRevenue(event);

      const status = flow.getQueueStatus();
      expect(status.length).toBe(1);
      expect(status.totalAmount).toBe(100);

      const result = await flow.processQueue();
      expect(result.processed).toBeGreaterThan(0);
    });
  });

  describe('partitionRevenueStreams', () => {
    it('should partition by revenue type', () => {
      const events = [
        {
          id: '1',
          amount: 100,
          currency: 'USD',
          processor: 'stripe' as const,
          status: 'completed' as const,
          timestamp: Date.now(),
          metadata: { type: 'digital' },
        },
        {
          id: '2',
          amount: 200,
          currency: 'USD',
          processor: 'stripe' as const,
          status: 'completed' as const,
          timestamp: Date.now(),
          metadata: { type: 'service' },
        },
        {
          id: '3',
          amount: 300,
          currency: 'USD',
          processor: 'stripe' as const,
          status: 'completed' as const,
          timestamp: Date.now(),
          metadata: { type: 'tool' },
        },
      ];

      const partitioned = flow.partitionRevenueStreams(events);

      expect(partitioned.digital).toHaveLength(1);
      expect(partitioned.service).toHaveLength(1);
      expect(partitioned.tool).toHaveLength(1);
    });
  });
});

describe('InfoFlow', () => {
  let flow: InfoFlow;

  beforeEach(() => {
    flow = new InfoFlow();
    flow.clearDocuments();
  });

  describe('document operations', () => {
    it('should add and retrieve document', async () => {
      const doc = {
        id: 'doc-1',
        title: 'Test Document',
        content: 'This is test content',
        tags: ['test', 'sample'],
        source: 'manual',
        timestamp: Date.now(),
      };

      await flow.addDocument(doc);
      const retrieved = await flow.getDocument('doc-1');

      expect(retrieved).toBeTruthy();
      expect(retrieved?.title).toBe('Test Document');
    });

    it('should search archive', async () => {
      const docs = [
        {
          id: 'doc-1',
          title: 'Quantum Computing',
          content: 'Introduction to quantum computing concepts',
          tags: ['quantum', 'computing'],
          source: 'manual',
          timestamp: Date.now(),
        },
        {
          id: 'doc-2',
          title: 'Machine Learning',
          content: 'Basics of machine learning algorithms',
          tags: ['ml', 'ai'],
          source: 'manual',
          timestamp: Date.now(),
        },
      ];

      for (const doc of docs) {
        await flow.addDocument(doc);
      }

      const results = await flow.searchArchive('quantum');

      expect(results.length).toBeGreaterThan(0);
      expect(results[0].document.title).toContain('Quantum');
      expect(results[0].score).toBeGreaterThan(0);
    });
  });

  describe('RSS operations', () => {
    it('should fetch and cache RSS feed', async () => {
      const url = 'https://example.com/feed';
      const entries = await flow.fetchRSSFeed(url);

      expect(entries).toBeTruthy();
      expect(Array.isArray(entries)).toBe(true);

      const cached = flow.getCachedFeeds();
      expect(cached).toContain(url);
    });
  });

  describe('batch import', () => {
    it('should batch import documents', async () => {
      const docs = [
        {
          id: 'doc-1',
          title: 'Doc 1',
          content: 'Content 1',
          tags: ['test'],
          source: 'batch',
          timestamp: Date.now(),
        },
        {
          id: 'doc-2',
          title: 'Doc 2',
          content: 'Content 2',
          tags: ['test'],
          source: 'batch',
          timestamp: Date.now(),
        },
      ];

      const result = await flow.batchImport(docs);

      expect(result.imported).toBe(2);
      expect(result.failed).toBe(0);
    });
  });

  describe('statistics', () => {
    it('should calculate archive statistics', async () => {
      const docs = [
        {
          id: 'doc-1',
          title: 'Doc 1',
          content: 'Content',
          tags: ['tag1', 'tag2'],
          source: 'source1',
          timestamp: Date.now(),
        },
        {
          id: 'doc-2',
          title: 'Doc 2',
          content: 'Content',
          tags: ['tag2', 'tag3'],
          source: 'source2',
          timestamp: Date.now(),
        },
      ];

      for (const doc of docs) {
        await flow.addDocument(doc);
      }

      const stats = flow.getStatistics();

      expect(stats.totalDocuments).toBe(2);
      expect(stats.totalTags).toBe(3);
      expect(stats.sources).toHaveLength(2);
    });
  });
});

describe('MythFlow', () => {
  let flow: MythFlow;

  beforeEach(() => {
    flow = new MythFlow();
    flow.clearQueue();
  });

  describe('post operations', () => {
    it('should create draft post', async () => {
      const post = await flow.createDraft('Test post content', 'twitter');

      expect(post.content).toBe('Test post content');
      expect(post.platform).toBe('twitter');
      expect(post.status).toBe('draft');
    });

    it('should schedule post', async () => {
      const post = await flow.createDraft('Scheduled post', 'molt');
      const scheduledTime = Date.now() + 3600000; // 1 hour from now

      const scheduled = await flow.schedulePost(post.id, scheduledTime);

      expect(scheduled.status).toBe('queued');
      expect(scheduled.scheduledFor).toBe(scheduledTime);
    });

    it('should publish queued posts', async () => {
      const post = await flow.createDraft('Ready to publish', 'twitter');
      await flow.schedulePost(post.id, Date.now() - 1000); // Already due

      const result = await flow.publishQueue();

      expect(result.published).toBeGreaterThan(0);
    });
  });

  describe('persona operations', () => {
    it('should rotate personas', async () => {
      const persona = await flow.rotatePersona('prophet');

      expect(persona.id).toBe('prophet');
      expect(persona.active).toBe(true);
    });

    it('should get active persona', () => {
      const persona = flow.getActivePersona();

      expect(persona).toBeTruthy();
      expect(persona?.active).toBe(true);
    });

    it('should get all personas', () => {
      const personas = flow.getAllPersonas();

      expect(personas.length).toBeGreaterThan(0);
      expect(personas.every(p => p.id)).toBe(true);
    });
  });

  describe('narrative operations', () => {
    it('should generate narrative seed', async () => {
      const seed = await flow.generateNarrativeSeed('transformation');

      expect(seed.theme).toBe('transformation');
      expect(seed.content).toBeTruthy();
      expect(seed.persona).toBeTruthy();
    });

    it('should retrieve narrative seeds', async () => {
      await flow.generateNarrativeSeed('theme1');
      await flow.generateNarrativeSeed('theme2');

      const seeds = flow.getNarrativeSeeds(10);

      expect(seeds.length).toBe(2);
    });
  });

  describe('SMS fallback', () => {
    it('should queue SMS fallback', async () => {
      const result = await flow.sendSMSFallback('Test message', '+1234567890');

      expect(result.queued).toBe(true);
      expect(result.webhookUrl).toBeTruthy();
    });
  });
});

describe('CircuitAuditBridge', () => {
  let bridge: CircuitAuditBridge;

  beforeEach(() => {
    bridge = new CircuitAuditBridge();
    bridge.clearBuffer();
  });

  describe('event creation', () => {
    it('should create revenue event', () => {
      const event = bridge.createRevenueEvent(1000, 'stripe', { test: true });

      expect(event.type).toBe('revenue');
      expect(event.data.amount).toBe(1000);
      expect(event.data.processor).toBe('stripe');
    });

    it('should create gate event', () => {
      const event = bridge.createGateEvent('archive', true, 'Access granted');

      expect(event.type).toBe('gate');
      expect(event.data.allowed).toBe(true);
      expect(event.severity).toBe('info');
    });

    it('should create anomaly event', () => {
      const event = bridge.createAnomalyEvent('revenue', 85, 'lockdown');

      expect(event.type).toBe('anomaly');
      expect(event.severity).toBe('critical');
      expect(event.data.severity).toBe(85);
    });
  });

  describe('event retrieval', () => {
    it('should emit and retrieve events', () => {
      const event = bridge.createRevenueEvent(100, 'stripe');
      bridge.emitCircuitEvent(event);

      const recent = bridge.getRecentEvents(10);

      expect(recent).toContain(event);
    });

    it('should filter events by type', () => {
      bridge.emitCircuitEvent(bridge.createRevenueEvent(100, 'stripe'));
      bridge.emitCircuitEvent(bridge.createGateEvent('archive', true, 'OK'));

      const revenueEvents = bridge.getRecentEvents(10, 'revenue');

      expect(revenueEvents.every(e => e.type === 'revenue')).toBe(true);
    });

    it('should get events by severity', () => {
      bridge.emitCircuitEvent(bridge.createAnomalyEvent('revenue', 90, 'lockdown'));
      bridge.emitCircuitEvent(bridge.createGateEvent('archive', true, 'OK'));

      const critical = bridge.getEventsBySeverity('critical');

      expect(critical.length).toBeGreaterThan(0);
      expect(critical.every(e => e.severity === 'critical')).toBe(true);
    });
  });

  describe('statistics', () => {
    it('should calculate event statistics', () => {
      bridge.emitCircuitEvent(bridge.createRevenueEvent(100, 'stripe'));
      bridge.emitCircuitEvent(bridge.createRevenueEvent(200, 'stripe'));
      bridge.emitCircuitEvent(bridge.createGateEvent('archive', true, 'OK'));

      const stats = bridge.getStatistics();

      expect(stats.total).toBe(3);
      expect(stats.byType.revenue).toBe(2);
      expect(stats.byType.gate).toBe(1);
    });
  });

  describe('audit conversion', () => {
    it('should convert to audit entry', () => {
      const event = bridge.createRevenueEvent(100, 'stripe');
      const auditEntry = bridge.toAuditEntry(event);

      expect(auditEntry.level).toBe('INFO');
      expect(auditEntry.source).toBe('wealth-flow');
      expect(auditEntry.message).toBeTruthy();
    });
  });
});

describe('Singleton instances', () => {
  it('should return same WealthFlow instance', () => {
    const flow1 = getWealthFlow();
    const flow2 = getWealthFlow();
    expect(flow1).toBe(flow2);
  });

  it('should return same InfoFlow instance', () => {
    const flow1 = getInfoFlow();
    const flow2 = getInfoFlow();
    expect(flow1).toBe(flow2);
  });

  it('should return same MythFlow instance', () => {
    const flow1 = getMythFlow();
    const flow2 = getMythFlow();
    expect(flow1).toBe(flow2);
  });

  it('should return same CircuitAuditBridge instance', () => {
    const bridge1 = getCircuitAuditBridge();
    const bridge2 = getCircuitAuditBridge();
    expect(bridge1).toBe(bridge2);
  });
});
