"""Regression tests for the canonical OpenClaw capability policy."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "os-evez"))

from openclaw.policy import DEFAULT_POLICY, assert_fs_read, assert_fs_write, assert_shell  # noqa: E402


def test_shell_policy_rejects_chaining_and_code_runners():
    policy = DEFAULT_POLICY
    assert assert_shell(policy, "cat sample.txt")
    assert assert_shell(policy, "ls -la")
    assert not assert_shell(policy, "cat sample.txt; id")
    assert not assert_shell(policy, "python -c print(1)")
    assert not assert_shell(policy, "ffmpeg -i input.mp4 output.mp4")
    assert not assert_shell(policy, "cat ../outside.txt")


def test_filesystem_policy_resolves_paths(tmp_path):
    allowed = tmp_path / "allowed"
    denied = tmp_path / "allowed-neighbor"
    allowed.mkdir()
    denied.mkdir()
    policy = {
        "capabilities": {
            "FS_READ": {"allow_paths": [str(allowed)]},
            "FS_WRITE": {"allow_paths": [str(allowed)]},
        }
    }
    assert assert_fs_read(policy, str(allowed / "file.txt"))
    assert assert_fs_write(policy, str(allowed / "file.txt"))
    assert not assert_fs_read(policy, str(denied / "file.txt"))
    assert not assert_fs_write(policy, str(denied / "file.txt"))
