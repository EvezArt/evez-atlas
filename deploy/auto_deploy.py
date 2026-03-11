"""Autonomous deployment watcher with rollback safety checks."""

from __future__ import annotations

import argparse
import os
import subprocess
import time
from typing import Final

import httpx

from agent_brain_retry import retry_with_backoff

HEALTH_TIMEOUT_SECONDS: Final[int] = 120


def trigger_deploy(provider: str, webhook_url: str) -> None:
    """Trigger deployment webhook for a provider."""
    with httpx.Client() as client:
        retry_with_backoff(lambda: client.post(webhook_url, timeout=20.0).raise_for_status())


def rollback() -> None:
    """Rollback by reverting latest commit on current branch."""
    subprocess.run(["git", "revert", "--no-edit", "HEAD"], check=True)


def wait_for_health(health_url: str) -> bool:
    """Wait for service to become healthy within timeout."""
    deadline = time.time() + HEALTH_TIMEOUT_SECONDS
    with httpx.Client() as client:
        while time.time() < deadline:
            try:
                resp = client.get(health_url, timeout=5.0)
                if resp.status_code == 200:
                    return True
            except Exception:  # noqa: BLE001
                pass
            time.sleep(5)
    return False


def main() -> None:
    """Entry point for autonomous deployment and rollback guardrail."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", required=True)
    parser.add_argument("--health-url", required=True)
    args = parser.parse_args()

    webhook_env = f"{args.provider.upper()}_DEPLOY_WEBHOOK"
    webhook = os.getenv(webhook_env)
    if not webhook:
        raise RuntimeError(f"Missing {webhook_env}")

    trigger_deploy(args.provider, webhook)
    if not wait_for_health(args.health_url):
        rollback()


if __name__ == "__main__":
    main()
