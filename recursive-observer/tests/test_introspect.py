from pathlib import Path

from recursive_observer.introspect import get_dependencies, get_structure


FIXTURE = Path(__file__).parent / "fixtures" / "sample_program.py"


def test_get_structure_extracts_defs():
    structure = get_structure(FIXTURE)
    assert "add" in structure.functions
    assert "square" in structure.functions
    assert "Greeter" in structure.classes


def test_get_dependencies_returns_imports():
    deps = get_dependencies(FIXTURE)
    assert "math" in deps
