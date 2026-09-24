"""Unit tests for .github/scripts/analyze_python_coverage_gaps.py in purpleair_data_logger."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
from pathlib import Path

_SCRIPT_PATH = (
    Path(__file__).resolve().parent.parent / "analyze_python_coverage_gaps.py"
)
spec = importlib.util.spec_from_file_location(
    "analyze_python_coverage_gaps", str(_SCRIPT_PATH)
)
gap_mod = importlib.util.module_from_spec(spec)
sys.modules["analyze_python_coverage_gaps"] = gap_mod
spec.loader.exec_module(gap_mod)

collect_callables = gap_mod.collect_callables
collect_conditional_markers = gap_mod.collect_conditional_markers
collect_test_references = gap_mod.collect_test_references
find_uncovered_callables = gap_mod.find_uncovered_callables


def test_collect_callables():
    code = """
def my_func():
    pass

class MyClass:
    def method_one(self):
        pass

    async def async_method(self):
        pass
"""
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as tf:
        tf.write(code)
        tf_path = Path(tf.name)

    try:
        callables = collect_callables(tf_path)
        assert callables == ["async_method", "method_one", "my_func"]
    finally:
        tf_path.unlink(missing_ok=True)


def test_collect_conditional_markers():
    code = """
def test():
    if False:  # pragma: no cover
        pass
"""
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as tf:
        tf.write(code)
        tf_path = Path(tf.name)

    try:
        markers = collect_conditional_markers(tf_path)
        assert len(markers) == 1
        assert "line 3" in markers[0]
        assert "pragma: no cover" in markers[0]
    finally:
        tf_path.unlink(missing_ok=True)


def test_find_uncovered_callables():
    callables = ["func_a", "func_b", "func_c", "__init__"]
    test_refs = {
        "test_one.py": {"func_a", "other_token"},
        "test_two.py": {"func_c"},
    }
    covered, uncovered = find_uncovered_callables(
        callables, test_refs, skip_private=True
    )
    assert "func_a" in covered
    assert "func_c" in covered
    assert "__init__" in covered  # dunder skipped
    assert uncovered == ["func_b"]
