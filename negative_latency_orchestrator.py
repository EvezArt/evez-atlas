"""
Negative Latency System Integration

Orchestrates all subsystems: EKF prediction, LORD rendering, GitHub execution,
content generation, and revenue staging.
"""

import sys
import os
import time
import json
from typing import Dict, Any, Optional
import threading

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import with correct module paths
import importlib.util

def import_module_from_file(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

base_dir = os.path.dirname(os.path.abspath(__file__))
ekf_module = import_module_from_file('negative_latency', os.path.join(base_dir, 'ekf-daemon', 'negative_latency.py'))
github_module = import_module_from_file('speculative_execution', os.path.join(base_dir, 'github-executor', 'speculative_execution.py'))
content_module = import_module_from_file('predictive_generator', os.path.join(base_dir, 'content-farm', 'predictive_generator.py'))
revenue_module = import_module_from_file('staged_monetization', os.path.join(base_dir, 'revenue-farm', 'staged', 'staged_monetization.py'))

NegativeLatencyEngine = ekf_module.NegativeLatencyEngine
NegativeLatencySafety = ekf_module.NegativeLatencySafety
SpeculativeExecutor = github_module.SpeculativeExecutor
PredictiveContentFarm = content_module.PredictiveContentFarm
StagedRevenueActions = revenue_module.StagedRevenueActions


class NegativeLatencyOrchestrator:
    """
    Main orchestrator for the entire negative latency system
    """
    
    def __init__(self, safe_mode: bool = True):
        """
        Initialize the orchestrator and all subsystems
        
        Args:
            safe_mode: Enable SAFE_MODE across all systems
        """
        self.safe_mode = safe_mode
        
        print("=" * 70)
        print("NEGATIVE LATENCY SYSTEM - Orchestrator Initializing")
        print("=" * 70)
        print(f"\n🛡️  SAFE_MODE: {'ENABLED' if safe_mode else 'DISABLED'}")
        print()
        
        # Initialize subsystems
        print("🔧 Initializing subsystems...")
        
        self.ekf_engine = NegativeLatencyEngine(
            horizon=10,
            cache_size=100,
            safe_mode=safe_mode
        )
        
        self.safety_system = NegativeLatencySafety(
            safety_threshold=0.15
        )
        
        self.github_executor = SpeculativeExecutor(
            safe_mode=safe_mode,
            min_confidence=0.85
        )
        
        self.content_farm = PredictiveContentFarm(
            buffer_size=50,
            safe_mode=safe_mode
        )
        
        self.revenue_stager = StagedRevenueActions(
            safe_mode=safe_mode
        )
        
        # Coordination state
        self.running = False
        self.coordination_thread: Optional[threading.Thread] = None
        
        print("✅ All subsystems initialized\n")
    
    def start(self):
        """Start all subsystems"""
        if self.running:
            print("⚠️  System already running")
            return
        
        print("🚀 Starting Negative Latency System...")
        print("-" * 70)
        
        # Start EKF prediction engine
        print("1️⃣  Starting EKF Trajectory Prediction Engine...")
        self.ekf_engine.start()
        time.sleep(1)
        
        # Start content farm
        print("2️⃣  Starting Predictive Content Farm...")
        self.content_farm.start()
        time.sleep(1)
        
        # Start coordination loop
        print("3️⃣  Starting Coordination Loop...")
        self.running = True
        self.coordination_thread = threading.Thread(target=self._coordination_loop, daemon=True)
        self.coordination_thread.start()
        
        print("\n✅ All systems operational - Negative latency active!")
        print("=" * 70)
    
    def stop(self):
        """Stop all subsystems"""
        print("\n" + "=" * 70)
        print("🛑 Stopping Negative Latency System...")
        print("-" * 70)
        
        self.running = False
        
        if self.coordination_thread:
            self.coordination_thread.join(timeout=5.0)
        
        self.ekf_engine.stop()
        self.content_farm.stop()
        
        print("✅ All systems stopped")
        print("=" * 70)
    
    def _coordination_loop(self):
        """
        Coordination loop that synchronizes all subsystems
        """
        while self.running:
            try:
                # Get current predictions from EKF
                if len(self.ekf_engine.trajectory_cache) > 0:
                    latest_trajectory = self.ekf_engine.trajectory_cache[-1]
                    
                    # Stage GitHub actions for predicted futures
                    self.github_executor.stage_future_actions(
                        trajectory=latest_trajectory.trajectory,
                        base_state=latest_trajectory.base_state,
                        confidence=latest_trajectory.confidence
                    )
                    
                    # Pre-generate revenue products for milestones
                    self.revenue_stager.pre_generate_products(
                        trajectory=latest_trajectory.trajectory
                    )
                
                # Coordination runs every 30 seconds
                time.sleep(30)
                
            except Exception as e:
                print(f"❌ Error in coordination loop: {e}")
                time.sleep(30)
    
    def handle_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle an event with negative latency (instant response)
        
        Args:
            event: Event to handle
        
        Returns:
            Response with timing information
        """
        start_time = time.time()
        
        # Get instant response from EKF engine
        policy = self.ekf_engine.instant_response(event)
        
        latency = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        return {
            'policy': policy,
            'latency_ms': latency,
            'cached': policy is not None and latency < 100,
            'safe_mode': self.safe_mode
        }
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get comprehensive system metrics"""
        return {
            'ekf_engine': self.ekf_engine.get_metrics(),
            'github_executor': self.github_executor.get_metrics(),
            'content_farm': self.content_farm.get_metrics(),
            'revenue_stager': self.revenue_stager.get_metrics(),
            'system': {
                'running': self.running,
                'safe_mode': self.safe_mode
            }
        }
    
    def print_dashboard(self):
        """Print a monitoring dashboard"""
        metrics = self.get_system_metrics()
        
        print("\n" + "=" * 70)
        print("📊 NEGATIVE LATENCY SYSTEM - Live Metrics")
        print("=" * 70)
        
        # EKF Metrics
        ekf = metrics['ekf_engine']
        print(f"\n🔮 EKF Prediction Engine:")
        print(f"   Cache Hit Rate: {ekf['cache_hit_rate']*100:.1f}%")
        print(f"   Cached Trajectories: {ekf['cached_trajectories']}")
        print(f"   Staged Policies: {ekf['staged_policies']}")
        print(f"   Current Confidence: {ekf['current_confidence']:.2f}")
        
        # GitHub Executor Metrics
        github = metrics['github_executor']
        print(f"\n⚡ GitHub Speculative Executor:")
        print(f"   Staged Actions: {github['total_staged']}")
        print(f"   Executed: {github['total_executed']}")
        print(f"   Rolled Back: {github['total_rolled_back']}")
        print(f"   False Positives: {github['false_positives']}")
        
        # Content Farm Metrics
        content = metrics['content_farm']
        print(f"\n📝 Predictive Content Farm:")
        print(f"   Generated: {content['total_generated']}")
        print(f"   Posted: {content['total_posted']}")
        print(f"   Cache Hit Rate: {content['cache_hit_rate']*100:.1f}%")
        print(f"   Buffered Content: {content['buffered_content']}")
        
        # Revenue Stager Metrics
        revenue = metrics['revenue_stager']
        print(f"\n💰 Revenue Action Stager:")
        print(f"   Staged Products: {revenue['total_staged_products']}")
        print(f"   Launched: {revenue['total_launched_products']}")
        print(f"   Total Revenue: ${revenue['total_revenue_tracked']:.2f}")
        
        # System Status
        system = metrics['system']
        print(f"\n🛡️  System Status:")
        print(f"   Running: {'✅ Yes' if system['running'] else '❌ No'}")
        print(f"   SAFE_MODE: {'✅ Enabled' if system['safe_mode'] else '⚠️  Disabled'}")
        
        print("\n" + "=" * 70)


def demo():
    """
    Comprehensive demo of the negative latency system
    """
    # Initialize orchestrator with SAFE_MODE
    orchestrator = NegativeLatencyOrchestrator(safe_mode=True)
    
    try:
        # Start all systems
        orchestrator.start()
        
        # Let systems build up predictions
        print("\n⏳ Building prediction cache (10 seconds)...")
        time.sleep(10)
        
        # Show initial dashboard
        orchestrator.print_dashboard()
        
        # Simulate some events
        print("\n📨 Simulating trigger events...")
        for i in range(5):
            event = {
                'event_id': i,
                'type': 'test_event',
                'timestamp': time.time()
            }
            
            response = orchestrator.handle_event(event)
            
            print(f"\n   Event {i}:")
            print(f"      Latency: {response['latency_ms']:.2f}ms")
            print(f"      Cached: {'⚡ Yes' if response['cached'] else '⏱️  No'}")
            
            time.sleep(2)
        
        # Wait a bit more for content generation
        print("\n⏳ Waiting for more predictions (10 seconds)...")
        time.sleep(10)
        
        # Show final dashboard
        orchestrator.print_dashboard()
        
        # Performance summary
        metrics = orchestrator.get_system_metrics()
        ekf_hit_rate = metrics['ekf_engine']['cache_hit_rate']
        content_hit_rate = metrics['content_farm']['cache_hit_rate']
        
        print("\n" + "=" * 70)
        print("📈 PERFORMANCE SUMMARY")
        print("=" * 70)
        print(f"\n✅ Target: <100ms latency for cached responses")
        print(f"✅ Target: >80% cache hit rate")
        print(f"✅ Target: >85% prediction accuracy")
        print(f"✅ Target: Zero false positives")
        
        print(f"\n📊 Achieved:")
        print(f"   EKF Cache Hit Rate: {ekf_hit_rate*100:.1f}%")
        print(f"   Content Cache Hit Rate: {content_hit_rate*100:.1f}%")
        print(f"   False Positives: {metrics['github_executor']['false_positives']}")
        
        if ekf_hit_rate > 0.8:
            print("\n🎉 SUCCESS: Cache hit rate exceeds 80% target!")
        
        print("\n" + "=" * 70)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    
    finally:
        # Stop all systems
        orchestrator.stop()
        
        print("\n✅ Demo complete")


if __name__ == "__main__":
    demo()
