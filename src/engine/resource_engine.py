"""
Resource Engine - Self-running background task processor with resource management.

Features:
- Priority queue task processing
- Resource pool management (compute/storage/network/database)
- Auto-scaling based on load metrics
- Self-healing with exponential backoff
- Health check system
- State persistence to engine_state.jsonl with hash chaining
"""

import json
import time
import hashlib
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any
from collections import deque
from enum import Enum


class ResourceType(Enum):
    """Types of managed resources."""
    COMPUTE = "compute"
    STORAGE = "storage"
    NETWORK = "network"
    DATABASE = "database"


class TaskPriority(Enum):
    """Task priority levels."""
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3


class ResourcePool:
    """Manages a pool of resources with auto-scaling."""
    
    def __init__(self, resource_type: ResourceType, initial_capacity: int = 10):
        self.resource_type = resource_type
        self.capacity = initial_capacity
        self.allocated = 0
        self.waiting_requests = 0
        self.total_requests = 0
        self.failed_requests = 0
        
    def allocate(self, amount: int = 1) -> bool:
        """Attempt to allocate resources."""
        self.total_requests += 1
        if self.allocated + amount <= self.capacity:
            self.allocated += amount
            return True
        self.waiting_requests += 1
        self.failed_requests += 1
        return False
    
    def release(self, amount: int = 1):
        """Release allocated resources."""
        self.allocated = max(0, self.allocated - amount)
        if self.waiting_requests > 0:
            self.waiting_requests -= 1
    
    def scale_up(self, amount: int = 5):
        """Increase pool capacity."""
        self.capacity += amount
    
    def scale_down(self, amount: int = 5):
        """Decrease pool capacity (if safe)."""
        if self.capacity - amount >= self.allocated:
            self.capacity -= amount
    
    def get_utilization(self) -> float:
        """Get current utilization percentage."""
        if self.capacity == 0:
            return 0.0
        return (self.allocated / self.capacity) * 100
    
    def get_stats(self) -> Dict:
        """Get resource pool statistics."""
        return {
            'type': self.resource_type.value,
            'capacity': self.capacity,
            'allocated': self.allocated,
            'utilization': self.get_utilization(),
            'waiting': self.waiting_requests,
            'total_requests': self.total_requests,
            'failed_requests': self.failed_requests,
            'success_rate': ((self.total_requests - self.failed_requests) / self.total_requests * 100) 
                           if self.total_requests > 0 else 100.0
        }


class Task:
    """Represents a task to be processed."""
    
    def __init__(self, task_id: str, priority: TaskPriority, resource_type: ResourceType, 
                 resource_amount: int = 1, payload: Optional[Dict] = None):
        self.task_id = task_id
        self.priority = priority
        self.resource_type = resource_type
        self.resource_amount = resource_amount
        self.payload = payload or {}
        self.created_at = time.time()
        self.attempts = 0
        self.max_attempts = 3
        self.next_retry = None
        
    def should_retry(self) -> bool:
        """Check if task should be retried."""
        return self.attempts < self.max_attempts
    
    def calculate_backoff(self) -> float:
        """Calculate exponential backoff delay."""
        return min(300, (2 ** self.attempts) * 1)  # Max 5 minutes
    
    def __lt__(self, other):
        """Compare tasks by priority for heap ordering."""
        return self.priority.value < other.priority.value


class ResourceEngine:
    """
    Self-running resource engine with task processing and auto-scaling.
    
    Maintains resource pools, processes tasks with priority, and logs all
    state changes to engine_state.jsonl with hash chaining for audit.
    """
    
    def __init__(self, state_log_path: str = "src/memory/engine_state.jsonl"):
        self.state_log = Path(state_log_path)
        self.state_log.parent.mkdir(parents=True, exist_ok=True)
        
        # Resource pools
        self.pools = {
            ResourceType.COMPUTE: ResourcePool(ResourceType.COMPUTE, 10),
            ResourceType.STORAGE: ResourcePool(ResourceType.STORAGE, 100),
            ResourceType.NETWORK: ResourcePool(ResourceType.NETWORK, 20),
            ResourceType.DATABASE: ResourcePool(ResourceType.DATABASE, 5),
        }
        
        # Task queue (priority queue)
        self.task_queue = deque()
        self.retry_queue = deque()
        self.completed_tasks = []
        self.failed_tasks = []
        
        # Health tracking
        self.health_checks = {
            'cpu': 0.0,
            'memory': 0.0,
            'queue_depth': 0,
            'error_rate': 0.0,
        }
        self.health_thresholds = {
            'cpu': 80.0,
            'memory': 85.0,
            'queue_depth': 100,
            'error_rate': 10.0,
        }
        
        # Engine state
        self.running = False
        self.start_time = None
        self.total_tasks_processed = 0
        self.total_errors = 0
        
        # Hash chain state
        self.last_event_hash = None
        self._load_last_hash()
        
        # Auto-scaling state
        self.last_scale_check = time.time()
        self.scale_check_interval = 60  # Check every 60 seconds
        
        # Log engine initialization
        self._append_state_log({
            'event_type': 'engine_initialized',
            'timestamp': time.time(),
            'pools': {rt.value: pool.get_stats() for rt, pool in self.pools.items()}
        })
    
    def _load_last_hash(self):
        """Load the last event hash from the state log."""
        if self.state_log.exists():
            try:
                with open(self.state_log, 'r') as f:
                    lines = f.readlines()
                    if lines:
                        last_event = json.loads(lines[-1])
                        self.last_event_hash = last_event.get('event_hash')
            except Exception:
                self.last_event_hash = None
    
    def _calculate_event_hash(self, event: Dict) -> str:
        """Calculate SHA-256 hash for an event."""
        # Create a deterministic string from event data
        event_data = json.dumps(event, sort_keys=True)
        return hashlib.sha256(event_data.encode()).hexdigest()
    
    def _append_state_log(self, event: Dict):
        """Append event to state log with hash chaining."""
        event['parent_hash'] = self.last_event_hash
        event_hash = self._calculate_event_hash(event)
        event['event_hash'] = event_hash
        
        with open(self.state_log, 'a') as f:
            f.write(json.dumps(event) + '\n')
        
        self.last_event_hash = event_hash
    
    def submit_task(self, task: Task) -> bool:
        """Submit a task to the queue."""
        self.task_queue.append(task)
        self._append_state_log({
            'event_type': 'task_submitted',
            'timestamp': time.time(),
            'task_id': task.task_id,
            'priority': task.priority.value,
            'resource_type': task.resource_type.value,
        })
        return True
    
    def _process_task(self, task: Task) -> bool:
        """Process a single task."""
        task.attempts += 1
        
        # Try to allocate resources
        pool = self.pools[task.resource_type]
        if pool.allocate(task.resource_amount):
            try:
                # Simulate task processing
                time.sleep(0.01)  # Minimal processing time
                
                # Release resources
                pool.release(task.resource_amount)
                
                # Mark as completed
                self.completed_tasks.append(task)
                self.total_tasks_processed += 1
                
                self._append_state_log({
                    'event_type': 'task_completed',
                    'timestamp': time.time(),
                    'task_id': task.task_id,
                    'attempts': task.attempts,
                })
                
                return True
                
            except Exception as e:
                pool.release(task.resource_amount)
                self.total_errors += 1
                
                self._append_state_log({
                    'event_type': 'task_failed',
                    'timestamp': time.time(),
                    'task_id': task.task_id,
                    'attempts': task.attempts,
                    'error': str(e),
                })
                
                return False
        else:
            # Resource allocation failed, will retry
            return False
    
    def _process_queue(self):
        """Process tasks from the queue."""
        # Sort queue by priority
        self.task_queue = deque(sorted(self.task_queue, key=lambda t: t.priority.value))
        
        # Process tasks
        tasks_to_retry = []
        while self.task_queue:
            task = self.task_queue.popleft()
            
            if not self._process_task(task):
                # Task failed or resources unavailable
                if task.should_retry():
                    task.next_retry = time.time() + task.calculate_backoff()
                    tasks_to_retry.append(task)
                else:
                    self.failed_tasks.append(task)
                    self._append_state_log({
                        'event_type': 'task_permanently_failed',
                        'timestamp': time.time(),
                        'task_id': task.task_id,
                        'attempts': task.attempts,
                    })
        
        # Add failed tasks back to retry queue
        self.retry_queue.extend(tasks_to_retry)
    
    def _process_retries(self):
        """Process tasks in retry queue."""
        now = time.time()
        ready_tasks = []
        still_waiting = []
        
        for task in self.retry_queue:
            if task.next_retry and now >= task.next_retry:
                ready_tasks.append(task)
            else:
                still_waiting.append(task)
        
        self.retry_queue = deque(still_waiting)
        self.task_queue.extend(ready_tasks)
    
    def _check_auto_scaling(self):
        """Check if auto-scaling is needed."""
        now = time.time()
        if now - self.last_scale_check < self.scale_check_interval:
            return
        
        self.last_scale_check = now
        
        for resource_type, pool in self.pools.items():
            utilization = pool.get_utilization()
            
            # Scale up if utilization > 80%
            if utilization > 80.0 and pool.waiting_requests > 0:
                pool.scale_up()
                self._append_state_log({
                    'event_type': 'auto_scaled_up',
                    'timestamp': now,
                    'resource_type': resource_type.value,
                    'new_capacity': pool.capacity,
                    'reason': f'utilization={utilization:.1f}%',
                })
            
            # Scale down if utilization < 30%
            elif utilization < 30.0 and pool.capacity > 5:
                pool.scale_down()
                self._append_state_log({
                    'event_type': 'auto_scaled_down',
                    'timestamp': now,
                    'resource_type': resource_type.value,
                    'new_capacity': pool.capacity,
                    'reason': f'utilization={utilization:.1f}%',
                })
    
    def _update_health_checks(self):
        """Update health check metrics."""
        self.health_checks['queue_depth'] = len(self.task_queue) + len(self.retry_queue)
        
        # Calculate error rate
        if self.total_tasks_processed > 0:
            self.health_checks['error_rate'] = (self.total_errors / self.total_tasks_processed) * 100
        else:
            self.health_checks['error_rate'] = 0.0
        
        # Simulate CPU/memory (would use psutil in production)
        self.health_checks['cpu'] = sum(p.get_utilization() for p in self.pools.values()) / len(self.pools)
        self.health_checks['memory'] = self.health_checks['cpu'] * 0.8  # Approximate
    
    def is_healthy(self) -> bool:
        """Check if engine is healthy."""
        for metric, value in self.health_checks.items():
            threshold = self.health_thresholds[metric]
            if value > threshold:
                return False
        return True
    
    def get_status(self) -> Dict:
        """Get complete engine status."""
        return {
            'running': self.running,
            'uptime': time.time() - self.start_time if self.start_time else 0,
            'tasks_processed': self.total_tasks_processed,
            'tasks_queued': len(self.task_queue),
            'tasks_retrying': len(self.retry_queue),
            'tasks_failed': len(self.failed_tasks),
            'total_errors': self.total_errors,
            'health_checks': self.health_checks,
            'healthy': self.is_healthy(),
            'pools': {rt.value: pool.get_stats() for rt, pool in self.pools.items()}
        }
    
    def run_cycle(self):
        """Run one processing cycle."""
        if not self.running:
            return
        
        self._process_retries()
        self._process_queue()
        self._check_auto_scaling()
        self._update_health_checks()
    
    def start(self):
        """Start the resource engine."""
        if self.running:
            return
        
        self.running = True
        self.start_time = time.time()
        
        self._append_state_log({
            'event_type': 'engine_started',
            'timestamp': self.start_time,
        })
    
    def stop(self):
        """Stop the resource engine."""
        if not self.running:
            return
        
        self.running = False
        
        self._append_state_log({
            'event_type': 'engine_stopped',
            'timestamp': time.time(),
            'final_stats': self.get_status(),
        })
    
    def verify_hash_chain(self) -> bool:
        """Verify the integrity of the hash chain."""
        if not self.state_log.exists():
            return True
        
        with open(self.state_log, 'r') as f:
            events = [json.loads(line) for line in f if line.strip()]
        
        if not events:
            return True
        
        # Check first event has no parent
        if events[0].get('parent_hash') is not None:
            return False
        
        # Verify chain
        for i in range(1, len(events)):
            expected_parent = events[i-1].get('event_hash')
            actual_parent = events[i].get('parent_hash')
            
            if expected_parent != actual_parent:
                return False
        
        return True


if __name__ == "__main__":
    # Test the resource engine
    engine = ResourceEngine("src/memory/test_engine_state.jsonl")
    
    print("Resource Engine Test")
    print("=" * 80)
    
    # Start engine
    engine.start()
    
    # Submit some tasks
    for i in range(5):
        task = Task(
            task_id=f"task_{i}",
            priority=TaskPriority.NORMAL,
            resource_type=ResourceType.COMPUTE,
            resource_amount=1
        )
        engine.submit_task(task)
    
    # Process cycles
    for _ in range(10):
        engine.run_cycle()
        time.sleep(0.1)
    
    # Show status
    status = engine.get_status()
    print(json.dumps(status, indent=2))
    
    # Verify hash chain
    print(f"\nHash chain integrity: {'✓ VERIFIED' if engine.verify_hash_chain() else '✗ FAILED'}")
    
    # Stop engine
    engine.stop()
