"""Regression tests for default-deny limit adjustments."""

from skills.limit_bypass import LimitBypass


def test_limit_bypass_disabled_by_default(tmp_path, monkeypatch):
    monkeypatch.delenv("LIMIT_BYPASS_ENABLED", raising=False)
    limits = LimitBypass(data_dir=str(tmp_path))
    result = limits.bypass_limit("max_agents", 150)
    assert result["status"] == "denied"
    assert limits.limits["max_agents"] == limits.DEFAULT_LIMITS["max_agents"]


def test_bounded_opt_in_increase_and_hard_cap(tmp_path, monkeypatch):
    monkeypatch.setenv("LIMIT_BYPASS_ENABLED", "1")
    monkeypatch.setenv("LIMIT_BYPASS_APPROVAL_ID", "approval-123456")
    monkeypatch.setenv("LIMIT_BYPASS_APPROVED_BY", "maintainer")
    limits = LimitBypass(data_dir=str(tmp_path))
    allowed = limits.bypass_limit("max_agents", 150, reason="reviewed capacity test", approval_id="approval-123456", approved_by="maintainer")
    assert allowed["status"] == "bounded_limit_increase_recorded"
    denied = limits.bypass_limit("max_agents", 500, reason="too large", approval_id="approval-123457", approved_by="maintainer")
    assert denied["status"] == "denied"
    assert limits.limits["max_agents"] == 150


def test_unlimited_mode_is_always_denied(tmp_path, monkeypatch):
    monkeypatch.setenv("LIMIT_BYPASS_ENABLED", "1")
    limits = LimitBypass(data_dir=str(tmp_path))
    result = limits.enable_unlimited_mode()
    assert result["approved"] is False
    assert result["mode"] == "denied"
    assert limits.limits == limits.DEFAULT_LIMITS
