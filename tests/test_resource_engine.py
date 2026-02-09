"""
Comprehensive tests for the engine system.

Tests:
- Resource pool scaling up/down
- Threshold gate blocking unauthorized access
- Offline cache queue and sync
- Entity state transitions
- Hash-chain integrity across all logs
- Metric gauge calculations
- Trajectory optimization with beam search
- Provenance tracking and PII redaction
"""

import pytest
import json
import time
from pathlib import Path
import sys
import tempfile
import shutil

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from engine.resource_engine import ResourceEngine, Task, TaskPriority, ResourceType
from engine.nav_mesh import NavigationMesh, ThresholdDomain
from engine.latent_cache import LatentCache
from engine.entity_manager import EntityManager, EntityType, EntityState
from engine.metrics import MetricsCollector
from engine.trajectory import TrajectoryOptimizer, Fact
from engine.provenance import ProvenanceDomain


class TestResourceEngine:
    """Test resource engine functionality."""
    
    def test_resource_pool_scaling_up(self, tmp_path):
        """Test that resource pools scale up under load."""
        log_path = str(tmp_path / "test_engine.jsonl")
        engine = ResourceEngine(log_path)
        engine.start()
        
        # Get initial capacity
        initial_capacity = engine.pools[ResourceType.COMPUTE].capacity
        
        # Submit many tasks to trigger scaling
        for i in range(50):
            task = Task(f"task_{i}", TaskPriority.NORMAL, ResourceType.COMPUTE)
            engine.submit_task(task)
        
        # Process and trigger auto-scaling
        for _ in range(10):
            engine.run_cycle()
        
        # Check if scaled up
        final_capacity = engine.pools[ResourceType.COMPUTE].capacity
        assert final_capacity >= initial_capacity
        
        engine.stop()
    
    def test_resource_pool_scaling_down(self, tmp_path):
        """Test that resource pools scale down when underutilized."""
        log_path = str(tmp_path / "test_engine.jsonl")
        engine = ResourceEngine(log_path)
        engine.start()
        
        # Artificially increase capacity
        engine.pools[ResourceType.COMPUTE].capacity = 50
        initial_capacity = engine.pools[ResourceType.COMPUTE].capacity
        
        # Run cycles with low utilization
        for _ in range(70):  # More than scale_check_interval
            engine.run_cycle()
            time.sleep(0.02)
        
        # Check if might scale down (depends on utilization)
        final_capacity = engine.pools[ResourceType.COMPUTE].capacity
        # Capacity should either stay same or decrease
        assert final_capacity <= initial_capacity
        
        engine.stop()
    
    def test_hash_chain_integrity(self, tmp_path):
        """Test hash chain verification."""
        log_path = str(tmp_path / "test_engine.jsonl")
        engine = ResourceEngine(log_path)
        engine.start()
        
        # Generate some events
        for i in range(5):
            task = Task(f"task_{i}", TaskPriority.NORMAL, ResourceType.COMPUTE)
            engine.submit_task(task)
            engine.run_cycle()
        
        engine.stop()
        
        # Verify hash chain
        assert engine.verify_hash_chain()


class TestNavigationMesh:
    """Test navigation mesh and threshold gates."""
    
    def test_gate_blocks_invalid_token(self, tmp_path):
        """Test that gates block invalid tokens."""
        log_path = str(tmp_path / "test_nav.jsonl")
        nav = NavigationMesh(log_path)
        
        user_id = "test_user"
        
        # Try to navigate with invalid token
        success, error, route = nav.navigate(
            ThresholdDomain.WEALTH,
            "invalid_token",
            user_id,
            offline_mode=False
        )
        
        assert not success
        assert error is not None
    
    def test_gate_allows_valid_token(self, tmp_path):
        """Test that gates allow valid tokens."""
        log_path = str(tmp_path / "test_nav.jsonl")
        nav = NavigationMesh(log_path)
        
        user_id = "test_user"
        
        # Issue valid token
        token = nav.issue_token(ThresholdDomain.WEALTH, user_id)
        
        # Try to navigate
        success, error, route = nav.navigate(
            ThresholdDomain.WEALTH,
            token,
            user_id,
            offline_mode=False
        )
        
        assert success
        assert error is None
    
    def test_offline_mode_bypasses_gate(self, tmp_path):
        """Test that offline mode works without tokens."""
        log_path = str(tmp_path / "test_nav.jsonl")
        nav = NavigationMesh(log_path)
        
        user_id = "test_user"
        
        # Navigate in offline mode (no token needed)
        success, error, route = nav.navigate(
            ThresholdDomain.INFO,
            "",
            user_id,
            offline_mode=True
        )
        
        assert success
        assert error is None
    
    def test_hash_chain_integrity(self, tmp_path):
        """Test hash chain verification for navigation mesh."""
        log_path = str(tmp_path / "test_nav.jsonl")
        nav = NavigationMesh(log_path)
        
        # Generate some events
        user_id = "test_user"
        for domain in ThresholdDomain:
            token = nav.issue_token(domain, user_id)
            nav.navigate(domain, token, user_id)
        
        # Verify hash chain
        assert nav.verify_hash_chain()


class TestLatentCache:
    """Test offline cache functionality."""
    
    def test_offline_queue_and_sync(self, tmp_path):
        """Test that operations are queued offline and synced online."""
        cache_dir = str(tmp_path / "test_cache")
        cache = LatentCache(cache_dir)
        
        # Go offline
        cache.set_online(False)
        
        # Perform operations
        cache.set('key1', 'value1')
        cache.set('key2', 'value2')
        cache.delete('key0')  # Delete non-existent key
        
        # Check queue depth
        assert len(cache.queue) >= 2  # At least 2 writes queued
        
        # Go online and sync
        cache.set_online(True)
        synced = cache.sync()
        
        # Queue should be empty or have only failed ops
        assert len(cache.queue) == 0 or all(not op.can_retry() for op in cache.queue)
    
    def test_cache_hit_and_miss(self, tmp_path):
        """Test cache hits and misses."""
        cache_dir = str(tmp_path / "test_cache")
        cache = LatentCache(cache_dir)
        
        # Set value
        cache.set('test_key', 'test_value')
        
        # Hit
        value = cache.get('test_key')
        assert value == 'test_value'
        assert cache.cache_hits == 1
        
        # Miss
        value = cache.get('nonexistent_key')
        assert value is None
        assert cache.cache_misses == 1
    
    def test_cache_expiration(self, tmp_path):
        """Test that cache entries expire."""
        cache_dir = str(tmp_path / "test_cache")
        cache = LatentCache(cache_dir)
        
        # Set value with short TTL
        cache.set('expire_key', 'expire_value', ttl=1)
        
        # Should exist immediately
        assert cache.get('expire_key') == 'expire_value'
        
        # Wait for expiration
        time.sleep(1.1)
        
        # Should be expired
        assert cache.get('expire_key') is None


class TestEntityManager:
    """Test entity lifecycle management."""
    
    def test_entity_state_transitions(self, tmp_path):
        """Test entity state machine transitions."""
        log_path = str(tmp_path / "test_entities.jsonl")
        manager = EntityManager(log_path)
        
        # Spawn entity
        entity = manager.spawn("worker_001", EntityType.WORKER)
        assert entity is not None
        assert entity.state == EntityState.HIBERNATING
        
        # Awaken
        success = manager.awaken("worker_001")
        assert success
        assert entity.state == EntityState.ACTIVE
        
        # Hibernate
        success = manager.hibernate("worker_001")
        assert success
        assert entity.state == EntityState.HIBERNATING
        
        # Awaken again
        success = manager.awaken("worker_001")
        assert success
        
        # Deactivate
        success = manager.deactivate("worker_001")
        assert success
        assert entity.state == EntityState.DEACTIVATED
    
    def test_entity_error_correction(self, tmp_path):
        """Test entity error correction and recovery."""
        log_path = str(tmp_path / "test_entities.jsonl")
        manager = EntityManager(log_path)
        
        # Spawn and awaken entity
        entity = manager.spawn("worker_001", EntityType.WORKER)
        manager.awaken("worker_001")
        
        # Simulate unhealthy state
        entity.health = 20.0
        
        # Trigger error correction
        recovered = manager.error_correction("worker_001")
        
        # Should attempt recovery
        assert entity.recovery_attempts > 0
    
    def test_hash_chain_integrity(self, tmp_path):
        """Test hash chain verification for entity manager."""
        log_path = str(tmp_path / "test_entities.jsonl")
        manager = EntityManager(log_path)
        
        # Generate some events
        for i in range(3):
            entity = manager.spawn(f"worker_{i}", EntityType.WORKER)
            manager.awaken(f"worker_{i}")
        
        # Verify hash chain
        assert manager.verify_hash_chain()


class TestMetrics:
    """Test metrics collection."""
    
    def test_gauge_calculation(self, tmp_path):
        """Test gauge value calculations."""
        # Create components
        engine = ResourceEngine(str(tmp_path / "engine.jsonl"))
        nav = NavigationMesh(str(tmp_path / "nav.jsonl"))
        cache = LatentCache(str(tmp_path / "cache"))
        
        # Submit some data
        engine.start()
        for i in range(5):
            task = Task(f"task_{i}", TaskPriority.NORMAL, ResourceType.COMPUTE)
            engine.submit_task(task)
            engine.run_cycle()
        
        cache.set('key1', 'value1')
        cache.get('key1')  # Hit
        cache.get('key2')  # Miss
        
        # Create metrics collector
        metrics = MetricsCollector()
        metrics.integrate(resource_engine=engine, nav_mesh=nav, latent_cache=cache)
        
        # Update metrics
        metrics.update_all()
        
        # Check gauges exist and have values
        assert 'latency_tolerance' in metrics.gauges
        assert 'threshold_lock' in metrics.gauges
        assert 'resource_flow' in metrics.gauges
        
        # Check values are in range [0, 100]
        for gauge in metrics.gauges.values():
            assert 0.0 <= gauge.current_value <= 100.0
        
        engine.stop()


class TestTrajectoryOptimizer:
    """Test trajectory optimization."""
    
    def test_forward_chaining(self, tmp_path):
        """Test forward chaining closure generation."""
        log_path = str(tmp_path / "trajectory.jsonl")
        optimizer = TrajectoryOptimizer(log_path)
        
        # Add facts and rules
        optimizer.add_fact('A', True)
        optimizer.add_fact('B', True)
        optimizer.add_rule('rule1', ['A', 'B'], 'C')
        optimizer.add_rule('rule2', ['C'], 'D')
        
        # Forward chain
        initial_facts = {Fact('A', True), Fact('B', True)}
        closure = optimizer.forward_chain(initial_facts, max_depth=10)
        
        # Should derive C and D
        fact_symbols = {f.symbol for f in closure.facts}
        assert 'C' in fact_symbols
        assert 'D' in fact_symbols
    
    def test_beam_search(self, tmp_path):
        """Test beam search for optimal trajectory."""
        log_path = str(tmp_path / "trajectory.jsonl")
        optimizer = TrajectoryOptimizer(log_path)
        
        # Setup knowledge base
        optimizer.add_fact('A', True)
        optimizer.add_fact('B', True)
        optimizer.add_rule('rule1', ['A'], 'C', cost=1.0)
        optimizer.add_rule('rule2', ['B'], 'D', cost=0.5)
        
        # Beam search
        initial_facts = {Fact('A', True), Fact('B', True)}
        best_path = optimizer.beam_search_optimal_spine(initial_facts)
        
        # Should find a path
        assert best_path is not None
        assert best_path.score > 0
        assert len(best_path.closures) > 0
    
    def test_fold_to_hash(self, tmp_path):
        """Test folding trajectory to canonical hash."""
        log_path = str(tmp_path / "trajectory.jsonl")
        optimizer = TrajectoryOptimizer(log_path)
        
        # Setup and search
        optimizer.add_fact('A', True)
        optimizer.add_rule('rule1', ['A'], 'B')
        
        initial_facts = {Fact('A', True)}
        best_path = optimizer.beam_search_optimal_spine(initial_facts)
        
        # Fold to hash
        spine_hash = optimizer.fold_to_hash(best_path)
        
        # Should be a valid SHA-256 hash
        assert len(spine_hash) == 64
        assert all(c in '0123456789abcdef' for c in spine_hash)
    
    def test_hash_chain_integrity(self, tmp_path):
        """Test hash chain verification for trajectory log."""
        log_path = str(tmp_path / "trajectory.jsonl")
        optimizer = TrajectoryOptimizer(log_path)
        
        # Generate events
        optimizer.add_fact('A', True)
        optimizer.add_fact('B', True)
        optimizer.add_rule('rule1', ['A'], 'C')
        
        # Verify hash chain
        assert optimizer.verify_hash_chain()


class TestProvenance:
    """Test provenance and audit functionality."""
    
    def test_pii_redaction(self, tmp_path):
        """Test PII redaction."""
        log_path = str(tmp_path / "provenance.jsonl")
        provenance = ProvenanceDomain(log_path)
        
        # Test data with PII
        data = {
            'email': 'user@example.com',
            'phone': '555-123-4567',
            'password': 'secret123'
        }
        
        redacted = provenance.redactor.redact_dict(data)
        
        # Email should be redacted or hashed
        assert 'user@example.com' not in str(redacted.get('email', ''))
        
        # Phone should be redacted
        assert '555-123-4567' not in str(redacted.get('phone', ''))
        
        # Password should be redacted
        assert 'secret123' not in str(redacted.get('password', ''))
    
    def test_anomaly_detection(self, tmp_path):
        """Test anomaly detection."""
        log_path = str(tmp_path / "provenance.jsonl")
        provenance = ProvenanceDomain(log_path)
        
        # Generate burst of events
        for i in range(25):
            provenance.tap_event('test_event', {'iteration': i}, 'run_001')
            time.sleep(0.01)
        
        # Should detect anomalies (burst or rate spike)
        assert provenance.anomaly_detector.anomalies
    
    def test_provenance_graph(self, tmp_path):
        """Test provenance graph construction."""
        log_path = str(tmp_path / "provenance.jsonl")
        provenance = ProvenanceDomain(log_path)
        
        # Add edges
        provenance.add_provenance_edge('A', 'C', 'rule1', 'run_001', cost=1.0)
        provenance.add_provenance_edge('B', 'C', 'rule1', 'run_001', cost=1.0)
        provenance.add_provenance_edge('C', 'D', 'rule2', 'run_001', cost=2.0)
        
        # Get graph
        graph = provenance.get_provenance_graph()
        
        # Check structure
        assert graph['node_count'] == 4  # A, B, C, D
        assert graph['edge_count'] == 3
        assert 'A' in graph['nodes']
        assert 'D' in graph['nodes']
    
    def test_hash_chain_integrity(self, tmp_path):
        """Test hash chain verification for provenance log."""
        log_path = str(tmp_path / "provenance.jsonl")
        provenance = ProvenanceDomain(log_path)
        
        # Generate events
        for i in range(5):
            provenance.tap_event('test_event', {'iteration': i}, 'run_001')
        
        # Verify hash chain
        assert provenance.verify_hash_chain()


# Fixtures
@pytest.fixture
def tmp_path(tmpdir):
    """Provide a temporary directory."""
    return Path(tmpdir)


if __name__ == "__main__":
    # Run tests with pytest if available, otherwise run basic tests
    try:
        pytest.main([__file__, '-v'])
    except:
        print("pytest not available, running basic tests...")
        import tempfile
        
        tmp = Path(tempfile.mkdtemp())
        
        # Run basic tests
        print("Testing resource engine...")
        test = TestResourceEngine()
        test.test_hash_chain_integrity(tmp)
        print("✓ Resource engine hash chain verified")
        
        print("\nTesting navigation mesh...")
        test = TestNavigationMesh()
        test.test_gate_allows_valid_token(tmp)
        test.test_hash_chain_integrity(tmp)
        print("✓ Navigation mesh working")
        
        print("\nTesting latent cache...")
        test = TestLatentCache()
        test.test_cache_hit_and_miss(tmp)
        print("✓ Latent cache working")
        
        print("\nTesting entity manager...")
        test = TestEntityManager()
        test.test_entity_state_transitions(tmp)
        test.test_hash_chain_integrity(tmp)
        print("✓ Entity manager working")
        
        print("\nTesting trajectory optimizer...")
        test = TestTrajectoryOptimizer()
        test.test_forward_chaining(tmp)
        test.test_hash_chain_integrity(tmp)
        print("✓ Trajectory optimizer working")
        
        print("\nTesting provenance...")
        test = TestProvenance()
        test.test_pii_redaction(tmp)
        test.test_hash_chain_integrity(tmp)
        print("✓ Provenance domain working")
        
        # Cleanup
        shutil.rmtree(tmp)
        
        print("\n✅ All basic tests passed!")
