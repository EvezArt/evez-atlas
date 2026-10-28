#!/usr/bin/env python3
"""
Parallel Build Deployment System
Executes multiple build tasks concurrently using parallel path exploration.
"""

import asyncio
import json
import os
import subprocess
import shlex
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class BuildStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    BLOCKED = "blocked"


@dataclass
class BuildTask:
    """Represents a single build task."""
    id: str
    command: str
    cwd: str = "."
    timeout: int = 300
    env: Dict[str, str] = field(default_factory=dict)
    priority: int = 0
    status: BuildStatus = BuildStatus.PENDING
    output: str = ""
    exit_code: Optional[int] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "command": self.command,
            "cwd": self.cwd,
            "timeout": self.timeout,
            "status": self.status.value,
            "exit_code": self.exit_code,
            "duration": self.end_time - self.start_time if self.start_time and self.end_time else None
        }


class ParallelBuildExecutor:
    """Executes build tasks in parallel with path optimization."""
    
    def __init__(self, max_workers: int = 4, data_dir: str = "data"):
        self.max_workers = max(1, min(int(max_workers), 8))
        self.build_root = Path(os.environ.get("EVEZ_BUILD_ROOT", os.getcwd())).expanduser().resolve()
        self.execution_enabled = os.environ.get("EVEZ_ENABLE_PARALLEL_BUILD_EXECUTION", "0").strip() == "1"
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.data_dir / "build_deployment.jsonl"

        self.tasks: Dict[str, BuildTask] = {}
        self.results: List[Dict[str, Any]] = []
        self.executor = None

    SAFE_PREFIXES = (
        ("python", "-m", "py_compile"),
        ("python3", "-m", "py_compile"),
        ("python", "-m", "compileall"),
        ("python3", "-m", "compileall"),
        ("python", "-m", "pytest"),
        ("python3", "-m", "pytest"),
        ("python", "-m", "unittest"),
        ("python3", "-m", "unittest"),
        ("python", "-m", "pyflakes"),
        ("python3", "-m", "pyflakes"),
        ("python", "-m", "pip", "check"),
        ("python3", "-m", "pip", "check"),
        ("pytest",),
        ("ruff",),
        ("mypy",),
        ("flake8",),
        ("pyflakes",),
        ("npm", "test"),
        ("npm", "run", "test"),
        ("npm", "run", "lint"),
        ("npm", "run", "build"),
        ("git", "status"),
        ("git", "diff"),
        ("git", "rev-parse"),
    )
    BASE_ENV_KEYS = {
        "PATH", "HOME", "LANG", "LC_ALL", "TZ", "TMPDIR", "VIRTUAL_ENV",
        "SYSTEMROOT", "WINDIR", "CI", "NO_COLOR",
    }
    TASK_ENV_KEYS = {
        "CI", "NO_COLOR", "PYTHONUNBUFFERED", "PIP_DISABLE_PIP_VERSION_CHECK",
        "NODE_ENV", "NPM_CONFIG_LOGLEVEL", "TZ",
    }

    def _parse_safe_command(self, command: str) -> List[str]:
        if not isinstance(command, str) or not command.strip():
            raise ValueError("empty command")
        if any(op in command for op in (";", "|", "&", ">", "<", chr(96), "$", "\\n", "\\r")):
            raise ValueError("shell operators and expansions are blocked")
        try:
            argv = shlex.split(command, posix=True)
        except ValueError as exc:
            raise ValueError("invalid command syntax") from exc
        if not argv or not any(tuple(argv[:len(prefix)]) == prefix for prefix in self.SAFE_PREFIXES):
            raise PermissionError("command is not in the build allowlist")
        for arg in argv[1:]:
            path_arg = Path(arg).expanduser()
            if path_arg.is_absolute() or ".." in path_arg.parts:
                raise PermissionError("absolute paths and parent traversal are blocked in build arguments")
        return argv

    def _resolve_task_cwd(self, raw_cwd: str) -> Path:
        cwd = Path(raw_cwd).expanduser()
        if not cwd.is_absolute():
            cwd = self.build_root / cwd
        cwd = cwd.resolve()
        if cwd != self.build_root and self.build_root not in cwd.parents:
            raise PermissionError("task cwd is outside EVEZ_BUILD_ROOT")
        if not cwd.is_dir():
            raise ValueError("task cwd must be an existing directory")
        return cwd
    
    def add_task(self, task_id: str, command: str, cwd: str = ".", 
                 timeout: int = 300, priority: int = 0, env: Dict = None) -> BuildTask:
        """Add a build task to the queue."""
        task = BuildTask(
            id=task_id,
            command=command,
            cwd=cwd,
            timeout=timeout,
            priority=priority,
            env=env or {}
        )
        self.tasks[task_id] = task
        return task
    
    def _execute_task(self, task: BuildTask) -> Dict[str, Any]:
        """Execute a bounded build task; unattended arbitrary shell execution is disabled."""
        task.status = BuildStatus.RUNNING
        task.start_time = time.time()

        try:
            if not self.execution_enabled:
                raise PermissionError(
                    "build execution is disabled by default; set "
                    "EVEZ_ENABLE_PARALLEL_BUILD_EXECUTION=1 in an isolated build runner"
                )
            argv = self._parse_safe_command(task.command)
            cwd = self._resolve_task_cwd(task.cwd)
            # Keep repository/API credentials out of code run by build tasks.
            full_env = {key: value for key, value in os.environ.items()
                        if key in self.BASE_ENV_KEYS}
            for key, value in task.env.items():
                if key in self.TASK_ENV_KEYS and isinstance(value, (str, int, float, bool)):
                    full_env[key] = str(value)

            timeout = max(1, min(int(task.timeout), 300))
            result = subprocess.run(
                argv,
                shell=False,
                cwd=str(cwd),
                capture_output=True,
                text=True,
                timeout=timeout,
                env=full_env,
            )
            task.exit_code = result.returncode
            task.output = (result.stdout + result.stderr)[:20000]
            task.status = BuildStatus.SUCCESS if result.returncode == 0 else BuildStatus.FAILED

        except subprocess.TimeoutExpired:
            task.status = BuildStatus.TIMEOUT
            task.exit_code = 124
            task.output = f"Task timed out after {max(1, min(int(task.timeout), 300))}s"
        except (ValueError, PermissionError) as exc:
            task.status = BuildStatus.BLOCKED
            task.exit_code = 126
            task.output = f"Blocked by build safety policy: {exc}"
        except Exception as exc:
            task.status = BuildStatus.FAILED
            task.exit_code = 1
            task.output = f"Build task failed: {type(exc).__name__}: {exc}"

        task.end_time = time.time()
        return task.to_dict()

    def execute_parallel(self, task_ids: List[str] = None) -> List[Dict[str, Any]]:
        """Execute tasks in parallel (up to max_workers)."""
        if task_ids is None:
            task_ids = list(self.tasks.keys())
        
        # Sort by priority
        sorted_tasks = sorted(
            [self.tasks[tid] for tid in task_ids if tid in self.tasks],
            key=lambda t: t.priority,
            reverse=True
        )
        
        self.results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self._execute_task, task): task.id 
                for task in sorted_tasks
            }
            
            for future in as_completed(futures):
                task_id = futures[future]
                try:
                    result = future.result()
                    self.results.append(result)
                    self._log_event("task_completed", result)
                except Exception as e:
                    error_result = {
                        "id": task_id,
                        "status": "error",
                        "error": str(e)
                    }
                    self.results.append(error_result)
        
        return self.results
    
    def execute_sequential(self, task_ids: List[str] = None) -> List[Dict[str, Any]]:
        """Execute tasks sequentially (for dependencies)."""
        if task_ids is None:
            task_ids = list(self.tasks.keys())
        
        sorted_tasks = sorted(
            [self.tasks[tid] for tid in task_ids if tid in self.tasks],
            key=lambda t: t.priority,
            reverse=True
        )
        
        self.results = []
        
        for task in sorted_tasks:
            result = self._execute_task(task)
            self.results.append(result)
            self._log_event("task_completed", result)
        
        return self.results
    
    def get_build_summary(self) -> Dict[str, Any]:
        """Get summary of build results."""
        if not self.results:
            return {"total": 0}
        
        status_counts = {}
        for r in self.results:
            status = r.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1
        
        total_duration = sum(
            r.get("duration", 0) for r in self.results 
            if r.get("duration") is not None
        )
        
        return {
            "total_tasks": len(self.results),
            "by_status": status_counts,
            "success_rate": status_counts.get("success", 0) / len(self.results) if self.results else 0,
            "total_duration": total_duration,
            "parallel_efficiency": total_duration / (len(self.results) * max(t.get("duration", 1) for t in self.results if t.get("duration"))) if self.results else 0
        }
    
    def _log_event(self, event_type: str, data: Dict):
        """Log build events."""
        event = {
            "type": event_type,
            "timestamp": time.time(),
            "data": data
        }
        
        try:
            with self.log_file.open("a") as f:
                f.write(json.dumps(event) + "\n")
        except IOError:
            pass


async def async_build_deploy(commands: List[Dict[str, Any]], max_parallel: int = 4) -> Dict[str, Any]:
    """Async version for use in async contexts."""
    executor = ParallelBuildExecutor(max_workers=max_parallel)
    
    for cmd in commands:
        executor.add_task(
            task_id=cmd.get("id", f"task-{len(executor.tasks)}"),
            command=cmd["command"],
            cwd=cmd.get("cwd", "."),
            timeout=cmd.get("timeout", 300),
            priority=cmd.get("priority", 0),
            env=cmd.get("env", {})
        )
    
    results = executor.execute_parallel()
    summary = executor.get_build_summary()
    
    return {
        "results": results,
        "summary": summary
    }


def run_parallel_builds(build_configs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Main entry point for parallel build deployment."""
    executor = ParallelBuildExecutor(max_workers=4)
    
    for config in build_configs:
        executor.add_task(
            task_id=config.get("id", f"build-{len(executor.tasks)}"),
            command=config["command"],
            cwd=config.get("cwd", "."),
            timeout=config.get("timeout", 300),
            priority=config.get("priority", 0),
            env=config.get("env", {})
        )
    
    results = executor.execute_parallel()
    summary = executor.get_build_summary()
    
    return {
        "results": results,
        "summary": summary,
        "parallel": True,
        "max_workers": executor.max_workers
    }


if __name__ == "__main__":
    # Demo: Run multiple build commands in parallel
    builds = [
        {"id": "lint", "command": "python -m pyflakes .", "priority": 1},
        {"id": "test", "command": "python -m pytest --collect-only", "priority": 2},
        {"id": "deps-check", "command": "python -m pip check", "priority": 0},
    ]
    
    print("Running parallel build demo...")
    result = run_parallel_builds(builds)
    
    print("\nBuild Results:")
    for r in result["results"]:
        print(f"  {r['id']}: {r['status']}")
    
    print(f"\nSummary: {result['summary']}")