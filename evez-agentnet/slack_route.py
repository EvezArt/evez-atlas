#!/usr/bin/env python3
"""
/api/slack/route — Slack webhook handler for EVEZ AgentNet
n8n-compatible payloads for Linear/Asana import.
"""
import json
from datetime import datetime, timezone

def handle_slack_event(payload):
    event_type = payload.get("type", "unknown")
    user = payload.get("user", "unknown")
    text = payload.get("text", "")

    # Parse commands
    if "@vez" in text or "@evez" in text:
        command = text.split("@vez")[-1].strip() if "@vez" in text else text.split("@evez")[-1].strip()
        return {
            "status": "COMMAND_RECEIVED",
            "command": command,
            "user": user,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "n8n_compatible": {
                "source": "slack",
                "action": "route_to_agent",
                "payload": {"command": command, "user": user, "channel": payload.get("channel")}
            }
        }

    return {"status": "IGNORED", "reason": "no_command_detected"}

if __name__ == "__main__":
    demo = {"type": "message", "user": "U123", "text": "@vez status", "channel": "C456"}
    print(json.dumps(handle_slack_event(demo), indent=2))
