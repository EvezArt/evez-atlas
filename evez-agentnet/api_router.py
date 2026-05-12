#!/usr/bin/env python3
"""
EVEZ AgentNet API Router
Autonomous API selection from 36 free providers with health tracking.
"""
import json, random, time
from pathlib import Path
from datetime import datetime, timezone

BASE = Path("/mnt/agents/output/evez-agentnet")
ARSENAL = BASE / "api_arsenal.json"
HEALTH_LOG = BASE / "logs" / "api_health.jsonl"
HEALTH_LOG.parent.mkdir(parents=True, exist_ok=True)

class APIRouter:
    def __init__(self):
        self.arsenal = json.loads(ARSENAL.read_text()) if ARSENAL.exists() else {"categories": {}}
        self.health = {}

    def select(self, task_type="ai_llm", prefer_no_cc=True, min_priority=1):
        candidates = self.arsenal.get("categories", {}).get(task_type, [])
        filtered = [a for a in candidates if a.get("priority", 3) <= min_priority]
        if prefer_no_cc:
            filtered = [a for a in filtered if not a.get("cc_required", False)]
        if not filtered:
            filtered = [a for a in candidates if a.get("priority", 3) <= min_priority + 1]
        if not filtered:
            return None
        filtered.sort(key=lambda x: x.get("priority", 3))
        best = filtered[0].get("priority", 3)
        top = [a for a in filtered if a.get("priority", 3) == best]
        return random.choice(top)

    def route(self, task_type="ai_llm", prompt=None):
        api = self.select(task_type)
        if not api:
            return {"error": "No available API for task type: " + task_type}
        endpoints = {
            "Google AI Studio": "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent",
            "Groq": "https://api.groq.com/openai/v1/chat/completions",
            "Cerebras": "https://api.cerebras.ai/v1/chat/completions",
            "DeepSeek": "https://api.deepseek.com/v1/chat/completions",
            "OpenRouter": "https://openrouter.ai/api/v1/chat/completions",
            "CoinGecko": "https://api.coingecko.com/api/v3/simple/price",
            "DexScreener": "https://api.dexscreener.com/latest/dex/search",
            "ipwhois.io": "https://ipwho.is/",
            "Open-Meteo": "https://api.open-meteo.com/v1/forecast",
        }
        return {
            "provider": api["name"],
            "endpoint": endpoints.get(api["name"], api["url"]),
            "auth_type": "none" if "No key" in api["free"] or "no key" in api["free"] else "bearer_token",
            "key_url": api["url"],
            "rate_limit": api["free"],
            "cc_required": api.get("cc_required", False),
            "priority": api.get("priority", 3),
            "task_type": task_type,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    def list_available(self):
        return {cat: [a["name"] for a in apis if not a.get("cc_required", False)] 
                for cat, apis in self.arsenal.get("categories", {}).items()}

if __name__ == "__main__":
    router = APIRouter()
    print(json.dumps(router.route("ai_llm", "Explain quantum computing"), indent=2))
    print(json.dumps(router.route("crypto"), indent=2))
