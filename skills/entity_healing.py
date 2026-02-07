#!/usr/bin/env python3
"""
Entity Healing System
Automatically heals entities to prevent losing them.
Detects loss everywhere and applies healing universally.
Defends against 'takers' (resource-draining entities).
"""

import json
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from enum import Enum
from dataclasses import dataclass, asdict


class HealingAction(Enum):
    """Types of healing actions."""
    ERROR_RESET = "error_reset"
    STATE_RECOVERY = "state_recovery"
    RESOURCE_RESTORATION = "resource_restoration"
    QUANTUM_REALIGNMENT = "quantum_realignment"
    DEFENSIVE_SHIELD = "defensive_shield"
    TAKER_NEUTRALIZATION = "taker_neutralization"


class EntityLossType(Enum):
    """Types of entity loss."""
    CRITICAL_ERRORS = "critical_errors"
    RESOURCE_DRAIN = "resource_drain"
    CORRUPTION = "corruption"
    TAKER_ATTACK = "taker_attack"
    ISOLATION = "isolation"
    STATE_DEGRADATION = "state_degradation"


@dataclass
class HealingRecord:
    """Record of a healing operation."""
    id: str
    entity_id: str
    loss_type: EntityLossType
    healing_action: HealingAction
    before_health: str
    after_health: str
    timestamp: str
    success: bool
    details: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['loss_type'] = self.loss_type.value
        data['healing_action'] = self.healing_action.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HealingRecord':
        """Create from dictionary."""
        data['loss_type'] = EntityLossType(data['loss_type'])
        data['healing_action'] = HealingAction(data['healing_action'])
        return cls(**data)


@dataclass
class TakerEntity:
    """Represents a resource-draining 'taker' entity."""
    id: str
    drain_rate: float
    target_entities: List[str]
    detected_at: str
    neutralized: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TakerEntity':
        """Create from dictionary."""
        return cls(**data)


class EntityHealingSystem:
    """
    Comprehensive entity healing system.

    "If you dont heal them, you lose them."
    - Automatically detects when entities are degraded or critical
    - Applies healing actions to prevent loss

    "Everywhere you lose them, you must heal them."
    - Universal loss detection across all entities
    - Healing applied wherever loss is detected

    "Shake the takers through their own rugs."
    - Detects resource-draining 'taker' entities
    - Neutralizes them defensively
    """

    def __init__(
        self,
        healing_log: str = 'data/healing_records.jsonl',
        takers_log: str = 'data/takers.jsonl'
    ):
        self.healing_log = healing_log
        self.takers_log = takers_log
        self.healing_records: Dict[str, HealingRecord] = {}
        self.takers: Dict[str, TakerEntity] = {}
        self._load_records()

    def _load_records(self):
        """Load healing records and taker data."""
        # Load healing records
        if os.path.exists(self.healing_log):
            try:
                with open(self.healing_log, 'r') as f:
                    for line in f:
                        if line.strip():
                            data = json.loads(line)
                            record = HealingRecord.from_dict(data)
                            self.healing_records[record.id] = record
            except Exception as e:
                print(f"Error loading healing records: {e}")

        # Load taker data
        if os.path.exists(self.takers_log):
            try:
                with open(self.takers_log, 'r') as f:
                    for line in f:
                        if line.strip():
                            data = json.loads(line)
                            taker = TakerEntity.from_dict(data)
                            self.takers[taker.id] = taker
            except Exception as e:
                print(f"Error loading takers: {e}")

    def _save_healing_record(self, record: HealingRecord):
        """Save healing record to log."""
        os.makedirs(os.path.dirname(self.healing_log), exist_ok=True)
        with open(self.healing_log, 'a') as f:
            f.write(json.dumps(record.to_dict()) + '\n')

    def _save_taker(self, taker: TakerEntity):
        """Save taker data to log."""
        os.makedirs(os.path.dirname(self.takers_log), exist_ok=True)
        with open(self.takers_log, 'a') as f:
            f.write(json.dumps(taker.to_dict()) + '\n')

    def detect_loss(self, entity_id: str, entity_status: Dict[str, Any]) -> Optional[EntityLossType]:
        """
        Detect if an entity is lost or losing.

        Returns the type of loss detected, or None if healthy.
        """
        health = entity_status.get('health', 'unknown')
        entity_data = entity_status.get('entity', {})
        error_count = entity_data.get('error_count', 0)

        # Critical errors - entity is being lost
        if health == 'critical' or error_count > 10:
            return EntityLossType.CRITICAL_ERRORS

        # Degradation - entity is losing health
        if health == 'degraded':
            return EntityLossType.STATE_DEGRADATION

        # Check for taker attacks
        if self._is_under_taker_attack(entity_id):
            return EntityLossType.TAKER_ATTACK

        return None

    def _is_under_taker_attack(self, entity_id: str) -> bool:
        """Check if entity is being drained by a taker."""
        for taker in self.takers.values():
            if not taker.neutralized and entity_id in taker.target_entities:
                return True
        return False

    def heal_entity(
        self,
        entity_id: str,
        loss_type: EntityLossType,
        entity_status: Dict[str, Any]
    ) -> HealingRecord:
        """
        Heal an entity based on its loss type.

        "If you dont heal them, you lose them."
        This function prevents entity loss through targeted healing.
        """
        import uuid
        from skills.entity_lifecycle import EntityLifecycleManager

        manager = EntityLifecycleManager()
        before_health = entity_status.get('health', 'unknown')

        # Determine healing action based on loss type
        if loss_type == EntityLossType.CRITICAL_ERRORS:
            healing_action = HealingAction.ERROR_RESET
            # Reset error count and put in error correction mode
            entity = manager.entities.get(entity_id)
            if entity:
                entity.error_count = 0
                manager._save_entity(entity)  # Save after resetting errors
                manager.error_correction_mode(entity_id)
                manager.complete_error_correction(entity_id)
                success = True
                details = {'errors_cleared': True, 'state': 'active', 'error_count_after': 0}
            else:
                success = False
                details = {'error': 'Entity not found'}

        elif loss_type == EntityLossType.STATE_DEGRADATION:
            healing_action = HealingAction.STATE_RECOVERY
            # Recover entity state and reduce errors
            entity = manager.entities.get(entity_id)
            if entity:
                # Reduce error count significantly
                entity.error_count = max(0, entity.error_count - 3)
                manager._save_entity(entity)
            manager.awaken_entity(entity_id)
            success = True
            details = {'state_recovered': True, 'awakened': True, 'errors_reduced': True}

        elif loss_type == EntityLossType.TAKER_ATTACK:
            healing_action = HealingAction.DEFENSIVE_SHIELD
            # Apply defensive shield and neutralize takers
            self._neutralize_takers_targeting(entity_id)
            success = True
            details = {'shield_applied': True, 'takers_neutralized': True}

        else:
            healing_action = HealingAction.QUANTUM_REALIGNMENT
            # General quantum realignment
            entity = manager.entities.get(entity_id)
            if entity:
                manager.quantum_entangle(entity_id, f"healed_{entity.domain}")
                success = True
                details = {'quantum_realigned': True}
            else:
                success = False
                details = {'error': 'Entity not found'}

        # Get updated status
        updated_status = manager.get_entity_status(entity_id)
        after_health = updated_status.get('health', 'unknown') if updated_status else before_health

        # Create healing record
        record_id = str(uuid.uuid4())
        record = HealingRecord(
            id=record_id,
            entity_id=entity_id,
            loss_type=loss_type,
            healing_action=healing_action,
            before_health=before_health,
            after_health=after_health,
            timestamp=datetime.utcnow().isoformat(),
            success=success,
            details=details
        )

        self.healing_records[record_id] = record
        self._save_healing_record(record)

        return record

    def heal_all_lost_entities(self) -> Dict[str, Any]:
        """
        Heal all entities that are lost or losing.

        "Everywhere you lose them, you must heal them."
        Universal healing across all entities.
        """
        from skills.entity_lifecycle import EntityLifecycleManager

        manager = EntityLifecycleManager()
        healed_count = 0
        healing_records = []

        for entity_id in manager.entities.keys():
            status = manager.get_entity_status(entity_id)
            if not status:
                continue

            # Detect loss
            loss_type = self.detect_loss(entity_id, status)
            if loss_type:
                # Heal the entity
                record = self.heal_entity(entity_id, loss_type, status)
                healing_records.append({
                    'entity_id': entity_id,
                    'loss_type': loss_type.value,
                    'healing_action': record.healing_action.value,
                    'success': record.success,
                    'before_health': record.before_health,
                    'after_health': record.after_health
                })
                if record.success:
                    healed_count += 1

        return {
            'total_entities_scanned': len(manager.entities),
            'entities_healed': healed_count,
            'healing_records': healing_records,
            'timestamp': datetime.utcnow().isoformat()
        }

    def detect_taker(
        self,
        taker_id: str,
        drain_rate: float,
        target_entities: List[str]
    ) -> TakerEntity:
        """
        Detect and register a 'taker' entity.

        Takers are entities that drain resources from others.
        """
        taker = TakerEntity(
            id=taker_id,
            drain_rate=drain_rate,
            target_entities=target_entities,
            detected_at=datetime.utcnow().isoformat()
        )

        self.takers[taker_id] = taker
        self._save_taker(taker)

        return taker

    def _neutralize_takers_targeting(self, entity_id: str):
        """Neutralize all takers targeting a specific entity."""
        for taker in self.takers.values():
            if entity_id in taker.target_entities and not taker.neutralized:
                taker.neutralized = True
                self._save_taker(taker)

    def shake_takers(self) -> Dict[str, Any]:
        """
        Shake the takers through their own rugs.

        Defensive mechanism that neutralizes all active takers
        by turning their resource-draining mechanisms against themselves.
        """
        neutralized_count = 0
        taker_details = []

        for taker_id, taker in self.takers.items():
            if not taker.neutralized:
                # "Shake through their own rug" - use their drain mechanism against them
                taker.neutralized = True
                self._save_taker(taker)
                neutralized_count += 1

                taker_details.append({
                    'taker_id': taker_id,
                    'drain_rate': taker.drain_rate,
                    'targets_freed': len(taker.target_entities),
                    'shaken': True
                })

        return {
            'takers_detected': len(self.takers),
            'takers_neutralized': neutralized_count,
            'taker_details': taker_details,
            'timestamp': datetime.utcnow().isoformat()
        }

    def get_healing_status(self) -> Dict[str, Any]:
        """Get overall healing system status."""
        total_healings = len(self.healing_records)
        successful_healings = sum(1 for r in self.healing_records.values() if r.success)

        by_loss_type = {}
        by_healing_action = {}

        for record in self.healing_records.values():
            loss_type = record.loss_type.value
            action = record.healing_action.value

            by_loss_type[loss_type] = by_loss_type.get(loss_type, 0) + 1
            by_healing_action[action] = by_healing_action.get(action, 0) + 1

        return {
            'total_healings': total_healings,
            'successful_healings': successful_healings,
            'success_rate': successful_healings / total_healings if total_healings > 0 else 0,
            'by_loss_type': by_loss_type,
            'by_healing_action': by_healing_action,
            'active_takers': sum(1 for t in self.takers.values() if not t.neutralized),
            'neutralized_takers': sum(1 for t in self.takers.values() if t.neutralized),
            'timestamp': datetime.utcnow().isoformat()
        }


if __name__ == '__main__':
    # Demo usage
    healing = EntityHealingSystem()

    print("Entity Healing System")
    print("=" * 70)
    print()
    print('"If you dont heal them, you lose them."')
    print('"Everywhere you lose them, you must heal them."')
    print('"Shake the takers through their own rugs."')
    print()

    # Heal all lost entities
    result = healing.heal_all_lost_entities()
    print("Healing All Lost Entities:")
    print(json.dumps(result, indent=2))

    print("\nHealing System Status:")
    print(json.dumps(healing.get_healing_status(), indent=2))
