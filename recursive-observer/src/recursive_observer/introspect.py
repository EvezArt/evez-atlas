from __future__ import annotations

import ast
import inspect
from pathlib import Path
from types import ModuleType
from typing import Any

from recursive_observer.metrics import get_metrics as calculate_metrics
from recursive_observer.models import ProgramStructure
from recursive_observer.observer_effect import record_introspection


def _load_source(module_or_file: ModuleType | str | Path) -> str:
    if isinstance(module_or_file, ModuleType):
        if not module_or_file.__file__:
            raise ValueError("Module has no file path")
        path = Path(module_or_file.__file__)
        return path.read_text(encoding="utf-8")
    path = Path(module_or_file)
    return path.read_text(encoding="utf-8")


def get_structure(module_or_file: ModuleType | str | Path) -> ProgramStructure:
    record_introspection("structure")
    source = _load_source(module_or_file)
    tree = ast.parse(source)
    functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
    classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
    imports = [
        node.names[0].name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import) and node.names
    ]
    imports += [
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module
    ]
    return ProgramStructure(
        ast_dump=ast.dump(tree),
        functions=functions,
        classes=classes,
        imports=imports,
    )


def get_metrics(code: str):
    record_introspection("metrics")
    return calculate_metrics(code)


def get_call_graph(module_or_file: ModuleType | str | Path) -> dict[str, set[str]]:
    record_introspection("call_graph")
    source = _load_source(module_or_file)
    tree = ast.parse(source)
    graph: dict[str, set[str]] = {}

    class CallVisitor(ast.NodeVisitor):
        def __init__(self) -> None:
            self.current: str | None = None

        def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
            previous = self.current
            self.current = node.name
            graph.setdefault(node.name, set())
            self.generic_visit(node)
            self.current = previous

        def visit_Call(self, node: ast.Call) -> Any:
            if self.current is None:
                return
            if isinstance(node.func, ast.Name):
                graph[self.current].add(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                graph[self.current].add(node.func.attr)
            self.generic_visit(node)

    CallVisitor().visit(tree)
    return graph


def get_dependencies(module_or_file: ModuleType | str | Path) -> list[str]:
    structure = get_structure(module_or_file)
    return sorted(set(structure.imports))


def get_runtime_state() -> dict[str, Any]:
    record_introspection("runtime_state")
    stack = inspect.stack()
    return {
        "call_depth": len(stack),
        "frames": [
            {
                "function": frame.function,
                "filename": frame.filename,
                "line": frame.lineno,
                "locals": dict(frame.frame.f_locals),
            }
            for frame in stack
        ],
    }
