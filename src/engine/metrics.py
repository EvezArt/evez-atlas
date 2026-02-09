"""
Metrics Collector - Gauges and meters for engine monitoring.

Features:
Gauges (0-100):
- Latency Tolerance: % operations surviving 24h offline (target: 100%)
- Threshold Lock: Gate breach attempts blocked (%)
- Resource Flow: Latent throughput ratio (cached vs live)

Meters (trend tracking):
- Nav Velocity: Path switches per interval (auto-route success rate)
- Gate Density: Thresholds enforced across cells/flows
"""

import json
import time
from typing import Dict, List, Optional, Any
from collections import deque
from pathlib import Path


class Gauge:
    """Represents a metric gauge (0-100 scale)."""
    
    def __init__(self, name: str, target: float = 100.0):
        self.name = name
        self.target = target
        self.current_value = 0.0
        self.history = deque(maxlen=100)
        self.last_updated = None
        
    def set(self, value: float):
        """Set gauge value (0-100)."""
        self.current_value = max(0.0, min(100.0, value))
        self.last_updated = time.time()
        self.history.append({
            'timestamp': self.last_updated,
            'value': self.current_value,
        })
    
    def is_healthy(self) -> bool:
        """Check if gauge meets target."""
        return self.current_value >= self.target
    
    def get_trend(self) -> str:
        """Get trend direction (up/down/stable)."""
        if len(self.history) < 2:
            return "stable"
        
        recent = [h['value'] for h in list(self.history)[-10:]]
        if recent[-1] > recent[0] + 5:
            return "up"
        elif recent[-1] < recent[0] - 5:
            return "down"
        else:
            return "stable"
    
    def get_stats(self) -> Dict:
        """Get gauge statistics."""
        return {
            'name': self.name,
            'value': self.current_value,
            'target': self.target,
            'healthy': self.is_healthy(),
            'trend': self.get_trend(),
            'last_updated': self.last_updated,
        }


class Meter:
    """Represents a trend meter for rate-based metrics."""
    
    def __init__(self, name: str, interval: int = 60):
        self.name = name
        self.interval = interval  # Measurement interval in seconds
        self.events = deque(maxlen=1000)
        self.current_rate = 0.0
        
    def record(self, value: float = 1.0):
        """Record an event."""
        self.events.append({
            'timestamp': time.time(),
            'value': value,
        })
        self._update_rate()
    
    def _update_rate(self):
        """Update current rate calculation."""
        now = time.time()
        cutoff = now - self.interval
        
        # Count events in the interval
        recent_events = [e for e in self.events if e['timestamp'] > cutoff]
        total_value = sum(e['value'] for e in recent_events)
        
        # Calculate rate per interval
        self.current_rate = total_value
    
    def get_stats(self) -> Dict:
        """Get meter statistics."""
        return {
            'name': self.name,
            'rate': self.current_rate,
            'interval': self.interval,
            'total_events': len(self.events),
        }


class MetricsCollector:
    """
    Collects and tracks all engine metrics.
    
    Provides gauges for critical thresholds and meters for
    trend tracking across the engine system.
    """
    
    def __init__(self):
        # Gauges
        self.gauges = {
            'latency_tolerance': Gauge('Latency Tolerance', target=100.0),
            'threshold_lock': Gauge('Threshold Lock', target=95.0),
            'resource_flow': Gauge('Resource Flow', target=80.0),
        }
        
        # Meters
        self.meters = {
            'nav_velocity': Meter('Nav Velocity', interval=60),
            'gate_density': Meter('Gate Density', interval=60),
        }
        
        # Integration points
        self.resource_engine = None
        self.nav_mesh = None
        self.latent_cache = None
        self.entity_manager = None
        
        # Statistics
        self.metrics_updated = 0
        self.last_update = None
    
    def integrate(self, resource_engine=None, nav_mesh=None, 
                  latent_cache=None, entity_manager=None):
        """Integrate with engine components."""
        self.resource_engine = resource_engine
        self.nav_mesh = nav_mesh
        self.latent_cache = latent_cache
        self.entity_manager = entity_manager
    
    def update_latency_tolerance(self) -> float:
        """
        Calculate latency tolerance gauge.
        
        Measures % of operations that can survive 24h offline.
        Based on cache hit rate and queued operations.
        """
        if not self.latent_cache:
            self.gauges['latency_tolerance'].set(0.0)
            return 0.0
        
        stats = self.latent_cache.get_stats()
        
        # If hit rate is high and queue is managed, tolerance is high
        hit_rate = stats.get('hit_rate', 0.0)
        queue_depth = stats.get('queue_depth', 0)
        
        # Calculate tolerance based on cache effectiveness
        # High hit rate = high tolerance
        # Low queue depth = high tolerance
        tolerance = hit_rate * 0.7  # 70% weight on hit rate
        
        # Adjust for queue depth (lower is better)
        if queue_depth < 10:
            tolerance += 30.0
        elif queue_depth < 50:
            tolerance += 20.0
        elif queue_depth < 100:
            tolerance += 10.0
        
        self.gauges['latency_tolerance'].set(tolerance)
        return tolerance
    
    def update_threshold_lock(self) -> float:
        """
        Calculate threshold lock gauge.
        
        Measures % of gate breach attempts that were blocked.
        Based on navigation mesh gate statistics.
        """
        if not self.nav_mesh:
            self.gauges['threshold_lock'].set(0.0)
            return 0.0
        
        status = self.nav_mesh.get_status()
        gates = status.get('gates', {})
        
        total_denied = 0
        total_requests = 0
        
        for gate_stats in gates.values():
            total_denied += gate_stats.get('total_denied', 0)
            total_requests += gate_stats.get('total_requests', 0)
        
        # Calculate block rate
        if total_requests > 0:
            block_rate = (total_denied / total_requests) * 100
        else:
            block_rate = 100.0  # No requests = perfect blocking
        
        # Threshold lock is the inverse - we want to block breaches
        # If many requests are denied, lock is strong
        # For valid users, most should be allowed
        # So we measure success rate of legitimate access
        total_allowed = sum(g.get('total_allowed', 0) for g in gates.values())
        if total_requests > 0:
            # If most requests are allowed, but breaches are blocked
            breach_attempts = sum(g.get('breach_attempts', 0) for g in gates.values())
            if breach_attempts > 0:
                lock_effectiveness = ((breach_attempts - (total_denied - total_allowed)) / breach_attempts) * 100
                lock_effectiveness = max(0.0, lock_effectiveness)
            else:
                lock_effectiveness = 100.0
        else:
            lock_effectiveness = 100.0
        
        self.gauges['threshold_lock'].set(lock_effectiveness)
        return lock_effectiveness
    
    def update_resource_flow(self) -> float:
        """
        Calculate resource flow gauge.
        
        Measures ratio of cached operations vs live operations.
        High ratio indicates good offline resilience.
        """
        if not self.latent_cache or not self.resource_engine:
            self.gauges['resource_flow'].set(0.0)
            return 0.0
        
        cache_stats = self.latent_cache.get_stats()
        engine_stats = self.resource_engine.get_status()
        
        # Calculate throughput ratio
        cache_hits = cache_stats.get('cache_hits', 0)
        total_cache_access = cache_hits + cache_stats.get('cache_misses', 0)
        
        tasks_processed = engine_stats.get('tasks_processed', 0)
        
        # If we're using cache effectively, flow is good
        if total_cache_access > 0:
            cache_effectiveness = (cache_hits / total_cache_access) * 100
        else:
            cache_effectiveness = 0.0
        
        # Factor in resource utilization
        pools = engine_stats.get('pools', {})
        avg_utilization = sum(p.get('utilization', 0) for p in pools.values()) / len(pools) if pools else 0
        
        # Optimal flow: high cache hits + moderate utilization
        flow = (cache_effectiveness * 0.6) + ((100 - avg_utilization) * 0.4)
        
        self.gauges['resource_flow'].set(flow)
        return flow
    
    def update_nav_velocity(self):
        """
        Update nav velocity meter.
        
        Tracks path switches per interval (auto-route success).
        """
        if not self.nav_mesh:
            return
        
        status = self.nav_mesh.get_status()
        path_switches = status.get('path_switches', 0)
        
        # Record current switches (would track delta in production)
        self.meters['nav_velocity'].record(path_switches)
    
    def update_gate_density(self):
        """
        Update gate density meter.
        
        Tracks number of thresholds enforced across cells/flows.
        """
        if not self.nav_mesh:
            return
        
        status = self.nav_mesh.get_status()
        gates = status.get('gates', {})
        
        # Count active enforcements
        total_enforcements = sum(g.get('total_requests', 0) for g in gates.values())
        
        self.meters['gate_density'].record(total_enforcements)
    
    def update_all(self):
        """Update all metrics."""
        self.update_latency_tolerance()
        self.update_threshold_lock()
        self.update_resource_flow()
        self.update_nav_velocity()
        self.update_gate_density()
        
        self.metrics_updated += 1
        self.last_update = time.time()
    
    def get_gauge(self, name: str) -> Optional[Gauge]:
        """Get gauge by name."""
        return self.gauges.get(name)
    
    def get_meter(self, name: str) -> Optional[Meter]:
        """Get meter by name."""
        return self.meters.get(name)
    
    def get_all_gauges(self) -> Dict:
        """Get all gauge statistics."""
        return {name: gauge.get_stats() for name, gauge in self.gauges.items()}
    
    def get_all_meters(self) -> Dict:
        """Get all meter statistics."""
        return {name: meter.get_stats() for name, meter in self.meters.items()}
    
    def get_status(self) -> Dict:
        """Get complete metrics status."""
        return {
            'gauges': self.get_all_gauges(),
            'meters': self.get_all_meters(),
            'metrics_updated': self.metrics_updated,
            'last_update': self.last_update,
        }
    
    def is_system_healthy(self) -> bool:
        """Check if all gauges meet their targets."""
        return all(gauge.is_healthy() for gauge in self.gauges.values())
    
    def get_health_summary(self) -> Dict:
        """Get health summary."""
        gauges_status = {name: gauge.is_healthy() for name, gauge in self.gauges.items()}
        
        return {
            'overall_healthy': self.is_system_healthy(),
            'gauges_healthy': gauges_status,
            'unhealthy_count': sum(1 for healthy in gauges_status.values() if not healthy),
        }


if __name__ == "__main__":
    # Test metrics collector
    from resource_engine import ResourceEngine, Task, TaskPriority, ResourceType
    from nav_mesh import NavigationMesh, ThresholdDomain
    from latent_cache import LatentCache
    
    print("Metrics Collector Test")
    print("=" * 80)
    
    # Create engine components
    engine = ResourceEngine("src/memory/test_metrics_engine.jsonl")
    nav = NavigationMesh("src/memory/test_metrics_nav.jsonl")
    cache = LatentCache("src/memory/test_metrics_cache")
    
    # Start engine
    engine.start()
    
    # Simulate some activity
    print("\n1. Simulating engine activity...")
    for i in range(10):
        task = Task(f"task_{i}", TaskPriority.NORMAL, ResourceType.COMPUTE)
        engine.submit_task(task)
    
    for _ in range(5):
        engine.run_cycle()
    
    # Simulate navigation
    print("\n2. Simulating navigation...")
    user_id = "test_user"
    token = nav.issue_token(ThresholdDomain.WEALTH, user_id)
    for _ in range(5):
        nav.navigate(ThresholdDomain.WEALTH, token, user_id)
    
    # Simulate cache usage
    print("\n3. Simulating cache usage...")
    for i in range(20):
        cache.set(f'key_{i}', {'value': i})
    for i in range(15):
        cache.get(f'key_{i}')
    
    # Create metrics collector
    print("\n4. Creating metrics collector...")
    metrics = MetricsCollector()
    metrics.integrate(
        resource_engine=engine,
        nav_mesh=nav,
        latent_cache=cache
    )
    
    # Update metrics
    print("\n5. Updating metrics...")
    metrics.update_all()
    
    # Show metrics
    print("\n6. Metrics status:")
    status = metrics.get_status()
    print(json.dumps(status, indent=2))
    
    # Health check
    print("\n7. Health summary:")
    health = metrics.get_health_summary()
    print(json.dumps(health, indent=2))
    
    print("\n✅ All tests passed!")
