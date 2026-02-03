from __future__ import annotations

import json
import runpy
from pathlib import Path
from typing import Any

import typer

from recursive_observer.introspect import get_metrics, get_structure
from recursive_observer.observer_effect import modify_behavior_on_observation
from recursive_observer.recursive_engine import measure_until_stable
from recursive_observer.tracer import trace_execution
from recursive_observer.transformer import add_trace_calls, inject_observer_hooks, rename_variables

app = typer.Typer(add_completion=False)


def _load_function(module_path: Path, function_name: str) -> Any:
    module_globals = runpy.run_path(str(module_path))
    return module_globals[function_name]


@app.command()
def analyze(target: Path, output: Path) -> None:
    code = target.read_text(encoding="utf-8")
    metrics = get_metrics(code)
    structure = get_structure(target)
    payload = {
        "metrics": metrics.__dict__,
        "structure": structure.__dict__,
    }
    output.write_text(json.dumps(payload, indent=2), encoding="utf-8")


@app.command("self-analyze")
def self_analyze(output: Path) -> None:
    target = Path(__file__).resolve()
    code = target.read_text(encoding="utf-8")
    metrics = get_metrics(code)
    output.write_text(json.dumps(metrics.__dict__, indent=2), encoding="utf-8")


@app.command()
def collapse(target: Path, max_iter: int = 10, tolerance: float = 0.01) -> None:
    report = measure_until_stable(target, max_iterations=max_iter, tolerance=tolerance)
    payload = {
        "converged": report.converged,
        "final_delta": report.final_delta,
        "snapshots": [
            {
                "iteration": snap.iteration,
                "metrics": snap.metrics.__dict__,
                "observer_state": snap.observer_state,
                "timestamp": snap.timestamp.isoformat(),
            }
            for snap in report.snapshots
        ],
    }
    typer.echo(json.dumps(payload, indent=2))


@app.command()
def trace(target: Path, function: str, args: str = "[]") -> None:
    import ast

    func = _load_function(target, function)
    call_args = ast.literal_eval(args)
    trace_data = trace_execution(func, *call_args)
    typer.echo(json.dumps(trace_data.__dict__, indent=2, default=str))


@app.command()
def transform(
    input: Path,
    output: Path,
    add_traces: bool = False,
    add_hooks: bool = False,
    rename: str | None = None,
) -> None:
    source = input.read_text(encoding="utf-8")
    transformed = source
    diff = ""
    if add_traces:
        transformed, diff = add_trace_calls(transformed, source_path=input)
    if add_hooks:
        transformed, diff = inject_observer_hooks(transformed, source_path=input)
    if rename:
        mapping = json.loads(rename)
        transformed, diff = rename_variables(transformed, mapping, source_path=input)
    output.write_text(transformed, encoding="utf-8")
    typer.echo(diff)


@app.command()
def observe(target: Path, show_behavior_change: bool = False) -> None:
    code = target.read_text(encoding="utf-8")
    metrics = get_metrics(code)
    payload = metrics.__dict__
    if show_behavior_change:
        payload = modify_behavior_on_observation(payload)
    typer.echo(json.dumps(payload, indent=2))


if __name__ == "__main__":
    app()
