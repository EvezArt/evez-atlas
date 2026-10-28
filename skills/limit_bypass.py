#!/usr/bin/env python3
"""Bounded limit adjustments. Disabled by default; unlimited mode is prohibited."""

import json
import os
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional


class LimitBypass:
    """Allows only explicit, bounded limit increases when an operator opts in."""

    DEFAULT_LIMITS = {
        "max_concurrent_tasks": 100,
        "max_delegation_depth": 10,
        "max_agents": 1000,
        "max_memory_mb": 4096,
        "max_execution_time": 600,
        "max_queue_size": 10000,
        "max_domain_size": 500,
    }
    MAX_SCALE_FACTOR = 2

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.data_dir / "limit_bypass.jsonl"
        self.enabled = os.environ.get("LIMIT_BYPASS_ENABLED", "0").strip() == "1"
        self.limits = self.DEFAULT_LIMITS.copy()
        self.bypassed_limits: Dict[str, Dict[str, Any]] = {}
        self.scaling_events: List[Dict[str, Any]] = []

    def check_limit(self, limit_name: str, current_value: int) -> Dict[str, Any]:
        known = limit_name in self.limits
        limit = self.limits.get(limit_name)
        valid_current = isinstance(current_value, int) and not isinstance(current_value, bool) and current_value >= 0
        usage = (current_value / limit * 100) if known and valid_current and limit > 0 else 0
        return {
            "limit_name": limit_name,
            "known_limit": known,
            "current": current_value,
            "limit": limit,
            "usage_percent": usage,
            "approaching": bool(known and valid_current and limit > 0 and current_value / limit > 0.8),
            "exceeded": bool(known and valid_current and current_value > limit),
        }

    def bypass_limit(
        self,
        limit_name: str,
        new_limit: int,
        reason: str = "operator_approved_bounded_scale",
        duration: Optional[int] = None,
        approval_id: Optional[str] = None,
        approved_by: Optional[str] = None,
    ) -> Dict[str, Any]:
        old_limit = self.limits.get(limit_name)
        if not self.enabled:
            return self._deny(limit_name, old_limit, new_limit, "limit bypass is disabled by default")
        if old_limit is None:
            return self._deny(limit_name, old_limit, new_limit, "unknown limit name")
        if not isinstance(new_limit, int) or isinstance(new_limit, bool) or new_limit <= 0:
            return self._deny(limit_name, old_limit, new_limit, "new limit must be a positive integer")
        if new_limit <= old_limit:
            return self._deny(limit_name, old_limit, new_limit, "this interface only handles increases")
        if new_limit > old_limit * self.MAX_SCALE_FACTOR:
            return self._deny(limit_name, old_limit, new_limit, "increase exceeds the hard 2x bound")
        if not isinstance(reason, str) or not reason.strip() or len(reason) > 200:
            return self._deny(limit_name, old_limit, new_limit, "a short, non-empty reason is required")
        if not isinstance(approval_id, str) or not re.fullmatch(r"[A-Za-z0-9._:-]{6,128}", approval_id):
            return self._deny(limit_name, old_limit, new_limit, "a valid external approval_id is required")
        if not isinstance(approved_by, str) or not approved_by.strip() or len(approved_by) > 120:
            return self._deny(limit_name, old_limit, new_limit, "an approving operator identity is required")
        if duration is not None and (not isinstance(duration, int) or isinstance(duration, bool) or duration < 1 or duration > 86400):
            return self._deny(limit_name, old_limit, new_limit, "duration must be between 1 and 86400 seconds")

        record = {
            "limit_name": limit_name,
            "old_limit": old_limit,
            "new_limit": new_limit,
            "reason": reason.strip(),
            "approval_id": approval_id,
            "approved_by": approved_by.strip(),
            "bypassed_at": time.time(),
            "duration": duration,
            "active": True,
            "status": "approved_by_opt_in_bounded_policy",
        }
        self.limits[limit_name] = new_limit
        self.bypassed_limits[limit_name] = record
        self._log_event("bounded_limit_increased", record)
        return record

    def _deny(self, limit_name: str, old_limit: Any, new_limit: Any, reason: str) -> Dict[str, Any]:
        record = {
            "limit_name": limit_name,
            "old_limit": old_limit,
            "requested_limit": new_limit,
            "reason": reason,
            "timestamp": time.time(),
            "status": "denied",
            "approved": False,
        }
        self._log_event("limit_change_denied", record)
        return record

    def restore_limit(self, limit_name: str) -> Dict[str, Any]:
        if limit_name not in self.bypassed_limits:
            return {"limit_name": limit_name, "status": "unchanged", "reason": "no active bounded increase"}
        old_limit = self.bypassed_limits[limit_name]["old_limit"]
        self.limits[limit_name] = old_limit
        self.bypassed_limits[limit_name]["active"] = False
        self.bypassed_limits[limit_name]["restored_at"] = time.time()
        self._log_event("limit_restored", {"limit_name": limit_name, "restored_to": old_limit})
        return {"limit_name": limit_name, "restored_to": old_limit, "status": "restored"}

    def auto_scale(self, limit_name: str, current_value: int, scale_factor: float = 2.0) -> Dict[str, Any]:
        if not self.enabled:
            return self._deny(limit_name, self.limits.get(limit_name), current_value, "automatic scaling is disabled by default")
        check = self.check_limit(limit_name, current_value)
        if not check["known_limit"] or not isinstance(current_value, int) or isinstance(current_value, bool) or current_value < 0:
            return self._deny(limit_name, self.limits.get(limit_name), current_value, "unknown limit or invalid usage metric")
        if scale_factor != 2.0:
            return self._deny(limit_name, self.limits[limit_name], current_value, "only the fixed 2x scale factor is permitted")
        if check["exceeded"] or check["approaching"]:
            return {
                "action": "approval_required",
                "reason": "automatic scaling cannot approve its own limit override",
                "limit_name": limit_name,
                "current_limit": self.limits[limit_name],
                "recommended_limit": min(self.limits[limit_name] * self.MAX_SCALE_FACTOR, self.limits[limit_name] * self.MAX_SCALE_FACTOR),
                "requires_approval": True,
                "status": "approval_required",
            }
        return {"action": "none", "reason": "within_limits", "usage": check["usage_percent"], "status": "unchanged"}

    def get_limits_status(self) -> Dict[str, Any]:
        status = {
            "enabled": self.enabled,
            "limits": self.limits,
            "active_bypassed": [name for name, record in self.bypassed_limits.items() if record.get("active")],
            "total_bypasses": len(self.bypassed_limits),
        }
        for name in self.limits:
            status[f"{name}_status"] = 0
        return status

    def enable_unlimited_mode(self) -> Dict[str, Any]:
        """Unlimited mode is deliberately forbidden, regardless of environment flags."""
        result = {
            "mode": "denied",
            "approved": False,
            "reason": "unlimited mode is prohibited; use bounded, reviewed increases",
            "limits": self.limits.copy(),
        }
        self._log_event("unlimited_mode_denied", result)
        return result

    def _log_event(self, event_type: str, data: Dict[str, Any]) -> None:
        event = {"type": event_type, "timestamp": time.time(), "data": data}
        try:
            with self.log_file.open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(event, sort_keys=True) + "\n")
        except OSError:
            pass


class EmergentArchitecture:
    """Reports demand pressure; automatic limit changes remain opt-in and bounded."""

    def __init__(self):
        self.bypass = LimitBypass()
        self.emergent_events: List[Dict[str, Any]] = []

    def detect_emergence(self, metrics: Dict[str, int]) -> Dict[str, Any]:
        events = []
        for metric_name, value in metrics.items():
            limit_name = f"max_{metric_name}"
            if limit_name in self.bypass.limits:
                result = self.bypass.auto_scale(limit_name, value)
                events.append({"metric": metric_name, "value": value, "decision": result})
        return {
            "emergence_detected": bool(events),
            "events": events,
            "current_limits": self.bypass.limits.copy(),
            "enabled": self.bypass.enabled,
        }

    def enable_unlimited_mode(self) -> Dict[str, Any]:
        return self.bypass.enable_unlimited_mode()

    def get_architecture_status(self) -> Dict[str, Any]:
        return {
            "limits": self.bypass.get_limits_status(),
            "bypassed_limits": self.bypass.bypassed_limits,
            "emergent_mode": "bounded" if self.bypass.enabled else "standard",
        }


def enable_scaling(
    limit_name: str,
    new_limit: int,
    approval_id: Optional[str] = None,
    approved_by: Optional[str] = None,
) -> Dict[str, Any]:
    return LimitBypass().bypass_limit(
        limit_name, new_limit, approval_id=approval_id, approved_by=approved_by
    )


def auto_scale_all(metrics: Dict[str, int]) -> Dict[str, Any]:
    return EmergentArchitecture().detect_emergence(metrics)


if __name__ == "__main__":
    bypass = LimitBypass()
    print(json.dumps({
        "status": "disabled-by-default",
        "limit_bypass_enabled": bypass.enabled,
        "unlimited_mode": bypass.enable_unlimited_mode()["mode"],
        "limits": bypass.get_limits_status(),
    }, indent=2))
