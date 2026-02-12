"""
Reversibility Manager - HandshakeOS-E

Action reversal system for safe experimentation and recovery.

Design Philosophy:
- Reversible by default: Actions should be reversible unless explicitly marked irreversible
- Undo tracking: Complete record of how to reverse each action
- Dependency chains: Track which actions depend on others
- Idempotency: Actions can only be reversed once
- Safety: Prevent cascading failures from reversal
- Transparency: Full audit trail of reversals

For the stranger who wears your shell tomorrow:
The ReversibilityManager enables safe experimentation by tracking how to undo
actions. Each action can be marked as reversible with an undo procedure (either
a callable function or a command string). The manager tracks dependencies so
reversing one action doesn't break others. This is critical for:
1. Safe testing (can undo changes)
2. Error recovery (rollback on failure)
3. Learning (try things without permanent consequences)
4. Debugging (step backward through execution)
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Union
from uuid import uuid4
import json
import subprocess


@dataclass
class ReversalRecord:
    """
    Record of a reversible action with undo information.
    
    Attributes:
        record_id: Unique identifier for this record
        action_id: ID of the action (e.g., event_id, intent_id)
        action_type: Type of action (event, intent, file_write, etc.)
        action_description: Human-readable description
        reversible: Whether this action can be reversed
        undo_procedure: How to reverse (command string or callable name)
        undo_data: Data needed for reversal
        dependencies: List of action IDs this depends on
        reversed: Whether this has been reversed
        reversal_timestamp: When it was reversed
        reversal_by: Who reversed it
    """
    record_id: str = field(default_factory=lambda: str(uuid4()))
    action_id: str = ""
    action_type: str = ""
    action_description: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    # Reversibility
    reversible: bool = True
    undo_procedure: Optional[str] = None  # Command string or callable name
    undo_data: Dict[str, Any] = field(default_factory=dict)
    
    # Dependencies
    dependencies: List[str] = field(default_factory=list)  # Action IDs this depends on
    dependents: List[str] = field(default_factory=list)  # Action IDs that depend on this
    
    # Reversal tracking
    reversed: bool = False
    reversal_timestamp: Optional[datetime] = None
    reversal_by: Optional[str] = None
    reversal_result: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'record_id': self.record_id,
            'action_id': self.action_id,
            'action_type': self.action_type,
            'action_description': self.action_description,
            'created_at': self.created_at.isoformat(),
            'reversible': self.reversible,
            'undo_procedure': self.undo_procedure,
            'undo_data': self.undo_data,
            'dependencies': self.dependencies,
            'dependents': self.dependents,
            'reversed': self.reversed,
            'reversal_timestamp': self.reversal_timestamp.isoformat() if self.reversal_timestamp else None,
            'reversal_by': self.reversal_by,
            'reversal_result': self.reversal_result,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ReversalRecord':
        """Create ReversalRecord from dictionary."""
        if isinstance(data.get('created_at'), str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if isinstance(data.get('reversal_timestamp'), str):
            data['reversal_timestamp'] = datetime.fromisoformat(data['reversal_timestamp'])
        return cls(**data)


class ReversibilityManager:
    """
    Manager for tracking and reversing actions.
    
    The ReversibilityManager maintains a registry of reversible actions and
    provides methods to reverse them safely, handling dependencies and ensuring
    idempotency.
    
    Key Features:
    1. Action tracking: Record all reversible actions
    2. Dependency management: Track action dependencies
    3. Safe reversal: Check dependencies before reversing
    4. Idempotency: Actions can only be reversed once
    5. Audit trail: Complete history of reversals
    6. Multiple undo strategies: Commands or callables
    
    Example Usage:
        >>> from src.mastra.core import ReversibilityManager
        >>> 
        >>> # Create manager
        >>> manager = ReversibilityManager(log_path="data/reversibility/reversals.jsonl")
        >>> 
        >>> # Mark action as reversible
        >>> manager.mark_reversible(
        ...     action_id="evt_001",
        ...     action_type="file_write",
        ...     action_description="Created output.txt",
        ...     undo_procedure="rm output.txt",
        ...     undo_data={"file": "output.txt"}
        ... )
        >>> 
        >>> # Check if reversible
        >>> if manager.is_reversible("evt_001"):
        ...     result = manager.reverse_action("evt_001", "admin")
        >>> 
        >>> # Get reversal chain
        >>> chain = manager.get_reversal_chain("evt_001")
    """
    
    def __init__(self, log_path: str = "data/reversibility/reversals.jsonl"):
        """
        Initialize ReversibilityManager.
        
        Args:
            log_path: Path to JSONL log file
        """
        self.log_path = log_path
        self._records: Dict[str, ReversalRecord] = {}
        self._ensure_log_directory()
        self._load_records()
    
    def _ensure_log_directory(self):
        """Ensure log directory exists."""
        import os
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
    
    def _load_records(self):
        """Load records from log file."""
        try:
            with open(self.log_path, 'r') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        record = ReversalRecord.from_dict(data)
                        self._records[record.action_id] = record
        except FileNotFoundError:
            pass
    
    def _save_record(self, record: ReversalRecord):
        """
        Save record to log file.
        
        Args:
            record: ReversalRecord to save
        """
        with open(self.log_path, 'a') as f:
            json.dump(record.to_dict(), f)
            f.write('\n')
    
    def mark_reversible(self,
                       action_id: str,
                       action_type: str,
                       action_description: str,
                       undo_procedure: Optional[str] = None,
                       undo_data: Optional[Dict[str, Any]] = None,
                       dependencies: Optional[List[str]] = None) -> str:
        """
        Mark an action as reversible.
        
        Args:
            action_id: Unique ID of the action
            action_type: Type of action (event, intent, file_write, etc.)
            action_description: Human-readable description
            undo_procedure: Command or callable name to reverse action
            undo_data: Data needed for reversal
            dependencies: List of action IDs this depends on
            
        Returns:
            Record ID
        """
        record = ReversalRecord(
            action_id=action_id,
            action_type=action_type,
            action_description=action_description,
            reversible=True,
            undo_procedure=undo_procedure,
            undo_data=undo_data or {},
            dependencies=dependencies or []
        )
        
        # Update dependents in dependency records
        for dep_id in record.dependencies:
            if dep_id in self._records:
                if action_id not in self._records[dep_id].dependents:
                    self._records[dep_id].dependents.append(action_id)
                    self._save_record(self._records[dep_id])
        
        self._records[action_id] = record
        self._save_record(record)
        
        return record.record_id
    
    def mark_irreversible(self, action_id: str, reason: str = ""):
        """
        Mark an action as irreversible.
        
        Args:
            action_id: ID of the action
            reason: Reason why it's irreversible
        """
        if action_id in self._records:
            record = self._records[action_id]
            record.reversible = False
            record.undo_data['irreversible_reason'] = reason
            self._save_record(record)
    
    def is_reversible(self, action_id: str) -> bool:
        """
        Check if an action is reversible.
        
        Args:
            action_id: ID of the action
            
        Returns:
            True if reversible and not yet reversed
        """
        if action_id not in self._records:
            return False
        
        record = self._records[action_id]
        return record.reversible and not record.reversed
    
    def reverse_action(self,
                      action_id: str,
                      reversed_by: str,
                      force: bool = False) -> Dict[str, Any]:
        """
        Reverse an action.
        
        Args:
            action_id: ID of action to reverse
            reversed_by: Who is reversing (bounded identity ID)
            force: Force reversal even if there are dependents
            
        Returns:
            Dict with reversal result
        """
        result = {
            'success': False,
            'action_id': action_id,
            'message': '',
            'output': None,
        }
        
        # Check if action exists
        if action_id not in self._records:
            result['message'] = "Action not found"
            return result
        
        record = self._records[action_id]
        
        # Check if already reversed
        if record.reversed:
            result['message'] = "Action already reversed"
            return result
        
        # Check if reversible
        if not record.reversible:
            result['message'] = f"Action is not reversible: {record.undo_data.get('irreversible_reason', 'Unknown')}"
            return result
        
        # Check for dependents
        if record.dependents and not force:
            result['message'] = f"Action has {len(record.dependents)} dependents. Use force=True to override."
            result['dependents'] = record.dependents
            return result
        
        # Execute undo procedure
        if record.undo_procedure:
            try:
                # Execute as shell command
                process = subprocess.run(
                    record.undo_procedure,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if process.returncode == 0:
                    result['success'] = True
                    result['message'] = "Action reversed successfully"
                    result['output'] = process.stdout
                else:
                    result['message'] = f"Undo procedure failed: {process.stderr}"
                    result['output'] = process.stderr
                    
            except Exception as e:
                result['message'] = f"Reversal failed: {str(e)}"
        else:
            result['message'] = "No undo procedure specified"
        
        # Update record if successful
        if result['success']:
            record.reversed = True
            record.reversal_timestamp = datetime.utcnow()
            record.reversal_by = reversed_by
            record.reversal_result = result
            self._save_record(record)
        
        return result
    
    def get_reversal_chain(self, action_id: str) -> List[ReversalRecord]:
        """
        Get chain of actions that would need to be reversed.
        
        This finds all actions that depend on the given action (directly or indirectly).
        
        Args:
            action_id: ID of action
            
        Returns:
            List of ReversalRecords in reverse order (deepest dependents first)
        """
        if action_id not in self._records:
            return []
        
        chain = []
        visited = set()
        
        def _collect_dependents(aid: str):
            if aid in visited or aid not in self._records:
                return
            
            visited.add(aid)
            record = self._records[aid]
            
            # Recurse on dependents
            for dep_id in record.dependents:
                _collect_dependents(dep_id)
            
            chain.append(record)
        
        _collect_dependents(action_id)
        
        return chain
    
    def get_dependencies(self, action_id: str) -> List[ReversalRecord]:
        """
        Get actions that the given action depends on.
        
        Args:
            action_id: ID of action
            
        Returns:
            List of ReversalRecords for dependencies
        """
        if action_id not in self._records:
            return []
        
        record = self._records[action_id]
        return [self._records[dep_id] for dep_id in record.dependencies if dep_id in self._records]
    
    def get_record(self, action_id: str) -> Optional[ReversalRecord]:
        """
        Get reversal record for an action.
        
        Args:
            action_id: ID of action
            
        Returns:
            ReversalRecord or None
        """
        return self._records.get(action_id)
    
    def get_all_reversible(self) -> List[ReversalRecord]:
        """
        Get all reversible (not yet reversed) actions.
        
        Returns:
            List of ReversalRecords
        """
        return [r for r in self._records.values() if r.reversible and not r.reversed]
    
    def get_all_reversed(self) -> List[ReversalRecord]:
        """
        Get all reversed actions.
        
        Returns:
            List of ReversalRecords
        """
        return [r for r in self._records.values() if r.reversed]
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about reversibility.
        
        Returns:
            Dict with statistics
        """
        total = len(self._records)
        reversible = len([r for r in self._records.values() if r.reversible])
        reversed_count = len([r for r in self._records.values() if r.reversed])
        irreversible = total - reversible
        
        return {
            'total_actions': total,
            'reversible': reversible,
            'irreversible': irreversible,
            'reversed': reversed_count,
            'pending_reversal': reversible - reversed_count,
        }


if __name__ == "__main__":
    # Demo: Use reversibility manager
    print("🎯 ReversibilityManager Demo")
    print("=" * 50)
    
    import tempfile
    import os
    with tempfile.TemporaryDirectory() as tmpdir:
        log_path = os.path.join(tmpdir, "reversibility", "reversals.jsonl")
        
        # Create manager
        manager = ReversibilityManager(log_path=log_path)
        print(f"\n✅ Created ReversibilityManager")
        print(f"   Log Path: {log_path}")
        
        # Create test files
        test_file1 = os.path.join(tmpdir, "test1.txt")
        test_file2 = os.path.join(tmpdir, "test2.txt")
        
        # Mark actions as reversible
        print(f"\n📝 Marking actions as reversible...")
        
        # Action 1: Create file
        with open(test_file1, 'w') as f:
            f.write("Test content 1")
        
        manager.mark_reversible(
            action_id="action_001",
            action_type="file_create",
            action_description="Created test1.txt",
            undo_procedure=f"rm {test_file1}",
            undo_data={"file": test_file1}
        )
        print(f"   ✓ Marked action_001 (file create)")
        
        # Action 2: Create another file (depends on action 1)
        with open(test_file2, 'w') as f:
            f.write("Test content 2")
        
        manager.mark_reversible(
            action_id="action_002",
            action_type="file_create",
            action_description="Created test2.txt",
            undo_procedure=f"rm {test_file2}",
            undo_data={"file": test_file2},
            dependencies=["action_001"]
        )
        print(f"   ✓ Marked action_002 (file create, depends on action_001)")
        
        # Action 3: Irreversible action
        manager.mark_reversible(
            action_id="action_003",
            action_type="api_call",
            action_description="Sent email notification",
            undo_procedure=None,
            undo_data={"recipient": "user@example.com"}
        )
        manager.mark_irreversible("action_003", "Cannot unsend email")
        print(f"   ✓ Marked action_003 (irreversible)")
        
        # Check reversibility
        print(f"\n🔍 Checking reversibility...")
        for action_id in ["action_001", "action_002", "action_003"]:
            reversible = manager.is_reversible(action_id)
            status = "✓" if reversible else "✗"
            print(f"   {status} {action_id}: {'reversible' if reversible else 'not reversible'}")
        
        # Get reversal chain
        print(f"\n🔗 Reversal chain for action_001:")
        chain = manager.get_reversal_chain("action_001")
        for i, record in enumerate(chain):
            print(f"   {i+1}. {record.action_id}: {record.action_description}")
        
        # Get dependencies
        print(f"\n🔗 Dependencies for action_002:")
        deps = manager.get_dependencies("action_002")
        for dep in deps:
            print(f"   - {dep.action_id}: {dep.action_description}")
        
        # Try to reverse action with dependents
        print(f"\n🔄 Attempting to reverse action_001 (has dependents)...")
        result = manager.reverse_action("action_001", "admin_user")
        print(f"   Success: {result['success']}")
        print(f"   Message: {result['message']}")
        
        # Reverse action_002 first
        print(f"\n🔄 Reversing action_002...")
        result = manager.reverse_action("action_002", "admin_user")
        print(f"   Success: {result['success']}")
        print(f"   Message: {result['message']}")
        print(f"   File exists: {os.path.exists(test_file2)}")
        
        # Now reverse action_001
        print(f"\n🔄 Reversing action_001...")
        result = manager.reverse_action("action_001", "admin_user")
        print(f"   Success: {result['success']}")
        print(f"   Message: {result['message']}")
        print(f"   File exists: {os.path.exists(test_file1)}")
        
        # Try to reverse again (idempotency check)
        print(f"\n🔄 Attempting to reverse action_001 again...")
        result = manager.reverse_action("action_001", "admin_user")
        print(f"   Success: {result['success']}")
        print(f"   Message: {result['message']}")
        
        # Get statistics
        print(f"\n📊 Reversibility Statistics:")
        stats = manager.get_statistics()
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
        # Get all reversible actions
        print(f"\n📋 All reversible actions:")
        reversible = manager.get_all_reversible()
        for record in reversible:
            print(f"   - {record.action_id}: {record.action_description}")
        
        # Get all reversed actions
        print(f"\n📋 All reversed actions:")
        reversed_actions = manager.get_all_reversed()
        for record in reversed_actions:
            print(f"   - {record.action_id}: {record.action_description}")
            print(f"     Reversed at: {record.reversal_timestamp}")
            print(f"     Reversed by: {record.reversal_by}")
    
    print("\n" + "=" * 50)
    print("✅ Demo complete!")
