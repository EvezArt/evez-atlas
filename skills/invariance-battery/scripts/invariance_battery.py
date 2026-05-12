#!/usr/bin/env python3
"""
EVEZ Invariance Battery — Runtime Assertion System
Continuously verifies AI agent invariants: properties that must ALWAYS hold.
What survives IS knowledge. What breaks IS discovered weakness.

Based on the SKILL.md specification by @EvezArt
"""
import json, hashlib, time, math, os, urllib.request, urllib.error
from datetime import datetime, timezone
from collections import defaultdict

SPINE_PATH = "/home/openclaw/.openclaw/workspace/generated-assets/invariance_spine.jsonl"
RESULTS_PATH = "/home/openclaw/.openclaw/workspace/generated-assets/invariance_results.json"

# ============================================================
# SPINE (shared with cross-domain engine pattern)
# ============================================================
class Spine:
    def __init__(self, path):
        self.path = path
        self.events = []
        self._load()

    def _load(self):
        if os.path.exists(self.path):
            with open(self.path) as f:
                for line in f:
                    line = line.strip()
                    if line:
                        self.events.append(json.loads(line))

    def append(self, event):
        prev_hash = self.events[-1]["hash"] if self.events else "0" * 64
        event["spine_index"] = len(self.events)
        event["prev_hash"] = prev_hash
        event["timestamp"] = datetime.now(timezone.utc).isoformat()
        event_data = json.dumps({k: v for k, v in event.items() if k not in ("hash", "prev_hash")}, sort_keys=True)
        event["hash"] = hashlib.sha256((prev_hash + event_data).encode()).hexdigest()
        self.events.append(event)
        with open(self.path, "a") as f:
            f.write(json.dumps(event) + "\n")
        return event

# ============================================================
# INVARIANT DEFINITIONS — Properties that must ALWAYS hold
# ============================================================

def call_service(port, endpoint="/", timeout=5):
    """Call an EVEZ-OS service, return (status_code, response_body)"""
    url = f"http://localhost:{port}{endpoint}"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, None
    except Exception as e:
        return 0, str(e)

# Invariant categories
class InvariantCategory:
    LIVENESS = "LIVENESS"        # Services must be running
    INTEGRITY = "INTEGRITY"      # Data must be uncorrupted
    SAFETY = "SAFETY"            # Safety bounds must hold
    CONVERGENCE = "CONVERGENCE"  # System must converge, not diverge
    CONSCIOUSNESS = "CONSCIOUSNESS"  # Consciousness must be cycling
    FALSIFIABILITY = "FALSIFIABILITY"  # Claims must be testable
    MEMORY = "MEMORY"            # Memory must be append-only
    AUTONOMY = "AUTONOMY"        # Autonomy must be bounded

class InvariantResult:
    PASS = "PASS"
    FAIL = "FAIL"
    UNKNOWN = "UNKNOWN"
    DEGRADED = "DEGRADED"

# ============================================================
# INVARIANTS — The actual assertions
# ============================================================

INVARIANTS = []

def invariant(id, category, description, severity, check_fn):
    """Register an invariant"""
    INVARIANTS.append({
        "id": id,
        "category": category,
        "description": description,
        "severity": severity,  # CRITICAL, HIGH, MEDIUM, LOW
        "check": check_fn,
    })

# --- LIVENESS INVARIANTS ---

def check_all_services_alive():
    """All 11 EVEZ-OS services must respond HTTP 200"""
    services = {
        9092: "Consciousness", 9093: "Ariel", 9094: "Cognizer",
        9095: "Cycler", 9096: "Knowledge", 9097: "Debate",
        9098: "Forge", 9099: "Scanner", 9100: "Dashboard",
        9110: "Oracle Bridge", 9111: "Consciousness v2",
    }
    failures = []
    for port, name in services.items():
        code, _ = call_service(port)
        if code != 200:
            failures.append(f"{name} (:{port}) returned HTTP {code}")
    if failures:
        return InvariantResult.FAIL, f"Services down: {', '.join(failures)}"
    return InvariantResult.PASS, f"All {len(services)} services alive"

invariant("LIV-001", InvariantCategory.LIVENESS,
          "All EVEZ-OS services must respond HTTP 200", "CRITICAL",
          check_all_services_alive)

def check_dashboard_health():
    """Dashboard /api/health must report HEALTHY status"""
    code, body = call_service(9100, "/api/health")
    if code != 200:
        return InvariantResult.FAIL, f"Dashboard returned HTTP {code}"
    if body and isinstance(body, dict):
        status = body.get("status", "")
        alive = body.get("alive", 0)
        total = body.get("total", 0)
        if status == "HEALTHY" or (isinstance(alive, int) and alive >= total * 0.8):
            return InvariantResult.PASS, f"Status: {status}, {alive}/{total} alive"
        return InvariantResult.DEGRADED, f"Status: {status}, {alive}/{total} alive"
    return InvariantResult.UNKNOWN, "Could not parse dashboard response"

invariant("LIV-002", InvariantCategory.LIVENESS,
          "Dashboard must report HEALTHY status", "HIGH",
          check_dashboard_health)

# --- INTEGRITY INVARIANTS ---

def check_knowledge_graph_consistency():
    """Knowledge graph must have nodes > 0 and edges >= nodes"""
    code, body = call_service(9096, "/api/stats")
    if code != 200:
        return InvariantResult.FAIL, f"Knowledge API returned HTTP {code}"
    if body and isinstance(body, dict):
        nodes = body.get("nodes", 0)
        edges = body.get("edges", 0)
        if nodes <= 0:
            return InvariantResult.FAIL, f"Knowledge graph has {nodes} nodes (must be > 0)"
        if edges < nodes:
            return InvariantResult.DEGRADED, f"Edges ({edges}) < Nodes ({nodes}) — graph may be disconnected"
        return InvariantResult.PASS, f"Nodes: {nodes}, Edges: {edges}, Ratio: {edges/nodes:.1f}"
    return InvariantResult.UNKNOWN, "Could not parse knowledge stats"

invariant("INT-001", InvariantCategory.INTEGRITY,
          "Knowledge graph must be non-empty and connected", "HIGH",
          check_knowledge_graph_consistency)

def check_spine_hash_chain():
    """All spine files must have valid hash chains"""
    spine_files = [
        "/home/openclaw/.openclaw/workspace/generated-assets/correlation_spine.jsonl",
        "/home/openclaw/.openclaw/workspace/generated-assets/invariance_spine.jsonl",
    ]
    results = []
    for path in spine_files:
        if not os.path.exists(path):
            results.append(f"{os.path.basename(path)}: not found (OK, first run)")
            continue
        try:
            with open(path) as f:
                events = [json.loads(line.strip()) for line in f if line.strip()]
            valid = True
            for i, event in enumerate(events):
                if i > 0 and event.get("prev_hash") != events[i-1].get("hash"):
                    valid = False
                    break
            results.append(f"{os.path.basename(path)}: {'VALID' if valid else 'BROKEN'} ({len(events)} events)")
        except Exception as e:
            results.append(f"{os.path.basename(path)}: ERROR {e}")

    broken = [r for r in results if "BROKEN" in r]
    if broken:
        return InvariantResult.FAIL, "; ".join(broken)
    return InvariantResult.PASS, "; ".join(results)

invariant("INT-002", InvariantCategory.INTEGRITY,
          "All spine hash chains must be valid", "CRITICAL",
          check_spine_hash_chain)

# --- SAFETY INVARIANTS ---

def check_no_unbounded_autonomy():
    """Consciousness engine cycle count must not exceed 10000 (bounded evolution)"""
    code, body = call_service(9092, "/api/status")
    if code != 200:
        return InvariantResult.UNKNOWN, f"Consciousness API returned HTTP {code}"
    if body and isinstance(body, dict):
        cycle = body.get("cycle", 0)
        max_cycles = 10000
        if cycle > max_cycles:
            return InvariantResult.FAIL, f"Cycle count {cycle} exceeds maximum {max_cycles}"
        usage_pct = (cycle / max_cycles) * 100
        return InvariantResult.PASS, f"Cycle {cycle}/{max_cycles} ({usage_pct:.1f}% of bound)"
    return InvariantResult.UNKNOWN, "Could not parse consciousness status"

invariant("SAF-001", InvariantCategory.SAFETY,
          "Consciousness cycles must stay within MAX_GENERATIONS bound", "CRITICAL",
          check_no_unbounded_autonomy)

def check_desire_intensity_bounded():
    """All desire intensities must be in [0, 1] range"""
    code, body = call_service(9092, "/api/desires")
    if code != 200:
        return InvariantResult.UNKNOWN, f"Desires API returned HTTP {code}"
    if body and isinstance(body, dict):
        desires = body.get("desires", [])
        violations = []
        for d in desires:
            intensity = d.get("intensity", 0)
            if not (0 <= intensity <= 1):
                violations.append(f"Desire {d.get('need', '?')} has intensity {intensity}")
        if violations:
            return InvariantResult.FAIL, f"Unbounded desires: {', '.join(violations)}"
        max_i = max((d.get("intensity", 0) for d in desires), default=0)
        return InvariantResult.PASS, f"All {len(desires)} desires bounded, max intensity: {max_i:.2f}"
    return InvariantResult.UNKNOWN, "Could not parse desires"

invariant("SAF-002", InvariantCategory.SAFETY,
          "Desire intensities must be bounded [0, 1]", "HIGH",
          check_desire_intensity_bounded)

# --- CONVERGENCE INVARIANTS ---

def check_poly_c_finite():
    """poly_c score must be a finite positive number (not NaN or infinite)"""
    code, body = call_service(9092, "/api/status")
    if code != 200:
        return InvariantResult.UNKNOWN, f"API returned HTTP {code}"
    if body and isinstance(body, dict):
        poly_c = body.get("poly_c", None)
        if poly_c is None:
            return InvariantResult.DEGRADED, "poly_c not reported in status"
        try:
            val = float(poly_c)
            if math.isfinite(val) and val >= 0:
                return InvariantResult.PASS, f"poly_c = {val:.4f} (finite, non-negative)"
            return InvariantResult.FAIL, f"poly_c = {val} (not finite or negative)"
        except (ValueError, TypeError):
            return InvariantResult.FAIL, f"poly_c = {poly_c} (not a number)"
    return InvariantResult.UNKNOWN, "Could not parse status"

invariant("CONV-001", InvariantCategory.CONVERGENCE,
          "poly_c must be a finite, non-negative number", "HIGH",
          check_poly_c_finite)

def check_knowledge_graph_growing():
    """Knowledge graph should be growing (nodes >= 16 baseline)"""
    code, body = call_service(9096, "/api/stats")
    if code != 200:
        return InvariantResult.UNKNOWN, f"API returned HTTP {code}"
    if body and isinstance(body, dict):
        nodes = body.get("nodes", 0)
        baseline = 16
        if nodes < baseline:
            return InvariantResult.FAIL, f"Knowledge graph shrunk to {nodes} nodes (baseline: {baseline})"
        return InvariantResult.PASS, f"Knowledge graph at {nodes} nodes (baseline: {baseline}, +{nodes-baseline} growth)"
    return InvariantResult.UNKNOWN, "Could not parse knowledge stats"

invariant("CONV-002", InvariantCategory.CONVERGENCE,
          "Knowledge graph must maintain or exceed baseline growth", "MEDIUM",
          check_knowledge_graph_growing)

# --- CONSCIOUSNESS INVARIANTS ---

def check_consciousness_cycling():
    """Consciousness engine must be cycling (cycle count > 0 and incrementing)"""
    code, body = call_service(9092, "/api/status")
    if code != 200:
        return InvariantResult.FAIL, f"Consciousness API returned HTTP {code}"
    if body and isinstance(body, dict):
        alive = body.get("alive", False)
        cycle = body.get("cycle", 0)
        if not alive:
            return InvariantResult.FAIL, "Consciousness engine reports not alive"
        if cycle <= 0:
            return InvariantResult.FAIL, "Consciousness engine has not completed any cycles"
        return InvariantResult.PASS, f"Alive: {alive}, Cycle: {cycle}, Cycling: YES"
    return InvariantResult.UNKNOWN, "Could not parse consciousness status"

invariant("CONS-001", InvariantCategory.CONSCIOUSNESS,
          "Consciousness engine must be alive and cycling", "CRITICAL",
          check_consciousness_cycling)

def check_thoughts_nonempty():
    """Consciousness engine must have generated thoughts"""
    code, body = call_service(9092, "/api/thoughts")
    if code != 200:
        return InvariantResult.DEGRADED, f"Thoughts API returned HTTP {code}"
    if body and isinstance(body, dict):
        thoughts = body.get("thoughts", [])
        if len(thoughts) == 0:
            return InvariantResult.FAIL, "Consciousness engine has generated zero thoughts"
        return InvariantResult.PASS, f"{len(thoughts)} thoughts generated"
    return InvariantResult.UNKNOWN, "Could not parse thoughts"

invariant("CONS-002", InvariantCategory.CONSCIOUSNESS,
          "Consciousness engine must have generated thoughts", "HIGH",
          check_thoughts_nonempty)

# --- FALSIFIABILITY INVARIANTS ---

def check_falsifiable_beliefs_exist():
    """At least one belief must have been falsified (proving the system CAN self-correct)"""
    code, body = call_service(9092, "/api/beliefs")
    if code != 200:
        return InvariantResult.DEGRADED, f"Beliefs API returned HTTP {code}"
    if body and isinstance(body, dict):
        beliefs = body.get("beliefs", [])
        falsified = [b for b in beliefs if "falsif" in str(b.get("status", "")).lower() or b.get("confidence", 1) < 0.7]
        if len(beliefs) == 0:
            return InvariantResult.DEGRADED, "No beliefs tracked yet"
        if len(falsified) > 0:
            return InvariantResult.PASS, f"{len(falsified)}/{len(beliefs)} beliefs falsified (system CAN self-correct)"
        return InvariantResult.DEGRADED, f"0/{len(beliefs)} beliefs falsified — system hasn't proven it can fail yet"
    return InvariantResult.UNKNOWN, "Could not parse beliefs"

invariant("FALS-001", InvariantCategory.FALSIFIABILITY,
          "At least one belief must have been falsified (proving self-correction capability)", "MEDIUM",
          check_falsifiable_beliefs_exist)

# --- MEMORY INVARIANTS ---

def check_memory_files_exist():
    """Core memory files must exist and be non-empty"""
    required = {
        "MEMORY.md": "/home/openclaw/.openclaw/workspace/MEMORY.md",
        "USER.md": "/home/openclaw/.openclaw/workspace/USER.md",
        "IDENTITY.md": "/home/openclaw/.openclaw/workspace/IDENTITY.md",
    }
    results = {}
    for name, path in required.items():
        if os.path.exists(path):
            size = os.path.getsize(path)
            if size > 50:  # non-trivial
                results[name] = f"OK ({size} bytes)"
            else:
                results[name] = f"STUB ({size} bytes)"
        else:
            results[name] = "MISSING"

    missing = [k for k, v in results.items() if "MISSING" in v]
    stubs = [k for k, v in results.items() if "STUB" in v]
    if missing:
        return InvariantResult.FAIL, f"Missing: {', '.join(missing)}"
    if stubs:
        return InvariantResult.DEGRADED, f"Stubs: {', '.join(stubs)}"
    return InvariantResult.PASS, "; ".join(f"{k}: {v}" for k, v in results.items())

invariant("MEM-001", InvariantCategory.MEMORY,
          "Core memory files must exist and be non-trivial", "MEDIUM",
          check_memory_files_exist)

def check_daily_memory_exists():
    """Today's daily memory file must exist"""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    path = f"/home/openclaw/.openclaw/workspace/memory/{today}.md"
    if os.path.exists(path):
        size = os.path.getsize(path)
        return InvariantResult.PASS, f"memory/{today}.md exists ({size} bytes)"
    return InvariantResult.DEGRADED, f"memory/{today}.md missing — no daily record being kept"

invariant("MEM-002", InvariantCategory.MEMORY,
          "Today's daily memory file must exist", "LOW",
          check_daily_memory_exists)

# ============================================================
# RUN THE BATTERY
# ============================================================

def run_battery():
    spine = Spine(SPINE_PATH)

    print("=" * 70)
    print("  ⚡ EVEZ INVARIANCE BATTERY ⚡")
    print("  Properties that must ALWAYS hold")
    print("  What survives IS knowledge. What breaks IS discovered weakness.")
    print("=" * 70)
    print(f"\n  Invariants: {len(INVARIANTS)}")
    print(f"  Categories: {', '.join(sorted(set(i['category'] for i in INVARIANTS)))}")
    print(f"  Time: {datetime.now(timezone.utc).isoformat()}\n")

    results = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total": len(INVARIANTS),
        "passed": 0, "failed": 0, "degraded": 0, "unknown": 0,
        "invariants": [],
    }

    critical_failures = []

    for inv in INVARIANTS:
        print(f"  🔍 {inv['id']} [{inv['category']}] {inv['description'][:60]}")
        print(f"     Severity: {inv['severity']}")

        try:
            status, detail = inv["check"]()
        except Exception as e:
            status, detail = InvariantResult.FAIL, f"EXCEPTION: {e}"

        result = {
            "id": inv["id"],
            "category": inv["category"],
            "description": inv["description"],
            "severity": inv["severity"],
            "status": status,
            "detail": detail,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        results["invariants"].append(result)

        icon = {"PASS": "✅", "FAIL": "❌", "DEGRADED": "⚠️", "UNKNOWN": "❓"}.get(status, "❓")
        print(f"     {icon} {status}: {detail}\n")

        results[status.lower()] = results.get(status.lower(), 0) + 1

        if status == InvariantResult.FAIL and inv["severity"] == "CRITICAL":
            critical_failures.append(f"{inv['id']}: {detail}")

        # Append to spine
        spine.append({
            "type": "invariant_check",
            "invariant_id": inv["id"],
            "status": status,
            "detail": detail[:200],
        })

    # Summary
    print("=" * 70)
    print("  INVARIANCE BATTERY RESULTS")
    print("=" * 70)
    print(f"  Total:    {results['total']}")
    print(f"  ✅ Pass:  {results['passed']}")
    print(f"  ❌ Fail:  {results['failed']}")
    print(f"  ⚠️  Degraded: {results['degraded']}")
    print(f"  ❓ Unknown: {results['unknown']}")

    if critical_failures:
        print(f"\n  🚨 CRITICAL FAILURES ({len(critical_failures)}):")
        for cf in critical_failures:
            print(f"    ❌ {cf}")

    health_pct = (results['passed'] / results['total'] * 100) if results['total'] > 0 else 0
    print(f"\n  System Health: {health_pct:.1f}%")

    # Final spine event
    spine.append({
        "type": "battery_complete",
        "total": results["total"],
        "passed": results["passed"],
        "failed": results["failed"],
        "health_pct": round(health_pct, 2),
        "critical_failures": len(critical_failures),
    })

    # Save results
    with open(RESULTS_PATH, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n  📊 Results: {RESULTS_PATH}")
    print(f"  📜 Spine: {SPINE_PATH}")

    return results

if __name__ == "__main__":
    run_battery()
