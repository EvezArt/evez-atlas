"""
Audit Logger - HandshakeOS-E

Centralized audit logging for complete system accountability and transparency.

Design Philosophy:
- Centralized: Single source of truth for all system actions
- Immutable: Logs cannot be modified after creation (append-only)
- Comprehensive: Captures all significant system activities
- Queryable: Efficient filtering and search capabilities
- Verifiable: Integrity checks to detect tampering
- Entity-traceable: Complete history for any bounded identity

For the stranger who wears your shell tomorrow:
The AuditLogger is the system's memory. Every significant action, event, intent,
hypothesis update, and test execution should be logged here. This creates an
immutable audit trail that enables:
1. Understanding what happened (forensics)
2. Who did what (attribution)
3. Detecting anomalies (security)
4. Learning patterns (analytics)
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4
import json
import hashlib
import os


@dataclass
class AuditEntry:
    """
    Single audit log entry.
    
    Attributes:
        entry_id: Unique identifier for this entry
        timestamp: When the action occurred
        log_type: Type of log (action, event, intent, hypothesis, test)
        entity_id: ID of entity that performed action
        action: Description of action
        details: Additional details
        hash: Hash of entry content for integrity verification
    """
    entry_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    log_type: str = "action"  # action, event, intent, hypothesis, test
    entity_id: str = ""
    action: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    hash: str = ""
    
    def __post_init__(self):
        """Compute hash if not provided."""
        if not self.hash:
            self.hash = self._compute_hash()
    
    def _compute_hash(self) -> str:
        """
        Compute SHA-256 hash of entry content.
        
        Returns:
            Hex string of hash
        """
        content = f"{self.entry_id}{self.timestamp.isoformat()}{self.log_type}{self.entity_id}{self.action}{json.dumps(self.details, sort_keys=True)}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    def verify_integrity(self) -> bool:
        """
        Verify entry hasn't been tampered with.
        
        Returns:
            True if hash matches content
        """
        return self.hash == self._compute_hash()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'entry_id': self.entry_id,
            'timestamp': self.timestamp.isoformat(),
            'log_type': self.log_type,
            'entity_id': self.entity_id,
            'action': self.action,
            'details': self.details,
            'hash': self.hash,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AuditEntry':
        """Create AuditEntry from dictionary."""
        if isinstance(data.get('timestamp'), str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)


class AuditLogger:
    """
    Centralized audit logger (singleton pattern).
    
    The AuditLogger provides a single point for recording all system activities.
    It maintains an append-only log with integrity verification.
    
    Key Features:
    1. Singleton: One logger instance per system
    2. Append-only: Immutable audit trail
    3. Type-aware: Different log types (action, event, intent, etc.)
    4. Queryable: Filter by entity, type, time range
    5. Verifiable: Hash-based integrity checking
    6. Entity history: Get all actions by a specific entity
    
    Example Usage:
        >>> from src.mastra.core import AuditLogger
        >>> 
        >>> # Get logger instance
        >>> logger = AuditLogger(log_path="data/audit/audit.jsonl")
        >>> 
        >>> # Log an action
        >>> logger.log_action(
        ...     entity_id="agent_001",
        ...     action="read_file",
        ...     details={"file": "data.json", "bytes": 1024}
        ... )
        >>> 
        >>> # Log an event
        >>> logger.log_event(
        ...     event_id="evt_123",
        ...     entity_id="user_alice",
        ...     event_type="user_query"
        ... )
        >>> 
        >>> # Query logs
        >>> recent = logger.query_logs(
        ...     entity_id="agent_001",
        ...     log_type="action",
        ...     limit=10
        ... )
        >>> 
        >>> # Verify integrity
        >>> is_valid, invalid_count = logger.verify_log_integrity()
    """
    
    _instance = None
    
    def __new__(cls, log_path: str = "data/audit/audit.jsonl"):
        """Singleton pattern: only one instance per log path."""
        if cls._instance is None:
            cls._instance = super(AuditLogger, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, log_path: str = "data/audit/audit.jsonl"):
        """Initialize audit logger."""
        if self._initialized:
            return
        
        self.log_path = log_path
        self._ensure_log_directory()
        self._initialized = True
    
    def _ensure_log_directory(self):
        """Ensure log directory exists."""
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
    
    def _append_entry(self, entry: AuditEntry):
        """
        Append entry to log file.
        
        Args:
            entry: AuditEntry to append
        """
        with open(self.log_path, 'a') as f:
            json.dump(entry.to_dict(), f)
            f.write('\n')
    
    def log_action(self,
                   entity_id: str,
                   action: str,
                   details: Optional[Dict[str, Any]] = None) -> str:
        """
        Log a general action.
        
        Args:
            entity_id: ID of entity performing action
            action: Description of action
            details: Optional additional details
            
        Returns:
            Entry ID
        """
        entry = AuditEntry(
            log_type="action",
            entity_id=entity_id,
            action=action,
            details=details or {}
        )
        self._append_entry(entry)
        return entry.entry_id
    
    def log_event(self,
                  event_id: str,
                  entity_id: str,
                  event_type: str,
                  details: Optional[Dict[str, Any]] = None) -> str:
        """
        Log a UniversalEventRecord.
        
        Args:
            event_id: ID of the event
            entity_id: ID of entity that created event
            event_type: Type of event
            details: Optional event details
            
        Returns:
            Entry ID
        """
        entry = AuditEntry(
            log_type="event",
            entity_id=entity_id,
            action=f"created_event:{event_type}",
            details={
                'event_id': event_id,
                'event_type': event_type,
                **(details or {})
            }
        )
        self._append_entry(entry)
        return entry.entry_id
    
    def log_intent(self,
                   intent_id: str,
                   entity_id: str,
                   goal: str,
                   status: str = "created",
                   details: Optional[Dict[str, Any]] = None) -> str:
        """
        Log an IntentToken.
        
        Args:
            intent_id: ID of the intent
            entity_id: ID of entity that created intent
            goal: Intent goal
            status: Intent status (created, completed, failed)
            details: Optional intent details
            
        Returns:
            Entry ID
        """
        entry = AuditEntry(
            log_type="intent",
            entity_id=entity_id,
            action=f"intent_{status}",
            details={
                'intent_id': intent_id,
                'goal': goal,
                'status': status,
                **(details or {})
            }
        )
        self._append_entry(entry)
        return entry.entry_id
    
    def log_hypothesis_update(self,
                              hypothesis_id: str,
                              entity_id: str,
                              update_type: str,
                              details: Optional[Dict[str, Any]] = None) -> str:
        """
        Log a ParallelHypotheses update.
        
        Args:
            hypothesis_id: ID of the hypothesis
            entity_id: ID of entity that updated hypothesis
            update_type: Type of update (created, tested, confidence_updated, etc.)
            details: Optional update details
            
        Returns:
            Entry ID
        """
        entry = AuditEntry(
            log_type="hypothesis",
            entity_id=entity_id,
            action=f"hypothesis_{update_type}",
            details={
                'hypothesis_id': hypothesis_id,
                'update_type': update_type,
                **(details or {})
            }
        )
        self._append_entry(entry)
        return entry.entry_id
    
    def log_test_execution(self,
                          test_id: str,
                          entity_id: str,
                          test_name: str,
                          passed: Optional[bool],
                          details: Optional[Dict[str, Any]] = None) -> str:
        """
        Log a TestObject execution.
        
        Args:
            test_id: ID of the test
            entity_id: ID of entity that executed test
            test_name: Name of test
            passed: Whether test passed
            details: Optional test details
            
        Returns:
            Entry ID
        """
        status = "passed" if passed else "failed" if passed is False else "error"
        entry = AuditEntry(
            log_type="test",
            entity_id=entity_id,
            action=f"test_{status}",
            details={
                'test_id': test_id,
                'test_name': test_name,
                'passed': passed,
                **(details or {})
            }
        )
        self._append_entry(entry)
        return entry.entry_id
    
    def query_logs(self,
                   entity_id: Optional[str] = None,
                   log_type: Optional[str] = None,
                   action: Optional[str] = None,
                   start_time: Optional[datetime] = None,
                   end_time: Optional[datetime] = None,
                   limit: Optional[int] = None) -> List[AuditEntry]:
        """
        Query audit logs with filters.
        
        Args:
            entity_id: Filter by entity ID
            log_type: Filter by log type
            action: Filter by action
            start_time: Filter by start time
            end_time: Filter by end time
            limit: Maximum number of results
            
        Returns:
            List of matching AuditEntry objects
        """
        results = []
        
        try:
            with open(self.log_path, 'r') as f:
                for line in f:
                    if not line.strip():
                        continue
                    
                    data = json.loads(line)
                    entry = AuditEntry.from_dict(data)
                    
                    # Apply filters
                    if entity_id and entry.entity_id != entity_id:
                        continue
                    if log_type and entry.log_type != log_type:
                        continue
                    if action and entry.action != action:
                        continue
                    if start_time and entry.timestamp < start_time:
                        continue
                    if end_time and entry.timestamp > end_time:
                        continue
                    
                    results.append(entry)
                    
                    # Check limit
                    if limit and len(results) >= limit:
                        break
        except FileNotFoundError:
            pass
        
        return results
    
    def get_entity_history(self, entity_id: str, limit: Optional[int] = None) -> List[AuditEntry]:
        """
        Get complete action history for an entity.
        
        Args:
            entity_id: ID of entity
            limit: Maximum number of results
            
        Returns:
            List of AuditEntry objects for this entity
        """
        return self.query_logs(entity_id=entity_id, limit=limit)
    
    def verify_log_integrity(self) -> tuple[bool, int]:
        """
        Verify integrity of all log entries.
        
        Checks that each entry's hash matches its content.
        
        Returns:
            Tuple of (all_valid, invalid_count)
        """
        invalid_count = 0
        
        try:
            with open(self.log_path, 'r') as f:
                for line in f:
                    if not line.strip():
                        continue
                    
                    data = json.loads(line)
                    entry = AuditEntry.from_dict(data)
                    
                    if not entry.verify_integrity():
                        invalid_count += 1
        except FileNotFoundError:
            return True, 0
        
        return invalid_count == 0, invalid_count
    
    def get_log_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the audit log.
        
        Returns:
            Dict with statistics
        """
        stats = {
            'total_entries': 0,
            'by_type': {},
            'by_entity': {},
            'earliest': None,
            'latest': None,
        }
        
        try:
            with open(self.log_path, 'r') as f:
                for line in f:
                    if not line.strip():
                        continue
                    
                    data = json.loads(line)
                    entry = AuditEntry.from_dict(data)
                    
                    stats['total_entries'] += 1
                    
                    # Count by type
                    stats['by_type'][entry.log_type] = stats['by_type'].get(entry.log_type, 0) + 1
                    
                    # Count by entity
                    stats['by_entity'][entry.entity_id] = stats['by_entity'].get(entry.entity_id, 0) + 1
                    
                    # Track time range
                    if stats['earliest'] is None or entry.timestamp < stats['earliest']:
                        stats['earliest'] = entry.timestamp
                    if stats['latest'] is None or entry.timestamp > stats['latest']:
                        stats['latest'] = entry.timestamp
        except FileNotFoundError:
            pass
        
        return stats
    
    def clear_log(self):
        """
        Clear the audit log (USE WITH CAUTION).
        
        This is mainly for testing. In production, logs should be immutable.
        """
        if os.path.exists(self.log_path):
            os.remove(self.log_path)


if __name__ == "__main__":
    # Demo: Use audit logger
    print("🎯 AuditLogger Demo")
    print("=" * 50)
    
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        log_path = os.path.join(tmpdir, "audit", "audit.jsonl")
        
        # Create logger
        logger = AuditLogger(log_path=log_path)
        print(f"\n✅ Created AuditLogger")
        print(f"   Log Path: {log_path}")
        
        # Log various actions
        print(f"\n📝 Logging actions...")
        
        logger.log_action(
            entity_id="agent_001",
            action="read_file",
            details={"file": "data.json", "bytes": 1024}
        )
        
        logger.log_action(
            entity_id="agent_001",
            action="write_file",
            details={"file": "output.json", "bytes": 512}
        )
        
        logger.log_action(
            entity_id="user_alice",
            action="query_submitted",
            details={"query": "What is X?"}
        )
        
        # Log events
        print(f"   Logging events...")
        logger.log_event(
            event_id="evt_001",
            entity_id="agent_001",
            event_type="data_processed",
            details={"records": 100}
        )
        
        # Log intents
        print(f"   Logging intents...")
        logger.log_intent(
            intent_id="int_001",
            entity_id="agent_001",
            goal="Fetch user data",
            status="created"
        )
        
        logger.log_intent(
            intent_id="int_001",
            entity_id="agent_001",
            goal="Fetch user data",
            status="completed",
            details={"payoff": 0.85}
        )
        
        # Log hypothesis updates
        print(f"   Logging hypothesis updates...")
        logger.log_hypothesis_update(
            hypothesis_id="hyp_001",
            entity_id="agent_001",
            update_type="created",
            details={"confidence": 0.7}
        )
        
        # Log test executions
        print(f"   Logging test executions...")
        logger.log_test_execution(
            test_id="test_001",
            entity_id="agent_tester",
            test_name="API Health Check",
            passed=True,
            details={"execution_time_ms": 45}
        )
        
        logger.log_test_execution(
            test_id="test_002",
            entity_id="agent_tester",
            test_name="Database Connection",
            passed=False,
            details={"error": "Connection refused"}
        )
        
        print(f"   ✓ Logged multiple entries")
        
        # Query logs
        print(f"\n🔍 Querying logs...")
        
        # Get all actions by agent_001
        agent_logs = logger.get_entity_history("agent_001")
        print(f"   Agent_001 actions: {len(agent_logs)}")
        
        # Get all test executions
        test_logs = logger.query_logs(log_type="test")
        print(f"   Test executions: {len(test_logs)}")
        for log in test_logs:
            passed = log.details.get('passed')
            status = "✓" if passed else "✗"
            print(f"     {status} {log.details.get('test_name')}")
        
        # Get all intents
        intent_logs = logger.query_logs(log_type="intent")
        print(f"   Intent logs: {len(intent_logs)}")
        
        # Verify integrity
        print(f"\n🔒 Verifying log integrity...")
        is_valid, invalid_count = logger.verify_log_integrity()
        print(f"   Valid: {is_valid}")
        print(f"   Invalid entries: {invalid_count}")
        
        # Get statistics
        print(f"\n📊 Log Statistics:")
        stats = logger.get_log_statistics()
        print(f"   Total entries: {stats['total_entries']}")
        print(f"   By type:")
        for log_type, count in stats['by_type'].items():
            print(f"     - {log_type}: {count}")
        print(f"   By entity:")
        for entity, count in stats['by_entity'].items():
            print(f"     - {entity}: {count}")
        print(f"   Time range: {stats['earliest']} to {stats['latest']}")
        
        # Query with filters
        print(f"\n🔎 Advanced queries...")
        
        # Get only actions
        actions = logger.query_logs(log_type="action", limit=5)
        print(f"   Actions (limit 5): {len(actions)}")
        
        # Get specific entity's actions
        alice_logs = logger.query_logs(entity_id="user_alice")
        print(f"   User Alice's actions: {len(alice_logs)}")
        for log in alice_logs:
            print(f"     - {log.action}: {log.details}")
    
    print("\n" + "=" * 50)
    print("✅ Demo complete!")
