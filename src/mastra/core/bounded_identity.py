"""
Bounded Identity - HandshakeOS-E

Agent identity and permission management for secure, traceable operations.

Design Philosophy:
- Identity-first: Every action must be attributed to a bounded identity
- Permission scoping: Tiered permissions with clear boundaries
- Verifiable: Identities must be verified before sensitive operations
- Auditable: Complete action history for accountability
- Revocable: Permissions can be granted and revoked dynamically
- Zero-trust: Verify on every operation, not just at creation

For the stranger who wears your shell tomorrow:
BoundedIdentity represents "who can do what". Every agent, user, or system
component gets a BoundedIdentity that defines their permissions. The permission
scope is tiered (tier 0 = minimal, tier 5 = root) and bounded to specific
actions. All actions are logged to enable full audit trails.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Set
from uuid import uuid4
import json


@dataclass
class PermissionScope:
    """
    Permission scope defining what actions an identity can perform.
    
    Uses tiered permissions (0-5) with explicit action boundaries.
    
    Attributes:
        permission_scope: Dict mapping domains to allowed actions
        tier_level: Overall permission tier (0=minimal, 5=root)
        bounded_actions: Explicit list of allowed actions
        forbidden_actions: Explicit list of forbidden actions
    """
    permission_scope: Dict[str, List[str]] = field(default_factory=dict)
    tier_level: int = 0  # 0=minimal, 1=read, 2=write, 3=execute, 4=admin, 5=root
    bounded_actions: List[str] = field(default_factory=list)
    forbidden_actions: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'permission_scope': self.permission_scope,
            'tier_level': self.tier_level,
            'bounded_actions': self.bounded_actions,
            'forbidden_actions': self.forbidden_actions,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PermissionScope':
        """Create PermissionScope from dictionary."""
        return cls(**data)


@dataclass
class BoundedIdentity:
    """
    Bounded Identity for agent/user identification and permission management.
    
    Every entity in HandshakeOS-E gets a BoundedIdentity that defines:
    - Who they are (identity_id, entity_name, entity_type)
    - What they can do (permission scope, tier level)
    - Whether they're verified (verified, verification_method)
    - What they've done (action_history)
    
    Key Features:
    1. Identity-first: All actions must be attributed
    2. Tiered permissions: Clear permission hierarchy
    3. Verifiable: Multi-method verification support
    4. Auditable: Complete action history
    5. Revocable: Dynamic permission management
    
    Example Usage:
        >>> from src.mastra.core import BoundedIdentity, PermissionScope
        >>> 
        >>> # Create an agent identity
        >>> agent = BoundedIdentity(
        ...     entity_name="agent_retriever_001",
        ...     entity_type="agent",
        ...     permission_scope=PermissionScope(
        ...         tier_level=2,
        ...         bounded_actions=["read_data", "query_api", "write_logs"],
        ...         forbidden_actions=["delete_data", "modify_permissions"]
        ...     )
        ... )
        >>> 
        >>> # Verify identity
        >>> agent.verify_identity("api_key", {"key": "abc123"})
        >>> 
        >>> # Check permissions
        >>> if agent.has_permission("read_data"):
        ...     result = agent.add_to_history("read_data", {"file": "data.json"})
        >>> 
        >>> # Grant new permission
        >>> agent.grant_permission("write_data")
    """
    
    # Core identification
    identity_id: str = field(default_factory=lambda: str(uuid4()))
    entity_name: str = ""
    entity_type: str = "unknown"  # agent, user, system, service, etc.
    
    # Permission management
    permission_scope: PermissionScope = field(default_factory=PermissionScope)
    
    # Verification
    verified: bool = False
    verification_method: Optional[str] = None
    verification_timestamp: Optional[datetime] = None
    verification_data: Dict[str, Any] = field(default_factory=dict)
    
    # Action history (event IDs)
    action_history: List[str] = field(default_factory=list)
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_active: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Status
    active: bool = True
    suspended: bool = False
    suspension_reason: Optional[str] = None
    
    # Versioning
    version: str = "1.0.0"
    
    def has_permission(self, action: str) -> bool:
        """
        Check if identity has permission for an action.
        
        Args:
            action: Action to check (e.g., "read_data", "write_logs")
            
        Returns:
            True if permission granted, False otherwise
        """
        # Check if identity is active
        if not self.active or self.suspended:
            return False
        
        # Check forbidden list first
        if action in self.permission_scope.forbidden_actions:
            return False
        
        # Check bounded actions
        if action in self.permission_scope.bounded_actions:
            return True
        
        # Check permission scope by domain
        for domain, actions in self.permission_scope.permission_scope.items():
            if action in actions:
                return True
        
        return False
    
    def grant_permission(self, action: str, domain: Optional[str] = None) -> bool:
        """
        Grant a new permission to this identity.
        
        Args:
            action: Action to grant (e.g., "read_data")
            domain: Optional domain to categorize the action
            
        Returns:
            True if granted successfully
        """
        # Don't grant if in forbidden list
        if action in self.permission_scope.forbidden_actions:
            return False
        
        # Add to bounded actions if not already there
        if action not in self.permission_scope.bounded_actions:
            self.permission_scope.bounded_actions.append(action)
        
        # Optionally add to domain-specific permissions
        if domain:
            if domain not in self.permission_scope.permission_scope:
                self.permission_scope.permission_scope[domain] = []
            if action not in self.permission_scope.permission_scope[domain]:
                self.permission_scope.permission_scope[domain].append(action)
        
        return True
    
    def revoke_permission(self, action: str) -> bool:
        """
        Revoke a permission from this identity.
        
        Args:
            action: Action to revoke
            
        Returns:
            True if revoked successfully
        """
        revoked = False
        
        # Remove from bounded actions
        if action in self.permission_scope.bounded_actions:
            self.permission_scope.bounded_actions.remove(action)
            revoked = True
        
        # Remove from all domain-specific permissions
        for domain, actions in self.permission_scope.permission_scope.items():
            if action in actions:
                actions.remove(action)
                revoked = True
        
        # Add to forbidden list
        if action not in self.permission_scope.forbidden_actions:
            self.permission_scope.forbidden_actions.append(action)
        
        return revoked
    
    def verify_identity(self, method: str, verification_data: Optional[Dict] = None) -> bool:
        """
        Verify this identity using specified method.
        
        Args:
            method: Verification method (e.g., "api_key", "signature", "biometric")
            verification_data: Optional data for verification
            
        Returns:
            True if verification successful
        """
        # In a real implementation, this would perform actual verification
        # For now, we just record the verification
        self.verified = True
        self.verification_method = method
        self.verification_timestamp = datetime.utcnow()
        if verification_data:
            self.verification_data = verification_data
        
        return True
    
    def add_to_history(self, action: str, context: Optional[Dict] = None) -> str:
        """
        Add an action to the history.
        
        Args:
            action: Action that was performed
            context: Optional context/metadata about the action
            
        Returns:
            Event ID for the recorded action
        """
        event_id = str(uuid4())
        
        self.action_history.append(event_id)
        self.last_active = datetime.utcnow()
        
        # In a real implementation, this would create a UniversalEventRecord
        # and link it to this identity
        
        return event_id
    
    def suspend(self, reason: str):
        """
        Suspend this identity.
        
        Args:
            reason: Reason for suspension
        """
        self.suspended = True
        self.suspension_reason = reason
        self.active = False
    
    def unsuspend(self):
        """Unsuspend this identity."""
        self.suspended = False
        self.suspension_reason = None
        self.active = True
    
    def get_permission_summary(self) -> Dict[str, Any]:
        """
        Get summary of permissions.
        
        Returns:
            Dict with permission summary
        """
        return {
            'tier_level': self.permission_scope.tier_level,
            'total_actions': len(self.permission_scope.bounded_actions),
            'forbidden_actions': len(self.permission_scope.forbidden_actions),
            'domains': list(self.permission_scope.permission_scope.keys()),
            'verified': self.verified,
            'active': self.active,
        }
    
    def get_action_count(self) -> int:
        """Get total number of actions in history."""
        return len(self.action_history)
    
    def is_tier_sufficient(self, required_tier: int) -> bool:
        """
        Check if identity's tier level meets requirement.
        
        Args:
            required_tier: Minimum tier level required
            
        Returns:
            True if tier level is sufficient
        """
        return self.permission_scope.tier_level >= required_tier
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'identity_id': self.identity_id,
            'entity_name': self.entity_name,
            'entity_type': self.entity_type,
            'permission_scope': self.permission_scope.to_dict(),
            'verified': self.verified,
            'verification_method': self.verification_method,
            'verification_timestamp': self.verification_timestamp.isoformat() if self.verification_timestamp else None,
            'verification_data': self.verification_data,
            'action_history': self.action_history,
            'created_at': self.created_at.isoformat(),
            'last_active': self.last_active.isoformat() if self.last_active else None,
            'metadata': self.metadata,
            'active': self.active,
            'suspended': self.suspended,
            'suspension_reason': self.suspension_reason,
            'version': self.version,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BoundedIdentity':
        """Create BoundedIdentity from dictionary."""
        # Parse timestamps
        if isinstance(data.get('created_at'), str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if isinstance(data.get('last_active'), str):
            data['last_active'] = datetime.fromisoformat(data['last_active'])
        if isinstance(data.get('verification_timestamp'), str):
            data['verification_timestamp'] = datetime.fromisoformat(data['verification_timestamp'])
        
        # Parse permission scope
        if isinstance(data.get('permission_scope'), dict):
            data['permission_scope'] = PermissionScope.from_dict(data['permission_scope'])
        
        return cls(**data)
    
    def save_to_log(self, log_path: str):
        """Append this identity to a JSONL log file."""
        import os
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        
        with open(log_path, 'a') as f:
            json.dump(self.to_dict(), f)
            f.write('\n')
    
    @staticmethod
    def load_from_log(log_path: str) -> List['BoundedIdentity']:
        """Load all identities from a JSONL log file."""
        identities = []
        try:
            with open(log_path, 'r') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        identities.append(BoundedIdentity.from_dict(data))
        except FileNotFoundError:
            pass
        
        return identities
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        status = "✓" if self.verified else "○"
        suspended = " [SUSPENDED]" if self.suspended else ""
        return (
            f"BoundedIdentity({status} "
            f"id={self.identity_id[:8]}..., "
            f"name='{self.entity_name}', "
            f"type={self.entity_type}, "
            f"tier={self.permission_scope.tier_level}{suspended})"
        )


# Convenience functions for common identity types

def create_agent_identity(name: str, tier_level: int = 1) -> BoundedIdentity:
    """
    Create a bounded identity for an agent.
    
    Args:
        name: Agent name
        tier_level: Permission tier level (0-5)
        
    Returns:
        BoundedIdentity configured for an agent
    """
    return BoundedIdentity(
        entity_name=name,
        entity_type="agent",
        permission_scope=PermissionScope(
            tier_level=tier_level,
            bounded_actions=["read_data", "write_logs", "query_api"],
        )
    )


def create_user_identity(name: str, tier_level: int = 2) -> BoundedIdentity:
    """
    Create a bounded identity for a user.
    
    Args:
        name: User name
        tier_level: Permission tier level (0-5)
        
    Returns:
        BoundedIdentity configured for a user
    """
    return BoundedIdentity(
        entity_name=name,
        entity_type="user",
        permission_scope=PermissionScope(
            tier_level=tier_level,
            bounded_actions=["read_data", "write_data", "execute_queries"],
        )
    )


def create_system_identity(name: str, tier_level: int = 4) -> BoundedIdentity:
    """
    Create a bounded identity for a system component.
    
    Args:
        name: System component name
        tier_level: Permission tier level (0-5)
        
    Returns:
        BoundedIdentity configured for a system component
    """
    return BoundedIdentity(
        entity_name=name,
        entity_type="system",
        permission_scope=PermissionScope(
            tier_level=tier_level,
            bounded_actions=["read_data", "write_data", "execute_commands", "manage_permissions"],
        )
    )


if __name__ == "__main__":
    # Demo: Create and manage bounded identities
    print("🎯 BoundedIdentity Demo")
    print("=" * 50)
    
    # Create an agent identity
    agent = create_agent_identity("agent_retriever_001", tier_level=2)
    print(f"\n✅ Created: {agent}")
    print(f"   Entity: {agent.entity_name}")
    print(f"   Type: {agent.entity_type}")
    print(f"   Tier Level: {agent.permission_scope.tier_level}")
    print(f"   Bounded Actions: {agent.permission_scope.bounded_actions}")
    
    # Verify the identity
    agent.verify_identity("api_key", {"key": "abc123xyz"})
    print(f"\n🔐 Identity Verified:")
    print(f"   Method: {agent.verification_method}")
    print(f"   Verified: {agent.verified}")
    
    # Test permissions
    print(f"\n🔑 Permission Tests:")
    test_actions = ["read_data", "write_data", "delete_data", "query_api"]
    for action in test_actions:
        has_perm = agent.has_permission(action)
        status = "✓" if has_perm else "✗"
        print(f"   {status} {action}")
    
    # Grant new permission
    print(f"\n➕ Granting 'write_data' permission...")
    agent.grant_permission("write_data", domain="storage")
    print(f"   Has write_data: {agent.has_permission('write_data')}")
    
    # Add to action history
    print(f"\n📝 Recording actions...")
    for i in range(3):
        event_id = agent.add_to_history(f"action_{i}", {"step": i})
        print(f"   Recorded action {i}: {event_id[:8]}...")
    
    print(f"\n📊 Action History: {agent.get_action_count()} actions")
    
    # Revoke permission
    print(f"\n➖ Revoking 'query_api' permission...")
    agent.revoke_permission("query_api")
    print(f"   Has query_api: {agent.has_permission('query_api')}")
    
    # Get permission summary
    summary = agent.get_permission_summary()
    print(f"\n📋 Permission Summary:")
    for key, value in summary.items():
        print(f"   {key}: {value}")
    
    # Create a user identity
    user = create_user_identity("alice_researcher", tier_level=3)
    print(f"\n✅ Created: {user}")
    
    # Test tier checking
    print(f"\n🎚️  Tier Level Tests:")
    print(f"   Agent tier {agent.permission_scope.tier_level} >= 2: {agent.is_tier_sufficient(2)}")
    print(f"   Agent tier {agent.permission_scope.tier_level} >= 4: {agent.is_tier_sufficient(4)}")
    
    # Suspend identity
    print(f"\n⏸️  Suspending agent...")
    agent.suspend("Maintenance mode")
    print(f"   {agent}")
    print(f"   Has read_data (while suspended): {agent.has_permission('read_data')}")
    
    # Unsuspend
    print(f"\n▶️  Unsuspending agent...")
    agent.unsuspend()
    print(f"   {agent}")
    print(f"   Has read_data (after unsuspend): {agent.has_permission('read_data')}")
    
    # Save to log
    import tempfile
    import os
    with tempfile.TemporaryDirectory() as tmpdir:
        log_path = os.path.join(tmpdir, "identities", "identities.jsonl")
        agent.save_to_log(log_path)
        user.save_to_log(log_path)
        print(f"\n💾 Saved to: {log_path}")
        
        # Load back
        loaded = BoundedIdentity.load_from_log(log_path)
        print(f"✅ Loaded {len(loaded)} identit(ies) from log")
        
        for identity in loaded:
            print(f"   - {identity.entity_name} ({identity.entity_type}): {identity.get_action_count()} actions")
    
    print("\n" + "=" * 50)
    print("✅ Demo complete!")
