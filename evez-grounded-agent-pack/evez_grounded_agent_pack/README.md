
# EVEZ Grounded Agent Pack

This pack turns the uploaded EVEZOS specs and live-only bundles into a single grounded registry.

Contents:
- `agents.manifest.json` — canonical agent roster
- `registry.schema.json` — validation schema for the roster
- `workspace-plan.json` — route/screen to agent mapping
- `n8n-bindings.json` — workflow to endpoint bindings
- `GROUNDED_CUTOVER.md` — deployment and truth-boundary checklist

Intent:
- preserve the live-only boundary
- stop declared-only roles from pretending to be live runtime
- make UI surfaces read backend-owned state
