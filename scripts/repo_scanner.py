"""Scan all repositories in a GitHub org and report operational gaps."""

from __future__ import annotations

import argparse
from dataclasses import dataclass, asdict
import json
import os
from pathlib import Path
from typing import Any

import httpx

from agent_brain_retry import retry_with_backoff


@dataclass
class RepoReport:
    """Summary health report for a single repository."""

    name: str
    missing_readme: bool
    missing_tests: bool
    missing_ci: bool


def _gh_get(client: httpx.Client, url: str, token: str) -> Any:
    def call() -> Any:
        resp = client.get(url, headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}, timeout=20.0)
        resp.raise_for_status()
        return resp.json()

    return retry_with_backoff(call)


def scan_org(org: str, token: str) -> list[RepoReport]:
    """Fetch repos and inspect baseline quality signals."""
    reports: list[RepoReport] = []
    with httpx.Client() as client:
        repos = _gh_get(client, f"https://api.github.com/orgs/{org}/repos?per_page=100", token)
        for repo in repos:
            name = repo["name"]
            contents_url = f"https://api.github.com/repos/{org}/{name}/contents"
            try:
                entries = _gh_get(client, contents_url, token)
                names = {entry["name"] for entry in entries if isinstance(entry, dict) and "name" in entry}
            except Exception:  # noqa: BLE001
                names = set()
            reports.append(
                RepoReport(
                    name=name,
                    missing_readme="README.md" not in names,
                    missing_tests="tests" not in names,
                    missing_ci=".github" not in names,
                )
            )
    return reports


def main() -> None:
    """CLI entrypoint for repo scanning."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--org", default="EvezArt")
    parser.add_argument("--out", default="logs/repo_scan.json")
    args = parser.parse_args()

    token = os.getenv("GITHUB_TOKEN", "")
    if not token:
        raise RuntimeError("GITHUB_TOKEN must be set")

    report = [asdict(r) for r in scan_org(args.org, token)]
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
