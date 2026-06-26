"""Structural tests for AppState refactoring in reviewer_html.html — TDD RED phase.

Tests FAIL until reviewer_html.html defines AppState and moves global vars.
"""
import re
import pathlib

HTML_PATH = pathlib.Path(__file__).parent.parent / "reviewer_html.html"


def _html():
    return HTML_PATH.read_text(encoding="utf-8")


class TestAppStateDeclared:
    def test_appstate_object_declared(self):
        """AppState must be declared as a var object literal."""
        assert re.search(r"\bvar AppState\s*=\s*\{", _html()), \
            "AppState object not declared in reviewer_html.html"

    def test_appstate_has_tasks(self):
        assert re.search(r"\btasks\s*:", _html())

    def test_appstate_has_decisions(self):
        assert re.search(r"\bdecisions\s*:", _html())

    def test_appstate_has_submit_queue(self):
        assert re.search(r"\bsubmitQueue\s*:", _html())

    def test_appstate_has_action_buttons(self):
        assert re.search(r"\bactionButtons\s*:", _html())


class TestBareGlobalsRemoved:
    """Top-level bare var declarations must be replaced by AppState properties."""

    def test_no_bare_var_tasks(self):
        for line in _html().splitlines():
            stripped = line.strip()
            assert not re.match(r"^var tasks\s*=\s*\[\s*\]", stripped), \
                f"Bare 'var tasks=[]' still present"

    def test_no_bare_var_decisions(self):
        for line in _html().splitlines():
            stripped = line.strip()
            assert not re.match(r"^var decisions\s*=\s*\{", stripped), \
                f"Bare 'var decisions={{}}' still present"

    def test_no_bare_var_submit_queue(self):
        for line in _html().splitlines():
            stripped = line.strip()
            assert not re.match(r"^var submitQueue\s*=\s*\[\s*\]", stripped), \
                f"Bare 'var submitQueue=[]' still present"
