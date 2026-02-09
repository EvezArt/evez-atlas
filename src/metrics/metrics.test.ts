/**
 * Tests for Metrics System
 */

import { Gauges, getGauges } from '../metrics/gauges';
import { Meters, getMeters } from '../metrics/meters';
import { ScopePolygon, getScopePolygon } from '../metrics/scope-polygon';

describe('Gauges', () => {
  let gauges: Gauges;

  beforeEach(() => {
    gauges = new Gauges();
    gauges.clearReadings();
  });

  describe('recordReading', () => {
    it('should record gauge reading', () => {
      const reading = gauges.recordReading('LatencyTolerance', 85);

      expect(reading.value).toBe(85);
      expect(reading.status).toBe('good');
      expect(reading.timestamp).toBeTruthy();
    });

    it('should clamp values to 0-100', () => {
      const reading1 = gauges.recordReading('LatencyTolerance', 150);
      const reading2 = gauges.recordReading('LatencyTolerance', -10);

      expect(reading1.value).toBe(100);
      expect(reading2.value).toBe(0);
    });

    it('should calculate correct status', () => {
      const optimal = gauges.recordReading('LatencyTolerance', 98);
      const good = gauges.recordReading('LatencyTolerance', 85);
      const warning = gauges.recordReading('LatencyTolerance', 65);
      const critical = gauges.recordReading('LatencyTolerance', 40);

      expect(optimal.status).toBe('optimal');
      expect(good.status).toBe('good');
      expect(warning.status).toBe('warning');
      expect(critical.status).toBe('critical');
    });
  });

  describe('gauge calculations', () => {
    it('should calculate latency tolerance', () => {
      const reading = gauges.calculateLatencyTolerance(80, 100);

      expect(reading.value).toBe(80);
      expect(gauges.getCurrentReading('LatencyTolerance')).toBeTruthy();
    });

    it('should calculate threshold lock', () => {
      const reading = gauges.calculateThresholdLock(95, 100);

      expect(reading.value).toBe(95);
    });

    it('should calculate resource flow', () => {
      const reading = gauges.calculateResourceFlow(30, 70);

      expect(reading.value).toBe(30);
    });

    it('should calculate archive depth', () => {
      const reading = gauges.calculateArchiveDepth(500, 1000);

      expect(reading.value).toBe(50);
    });

    it('should calculate persona entropy', () => {
      const reading = gauges.calculatePersonaEntropy(2, 3, 5);

      expect(reading.value).toBeGreaterThan(0);
      expect(reading.value).toBeLessThanOrEqual(100);
    });

    it('should calculate proof density', () => {
      const reading = gauges.calculateProofDensity(90, 100);

      expect(reading.value).toBe(90);
    });

    it('should calculate threat awareness', () => {
      const reading = gauges.calculateThreatAwareness(5, 100, 0.05);

      expect(reading.value).toBeGreaterThan(0);
      expect(reading.value).toBeLessThanOrEqual(100);
    });
  });

  describe('readings history', () => {
    it('should maintain history', () => {
      gauges.recordReading('LatencyTolerance', 80);
      gauges.recordReading('LatencyTolerance', 85);
      gauges.recordReading('LatencyTolerance', 90);

      const history = gauges.getHistory('LatencyTolerance', 10);

      expect(history.length).toBe(3);
      expect(history[2].value).toBe(90);
    });

    it('should limit history size', () => {
      for (let i = 0; i < 150; i++) {
        gauges.recordReading('LatencyTolerance', 80);
      }

      const history = gauges.getHistory('LatencyTolerance', 200);

      expect(history.length).toBeLessThanOrEqual(100);
    });
  });

  describe('health summary', () => {
    it('should generate health summary', () => {
      gauges.calculateLatencyTolerance(95, 100);
      gauges.calculateThresholdLock(98, 100);
      gauges.calculateResourceFlow(40, 60);

      const summary = gauges.getHealthSummary();

      expect(summary.overall).toBeTruthy();
      expect(summary.gauges.length).toBeGreaterThan(0);
      expect(summary.gauges[0]).toHaveProperty('name');
      expect(summary.gauges[0]).toHaveProperty('value');
      expect(summary.gauges[0]).toHaveProperty('status');
    });

    it('should calculate overall status correctly', () => {
      // All optimal
      gauges.calculateLatencyTolerance(98, 100);
      gauges.calculateThresholdLock(99, 100);
      const summary1 = gauges.getHealthSummary();
      expect(summary1.overall).toBe('optimal');

      // Mix of values
      gauges.clearReadings();
      gauges.calculateLatencyTolerance(70, 100);
      gauges.calculateThresholdLock(75, 100);
      const summary2 = gauges.getHealthSummary();
      expect(['good', 'warning']).toContain(summary2.overall);
    });
  });

  describe('configurations', () => {
    it('should get gauge config', () => {
      const config = gauges.getConfig('LatencyTolerance');

      expect(config).toBeTruthy();
      expect(config?.name).toBe('LatencyTolerance');
      expect(config?.target).toBe(100);
    });

    it('should get all configs', () => {
      const configs = gauges.getAllConfigs();

      expect(configs.size).toBeGreaterThan(0);
      expect(configs.has('LatencyTolerance')).toBe(true);
    });
  });
});

describe('Meters', () => {
  let meters: Meters;

  beforeEach(() => {
    meters = new Meters();
    meters.clearReadings();
  });

  describe('recordReading', () => {
    it('should record meter reading', () => {
      const reading = meters.recordReading('NavVelocity', 10);

      expect(reading.value).toBe(10);
      expect(reading.trend).toBe('stable');
      expect(reading.timestamp).toBeTruthy();
    });

    it('should calculate trend', () => {
      meters.recordReading('NavVelocity', 10);
      meters.recordReading('NavVelocity', 12);
      meters.recordReading('NavVelocity', 14);
      const reading = meters.recordReading('NavVelocity', 20);

      expect(reading.trend).toBe('increasing');
    });

    it('should detect decreasing trend', () => {
      meters.recordReading('NavVelocity', 20);
      meters.recordReading('NavVelocity', 18);
      meters.recordReading('NavVelocity', 16);
      const reading = meters.recordReading('NavVelocity', 10);

      expect(reading.trend).toBe('decreasing');
    });
  });

  describe('meter calculations', () => {
    it('should calculate navigation velocity', () => {
      const reading = meters.calculateNavVelocity(10, 0.9);

      expect(reading.value).toBe(9);
    });

    it('should calculate gate density', () => {
      const reading = meters.calculateGateDensity(4, 4, 0.95);

      expect(reading.value).toBeGreaterThan(0);
    });

    it('should calculate flywheel momentum', () => {
      const reading = meters.calculateFlywheelMomentum(1000, 1000, 1000);

      expect(reading.value).toBeGreaterThan(0);
      expect(reading.value).toBeLessThanOrEqual(100);
    });

    it('should detect balanced revenue streams', () => {
      const balanced = meters.calculateFlywheelMomentum(333, 333, 334);
      expect(balanced.value).toBeGreaterThan(90);

      const unbalanced = meters.calculateFlywheelMomentum(900, 50, 50);
      expect(unbalanced.value).toBeLessThan(90);
    });
  });

  describe('trend summary', () => {
    it('should generate trend summary', () => {
      meters.recordReading('NavVelocity', 10);
      meters.recordReading('NavVelocity', 12);
      meters.recordReading('NavVelocity', 14);
      meters.recordReading('NavVelocity', 20);

      meters.calculateGateDensity(4, 4, 0.95);
      meters.calculateFlywheelMomentum(1000, 1000, 1000);

      const summary = meters.getTrendSummary();

      expect(summary).toHaveProperty('increasing');
      expect(summary).toHaveProperty('stable');
      expect(summary).toHaveProperty('decreasing');
      expect(Array.isArray(summary.increasing)).toBe(true);
    });
  });

  describe('configurations', () => {
    it('should get meter config', () => {
      const config = meters.getConfig('NavVelocity');

      expect(config).toBeTruthy();
      expect(config?.name).toBe('NavVelocity');
      expect(config?.unit).toBeTruthy();
    });

    it('should get all configs', () => {
      const configs = meters.getAllConfigs();

      expect(configs.size).toBeGreaterThan(0);
      expect(configs.has('NavVelocity')).toBe(true);
    });
  });
});

describe('ScopePolygon', () => {
  let polygon: ScopePolygon;

  beforeEach(() => {
    polygon = new ScopePolygon();
    polygon.clearHistory();
  });

  describe('calculatePolygon', () => {
    it('should calculate polygon from metrics', () => {
      const data = polygon.calculatePolygon({
        archiveDepth: 80,
        personaEntropy: 70,
        proofDensity: 90,
        gateDensity: 85,
        threatAwareness: 75,
        mythFlowRate: 65,
        latencyTolerance: 95,
        resourceFlowRatio: 50,
      });

      expect(data.axes).toHaveProperty('Archive');
      expect(data.axes).toHaveProperty('Persona');
      expect(data.axes).toHaveProperty('Proof');
      expect(data.axes).toHaveProperty('Gate');
      expect(data.axes).toHaveProperty('Threat');
      expect(data.axes).toHaveProperty('Myth');
      expect(data.axes).toHaveProperty('NavLatency');
      expect(data.axes).toHaveProperty('ResourceLock');

      expect(data.area).toBeGreaterThan(0);
      expect(data.area).toBeLessThanOrEqual(100);
      expect(data.balance).toBeGreaterThan(0);
      expect(data.balance).toBeLessThanOrEqual(100);
    });

    it('should scale values correctly', () => {
      const data = polygon.calculatePolygon({
        archiveDepth: 100,
        personaEntropy: 0,
        proofDensity: 50,
        gateDensity: 50,
        threatAwareness: 50,
        mythFlowRate: 50,
        latencyTolerance: 50,
        resourceFlowRatio: 50,
      });

      expect(data.axes.Archive).toBe(10);
      expect(data.axes.Persona).toBe(0);
      expect(data.axes.Proof).toBe(5);
    });

    it('should calculate balance correctly', () => {
      // Balanced polygon (all axes same)
      const balanced = polygon.calculatePolygon({
        archiveDepth: 80,
        personaEntropy: 80,
        proofDensity: 80,
        gateDensity: 80,
        threatAwareness: 80,
        mythFlowRate: 80,
        latencyTolerance: 80,
        resourceFlowRatio: 80,
      });

      // Unbalanced polygon
      const unbalanced = polygon.calculatePolygon({
        archiveDepth: 100,
        personaEntropy: 10,
        proofDensity: 100,
        gateDensity: 10,
        threatAwareness: 100,
        mythFlowRate: 10,
        latencyTolerance: 100,
        resourceFlowRatio: 10,
      });

      expect(balanced.balance).toBeGreaterThan(unbalanced.balance);
    });
  });

  describe('export formats', () => {
    it('should export ASCII art', () => {
      const data = polygon.calculatePolygon({
        archiveDepth: 80,
        personaEntropy: 70,
        proofDensity: 90,
        gateDensity: 85,
        threatAwareness: 75,
        mythFlowRate: 65,
        latencyTolerance: 95,
        resourceFlowRatio: 50,
      });

      const ascii = polygon.exportPolygonASCII(data);

      expect(ascii).toContain('EVEZ666 POLYGON');
      expect(ascii).toContain('Archive');
      expect(ascii).toContain('Area:');
      expect(ascii).toContain('Balance:');
    });

    it('should export JSON', () => {
      const data = polygon.calculatePolygon({
        archiveDepth: 80,
        personaEntropy: 70,
        proofDensity: 90,
        gateDensity: 85,
        threatAwareness: 75,
        mythFlowRate: 65,
        latencyTolerance: 95,
        resourceFlowRatio: 50,
      });

      const json = polygon.exportPolygonJSON(data);
      const parsed = JSON.parse(json);

      expect(parsed.axes).toBeTruthy();
      expect(parsed.area).toBeTruthy();
      expect(parsed.balance).toBeTruthy();
    });

    it('should export SVG', () => {
      const data = polygon.calculatePolygon({
        archiveDepth: 80,
        personaEntropy: 70,
        proofDensity: 90,
        gateDensity: 85,
        threatAwareness: 75,
        mythFlowRate: 65,
        latencyTolerance: 95,
        resourceFlowRatio: 50,
      });

      const svg = polygon.exportPolygonSVG(data);

      expect(svg).toContain('<svg');
      expect(svg).toContain('polygon');
      expect(svg).toContain('EVEZ666 POLYGON');
    });
  });

  describe('history', () => {
    it('should maintain polygon history', () => {
      polygon.calculatePolygon({
        archiveDepth: 80,
        personaEntropy: 70,
        proofDensity: 90,
        gateDensity: 85,
        threatAwareness: 75,
        mythFlowRate: 65,
        latencyTolerance: 95,
        resourceFlowRatio: 50,
      });

      polygon.calculatePolygon({
        archiveDepth: 85,
        personaEntropy: 75,
        proofDensity: 92,
        gateDensity: 88,
        threatAwareness: 78,
        mythFlowRate: 68,
        latencyTolerance: 96,
        resourceFlowRatio: 52,
      });

      const history = polygon.getHistory(10);

      expect(history.length).toBe(2);
    });

    it('should get current polygon', () => {
      const data = polygon.calculatePolygon({
        archiveDepth: 80,
        personaEntropy: 70,
        proofDensity: 90,
        gateDensity: 85,
        threatAwareness: 75,
        mythFlowRate: 65,
        latencyTolerance: 95,
        resourceFlowRatio: 50,
      });

      const current = polygon.getCurrentPolygon();

      expect(current).toBeTruthy();
      expect(current?.timestamp).toBe(data.timestamp);
    });
  });

  describe('comparePolygons', () => {
    it('should compare two polygons', () => {
      const data1 = polygon.calculatePolygon({
        archiveDepth: 80,
        personaEntropy: 70,
        proofDensity: 90,
        gateDensity: 85,
        threatAwareness: 75,
        mythFlowRate: 65,
        latencyTolerance: 95,
        resourceFlowRatio: 50,
      });

      const data2 = polygon.calculatePolygon({
        archiveDepth: 85,
        personaEntropy: 75,
        proofDensity: 92,
        gateDensity: 88,
        threatAwareness: 78,
        mythFlowRate: 68,
        latencyTolerance: 96,
        resourceFlowRatio: 52,
      });

      const comparison = polygon.comparePolygons(data1, data2);

      expect(comparison.areaDiff).toBeTruthy();
      expect(comparison.balanceDiff).toBeTruthy();
      expect(comparison.axisDiffs).toHaveProperty('Archive');
      expect(comparison.axisDiffs.Archive).toBeGreaterThan(0);
    });
  });
});

describe('Singleton instances', () => {
  it('should return same Gauges instance', () => {
    const gauges1 = getGauges();
    const gauges2 = getGauges();
    expect(gauges1).toBe(gauges2);
  });

  it('should return same Meters instance', () => {
    const meters1 = getMeters();
    const meters2 = getMeters();
    expect(meters1).toBe(meters2);
  });

  it('should return same ScopePolygon instance', () => {
    const polygon1 = getScopePolygon();
    const polygon2 = getScopePolygon();
    expect(polygon1).toBe(polygon2);
  });
});
