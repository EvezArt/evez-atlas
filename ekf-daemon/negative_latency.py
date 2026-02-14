"""
Negative Latency Engine: EKF Trajectory Prediction with Ring Buffer Caching

Continuously predicts future states, caches trajectories, and stages control policies
for instant response when events occur.
"""

from collections import deque
import numpy as np
import time
import threading
from typing import Dict, List, Optional, Any
from filterpy.kalman import ExtendedKalmanFilter
from dataclasses import dataclass, field
import json


@dataclass
class TrajectoryCache:
    """Cached trajectory with metadata"""
    timestamp: float
    base_state: np.ndarray
    trajectory: List[np.ndarray]
    confidence: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ControlPolicy:
    """Pre-computed control policy for a future state"""
    state_hash: str
    action: str
    parameters: Dict[str, Any]
    urgency: float
    reason: str
    timestamp: float


class CognitiveEKF:
    """
    Extended Kalman Filter for cognitive state estimation and prediction
    """
    
    def __init__(self, dim_x=6, dim_z=3):
        """
        Initialize EKF for cognitive state tracking
        
        Args:
            dim_x: State dimension (position, velocity, acceleration)
            dim_z: Measurement dimension
        """
        self.ekf = ExtendedKalmanFilter(dim_x=dim_x, dim_z=dim_z)
        
        # Initialize state vector (3D position + 3D velocity)
        self.ekf.x = np.zeros(dim_x)
        
        # Initial state covariance
        self.ekf.P = np.eye(dim_x) * 0.1
        
        # Process noise
        self.ekf.Q = np.eye(dim_x) * 0.01
        
        # Measurement noise
        self.ekf.R = np.eye(dim_z) * 0.1
        
        self.confidence = 1.0
    
    def predict_trajectory(self, current_state: np.ndarray, steps: int = 10, dt: float = 1.0) -> List[np.ndarray]:
        """
        Predict N future states from current state
        
        Args:
            current_state: Current system state
            steps: Number of prediction steps
            dt: Time step between predictions
        
        Returns:
            List of predicted future states
        """
        trajectory = []
        state = current_state.copy()
        
        for _ in range(steps):
            # Simple linear prediction model (can be made more sophisticated)
            # State transition: x_k+1 = F * x_k
            F = self._get_state_transition_matrix(dt)
            state = F @ state
            trajectory.append(state.copy())
        
        return trajectory
    
    def _get_state_transition_matrix(self, dt: float) -> np.ndarray:
        """Get state transition matrix for constant velocity model"""
        dim = len(self.ekf.x)
        F = np.eye(dim)
        
        # For position-velocity pairs, add velocity to position
        for i in range(dim // 2):
            F[i, i + dim // 2] = dt
        
        return F
    
    def update(self, measurement: np.ndarray):
        """Update EKF with new measurement"""
        self.ekf.predict()
        self.ekf.update(measurement, self._hx, self._HJacobian)
        
        # Update confidence based on covariance
        self.confidence = self._calculate_confidence()
    
    def _hx(self, x):
        """Measurement function: maps state to measurement space"""
        # Extract position components from state
        return x[:len(x)//2]
    
    def _HJacobian(self, x):
        """Jacobian of measurement function"""
        dim_z = len(x) // 2
        dim_x = len(x)
        H = np.zeros((dim_z, dim_x))
        H[:dim_z, :dim_z] = np.eye(dim_z)
        return H
    
    def _calculate_confidence(self) -> float:
        """Calculate confidence based on state covariance"""
        # Use trace of covariance matrix as uncertainty measure
        uncertainty = np.trace(self.ekf.P)
        # Convert to confidence (0-1 scale)
        confidence = np.exp(-uncertainty)
        return float(np.clip(confidence, 0.0, 1.0))
    
    def get_confidence(self) -> float:
        """Get current prediction confidence"""
        return self.confidence


class NegativeLatencyEngine:
    """
    Main engine for negative latency: continuous prediction, caching, and instant response
    """
    
    def __init__(self, horizon: int = 10, cache_size: int = 100, safe_mode: bool = True):
        """
        Initialize Negative Latency Engine
        
        Args:
            horizon: Number of prediction steps ahead
            cache_size: Maximum number of cached trajectories
            safe_mode: Enable safety checks before execution
        """
        self.ekf = CognitiveEKF()
        self.trajectory_cache = deque(maxlen=cache_size)
        self.policy_cache: Dict[str, ControlPolicy] = {}
        self.prediction_horizon = horizon
        self.safe_mode = safe_mode
        
        # Metrics
        self.cache_hits = 0
        self.cache_misses = 0
        self.total_responses = 0
        
        # State
        self.running = False
        self.prediction_thread: Optional[threading.Thread] = None
        self.current_state = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        
        # Safety thresholds
        self.CONFIDENCE_THRESHOLD = 0.8
        self.DEVIATION_THRESHOLD = 0.15
    
    def start(self):
        """Start continuous prediction loop in background thread"""
        if self.running:
            return
        
        self.running = True
        self.prediction_thread = threading.Thread(target=self._continuous_prediction_loop, daemon=True)
        self.prediction_thread.start()
        print("🚀 Negative Latency Engine started - predicting futures continuously")
    
    def stop(self):
        """Stop continuous prediction loop"""
        self.running = False
        if self.prediction_thread:
            self.prediction_thread.join(timeout=5.0)
        print("🛑 Negative Latency Engine stopped")
    
    def _continuous_prediction_loop(self):
        """
        Runs continuously, always computing futures
        """
        while self.running:
            try:
                current_state = self.get_current_state()
                
                # Predict next N states
                trajectory = self.ekf.predict_trajectory(
                    current_state, 
                    steps=self.prediction_horizon
                )
                
                # Cache trajectory with timestamp
                cache_entry = TrajectoryCache(
                    timestamp=time.time(),
                    base_state=current_state.copy(),
                    trajectory=trajectory,
                    confidence=self.ekf.get_confidence(),
                    metadata={'horizon': self.prediction_horizon}
                )
                
                self.trajectory_cache.append(cache_entry)
                
                # Pre-compute control policies for each future state
                for i, future_state in enumerate(trajectory):
                    policy = self._generate_control_policy(future_state, i)
                    if policy:
                        # Stage policy (don't execute yet)
                        self.policy_cache[f't+{i}'] = policy
                
                # Sleep for 1 second before next prediction
                time.sleep(1.0)
                
            except Exception as e:
                print(f"❌ Error in prediction loop: {e}")
                time.sleep(1.0)
    
    def get_current_state(self) -> np.ndarray:
        """
        Get current system state (placeholder - should be overridden or connected to real data)
        """
        # In a real system, this would read from sensors, metrics, etc.
        # For now, simulate gradual state evolution
        self.current_state += np.random.normal(0, 0.01, size=len(self.current_state))
        return self.current_state.copy()
    
    def _generate_control_policy(self, future_state: np.ndarray, step: int) -> Optional[ControlPolicy]:
        """
        Generate control policy for a predicted future state
        
        Args:
            future_state: Predicted future state
            step: Prediction step number
        
        Returns:
            Control policy or None if no action needed
        """
        # Simple policy: take action if state exceeds threshold
        state_magnitude = np.linalg.norm(future_state)
        
        if state_magnitude > 1.0:
            state_hash = self._hash_state(future_state)
            return ControlPolicy(
                state_hash=state_hash,
                action='correct',
                parameters={'magnitude': float(state_magnitude)},
                urgency=min(state_magnitude / 2.0, 1.0),
                reason=f'State magnitude {state_magnitude:.2f} exceeds threshold',
                timestamp=time.time()
            )
        
        return None
    
    def _hash_state(self, state: np.ndarray) -> str:
        """Create hash of state for caching"""
        # Round to reduce hash collisions from minor variations
        rounded = np.round(state, decimals=2)
        return str(hash(rounded.tobytes()))
    
    def instant_response(self, trigger_event: Dict[str, Any]) -> Optional[ControlPolicy]:
        """
        When event occurs, retrieve pre-computed response
        
        Args:
            trigger_event: Event that triggered the response
        
        Returns:
            Pre-computed policy if available, None otherwise
        """
        self.total_responses += 1
        
        # Find best matching cached trajectory
        best_match = self._find_best_trajectory_match(trigger_event)
        
        if best_match and best_match.confidence > self.CONFIDENCE_THRESHOLD:
            # High confidence: use cached policy
            policy = self.policy_cache.get('t+1')  # Next step policy
            
            if policy:
                # Verify before execution in SAFE_MODE
                if self.safe_mode and not self._verify_before_execute(policy, trigger_event):
                    print(f"⚠️  SAFE_MODE: Policy verification failed, falling back to compute")
                    self.cache_misses += 1
                    return self._compute_policy_now(trigger_event)
                
                self.cache_hits += 1
                print(f"⚡ INSTANT RESPONSE: Using cached policy (confidence: {best_match.confidence:.2f})")
                return policy
        
        # Low confidence or no match: recompute (fallback to normal latency)
        self.cache_misses += 1
        print(f"⏱️  Cache miss: computing policy on demand")
        return self._compute_policy_now(trigger_event)
    
    def _find_best_trajectory_match(self, trigger_event: Dict[str, Any]) -> Optional[TrajectoryCache]:
        """
        Find cached trajectory that best matches the trigger event
        
        Args:
            trigger_event: Event to match against
        
        Returns:
            Best matching trajectory cache entry
        """
        if not self.trajectory_cache:
            return None
        
        # Get most recent trajectory with highest confidence
        # In a real system, this would do more sophisticated matching
        recent_trajectories = sorted(
            self.trajectory_cache,
            key=lambda x: (x.timestamp, x.confidence),
            reverse=True
        )
        
        return recent_trajectories[0] if recent_trajectories else None
    
    def _verify_before_execute(self, policy: ControlPolicy, actual_event: Dict[str, Any]) -> bool:
        """
        Verify prediction matches reality before executing (SAFE_MODE)
        
        Args:
            policy: Pre-computed policy
            actual_event: Actual event that occurred
        
        Returns:
            True if safe to execute, False otherwise
        """
        # Check policy age (don't use stale policies)
        age = time.time() - policy.timestamp
        if age > 10.0:  # Policy older than 10 seconds
            return False
        
        # In a real system, would check if predicted state matches actual state
        # For now, allow execution
        return True
    
    def _compute_policy_now(self, trigger_event: Dict[str, Any]) -> ControlPolicy:
        """
        Compute policy on demand (fallback when cache miss)
        
        Args:
            trigger_event: Event that triggered the need for policy
        
        Returns:
            Newly computed policy
        """
        current_state = self.get_current_state()
        state_hash = self._hash_state(current_state)
        
        return ControlPolicy(
            state_hash=state_hash,
            action='respond',
            parameters={'event': trigger_event},
            urgency=0.5,
            reason='On-demand computation (cache miss)',
            timestamp=time.time()
        )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        hit_rate = self.cache_hits / max(self.total_responses, 1)
        
        return {
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'total_responses': self.total_responses,
            'cache_hit_rate': hit_rate,
            'cached_trajectories': len(self.trajectory_cache),
            'staged_policies': len(self.policy_cache),
            'current_confidence': self.ekf.get_confidence(),
            'safe_mode': self.safe_mode
        }
    
    def clear_caches(self):
        """Clear all caches (for testing or reset)"""
        self.trajectory_cache.clear()
        self.policy_cache.clear()
        self.cache_hits = 0
        self.cache_misses = 0
        self.total_responses = 0


class NegativeLatencySafety:
    """
    Safety mechanisms for negative latency system
    """
    
    def __init__(self, safety_threshold: float = 0.15):
        """
        Initialize safety system
        
        Args:
            safety_threshold: Maximum allowed deviation before rejecting prediction
        """
        self.SAFETY_THRESHOLD = safety_threshold
        self.executed_actions: List[Dict[str, Any]] = []
        self.rollback_stack: List[Dict[str, Any]] = []
    
    def verify_before_execute(self, staged_action: Dict[str, Any], actual_state: np.ndarray) -> bool:
        """
        Always verify prediction matches reality before executing
        
        Args:
            staged_action: Action that was pre-staged
            actual_state: Actual observed state
        
        Returns:
            True if safe to execute, False otherwise
        """
        predicted_state = staged_action.get('base_state')
        
        if predicted_state is None:
            return False
        
        deviation = self.calculate_deviation(predicted_state, actual_state)
        
        if deviation > self.SAFETY_THRESHOLD:
            # Prediction was wrong, don't execute
            self._log_prediction_miss(staged_action, actual_state, deviation)
            return False
        
        # Prediction was correct, safe to execute
        return True
    
    def calculate_deviation(self, predicted: np.ndarray, actual: np.ndarray) -> float:
        """
        Calculate normalized deviation between predicted and actual states
        
        Args:
            predicted: Predicted state
            actual: Actual state
        
        Returns:
            Normalized deviation (0-1 scale)
        """
        if len(predicted) != len(actual):
            return 1.0  # Maximum deviation if dimensions don't match
        
        # Calculate relative error
        diff = np.linalg.norm(predicted - actual)
        norm = max(np.linalg.norm(actual), 1e-6)  # Avoid division by zero
        
        return float(diff / norm)
    
    def _log_prediction_miss(self, staged_action: Dict[str, Any], actual_state: np.ndarray, deviation: float):
        """Log when prediction doesn't match reality"""
        print(f"⚠️  Prediction miss detected - deviation: {deviation:.3f} > threshold: {self.SAFETY_THRESHOLD}")
        print(f"   Action: {staged_action.get('action', 'unknown')}")
    
    def rollback_on_error(self, executed_actions: List[Dict[str, Any]]):
        """
        If speculative action was wrong, reverse it
        
        Args:
            executed_actions: List of actions to rollback
        """
        for action in executed_actions:
            action_type = action.get('type')
            
            if action_type == 'issue':
                print(f"🔄 Rolling back issue: {action.get('issue_id')}")
                # Would close issue in real implementation
            elif action_type == 'post':
                print(f"🔄 Rolling back post: {action.get('post_id')}")
                # Would delete post in real implementation
            
            self.rollback_stack.append(action)


def main():
    """
    Example usage of Negative Latency Engine
    """
    print("=" * 60)
    print("NEGATIVE LATENCY ENGINE - Demo")
    print("=" * 60)
    
    # Initialize engine
    engine = NegativeLatencyEngine(
        horizon=10,
        cache_size=100,
        safe_mode=True
    )
    
    # Start continuous prediction
    engine.start()
    
    # Let it build up cache
    print("\n⏳ Building prediction cache...")
    time.sleep(5)
    
    # Simulate some events
    print("\n📨 Simulating trigger events...")
    for i in range(5):
        trigger = {'event_id': i, 'type': 'test_event'}
        policy = engine.instant_response(trigger)
        
        if policy:
            print(f"   Event {i}: {policy.action} (urgency: {policy.urgency:.2f})")
        
        time.sleep(0.5)
    
    # Show metrics
    print("\n📊 Performance Metrics:")
    metrics = engine.get_metrics()
    for key, value in metrics.items():
        print(f"   {key}: {value}")
    
    # Stop engine
    engine.stop()
    
    print("\n✅ Demo complete")


if __name__ == "__main__":
    main()
