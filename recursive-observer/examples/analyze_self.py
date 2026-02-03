from recursive_observer import get_metrics, get_structure

# Analyze this very script
import __main__

structure = get_structure(__main__.__file__)
metrics = get_metrics(open(__main__.__file__).read())
print(f"This script has {metrics.loc} lines and complexity {metrics.complexity}")
print(f"Functions: {structure.functions}")
