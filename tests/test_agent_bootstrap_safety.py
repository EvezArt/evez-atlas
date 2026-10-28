"""Regression tests for least-privilege agent bootstrapping."""

import json

from skills.agent_bootstrap import AgentBootstrap


def test_bootstrap_defaults_to_supervised_and_cannot_self_authorize(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    bootstrap = AgentBootstrap(data_dir=str(tmp_path / "data"))
    agent = bootstrap.bootstrap_agent("test-agent")
    assert agent["autonomy_level"] == "supervised"
    assert agent["status"] == "pending_approval"
    assert agent["config"]["can_self_authorize"] is False
    assert agent["config"]["requires_approval"] is True
    assert agent["config"]["max_delegation_depth"] == 1
    assert agent["capabilities"] == ["read_only"]


def test_full_request_is_downgraded(tmp_path):
    bootstrap = AgentBootstrap(data_dir=str(tmp_path / "data"))
    agent = bootstrap.bootstrap_agent("test-agent", autonomy_level="full",
                                      capabilities=["execute", "delegate", "unknown"])
    assert agent["autonomy_level"] == "supervised"
    assert agent["config"]["can_self_authorize"] is False
    assert agent["config"]["can_delegate"] is False
    assert agent["capabilities"] == ["execute"]


def test_batch_size_is_bounded(tmp_path):
    bootstrap = AgentBootstrap(data_dir=str(tmp_path / "data"))
    try:
        bootstrap.bootstrap_batch(11, "agent")
    except ValueError:
        pass
    else:
        raise AssertionError("batch sizes above 10 must be rejected")
