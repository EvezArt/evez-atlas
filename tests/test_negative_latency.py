"""
Tests for Negative Latency Engine
"""

import pytest
import numpy as np
import time
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import importlib.util
spec = importlib.util.spec_from_file_location(
    "negative_latency",
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "ekf-daemon", "negative_latency.py")
)
negative_latency = importlib.util.module_from_spec(spec)
spec.loader.exec_module(negative_latency)

NegativeLatencyEngine = negative_latency.NegativeLatencyEngine
NegativeLatencySafety = negative_latency.NegativeLatencySafety
CognitiveEKF = negative_latency.CognitiveEKF


def test_cognitive_ekf_initialization():
    """Test EKF initialization"""
    ekf = CognitiveEKF(dim_x=6, dim_z=3)
    
    assert ekf.ekf.x.shape == (6,)
    assert ekf.ekf.P.shape == (6, 6)
    assert ekf.confidence == 1.0


def test_ekf_trajectory_prediction():
    """Test trajectory prediction"""
    ekf = CognitiveEKF()
    current_state = np.array([1.0, 0.5, 0.3, 0.1, 0.2, 0.4])
    
    trajectory = ekf.predict_trajectory(current_state, steps=10)
    
    assert len(trajectory) == 10
    assert all(isinstance(state, np.ndarray) for state in trajectory)


def test_negative_latency_engine_initialization():
    """Test engine initialization"""
    engine = NegativeLatencyEngine(horizon=10, cache_size=100, safe_mode=True)
    
    assert engine.prediction_horizon == 10
    assert engine.trajectory_cache.maxlen == 100
    assert engine.safe_mode is True


def test_cache_accumulation():
    """Test that cache accumulates predictions"""
    engine = NegativeLatencyEngine(horizon=5, cache_size=10, safe_mode=True)
    engine.start()
    
    # Wait for cache to build
    time.sleep(3)
    
    assert len(engine.trajectory_cache) > 0
    
    engine.stop()


def test_instant_response():
    """Test instant response mechanism"""
    engine = NegativeLatencyEngine(horizon=5, cache_size=10, safe_mode=True)
    engine.start()
    
    # Wait for cache
    time.sleep(2)
    
    # Trigger event
    event = {'type': 'test', 'id': 1}
    policy = engine.instant_response(event)
    
    # Should get a policy (either cached or computed)
    assert policy is not None
    
    engine.stop()


def test_cache_hit_tracking():
    """Test cache hit/miss tracking"""
    engine = NegativeLatencyEngine(horizon=5, cache_size=10, safe_mode=True)
    engine.start()
    
    time.sleep(2)
    
    # Trigger multiple events
    for i in range(5):
        engine.instant_response({'type': 'test', 'id': i})
    
    metrics = engine.get_metrics()
    
    assert metrics['total_responses'] == 5
    assert metrics['cache_hits'] >= 0
    assert metrics['cache_misses'] >= 0
    
    engine.stop()


def test_safety_verification():
    """Test safety verification system"""
    safety = NegativeLatencySafety(safety_threshold=0.15)
    
    # Test with close states (should pass)
    predicted = np.array([1.0, 0.5, 0.3])
    actual = np.array([1.05, 0.52, 0.31])
    
    deviation = safety.calculate_deviation(predicted, actual)
    assert deviation < 0.15
    
    # Test with distant states (should fail)
    actual_far = np.array([5.0, 5.0, 5.0])
    deviation_far = safety.calculate_deviation(predicted, actual_far)
    assert deviation_far > 0.15


def test_metrics_reporting():
    """Test metrics reporting"""
    engine = NegativeLatencyEngine(horizon=5, cache_size=10, safe_mode=True)
    engine.start()
    
    time.sleep(2)
    
    metrics = engine.get_metrics()
    
    required_keys = [
        'cache_hits', 'cache_misses', 'total_responses',
        'cache_hit_rate', 'cached_trajectories', 'staged_policies',
        'current_confidence', 'safe_mode'
    ]
    
    for key in required_keys:
        assert key in metrics
    
    engine.stop()


def test_clear_caches():
    """Test cache clearing"""
    engine = NegativeLatencyEngine(horizon=5, cache_size=10, safe_mode=True)
    engine.start()
    
    time.sleep(2)
    
    assert len(engine.trajectory_cache) > 0
    
    engine.clear_caches()
    
    assert len(engine.trajectory_cache) == 0
    assert len(engine.policy_cache) == 0
    
    engine.stop()


def test_safe_mode_enforcement():
    """Test SAFE_MODE enforcement"""
    engine = NegativeLatencyEngine(safe_mode=True)
    
    assert engine.safe_mode is True
    assert engine.CONFIDENCE_THRESHOLD == 0.8
    assert engine.DEVIATION_THRESHOLD == 0.15


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
