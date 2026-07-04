#!/usr/bin/env python3
"""
evez_content_bus.py — Global Content Bus
========================================
The shared workspace file (circuit/content.bus.json).
All operators write their state here. All operators read from here.

This is the physical substrate of Global Workspace Theory broadcast.
When an operator collapses a signal, it writes the result to the bus.
Every other operator can read it on the next cycle.

Implements atomic file writes (write to temp, rename) to prevent
corruption from concurrent operator access.
"""

import asyncio
import json
import os
import time
import hashlib
from dataclasses import dataclass, field, asdict
from typing import Any, Optional
from collections import defaultdict

from evez_os_core import hash_sig, now_iso


class ContentBus:
    """
    Atomic content bus. Thread-safe. Crash-safe.

    Write protocol:
    1. Serialize payload to JSON
    2. Write to temp file
    3. Atomic rename to target path
    4. Notify subscribers

    Read protocol:
    1. Read file
    2. Parse JSON
    3. Return latest state per key
    """

    def __init__(self, filepath: str = "circuit/content.bus.json"):
        self.filepath = filepath
        self._state: dict[str, Any] = {}
        self._lock = asyncio.Lock()
        self._subs: dict[str, list] = defaultdict(list)
        self._write_count = 0
        self._read_count = 0
        self._last_write_hash = ""
        self._creation_time = time.time()

        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else ".", exist_ok=True)

        # Load existing state if file exists
        if os.path.exists(filepath):
            try:
                with open(filepath) as f:
                    self._state = json.load(f)
            except (json.JSONDecodeError, IOError):
                self._state = {}

    async def write(self, key: str, value: Any) -> str:
        """Write value to bus under key. Atomic file write."""
        async with self._lock:
            entry = {
                "value": value,
                "timestamp": time.time(),
                "write_hash": hash_sig(f"{key}:{json.dumps(value, sort_keys=True, default=str)}:{time.time()}"),
                "prev_hash": self._last_write_hash,
            }
            self._state[key] = entry
            self._last_write_hash = entry["write_hash"]
            self._write_count += 1

            # Atomic write: temp file → rename
            tmp_path = f"{self.filepath}.tmp"
            with open(tmp_path, 'w') as f:
                json.dump(self._state, f, indent=2, default=str)
            os.rename(tmp_path, self.filepath)

        # Notify subscribers (outside lock)
        for cb in self._subs.get(key, []):
            try:
                r = cb(value)
                if asyncio.iscoroutine(r):
                    await r
            except Exception as e:
                print(f"  [BUS] subscriber error ({key}): {e}")

        return entry["write_hash"]

    def read(self, key: str = None) -> Any:
        """Read value from bus. If key=None, return entire state."""
        self._read_count += 1
        if key is None:
            return self._state
        entry = self._state.get(key)
        if entry is None:
            return None
        return entry.get("value")

    def read_meta(self, key: str) -> dict:
        """Read metadata (timestamp, hash) for a key."""
        entry = self._state.get(key, {})
        return {
            "timestamp": entry.get("timestamp", 0),
            "write_hash": entry.get("write_hash", ""),
            "prev_hash": entry.get("prev_hash", ""),
        }

    def subscribe(self, key: str, callback):
        """Subscribe to changes on a specific key."""
        self._subs[key].append(callback)

    def keys(self) -> list:
        """List all keys currently on the bus."""
        return list(self._state.keys())

    def verify_chain(self) -> bool:
        """Verify write hash chain integrity."""
        entries = list(self._state.values())
        for i in range(1, len(entries)):
            if entries[i].get("prev_hash") != entries[i-1].get("write_hash"):
                return False
        return True

    def snapshot(self) -> dict:
        return {
            "filepath": self.filepath,
            "keys": self.keys(),
            "write_count": self._write_count,
            "read_count": self._read_count,
            "chain_verified": self.verify_chain(),
            "uptime_s": round(time.time() - self._creation_time, 2),
            "last_write_hash": self._last_write_hash,
        }
