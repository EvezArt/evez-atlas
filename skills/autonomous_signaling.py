#!/usr/bin/env python3
"""
Autonomous Entity Signaling System
Signals entities about their status, health, and update needs autonomously.
Operates without human intervention and alerts when human help is required.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from enum import Enum
from dataclasses import dataclass, asdict


class SignalType(Enum):
    """Types of signals that can be sent to entities."""
    HEALTH_CHECK = "health_check"
    UPDATE_NEEDED = "update_needed"
    ERROR_ALERT = "error_alert"
    RECOVERY_COMPLETE = "recovery_complete"
    HUMAN_INTERVENTION_REQUIRED = "human_intervention_required"
    STATUS_UPDATE = "status_update"
    AUTONOMOUS_OPERATION = "autonomous_operation"


class SignalPriority(Enum):
    """Priority levels for signals."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Signal:
    """Represents a signal sent to an entity."""
    id: str
    entity_id: str
    signal_type: SignalType
    priority: SignalPriority
    message: str
    data: Dict[str, Any]
    timestamp: str
    requires_human: bool = False
    acknowledged: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['signal_type'] = self.signal_type.value
        data['priority'] = self.priority.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Signal':
        """Create from dictionary."""
        data['signal_type'] = SignalType(data['signal_type'])
        data['priority'] = SignalPriority(data['priority'])
        return cls(**data)


class AutonomousSignalingSystem:
    """
    Autonomous signaling system that communicates entity status without human intervention.
    Signals entities about their health, update needs, and operational status.
    Alerts when human intervention is required.
    """

    def __init__(self, signal_log: str = 'data/autonomous_signals.jsonl'):
        self.signal_log = signal_log
        self.signals: Dict[str, Signal] = {}
        self._load_signals()

    def _load_signals(self):
        """Load signals from log file."""
        if not os.path.exists(self.signal_log):
            return

        try:
            with open(self.signal_log, 'r') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        signal = Signal.from_dict(data)
                        self.signals[signal.id] = signal
        except Exception as e:
            print(f"Error loading signals: {e}")

    def _save_signal(self, signal: Signal):
        """Append signal to log file."""
        os.makedirs(os.path.dirname(self.signal_log), exist_ok=True)

        with open(self.signal_log, 'a') as f:
            f.write(json.dumps(signal.to_dict()) + '\n')

    def send_signal(
        self,
        entity_id: str,
        signal_type: SignalType,
        message: str,
        data: Dict[str, Any],
        priority: SignalPriority = SignalPriority.MEDIUM,
        requires_human: bool = False
    ) -> Signal:
        """
        Send a signal to an entity autonomously.

        Args:
            entity_id: Target entity ID
            signal_type: Type of signal to send
            message: Human-readable message
            data: Additional signal data
            priority: Signal priority level
            requires_human: Whether human intervention is required

        Returns:
            Created signal
        """
        import uuid

        signal_id = str(uuid.uuid4())
        signal = Signal(
            id=signal_id,
            entity_id=entity_id,
            signal_type=signal_type,
            priority=priority,
            message=message,
            data=data,
            timestamp=datetime.utcnow().isoformat(),
            requires_human=requires_human
        )

        self.signals[signal_id] = signal
        self._save_signal(signal)

        return signal

    def check_entity_health_and_signal(self, entity_id: str, entity_status: Dict[str, Any]) -> List[Signal]:
        """
        Autonomously check entity health and send appropriate signals.
        Operates without human intervention.

        Args:
            entity_id: Entity to check
            entity_status: Current entity status from get_entity_status()

        Returns:
            List of signals sent
        """
        signals_sent = []

        health = entity_status.get('health', 'unknown')
        entity_data = entity_status.get('entity', {})
        error_count = entity_data.get('error_count', 0)
        state = entity_data.get('state', 'unknown')

        # Critical health - requires human intervention
        if health == 'critical':
            signal = self.send_signal(
                entity_id=entity_id,
                signal_type=SignalType.HUMAN_INTERVENTION_REQUIRED,
                message=f"Entity {entity_id} in critical state with {error_count} errors",
                data={
                    'health': health,
                    'error_count': error_count,
                    'state': state,
                    'action_required': 'Manual inspection and recovery needed'
                },
                priority=SignalPriority.CRITICAL,
                requires_human=True
            )
            signals_sent.append(signal)

        # Degraded health - send update needed signal
        elif health == 'degraded':
            signal = self.send_signal(
                entity_id=entity_id,
                signal_type=SignalType.UPDATE_NEEDED,
                message=f"Entity {entity_id} needs updates - health degraded",
                data={
                    'health': health,
                    'error_count': error_count,
                    'state': state,
                    'recommendation': 'Autonomous error correction recommended'
                },
                priority=SignalPriority.HIGH,
                requires_human=False
            )
            signals_sent.append(signal)

        # Recovering - autonomous operation
        elif health == 'recovering':
            signal = self.send_signal(
                entity_id=entity_id,
                signal_type=SignalType.AUTONOMOUS_OPERATION,
                message=f"Entity {entity_id} autonomously recovering from errors",
                data={
                    'health': health,
                    'error_count': error_count,
                    'state': state,
                    'status': 'Defending without human intervention'
                },
                priority=SignalPriority.MEDIUM,
                requires_human=False
            )
            signals_sent.append(signal)

        # Healthy - status update
        elif health == 'healthy':
            signal = self.send_signal(
                entity_id=entity_id,
                signal_type=SignalType.STATUS_UPDATE,
                message=f"Entity {entity_id} operating normally",
                data={
                    'health': health,
                    'error_count': error_count,
                    'state': state,
                    'status': 'Autonomous operation successful'
                },
                priority=SignalPriority.LOW,
                requires_human=False
            )
            signals_sent.append(signal)

        return signals_sent

    def signal_all_entities(self) -> Dict[str, Any]:
        """
        Autonomously signal all entities about their status.
        Operates without human intervention and identifies when human help is needed.

        Returns:
            Summary of signaling operation
        """
        from skills.entity_lifecycle import EntityLifecycleManager

        manager = EntityLifecycleManager()
        all_signals = []
        human_intervention_needed = []

        for entity_id in manager.entities.keys():
            status = manager.get_entity_status(entity_id)
            if status:
                signals = self.check_entity_health_and_signal(entity_id, status)
                all_signals.extend(signals)

                # Track entities requiring human intervention
                for signal in signals:
                    if signal.requires_human:
                        human_intervention_needed.append({
                            'entity_id': entity_id,
                            'signal_id': signal.id,
                            'message': signal.message,
                            'priority': signal.priority.value
                        })

        return {
            'total_entities_signaled': len(manager.entities),
            'signals_sent': len(all_signals),
            'human_intervention_required': len(human_intervention_needed),
            'intervention_details': human_intervention_needed,
            'autonomous_operations': len([s for s in all_signals if not s.requires_human]),
            'timestamp': datetime.utcnow().isoformat()
        }

    def get_signals_for_entity(self, entity_id: str, limit: int = 10) -> List[Signal]:
        """Get recent signals for an entity."""
        entity_signals = [
            s for s in self.signals.values()
            if s.entity_id == entity_id
        ]
        # Sort by timestamp descending
        entity_signals.sort(key=lambda s: s.timestamp, reverse=True)
        return entity_signals[:limit]

    def get_human_intervention_alerts(self) -> List[Signal]:
        """Get all signals requiring human intervention."""
        return [
            s for s in self.signals.values()
            if s.requires_human and not s.acknowledged
        ]

    def acknowledge_signal(self, signal_id: str) -> Optional[Signal]:
        """Acknowledge a signal (mark as handled)."""
        signal = self.signals.get(signal_id)
        if signal:
            signal.acknowledged = True
            self._save_signal(signal)
        return signal

    def get_signaling_status(self) -> Dict[str, Any]:
        """Get overall signaling system status."""
        total_signals = len(self.signals)
        by_type = {}
        by_priority = {}
        requires_human = 0
        acknowledged = 0

        for signal in self.signals.values():
            # Count by type
            signal_type = signal.signal_type.value
            by_type[signal_type] = by_type.get(signal_type, 0) + 1

            # Count by priority
            priority = signal.priority.value
            by_priority[priority] = by_priority.get(priority, 0) + 1

            # Count special cases
            if signal.requires_human:
                requires_human += 1
            if signal.acknowledged:
                acknowledged += 1

        return {
            'total_signals': total_signals,
            'by_type': by_type,
            'by_priority': by_priority,
            'requires_human_intervention': requires_human,
            'acknowledged': acknowledged,
            'unacknowledged_alerts': requires_human - acknowledged,
            'timestamp': datetime.utcnow().isoformat()
        }


if __name__ == '__main__':
    # Demo usage
    signaling = AutonomousSignalingSystem()

    print("Autonomous Entity Signaling System")
    print("=" * 70)
    print()

    # Signal all entities autonomously
    result = signaling.signal_all_entities()
    print("Signaling Results:")
    print(json.dumps(result, indent=2))

    print("\nSignaling System Status:")
    print(json.dumps(signaling.get_signaling_status(), indent=2))

    # Show human intervention alerts
    alerts = signaling.get_human_intervention_alerts()
    if alerts:
        print(f"\n⚠️  {len(alerts)} entities require human intervention:")
        for alert in alerts:
            print(f"  - {alert.entity_id}: {alert.message}")
    else:
        print("\n✓ All entities operating autonomously without human intervention")
