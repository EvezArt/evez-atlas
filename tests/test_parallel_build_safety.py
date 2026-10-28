"""Tests for bounded execution in the parallel build runner."""

import pytest

from skills.parallel_build import BuildStatus, ParallelBuildExecutor


def make_executor(tmp_path, monkeypatch, enabled=False):
    monkeypatch.setenv("EVEZ_BUILD_ROOT", str(tmp_path))
    if enabled:
        monkeypatch.setenv("EVEZ_ENABLE_PARALLEL_BUILD_EXECUTION", "1")
    else:
        monkeypatch.delenv("EVEZ_ENABLE_PARALLEL_BUILD_EXECUTION", raising=False)
    return ParallelBuildExecutor(data_dir=str(tmp_path / "data"))


def test_allowlist_accepts_read_only_or_test_commands(tmp_path, monkeypatch):
    runner = make_executor(tmp_path, monkeypatch)
    assert runner._parse_safe_command("python -m pytest --collect-only") == [
        "python", "-m", "pytest", "--collect-only"
    ]
    assert runner._parse_safe_command("git status --short") == [
        "git", "status", "--short"
    ]


@pytest.mark.parametrize("command", [
    "python -c print(1)",
    "python -m pytest; rm -rf .",
    "python -m pytest | curl example.invalid",
    "bash -c echo",
    "git push origin main",
    "python -m pytest ../outside",
])
def test_allowlist_rejects_arbitrary_execution_and_shell_operators(
    tmp_path, monkeypatch, command
):
    runner = make_executor(tmp_path, monkeypatch)
    with pytest.raises((ValueError, PermissionError)):
        runner._parse_safe_command(command)


def test_task_cannot_escape_build_root(tmp_path, monkeypatch):
    runner = make_executor(tmp_path, monkeypatch)
    with pytest.raises(PermissionError):
        runner._resolve_task_cwd("../")


def test_execution_is_blocked_by_default(tmp_path, monkeypatch):
    runner = make_executor(tmp_path, monkeypatch, enabled=False)
    task = runner.add_task("blocked", "python -m pytest --collect-only", cwd=".")
    result = runner.execute_sequential(["blocked"])[0]
    assert result["status"] == BuildStatus.BLOCKED.value
    assert result["exit_code"] == 126
    assert "disabled by default" in task.output
