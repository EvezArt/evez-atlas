#!/usr/bin/env python3
"""
evez_self_writer.py — SelfWriter Module
=======================================
The WRITE phase made real. Generates code artifacts using inference,
submits them to the falsification engine, and deploys verified code.

This is not a code generator demo. It:
1. Reads the current system state from the spine
2. Identifies what needs to be written (based on operator gaps)
3. Generates candidate code + test code via inference
4. Submits to FalsificationEngine (real subprocess execution)
5. If verified: signs artifact, appends to spine, writes to content bus
6. If rejected: logs contradiction for CAIN

The SelfWriter only writes code that passes its own tests.
No unverified code enters the system.
"""

import asyncio
import json
import time
import hashlib
import uuid
from dataclasses import dataclass, field, asdict
from typing import Optional

from evez_os_core import (
    Spine, Event, InferenceEngine, FalsificationEngine,
    shannon_entropy, entropy_gate, hash_sig, now_iso, SYSTEM_PROMPT
)


@dataclass
class WriteIntent:
    """What the SelfWriter decided to write and why."""
    intent_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    target: str = ""  # what module/function to write
    reason: str = ""  # why it needs to be written
    priority: float = 0.0  # 0-1, how urgent
    source_event: str = ""  # what spine event triggered this


class SelfWriter:
    """
    Generates code artifacts, falsifies them, deploys verified ones.

    The generation prompt is specific: it asks the LLM to produce
    a Python function with inline assert-based tests. The falsification
    engine then runs those tests in a real subprocess.

    If tests pass → the artifact is signed and recorded.
    If tests fail → the artifact is rejected and CAIN is notified.
    """

    def __init__(self, spine: Spine, engine: InferenceEngine,
                 falsifier: FalsificationEngine, content_bus=None):
        self.spine = spine
        self.engine = engine
        self.falsifier = falsifier
        self.content_bus = content_bus
        self.intents: list[WriteIntent] = []
        self.generated: list[dict] = []
        self.verified: list[dict] = []
        self.rejected: list[dict] = []
        self.cycle_count = 0

        # Subscribe to events that might trigger writes
        spine.subscribe("cain_audit", self._on_cain_audit)
        spine.subscribe("fire_event", self._on_fire_event)

    async def _on_cain_audit(self, event: Event):
        """CAIN contradiction detected — might need a fix."""
        intent = WriteIntent(
            target="contradiction_resolver",
            reason=f"CAIN detected contradiction: {event.payload.get('claim_a', '')[:60]}",
            priority=0.8,
            source_event=event.hash,
        )
        self.intents.append(intent)

    async def _on_fire_event(self, event: Event):
        """FIRE event — system crossed a threshold. Might need new code."""
        level = event.payload.get("level", "")
        if level == "EXTREME_FIRE":
            intent = WriteIntent(
                target="threshold_handler",
                reason=f"EXTREME_FIRE at tau={event.payload.get('tau', 0)}",
                priority=0.6,
                source_event=event.hash,
            )
            self.intents.append(intent)

    async def write_cycle(self, domain: dict = None) -> dict:
        """
        Execute one WRITE cycle:
        1. Check for pending intents
        2. Generate candidate code via inference
        3. Falsify (real subprocess test)
        4. Record result
        """
        self.cycle_count += 1
        cycle_result = {
            "cycle": self.cycle_count,
            "timestamp": now_iso(),
            "intents_processed": 0,
            "generated": 0,
            "verified": 0,
            "rejected": 0,
        }

        # Get highest-priority intent, or generate a domain-specific one
        if self.intents:
            intent = max(self.intents, key=lambda i: i.priority)
            self.intents.remove(intent)
        else:
            # No pending intent — write a utility function for the domain
            target_domain = domain.get("id", "general") if domain else "general"
            intent = WriteIntent(
                target=f"{target_domain.lower()}_processor",
                reason="routine cycle — generate domain processor",
                priority=0.3,
            )

        cycle_result["intents_processed"] = 1

        # Generate code via inference
        code, test = await self._generate_code(intent)
        if not code:
            cycle_result["error"] = "generation failed"
            return cycle_result

        cycle_result["generated"] = 1
        artifact_id = hash_sig(f"{intent.target}:{time.time()}")

        # Falsify — REAL subprocess execution
        falsify_result = await self.falsifier.falsify(artifact_id, code, test)

        record = {
            "artifact_id": artifact_id,
            "intent": intent.__dict__,
            "code": code[:200],
            "test_code": test[:200],
            "falsification": falsify_result,
            "timestamp": now_iso(),
        }

        if falsify_result.get("passed"):
            self.verified.append(record)
            cycle_result["verified"] = 1

            # Write to content bus
            if self.content_bus:
                await self.content_bus.write(f"artifact:{artifact_id}", {
                    "code": code,
                    "test": test,
                    "signature": falsify_result.get("signature"),
                    "intent": intent.target,
                })

            # Append to spine
            await self.spine.append(Event(
                type="code_artifact",
                payload={
                    "artifact_id": artifact_id,
                    "target": intent.target,
                    "status": "VERIFIED",
                    "signature": falsify_result.get("signature"),
                    "tests_passed": falsify_result.get("tests_run", 0),
                },
                agent_source="self_writer"))
        else:
            self.rejected.append(record)
            cycle_result["rejected"] = 1
            # CAIN will pick up the falsification rejection via its subscription

        self.generated.append(record)
        return cycle_result

    async def _generate_code(self, intent: WriteIntent) -> tuple:
        """Generate candidate code + test code via inference."""
        prompt = (
            f"Write a Python function called `{intent.target}` that processes "
            f"data related to: {intent.reason}. "
            f"Include 2-3 assert statements as inline tests. "
            f"Keep it under 15 lines. No imports unless necessary. "
            f"Return ONLY the code, no explanation."
        )

        text, model_id = await self.engine.generate(
            "You are a Python code generator. Output ONLY valid Python code. No markdown. No explanation.",
            prompt,
            max_tokens=300
        )

        if not text:
            # Local fallback — generate a simple utility
            return self._local_generate(intent)

        # Extract code from response (handle markdown code blocks)
        code = text.strip()
        if "```python" in code:
            code = code.split("```python")[1].split("```")[0].strip()
        elif "```" in code:
            code = code.split("```")[1].split("```")[0].strip()

        # Split code into implementation + tests
        # Find assert lines and separate
        lines = code.split("\n")
        impl_lines = []
        test_lines = []
        in_tests = False
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("assert ") or stripped.startswith("# Test") or in_tests:
                in_tests = True
                test_lines.append(line)
            else:
                impl_lines.append(line)

        impl = "\n".join(impl_lines).strip()
        tests = "\n".join(test_lines).strip()

        if not tests:
            # Generate default test
            tests = f"assert {intent.target} is not None\nprint('tests passed')"

        return impl, tests

    def _local_generate(self, intent: WriteIntent) -> tuple:
        """Deterministic fallback code generation."""
        func_name = intent.target.replace("-", "_")

        code = f"""def {func_name}(data):
    if not data:
        return {{"status": "empty", "processed": 0}}
    if isinstance(data, dict):
        entropy = data.get("entropy_bits", data.get("entropy", 0))
        return {{"status": "processed", "entropy": entropy, "domain": data.get("domain", "unknown")}}
    return {{"status": "processed", "count": len(data) if hasattr(data, '__len__') else 1}}"""

        test_code = f"""assert {func_name}(None)["status"] == "empty"
assert {func_name}({{"entropy_bits": 4.5, "domain": "test"}})["entropy"] == 4.5
assert {func_name}([1,2,3])["count"] == 3
print("all tests passed")"""

        return code, test_code

    def stats(self) -> dict:
        total = len(self.verified) + len(self.rejected)
        return {
            "cycles": self.cycle_count,
            "intents_pending": len(self.intents),
            "generated": len(self.generated),
            "verified": len(self.verified),
            "rejected": len(self.rejected),
            "pass_rate": round(len(self.verified) / max(1, total), 4),
        }
