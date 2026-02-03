from __future__ import annotations

import ast
from pathlib import Path
from typing import Any


def _backup_source(source_path: Path, source_code: str) -> None:
    backup_path = source_path.with_suffix(source_path.suffix + ".original")
    backup_path.write_text(source_code, encoding="utf-8")


def _render(tree: ast.AST) -> str:
    ast.fix_missing_locations(tree)
    return ast.unparse(tree)


def add_trace_calls(source_code: str, source_path: Path | None = None) -> tuple[str, str]:
    tree = ast.parse(source_code)

    class TraceTransformer(ast.NodeTransformer):
        def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
            trace_call = ast.Expr(
                value=ast.Call(
                    func=ast.Name(id="print", ctx=ast.Load()),
                    args=[
                        ast.JoinedStr(
                            values=[
                                ast.Constant(value="Entering "),
                                ast.FormattedValue(
                                    value=ast.Constant(value=node.name),
                                    conversion=-1,
                                ),
                            ]
                        )
                    ],
                    keywords=[],
                )
            )
            node.body.insert(0, trace_call)
            return node

    transformed = TraceTransformer().visit(tree)
    if source_path:
        _backup_source(source_path, source_code)
    return _render(transformed), ast.dump(transformed)


def rename_variables(
    source_code: str, mapping: dict[str, str], source_path: Path | None = None
) -> tuple[str, str]:
    tree = ast.parse(source_code)

    class RenameTransformer(ast.NodeTransformer):
        def visit_Name(self, node: ast.Name) -> Any:
            if node.id in mapping:
                return ast.copy_location(ast.Name(id=mapping[node.id], ctx=node.ctx), node)
            return node

    transformed = RenameTransformer().visit(tree)
    if source_path:
        _backup_source(source_path, source_code)
    return _render(transformed), ast.dump(transformed)


def inject_observer_hooks(source_code: str, source_path: Path | None = None) -> tuple[str, str]:
    tree = ast.parse(source_code)

    class HookTransformer(ast.NodeTransformer):
        def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
            hook = ast.If(
                test=ast.Call(
                    func=ast.Name(id="is_being_observed", ctx=ast.Load()),
                    args=[],
                    keywords=[],
                ),
                body=[
                    ast.Expr(
                        value=ast.Call(
                            func=ast.Name(id="modify_behavior_on_observation", ctx=ast.Load()),
                            args=[ast.Dict(keys=[], values=[])],
                            keywords=[],
                        )
                    )
                ],
                orelse=[],
            )
            node.body.insert(0, hook)
            return node

    transformer = HookTransformer()
    transformed = transformer.visit(tree)

    insert_import = ast.ImportFrom(
        module="recursive_observer.observer_effect",
        names=[
            ast.alias(name="is_being_observed", asname=None),
            ast.alias(name="modify_behavior_on_observation", asname=None),
        ],
        level=0,
    )
    if isinstance(transformed, ast.Module):
        transformed.body.insert(0, insert_import)

    if source_path:
        _backup_source(source_path, source_code)
    return _render(transformed), ast.dump(transformed)
