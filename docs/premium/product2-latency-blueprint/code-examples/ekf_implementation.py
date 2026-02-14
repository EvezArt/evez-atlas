"""
Extended Kalman Filter Implementation for Negative Latency
Negative Latency Implementation Blueprint - Chapter 9

This module implements an EKF for predictive state estimation
with ring buffer optimization for real-time performance.
"""

import numpy as np
from collections import deque
from typing import Tuple, Optional, Callable


class ExtendedKalmanFilter:
    """
    Extended Kalman Filter for nonlinear state estimation
    
    Implements prediction and update steps for continuous state tracking
    with negative latency characteristics through predictive sampling.
    """
    
    def __init__(self, state_dim: int, measurement_dim: int):
        """
        Initialize EKF
        
        Args:
            state_dim: Dimension of state vector
            measurement_dim: Dimension of measurement vector
        """
        self.state_dim = state_dim
        self.measurement_dim = measurement_dim
        
        # State estimate
        self.x = np.zeros(state_dim)
        
        # Error covariance
        self.P = np.eye(state_dim)
        
        # Process noise covariance
        self.Q = np.eye(state_dim) * 0.01
        
        # Measurement noise covariance
        self.R = np.eye(measurement_dim) * 0.1
        
        # Prediction horizon
        self.prediction_steps = 5
        
    def predict(self, 
                f: Callable[[np.ndarray], np.ndarray],
                F_jacobian: Callable[[np.ndarray], np.ndarray],
                dt: float) -> np.ndarray:
        """
        Prediction step
        
        Args:
            f: State transition function x_k+1 = f(x_k)
            F_jacobian: Jacobian of f with respect to state
            dt: Time step
            
        Returns:
            Predicted state
        """
        # Predict state
        self.x = f(self.x)
        
        # Predict covariance
        F = F_jacobian(self.x)
        self.P = F @ self.P @ F.T + self.Q
        
        return self.x.copy()
    
    def update(self,
               z: np.ndarray,
               h: Callable[[np.ndarray], np.ndarray],
               H_jacobian: Callable[[np.ndarray], np.ndarray]) -> np.ndarray:
        """
        Update step with measurement
        
        Args:
            z: Measurement vector
            h: Measurement function z = h(x)
            H_jacobian: Jacobian of h with respect to state
            
        Returns:
            Updated state estimate
        """
        # Innovation
        y = z - h(self.x)
        
        # Innovation covariance
        H = H_jacobian(self.x)
        S = H @ self.P @ H.T + self.R
        
        # Kalman gain
        K = self.P @ H.T @ np.linalg.inv(S)
        
        # Update state
        self.x = self.x + K @ y
        
        # Update covariance
        I = np.eye(self.state_dim)
        self.P = (I - K @ H) @ self.P
        
        return self.x.copy()
    
    def predict_trajectory(self,
                          f: Callable[[np.ndarray], np.ndarray],
                          steps: int,
                          dt: float) -> np.ndarray:
        """
        Predict future trajectory (negative latency)
        
        Args:
            f: State transition function
            steps: Number of steps to predict
            dt: Time step
            
        Returns:
            Array of predicted states (steps x state_dim)
        """
        trajectory = np.zeros((steps, self.state_dim))
        x_pred = self.x.copy()
        
        for i in range(steps):
            x_pred = f(x_pred)
            trajectory[i] = x_pred
            
        return trajectory
    
    def get_confidence_interval(self, 
                               confidence: float = 0.95) -> Tuple[np.ndarray, np.ndarray]:
        """
        Get confidence interval for current state estimate
        
        Args:
            confidence: Confidence level (default 95%)
            
        Returns:
            Lower and upper bounds
        """
        from scipy.stats import chi2
        
        # Chi-square quantile for confidence level
        k = chi2.ppf(confidence, self.state_dim)
        
        # Eigenvalues of covariance
        eigvals = np.linalg.eigvalsh(self.P)
        std = np.sqrt(eigvals * k)
        
        lower = self.x - std
        upper = self.x + std
        
        return lower, upper


class RingBuffer:
    """
    High-performance ring buffer for state history
    Optimized for negative latency applications
    """
    
    def __init__(self, maxlen: int, dtype=np.float64):
        """
        Initialize ring buffer
        
        Args:
            maxlen: Maximum buffer size
            dtype: Data type for numpy array
        """
        self.maxlen = maxlen
        self.dtype = dtype
        self.buffer = deque(maxlen=maxlen)
        self.timestamps = deque(maxlen=maxlen)
        
    def append(self, data: np.ndarray, timestamp: float):
        """Add data to buffer"""
        self.buffer.append(data.copy())
        self.timestamps.append(timestamp)
    
    def get_recent(self, n: int) -> Tuple[list, list]:
        """Get n most recent items"""
        n = min(n, len(self.buffer))
        return list(self.buffer)[-n:], list(self.timestamps)[-n:]
    
    def get_range(self, start_time: float, end_time: float) -> Tuple[list, list]:
        """Get items in time range"""
        result_data = []
        result_times = []
        
        for data, ts in zip(self.buffer, self.timestamps):
            if start_time <= ts <= end_time:
                result_data.append(data)
                result_times.append(ts)
                
        return result_data, result_times
    
    def to_array(self) -> np.ndarray:
        """Convert buffer to numpy array"""
        return np.array(list(self.buffer), dtype=self.dtype)
    
    def clear(self):
        """Clear buffer"""
        self.buffer.clear()
        self.timestamps.clear()
    
    def __len__(self):
        return len(self.buffer)


class StateSpaceCache:
    """
    Efficient state space caching with LRU eviction
    """
    
    def __init__(self, max_size: int = 1000):
        """
        Initialize cache
        
        Args:
            max_size: Maximum number of cached states
        """
        self.max_size = max_size
        self.cache = {}
        self.access_order = deque()
        
    def get(self, key: str) -> Optional[np.ndarray]:
        """Get state from cache"""
        if key in self.cache:
            # Update access order
            self.access_order.remove(key)
            self.access_order.append(key)
            return self.cache[key].copy()
        return None
    
    def put(self, key: str, state: np.ndarray):
        """Put state in cache"""
        if key in self.cache:
            # Update existing
            self.cache[key] = state.copy()
            self.access_order.remove(key)
            self.access_order.append(key)
        else:
            # Add new
            if len(self.cache) >= self.max_size:
                # Evict least recently used
                lru_key = self.access_order.popleft()
                del self.cache[lru_key]
            
            self.cache[key] = state.copy()
            self.access_order.append(key)
    
    def invalidate(self, key: str):
        """Remove state from cache"""
        if key in self.cache:
            del self.cache[key]
            self.access_order.remove(key)
    
    def clear(self):
        """Clear entire cache"""
        self.cache.clear()
        self.access_order.clear()
    
    def size(self) -> int:
        """Get current cache size"""
        return len(self.cache)


# Example usage
if __name__ == "__main__":
    # Define state transition (constant velocity model)
    def f(x):
        # x = [position, velocity]
        dt = 0.1
        F = np.array([[1, dt], [0, 1]])
        return F @ x
    
    def F_jacobian(x):
        dt = 0.1
        return np.array([[1, dt], [0, 1]])
    
    # Define measurement function (position only)
    def h(x):
        return np.array([x[0]])
    
    def H_jacobian(x):
        return np.array([[1, 0]])
    
    # Initialize EKF
    ekf = ExtendedKalmanFilter(state_dim=2, measurement_dim=1)
    ekf.x = np.array([0.0, 1.0])  # Initial state: position=0, velocity=1
    
    # Initialize ring buffer
    buffer = RingBuffer(maxlen=100)
    
    # Simulate tracking
    print("🎯 Negative Latency EKF Simulation")
    print("-" * 50)
    
    for t in range(10):
        # Predict
        x_pred = ekf.predict(f, F_jacobian, dt=0.1)
        
        # Simulate measurement (position with noise)
        true_position = t * 0.1
        z = np.array([true_position + np.random.normal(0, 0.1)])
        
        # Update
        x_est = ekf.update(z, h, H_jacobian)
        
        # Store in buffer
        buffer.append(x_est, t * 0.1)
        
        # Predict trajectory (negative latency!)
        trajectory = ekf.predict_trajectory(f, steps=5, dt=0.1)
        
        print(f"Time {t:2d}: Est={x_est[0]:6.3f}, "
              f"Vel={x_est[1]:6.3f}, "
              f"Pred_5={trajectory[-1, 0]:6.3f}")
    
    print("-" * 50)
    print(f"✅ Buffer size: {len(buffer)}")
