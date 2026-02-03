import sys

from recursive_observer.introspect import get_structure
from recursive_observer.observer_effect import is_being_observed, modify_behavior_on_observation


def test_observer_effect_detects_trace():
    def tracer(frame, event, arg):
        return tracer

    sys.settrace(tracer)
    try:
        assert is_being_observed()
    finally:
        sys.settrace(None)


def test_observer_effect_changes_metrics(tmp_path):
    sample = tmp_path / "sample.py"
    sample.write_text("def demo():\n    return 1\n", encoding="utf-8")
    get_structure(sample)
    metrics = {"loc": 2, "complexity": 1.0, "maintainability_index": 100.0}
    modified = modify_behavior_on_observation(metrics)
    assert modified["observer_note"] == "OBSERVATION DETECTED"
