import textwrap

from recursive_observer.transformer import add_trace_calls, rename_variables
from recursive_observer.tracer import trace_execution


def test_add_trace_calls_preserves_return_value():
    source = textwrap.dedent(
        """
        def add(a, b):
            return a + b
        """
    )
    transformed, _ = add_trace_calls(source)
    scope = {}
    exec(transformed, scope)
    assert scope["add"](1, 2) == 3


def test_rename_variables_changes_binding():
    source = textwrap.dedent(
        """
        def add(a, b):
            total = a + b
            return total
        """
    )
    transformed, _ = rename_variables(source, {"total": "sum_value"})
    scope = {}
    exec(transformed, scope)
    assert scope["add"](2, 3) == 5


def test_trace_execution_orders_calls():
    def inner():
        return "ok"

    def outer():
        return inner()

    trace = trace_execution(outer)
    filtered = [event for event in trace.events if event[0] in {"outer", "inner"}]
    assert [event[0] for event in filtered] == ["outer", "inner", "inner", "outer"]
