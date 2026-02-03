from recursive_observer.recursive_engine import measure_until_stable
from recursive_observer.recursive_engine import recursive_self_measure


def test_measure_until_stable_converges():
    def target():
        return sum(range(10))

    report = measure_until_stable(target, max_iterations=3, tolerance=1000.0)
    assert report.converged
    assert report.snapshots


def test_recursive_self_measure_layers():
    def target():
        return sum(range(5))

    snapshots = recursive_self_measure(target, depth=3)
    assert len(snapshots) == 3
