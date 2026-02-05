"""
Telemetry module for automation assistant

Tracks helper spawn latency, backend success rates, and error rates.
Appends structured JSONL entries to src/memory/audit.jsonl
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import threading


class TelemetryLogger:
    """Thread-safe telemetry logger for automation assistant."""
    
    def __init__(self, audit_file: str = "src/memory/audit.jsonl"):
        self.audit_file = Path(audit_file)
        self.audit_file.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self.run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def log_event(self, event: str, **kwargs):
        """Log a telemetry event to the audit file."""
        entry = {
            "timestamp": time.time(),
            "run_id": self.run_id,
            "event": event,
            **kwargs
        }
        
        with self._lock:
            try:
                with open(self.audit_file, 'a') as f:
                    f.write(json.dumps(entry) + '\n')
            except Exception as e:
                # Don't let telemetry failures crash the app
                print(f"Telemetry logging failed: {e}")
    
    def log_helper_spawn(self, helper_id: str, backend: str, latency_ms: float, success: bool, error: Optional[str] = None):
        """Log a helper spawn event."""
        self.log_event(
            "helper_spawn",
            helper_id=helper_id,
            backend=backend,
            latency_ms=latency_ms,
            success=success,
            error=error
        )
    
    def log_backend_call(self, helper_id: str, backend: str, latency_ms: float, success: bool, error: Optional[str] = None):
        """Log a backend API call event."""
        self.log_event(
            "backend_call",
            helper_id=helper_id,
            backend=backend,
            latency_ms=latency_ms,
            success=success,
            error=error
        )
    
    def log_task_complete(self, helper_id: str, task_id: str, backend: str, latency_ms: float, success: bool, error: Optional[str] = None):
        """Log a task completion event."""
        self.log_event(
            "task_complete",
            helper_id=helper_id,
            task_id=task_id,
            backend=backend,
            latency_ms=latency_ms,
            success=success,
            error=error
        )


# Global telemetry instance
_telemetry = None


def get_telemetry() -> TelemetryLogger:
    """Get or create the global telemetry logger instance."""
    global _telemetry
    if _telemetry is None:
        _telemetry = TelemetryLogger()
    return _telemetry


def compute_stability_score(success_count: int, error_count: int) -> float:
    """
    Compute stability score as 1 - (errors / total).
    Returns 1.0 for perfect stability, 0.0 for complete failure.
    """
    total = success_count + error_count
    if total == 0:
        return 1.0
    return 1.0 - (error_count / total)
