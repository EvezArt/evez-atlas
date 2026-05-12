#!/usr/bin/env python3
"""
EVEZ-OS Live Workflow Orchestrator
Wires the workflow-orchestrator skill to actual EVEZ-OS services
"""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from orchestrator import Workflow, Step, Runner

# Real EVEZ-OS agent executors — they call the actual services
import urllib.request, urllib.error

def call_service(port, endpoint, method="GET", data=None):
    """Call an actual EVEZ-OS service"""
    url = f"http://localhost:{port}{endpoint}"
    try:
        if method == "POST" and data:
            req = urllib.request.Request(url, data=json.dumps(data).encode(), headers={"Content-Type": "application/json"}, method="POST")
        else:
            req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        return {"error": str(e)}

# Register real agent executors
def consciousness_agent(action, params, ctx):
    """Consciousness Engine agent"""
    if action == "observe":
        return call_service(9111, "/api/observe", "POST", {"observation": params.get("observation",""), "priority": params.get("priority","medium")})
    elif action == "status":
        return call_service(9092, "/api/status")
    elif action == "desires":
        return call_service(9092, "/api/desires")
    elif action == "thoughts":
        return call_service(9092, "/api/thoughts")
    return {"result": f"unknown action {action}"}

def knowledge_agent(action, params, ctx):
    """Knowledge Graph agent"""
    if action == "stats":
        return call_service(9096, "/api/stats")
    elif action == "add":
        return call_service(9096, "/api/add", "POST", params)
    elif action == "query":
        return call_service(9096, "/api/query", "POST", params)
    return {"result": f"unknown action {action}"}

def debate_agent(action, params, ctx):
    """Debate Engine agent"""
    if action == "debate":
        return call_service(9097, "/api/debate", "POST", params)
    return {"result": f"unknown action {action}"}

def dashboard_agent(action, params, ctx):
    """Dashboard / Health agent"""
    if action == "health":
        return call_service(9100, "/api/health")
    elif action == "metrics":
        return call_service(9100, "/api/metrics")
    return {"result": f"unknown action {action}"}

def scanner_agent(action, params, ctx):
    """Scanner agent"""
    if action == "scan":
        return call_service(9099, "/api/scan", "POST", {})
    return {"result": f"unknown action {action}"}

def forge_agent(action, params, ctx):
    """Evolutionary Forge agent"""
    if action == "forge":
        return call_service(9098, "/api/forge", "POST", params)
    return {"result": f"unknown action {action}"}

# ============================================================
# WORKFLOW 1: Full System Health Check + Knowledge Growth
# ============================================================
def run_health_workflow():
    wf = Workflow("evez-health-check")
    wf.add_step(Step("check_health", agent="dashboard", action="health", params={}))
    wf.add_step(Step("scan_services", agent="scanner", action="scan", depends_on=["check_health"]))
    wf.add_step(Step("check_knowledge", agent="knowledge", action="stats", depends_on=["check_health"]))
    wf.add_step(Step("check_consciousness", agent="consciousness", action="status", depends_on=["check_health"]))
    wf.add_step(Step("debate_knowledge", agent="debate", action="debate", 
                     params={"topic": "Is the knowledge graph growing healthily?", "rounds": 1},
                     depends_on=["check_knowledge"]))
    wf.add_step(Step("observe_results", agent="consciousness", action="observe",
                     params={"observation": "Health workflow completed", "priority": "low"},
                     depends_on=["debate_knowledge", "check_consciousness"]))
    return wf

# ============================================================
# WORKFLOW 2: Consciousness-Driven Knowledge Expansion
# ============================================================
def run_expansion_workflow():
    wf = Workflow("consciousness-expansion")
    wf.add_step(Step("sense_state", agent="consciousness", action="status", params={}))
    wf.add_step(Step("check_graph", agent="knowledge", action="stats", depends_on=["sense_state"]))
    wf.add_step(Step("debate_direction", agent="debate", action="debate",
                     params={"topic": "What knowledge should EVEZ-OS acquire next?", "rounds": 1},
                     depends_on=["check_graph"]))
    wf.add_step(Step("add_knowledge", agent="knowledge", action="add",
                     params={"node": {"label": "Workflow_Result", "type": "outcome"},
                             "edge": {"from": "MetaPipeline", "to": "Workflow_Result", "relation": "produces"}},
                     depends_on=["debate_direction"],
                     on_failure="skip"))
    wf.add_step(Step("observe_expansion", agent="consciousness", action="observe",
                     params={"observation": "Knowledge expansion workflow completed", "priority": "medium"},
                     depends_on=["add_knowledge"]))
    return wf

# ============================================================
# WORKFLOW 3: Self-Modification Pipeline
# ============================================================
def run_modification_workflow():
    wf = Workflow("self-modification")
    wf.add_step(Step("health_baseline", agent="dashboard", action="health", params={}))
    wf.add_step(Step("conscious_desires", agent="consciousness", action="desires", depends_on=["health_baseline"]))
    wf.add_step(Step("knowledge_state", agent="knowledge", action="stats", depends_on=["health_baseline"]))
    wf.add_step(Step("debate_modification", agent="debate", action="debate",
                     params={"topic": "Should EVEZ-OS modify any subsystems based on current state?", "rounds": 1},
                     depends_on=["conscious_desires", "knowledge_state"]))
    return wf

# Run all workflows
if __name__ == "__main__":
    runner = Runner(max_workers=4)
    runner.register_agent("consciousness", consciousness_agent)
    runner.register_agent("knowledge", knowledge_agent)
    runner.register_agent("debate", debate_agent)
    runner.register_agent("dashboard", dashboard_agent)
    runner.register_agent("scanner", scanner_agent)
    runner.register_agent("forge", forge_agent)

    workflows = [
        ("Health Check", run_health_workflow),
        ("Knowledge Expansion", run_expansion_workflow),
        ("Self-Modification", run_modification_workflow),
    ]

    results = {}
    for name, wf_fn in workflows:
        print(f"\n{'='*60}")
        print(f"  WORKFLOW: {name}")
        print(f"{'='*60}")
        wf = wf_fn()
        result = runner.execute(wf)
        results[name] = result

        print(f"\n  Status: {result['status']} ({result['completed']}/{result['total']} completed, {result['failed']} failed)")
        print(f"\n  Step Results:")
        for step_name, sr in result["results"].items():
            st = sr["status"]
            dur = sr["duration_sec"]
            err = sr.get("error", "")
            icon = "✅" if st == "completed" else "⚠️" if st == "skipped" else "❌"
            line = f"    {icon} {step_name}: {st} ({dur}s)"
            if err: line += f" — {str(err)[:60]}"
            print(line)
            output = sr.get("output")
            if output and isinstance(output, dict):
                for k, v in list(output.items())[:3]:
                    print(f"       {k}: {str(v)[:80]}")

    # Save results
    out_path = "/home/openclaw/.openclaw/workspace/generated-assets/workflow_results.json"
    with open(out_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n📊 Results saved to {out_path}")
