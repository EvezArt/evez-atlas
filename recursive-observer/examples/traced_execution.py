from recursive_observer.tracer import trace_execution


def main():
    return sum(i * 2 for i in range(5))


trace = trace_execution(main)
print(trace.events)
print(trace.timing)
