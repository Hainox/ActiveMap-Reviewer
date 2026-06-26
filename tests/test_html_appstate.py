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


class TestLightboxStateDeclared:
    """LightboxState must consolidate scattered lightbox globals — Task 2.3."""

    def test_lightboxstate_object_declared(self):
        assert re.search(r"\bvar LightboxState\s*=\s*\{", _html()), \
            "LightboxState object not declared in reviewer_html.html"

    def test_lightboxstate_has_photos(self):
        assert re.search(r"\bphotos\s*:", _html())

    def test_lightboxstate_has_cur_idx(self):
        assert re.search(r"\bcurIdx\s*:", _html())

    def test_lightboxstate_has_zoom(self):
        assert re.search(r"\bzoom\s*:", _html())

    def test_lightboxstate_has_dx(self):
        assert re.search(r"\bdx\s*:", _html())

    def test_lightboxstate_has_dy(self):
        assert re.search(r"\bdy\s*:", _html())


class TestLightboxBareGlobalsRemoved:
    """Bare lb* globals must be replaced by LightboxState properties."""

    def test_no_bare_lb_photos(self):
        for line in _html().splitlines():
            stripped = line.strip()
            assert not re.match(r"^var lbPhotos\s*=", stripped), \
                "Bare 'var lbPhotos' still present"

    def test_no_bare_lb_cur_idx(self):
        for line in _html().splitlines():
            stripped = line.strip()
            assert not re.match(r"^var lbCurIdx\s*=", stripped), \
                "Bare 'var lbCurIdx' still present"

    def test_no_bare_lb_zoom_dx_dy(self):
        for line in _html().splitlines():
            stripped = line.strip()
            assert not re.match(r"^var lbZoom\s*=", stripped), \
                "Bare 'var lbZoom' still present"


class TestCatchHandlers:
    """All .catch() blocks must log + notify — Task 2.4."""

    def test_no_empty_catch_blocks(self):
        """Catch blocks with no body (function(){}) must not exist."""
        html = _html()
        # Match .catch(function(){}) with optional whitespace/newlines inside braces
        empty_catches = re.findall(r'\.catch\s*\(\s*function\s*\(\s*\)\s*\{\s*\}\s*\)', html)
        assert not empty_catches, \
            f"Found {len(empty_catches)} empty .catch(function(){{}}) block(s)"

    def test_submit_catch_logs_error(self):
        """Submit queue catch must include error parameter and log it."""
        html = _html()
        # The submit catch (processNext) must capture the error variable
        assert re.search(r'submitStatus\[taskId\]=.err.*\bconsole\.(error|warn)', html, re.DOTALL) or \
               re.search(r'\.catch\s*\(\s*function\s*\(\s*e\s*\).*submitStatus\[taskId\]=', html, re.DOTALL), \
            "Submit catch must capture error and log it"


class TestButtonLocking:
    """Decision buttons must be locked on click and unlocked after PATCH — Task 2.5."""

    def test_decide_disables_buttons(self):
        """decide() must disable .dec-btn elements when a real decision is made."""
        html = _html()
        # decide function should set disabled on dec-btn elements
        assert re.search(
            r'function decide\b.*?\.dec-btn.*?\.disabled\s*=\s*true',
            html, re.DOTALL
        ), "decide() must disable .dec-btn buttons on click"

    def test_process_next_reenables_buttons(self):
        """processNext() must re-enable .dec-btn after PATCH resolves."""
        html = _html()
        assert re.search(
            r'function processNext\b.*?\.dec-btn.*?\.disabled\s*=\s*false',
            html, re.DOTALL
        ), "processNext() must re-enable .dec-btn buttons after PATCH response"
