-- EVEZ666 Threshold Navigation Mesh - Database Schema
-- Navigation mesh tables for PostgreSQL

-- Navigation logs table
CREATE TABLE IF NOT EXISTS nav_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  path_used TEXT NOT NULL,
  threshold TEXT NOT NULL CHECK (threshold IN ('wealth', 'info', 'myth')),
  latency_ms INTEGER,
  breach_attempts INTEGER DEFAULT 0,
  route_status TEXT CHECK (route_status IN ('primary', 'failover', 'local')),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_nav_logs_threshold ON nav_logs(threshold);
CREATE INDEX IF NOT EXISTS idx_nav_logs_created_at ON nav_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_nav_logs_route_status ON nav_logs(route_status);

-- Gate state table
CREATE TABLE IF NOT EXISTS gate_state (
  cell_id TEXT PRIMARY KEY,
  jwt_hash TEXT,
  anomaly_count INTEGER DEFAULT 0,
  lockdown BOOLEAN DEFAULT FALSE,
  last_validated TIMESTAMPTZ,
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_gate_state_lockdown ON gate_state(lockdown) WHERE lockdown = TRUE;
CREATE INDEX IF NOT EXISTS idx_gate_state_anomaly ON gate_state(anomaly_count) WHERE anomaly_count > 0;

-- Resource cache table
CREATE TABLE IF NOT EXISTS resource_cache (
  key TEXT PRIMARY KEY,
  threshold TEXT NOT NULL,
  payload JSONB,
  cached_at TIMESTAMPTZ DEFAULT NOW(),
  expires_at TIMESTAMPTZ,
  sync_status TEXT DEFAULT 'pending' CHECK (sync_status IN ('pending', 'synced', 'conflict'))
);

CREATE INDEX IF NOT EXISTS idx_resource_cache_threshold ON resource_cache(threshold);
CREATE INDEX IF NOT EXISTS idx_resource_cache_sync_status ON resource_cache(sync_status);
CREATE INDEX IF NOT EXISTS idx_resource_cache_expires_at ON resource_cache(expires_at);

-- Circuit events table (for audit bridge)
CREATE TABLE IF NOT EXISTS circuit_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  event_type TEXT NOT NULL CHECK (event_type IN ('revenue', 'payout', 'gate', 'flow', 'anomaly')),
  severity TEXT NOT NULL CHECK (severity IN ('info', 'warning', 'error', 'critical')),
  source TEXT NOT NULL,
  data JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_circuit_events_type ON circuit_events(event_type);
CREATE INDEX IF NOT EXISTS idx_circuit_events_severity ON circuit_events(severity);
CREATE INDEX IF NOT EXISTS idx_circuit_events_created_at ON circuit_events(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_circuit_events_source ON circuit_events(source);

-- Metrics table
CREATE TABLE IF NOT EXISTS metrics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  metric_name TEXT NOT NULL,
  metric_type TEXT NOT NULL CHECK (metric_type IN ('gauge', 'meter', 'polygon')),
  value NUMERIC NOT NULL,
  metadata JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_metrics_name ON metrics(metric_name);
CREATE INDEX IF NOT EXISTS idx_metrics_type ON metrics(metric_type);
CREATE INDEX IF NOT EXISTS idx_metrics_created_at ON metrics(created_at DESC);

-- Views for analytics

-- Latency tolerance view
CREATE OR REPLACE VIEW v_latency_tolerance AS
SELECT 
  DATE_TRUNC('hour', created_at) as hour,
  COUNT(*) as total_ops,
  COUNT(*) FILTER (WHERE route_status IN ('local', 'failover')) as offline_capable,
  ROUND(100.0 * COUNT(*) FILTER (WHERE route_status IN ('local', 'failover')) / COUNT(*), 2) as tolerance_pct
FROM nav_logs
GROUP BY hour
ORDER BY hour DESC;

-- Gate breach view
CREATE OR REPLACE VIEW v_gate_breaches AS
SELECT 
  cell_id,
  anomaly_count,
  lockdown,
  last_validated,
  AGE(NOW(), last_validated) as time_since_validation
FROM gate_state
WHERE anomaly_count > 0 OR lockdown = TRUE
ORDER BY anomaly_count DESC;

-- Resource sync view
CREATE OR REPLACE VIEW v_resource_sync_status AS
SELECT 
  threshold,
  sync_status,
  COUNT(*) as count,
  MIN(cached_at) as oldest_cached,
  MAX(cached_at) as newest_cached
FROM resource_cache
GROUP BY threshold, sync_status;

-- Circuit events summary view
CREATE OR REPLACE VIEW v_circuit_events_summary AS
SELECT 
  DATE_TRUNC('hour', created_at) as hour,
  event_type,
  severity,
  COUNT(*) as event_count
FROM circuit_events
GROUP BY hour, event_type, severity
ORDER BY hour DESC, event_count DESC;

-- Comments for documentation
COMMENT ON TABLE nav_logs IS 'Navigation path logs with latency and failover tracking';
COMMENT ON TABLE gate_state IS 'Zero-trust gate state for each cell with anomaly tracking';
COMMENT ON TABLE resource_cache IS 'Offline resource cache with sync status';
COMMENT ON TABLE circuit_events IS 'Audit events from profit circuit and flows';
COMMENT ON TABLE metrics IS 'Time-series metrics for gauges, meters, and polygons';

COMMENT ON COLUMN nav_logs.threshold IS 'Threshold type: wealth, info, or myth';
COMMENT ON COLUMN nav_logs.route_status IS 'Route used: primary, failover, or local';
COMMENT ON COLUMN gate_state.lockdown IS 'Whether cell is in lockdown mode';
COMMENT ON COLUMN resource_cache.sync_status IS 'Sync status: pending, synced, or conflict';
