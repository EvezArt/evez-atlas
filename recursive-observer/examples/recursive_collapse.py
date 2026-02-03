from recursive_observer import measure_until_stable


def target():
    return sum(range(1000))


report = measure_until_stable(target, max_iterations=5)
print(f"Converged after {len(report.snapshots)} iterations")
print(f"Final delta: {report.final_delta}")
