"""Structural tests for Phase 4: Feature Completion — TDD RED phase.

Tests verify auto-pagination for tasks >500 and CSV export.
"""
import re
import pathlib

HTML_PATH = pathlib.Path(__file__).parent.parent / "reviewer_html.html"


def _html():
    return HTML_PATH.read_text(encoding="utf-8")


class TestAutoPagination:
    """Task 4.1: Replace 500-task warning with automatic pagination."""

    def test_fetch_tasks_page_function_exists(self):
        assert re.search(r"function fetchTasksPage\s*\(", _html()), \
            "fetchTasksPage() helper not found in HTML"

    def test_no_limit_warning_text(self):
        html = _html()
        assert "лимит 500" not in html and "Достигнут лимит" not in html, \
            "500-task limit warning text must be removed"

    def test_pagination_uses_offset(self):
        html = _html()
        m = re.search(r"function fetchTasksPage\s*\(.*?\n\}", html, re.DOTALL)
        assert m, "fetchTasksPage() not found"
        assert "offset" in m.group(0), \
            "fetchTasksPage() must use offset for pagination"

    def test_start_review_calls_fetch_tasks_page(self):
        html = _html()
        m = re.search(r"function startReview\s*\(.*?\n\}", html, re.DOTALL)
        assert m, "startReview() not found"
        assert "fetchTasksPage" in m.group(0), \
            "startReview() must use fetchTasksPage() for loading"

    def test_pagination_appends_tasks(self):
        html = _html()
        m = re.search(r"function fetchTasksPage\s*\(.*?\n\}", html, re.DOTALL)
        assert m, "fetchTasksPage() not found"
        body = m.group(0)
        assert "concat" in body or "push" in body, \
            "fetchTasksPage() must accumulate pages via concat or push"


class TestCsvExport:
    """Task 4.2: CSV export of session results."""

    def test_export_csv_function_exists(self):
        assert re.search(r"function exportCSV\s*\(", _html()), \
            "exportCSV() function not found in HTML"

    def test_export_csv_creates_download(self):
        html = _html()
        m = re.search(r"function exportCSV\s*\(.*?\n\}", html, re.DOTALL)
        assert m, "exportCSV() function not found"
        body = m.group(0)
        assert "download" in body or "Blob" in body or "createObjectURL" in body, \
            "exportCSV() must trigger a file download"

    def test_export_csv_includes_task_number(self):
        html = _html()
        m = re.search(r"function exportCSV\s*\(.*?\n\}", html, re.DOTALL)
        assert m, "exportCSV() not found"
        body = m.group(0)
        assert ".no" in body or "externalId" in body or "taskNo" in body or "number" in body, \
            "exportCSV() must include task number field"

    def test_export_csv_includes_decision_label(self):
        html = _html()
        m = re.search(r"function exportCSV\s*\(.*?\n\}", html, re.DOTALL)
        assert m, "exportCSV() not found"
        body = m.group(0)
        assert "actionButtons" in body or "label" in body, \
            "exportCSV() must include decision label from actionButtons"

    def test_export_button_exists_in_summary(self):
        html = _html()
        assert re.search(r"exportCSV\(\)", html), \
            "exportCSV() must be called from a button in the summary screen"
