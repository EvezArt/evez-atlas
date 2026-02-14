"""
EKF Prediction Daemon
Extended Kalman Filter for cognitive state prediction and control policy generation
"""

import numpy as np
from filterpy.kalman import ExtendedKalmanFilter
from collections import deque
import json
import os
import time
from datetime import datetime

# Configuration
SAFE_MODE = os.environ.get('SAFE_MODE', 'true').lower() == 'true'

class RingBuffer:
    """Ring buffer for trajectory caching"""
    def __init__(self, size=100):
        self.size = size
        self.buffer = deque(maxlen=size)
    
    def append(self, item):
        self.buffer.append(item)
    
    def get_all(self):
        return list(self.buffer)
    
    def get_latest(self, n=10):
        return list(self.buffer)[-n:]
    
    def clear(self):
        self.buffer.clear()

class CognitiveEKF:
    """
    Extended Kalman Filter for cognitive state estimation
    
    State vector: [recursion, crystallization, velocity, uncertainty]
    Observation: [recursion, crystallization]
    """
    
    def __init__(self):
        # Initialize EKF
        self.ekf = ExtendedKalmanFilter(dim_x=4, dim_z=2)
        
        # State: [recursion, crystallization, velocity, uncertainty]
        self.ekf.x = np.array([0., 0., 0., 1.])
        
        # State covariance (initial uncertainty)
        self.ekf.P = np.eye(4) * 100
        
        # Process noise
        self.ekf.Q = np.eye(4) * 0.1
        
        # Measurement noise
        self.ekf.R = np.eye(2) * 1.0
        
        # Trajectory cache
        self.trajectory_cache = RingBuffer(size=100)
        
        # History
        self.state_history = []
    
    def state_transition(self, x, dt=1.0):
        """
        State transition function: x(k+1) = f(x(k))
        
        Assumes linear dynamics with velocity:
        - recursion increases with velocity
        - crystallization increases with velocity
        - velocity decays slightly
        - uncertainty increases with time
        """
        F = np.array([
            [1, 0, dt, 0],      # recursion += velocity * dt
            [0, 1, dt, 0],      # crystallization += velocity * dt
            [0, 0, 0.95, 0],    # velocity decays
            [0, 0, 0, 1.05]     # uncertainty grows
        ])
        
        return F @ x
    
    def jacobian_F(self, x, dt=1.0):
        """Jacobian of state transition function"""
        return np.array([
            [1, 0, dt, 0],
            [0, 1, dt, 0],
            [0, 0, 0.95, 0],
            [0, 0, 0, 1.05]
        ])
    
    def measurement_function(self, x):
        """
        Measurement function: z = h(x)
        We observe recursion and crystallization directly
        """
        H = np.array([
            [1, 0, 0, 0],  # observe recursion
            [0, 1, 0, 0]   # observe crystallization
        ])
        return H @ x
    
    def jacobian_H(self, x):
        """Jacobian of measurement function"""
        return np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0]
        ])
    
    def update(self, observation):
        """
        Update EKF with new observation
        
        Args:
            observation: dict with 'recursionLevel' and 'crystallization'
        
        Note: Uses manual EKF implementation instead of filterpy's predict/update methods
        due to API compatibility issues with different filterpy versions. This ensures
        consistent behavior across Python 3.9-3.12 environments.
        """
        # Extract measurements
        z = np.array([
            observation.get('recursionLevel', 0),
            observation.get('crystallization', 0)
        ])
        
        # Predict step - manual calculation for compatibility
        F = self.jacobian_F(self.ekf.x)
        self.ekf.x = F @ self.ekf.x
        self.ekf.P = F @ self.ekf.P @ F.T + self.ekf.Q
        
        # Update step - manual calculation for compatibility
        H = self.jacobian_H(self.ekf.x)
        y = z - H @ self.ekf.x  # Innovation
        S = H @ self.ekf.P @ H.T + self.ekf.R  # Innovation covariance
        K = self.ekf.P @ H.T @ np.linalg.inv(S)  # Kalman gain
        
        self.ekf.x = self.ekf.x + K @ y
        self.ekf.P = (np.eye(4) - K @ H) @ self.ekf.P
        
        # Store state
        self.state_history.append({
            'timestamp': datetime.utcnow().isoformat(),
            'state': self.ekf.x.tolist(),
            'covariance': self.ekf.P.tolist()
        })
        
        return self.ekf.x
    
    def predict_trajectory(self, steps=10):
        """
        Predict future states (negative latency)
        
        Args:
            steps: Number of time steps to predict ahead
        
        Returns:
            List of predicted states
        """
        predictions = []
        
        # Start from current state
        x = self.ekf.x.copy()
        P = self.ekf.P.copy()
        
        for t in range(1, steps + 1):
            # Predict next state
            x = self.state_transition(x)
            
            # Predict covariance
            F = self.jacobian_F(x)
            P = F @ P @ F.T + self.ekf.Q
            
            predictions.append({
                'step': t,
                'recursion': float(x[0]),
                'crystallization': float(x[1]),
                'velocity': float(x[2]),
                'uncertainty': float(x[3]),
                'covariance': P.tolist()
            })
        
        # Cache predictions
        self.trajectory_cache.append({
            'timestamp': datetime.utcnow().isoformat(),
            'predictions': predictions
        })
        
        return predictions
    
    def generate_control_policy(self, state, predictions, corrections):
        """
        Convert predictions to GitHub actions
        
        Args:
            state: Current state dict
            predictions: List of predicted states
            corrections: Current correction rate
        
        Returns:
            Control policy dict or None
        """
        # Extract metrics
        recursion = state.get('recursionLevel', 0)
        crystallization = state.get('crystallization', 0)
        divine_gap = state.get('divineGap', 0)
        
        # Check thresholds
        if divine_gap > 1e4:
            # High gap - need refactoring
            return {
                'action': 'create_issue',
                'labels': ['task:refactor', 'urgency:high', 'lord:autonomous'],
                'title': f'High Divine Gap Detected: ΔΩ = {divine_gap:.2e}',
                'body': self.generate_issue_body(state, predictions, 'divine_gap'),
                'assign_copilot': True,
                'reason': 'divine_gap_threshold'
            }
        
        elif corrections < 0.5:
            # Low corrections - need stability
            return {
                'action': 'create_issue',
                'labels': ['task:stabilize', 'task:test', 'lord:autonomous'],
                'title': f'Low Correction Rate Detected: C(R) = {corrections:.2f}',
                'body': self.generate_issue_body(state, predictions, 'low_corrections'),
                'assign_copilot': True,
                'reason': 'low_corrections'
            }
        
        elif crystallization < 0.3 and predictions:
            # Check if crystallization is predicted to drop further
            future_cryst = [p['crystallization'] for p in predictions[:3]]
            if all(c < crystallization for c in future_cryst):
                return {
                    'action': 'create_issue',
                    'labels': ['task:documentation', 'lord:autonomous'],
                    'title': 'Crystallization Decline Predicted - Documentation Needed',
                    'body': self.generate_issue_body(state, predictions, 'declining_crystallization'),
                    'assign_copilot': True,
                    'reason': 'crystallization_decline'
                }
        
        return None  # No action needed
    
    def generate_issue_body(self, state, predictions, reason):
        """Generate issue body with metrics and predictions"""
        body = "## LORD Autonomous Issue\n\n"
        body += "This issue was automatically generated by the LORD cognitive loop.\n\n"
        body += f"**Trigger:** {reason}\n\n"
        body += "### Current State\n\n"
        body += f"- **Recursion Level:** {state.get('recursionLevel', 0):.2f}\n"
        body += f"- **Crystallization:** {state.get('crystallization', 0) * 100:.1f}%\n"
        body += f"- **Divine Gap (ΔΩ):** {state.get('divineGap', 0):.2e}\n"
        body += f"- **Correction Rate:** {state.get('corrections', {}).get('current', 0):.2f}\n"
        body += f"- **Entity Type:** {state.get('meta', {}).get('entityType', 'unknown')}\n\n"
        
        if predictions:
            body += "### Predicted Trajectory (Next 10 Steps)\n\n"
            body += "```\n"
            for p in predictions[:5]:
                body += f"Step {p['step']}: "
                body += f"Recursion={p['recursion']:.1f}, "
                body += f"Crystallization={p['crystallization'] * 100:.1f}%, "
                body += f"Velocity={p['velocity']:.3f}\n"
            body += "```\n\n"
        
        body += "### Recommended Actions\n\n"
        
        if reason == 'divine_gap':
            body += "1. Review recent changes for architectural issues\n"
            body += "2. Improve test coverage and validation\n"
            body += "3. Refactor complex components\n"
            body += "4. Add documentation for unclear areas\n"
        elif reason == 'low_corrections':
            body += "1. Run comprehensive test suite\n"
            body += "2. Review CI/CD pipeline for issues\n"
            body += "3. Add more integration tests\n"
            body += "4. Stabilize core functionality\n"
        elif reason == 'declining_crystallization':
            body += "1. Update documentation\n"
            body += "2. Add examples and tutorials\n"
            body += "3. Improve code comments\n"
            body += "4. Create architectural diagrams\n"
        
        body += "\n---\n"
        
        # Only add SAFE_MODE disclaimer if actually in SAFE_MODE
        if SAFE_MODE:
            body += "*This issue follows SAFE_MODE protocols and requires human approval before execution.*\n"
        
        return body

def daemon_loop():
    """Main daemon loop"""
    print("Starting EKF Daemon...")
    print(f"SAFE_MODE: {SAFE_MODE}")
    
    ekf = CognitiveEKF()
    
    while True:
        try:
            # In production, this would read from message queue or webhook listener
            # For now, simulate with sample data
            
            # Read latest metrics (would come from webhook listener)
            # observation = fetch_latest_metrics()
            
            # For demo, skip actual processing
            time.sleep(10)
            
        except KeyboardInterrupt:
            print("\nShutting down EKF Daemon...")
            break
        except Exception as e:
            print(f"Error in daemon loop: {e}")
            time.sleep(5)

if __name__ == '__main__':
    daemon_loop()
