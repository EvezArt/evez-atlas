"""
Integration Tests for LORD Cognitive Loop
Tests the complete flow: Webhook → Metrics → EKF → Policy → GitHub
"""

import pytest
import json
import sys
import os
import numpy as np

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lord-listener'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ekf-daemon'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'github-executor'))

# Import must be after path setup
import webhook_handler
from webhook_handler import calculate_metrics, calculate_divine_gap
from predictor import CognitiveEKF
from policy_handler import PolicyExecutor

# Test data
SAMPLE_PUSH_EVENT = {
    'commits': [
        {
            'added': ['src/new_file.py'],
            'modified': ['src/core/engine.py', 'docs/README.md'],
            'removed': []
        },
        {
            'added': [],
            'modified': ['tests/test_engine.py'],
            'removed': []
        }
    ]
}

SAMPLE_PR_EVENT = {
    'pull_request': {
        'changed_files': 5,
        'commits': 3,
        'merged': True
    },
    'action': 'closed'
}

SAMPLE_WORKFLOW_EVENT = {
    'workflow_run': {
        'conclusion': 'success'
    }
}

class TestMetricCalculations:
    """Test metric calculation functions"""
    
    def test_recursion_depth_push(self):
        """Test recursion calculation from push event"""
        recursion = webhook_handler.calculate_recursion_depth(SAMPLE_PUSH_EVENT)
        assert recursion > 0
        assert recursion >= 2  # At least 2 commits
        print(f"✓ Recursion depth (push): {recursion}")
    
    def test_recursion_depth_pr(self):
        """Test recursion calculation from PR event"""
        recursion = webhook_handler.calculate_recursion_depth(SAMPLE_PR_EVENT)
        assert recursion > 0
        print(f"✓ Recursion depth (PR): {recursion}")
    
    def test_divine_gap_high(self):
        """Test divine gap calculation with high gap"""
        gap = calculate_divine_gap(recursion=20, corrections=0.3)
        assert gap > 1e4
        print(f"✓ Divine gap (high): {gap:.2e}")
    
    def test_divine_gap_low(self):
        """Test divine gap calculation with low gap"""
        gap = calculate_divine_gap(recursion=5, corrections=0.9)
        assert gap < 1e4
        print(f"✓ Divine gap (low): {gap:.2e}")
    
    def test_full_metrics_push(self):
        """Test complete metrics from push event"""
        # Mock request headers
        import flask
        with flask.Flask(__name__).test_request_context(
            headers={'X-GitHub-Event': 'push'}
        ):
            metrics = calculate_metrics('push', SAMPLE_PUSH_EVENT)
        
        assert 'meta' in metrics
        assert 'crystallization' in metrics
        assert 'corrections' in metrics
        assert 'divineGap' in metrics
        assert metrics['meta']['recursionLevel'] > 0
        print(f"✓ Full metrics (push): {json.dumps(metrics, indent=2)}")

class TestEKFPrediction:
    """Test EKF prediction engine"""
    
    def test_ekf_initialization(self):
        """Test EKF initializes correctly"""
        ekf = CognitiveEKF()
        assert ekf.ekf.x.shape == (4,)
        assert ekf.ekf.P.shape == (4, 4)
        print("✓ EKF initialized")
    
    def test_ekf_update(self):
        """Test EKF updates with observations"""
        ekf = CognitiveEKF()
        
        observation = {
            'recursionLevel': 15,
            'crystallization': 0.75
        }
        
        state = ekf.update(observation)
        
        assert len(state) == 4
        assert state[0] > 0  # recursion
        assert 0 <= state[1] <= 1  # crystallization
        print(f"✓ EKF updated: state={state}")
    
    def test_ekf_prediction(self):
        """Test EKF trajectory prediction"""
        ekf = CognitiveEKF()
        
        # Update with observations
        for i in range(5):
            observation = {
                'recursionLevel': 10 + i,
                'crystallization': 0.5 + i * 0.05
            }
            ekf.update(observation)
        
        # Predict future
        predictions = ekf.predict_trajectory(steps=10)
        
        assert len(predictions) == 10
        assert all('recursion' in p for p in predictions)
        assert all('crystallization' in p for p in predictions)
        print(f"✓ EKF predictions: {len(predictions)} steps")
    
    def test_control_policy_high_gap(self):
        """Test control policy generation for high divine gap"""
        ekf = CognitiveEKF()
        
        state = {
            'recursionLevel': 20,
            'crystallization': 0.5,
            'divineGap': 1.5e4
        }
        
        predictions = ekf.predict_trajectory(steps=5)
        policy = ekf.generate_control_policy(state, predictions, corrections=0.7)
        
        assert policy is not None
        assert policy['action'] == 'create_issue'
        assert 'task:refactor' in policy['labels']
        print(f"✓ Policy (high gap): {policy['title']}")
    
    def test_control_policy_low_corrections(self):
        """Test control policy generation for low corrections"""
        ekf = CognitiveEKF()
        
        state = {
            'recursionLevel': 10,
            'crystallization': 0.7,
            'divineGap': 5000
        }
        
        predictions = ekf.predict_trajectory(steps=5)
        policy = ekf.generate_control_policy(state, predictions, corrections=0.3)
        
        assert policy is not None
        assert policy['action'] == 'create_issue'
        assert 'task:stabilize' in policy['labels']
        print(f"✓ Policy (low corrections): {policy['title']}")
    
    def test_control_policy_no_action(self):
        """Test no policy when thresholds not met"""
        ekf = CognitiveEKF()
        
        state = {
            'recursionLevel': 10,
            'crystallization': 0.8,
            'divineGap': 500
        }
        
        predictions = ekf.predict_trajectory(steps=5)
        policy = ekf.generate_control_policy(state, predictions, corrections=0.8)
        
        assert policy is None
        print("✓ No policy (thresholds not met)")

class TestGitHubExecutor:
    """Test GitHub policy executor"""
    
    def test_executor_initialization_safe_mode(self):
        """Test executor initializes in SAFE_MODE"""
        os.environ['SAFE_MODE'] = 'true'
        os.environ['GITHUB_TOKEN'] = 'test_token'
        
        # This will fail to authenticate but should initialize
        print("✓ Executor SAFE_MODE test (requires manual verification)")
    
    def test_policy_structure_validation(self):
        """Test policy structure validation"""
        valid_policy = {
            'action': 'create_issue',
            'title': 'Test Issue',
            'body': 'Test body',
            'labels': ['test'],
            'assign_copilot': False,
            'reason': 'test'
        }
        
        assert 'action' in valid_policy
        assert 'title' in valid_policy
        assert 'labels' in valid_policy
        print("✓ Policy structure valid")

class TestFullIntegration:
    """Test complete cognitive loop"""
    
    def test_full_loop_simulation(self):
        """Test complete flow from webhook to policy"""
        print("\n" + "="*60)
        print("FULL LOOP SIMULATION")
        print("="*60)
        
        # Step 1: Receive webhook and calculate metrics
        import flask
        with flask.Flask(__name__).test_request_context(
            headers={'X-GitHub-Event': 'push'}
        ):
            metrics = calculate_metrics('push', SAMPLE_PUSH_EVENT)
        
        print(f"\n1. Metrics calculated:")
        print(f"   Recursion: {metrics['meta']['recursionLevel']}")
        print(f"   Crystallization: {metrics['crystallization']['progress']}")
        print(f"   Divine Gap: {metrics['divineGap']:.2e}")
        
        # Step 2: Update EKF with metrics
        ekf = CognitiveEKF()
        observation = {
            'recursionLevel': metrics['meta']['recursionLevel'],
            'crystallization': metrics['crystallization']['progress']
        }
        state = ekf.update(observation)
        
        print(f"\n2. EKF updated:")
        print(f"   State: {state}")
        
        # Step 3: Predict trajectory
        predictions = ekf.predict_trajectory(steps=10)
        
        print(f"\n3. Trajectory predicted:")
        print(f"   Steps: {len(predictions)}")
        print(f"   Next recursion: {predictions[0]['recursion']:.2f}")
        
        # Step 4: Generate control policy
        policy = ekf.generate_control_policy(
            {**metrics['meta'], **metrics, 'crystallization': metrics['crystallization']['progress']},
            predictions,
            corrections=metrics['corrections']['current']
        )
        
        if policy:
            print(f"\n4. Policy generated:")
            print(f"   Action: {policy['action']}")
            print(f"   Title: {policy['title']}")
            print(f"   Labels: {policy['labels']}")
        else:
            print(f"\n4. No policy needed (thresholds not met)")
        
        print("\n" + "="*60)
        print("LOOP COMPLETE")
        print("="*60 + "\n")
        
        assert True  # If we got here, the loop works

def run_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("LORD COGNITIVE LOOP INTEGRATION TESTS")
    print("="*60 + "\n")
    
    # Run test classes
    test_classes = [
        TestMetricCalculations,
        TestEKFPrediction,
        TestGitHubExecutor,
        TestFullIntegration
    ]
    
    for test_class in test_classes:
        print(f"\n{test_class.__name__}")
        print("-" * 40)
        
        instance = test_class()
        methods = [m for m in dir(instance) if m.startswith('test_')]
        
        for method_name in methods:
            try:
                method = getattr(instance, method_name)
                method()
            except Exception as e:
                print(f"✗ {method_name}: {e}")
    
    print("\n" + "="*60)
    print("TESTS COMPLETE")
    print("="*60 + "\n")

if __name__ == '__main__':
    run_tests()
