"""Structural tests for Phase 3: Persistence — TDD RED phase.

Tests verify localStorage save/restore for filter settings and button config,
and loading indicator for org fetch.
"""
import re
import pathlib

HTML_PATH = pathlib.Path(__file__).parent.parent / "reviewer_html.html"


def _html():
    return HTML_PATH.read_text(encoding="utf-8")


class TestFilterSave:
    """Task 3.1: Save filter settings to localStorage on 'Начать проверку'."""

    def test_save_filters_function_exists(self):
        assert re.search(r"function saveFilters\s*\(", _html()), \
            "saveFilters() function not found in HTML"

    def test_save_filters_writes_to_localstorage(self):
        html = _html()
        m = re.search(r"function saveFilters\s*\(.*?\n\}", html, re.DOTALL)
        assert m, "saveFilters() function body not found"
        assert "localStorage.setItem" in m.group(0), \
            "saveFilters() must call localStorage.setItem"

    def test_start_review_calls_save_filters(self):
        html = _html()
        m = re.search(r"function startReview\s*\(.*?\n\}", html, re.DOTALL)
        assert m, "startReview() function body not found"
        assert "saveFilters" in m.group(0), \
            "startReview() must call saveFilters()"

    def test_save_filters_saves_type_id(self):
        html = _html()
        m = re.search(r"function saveFilters\s*\(.*?\n\}", html, re.DOTALL)
        assert m, "saveFilters() not found"
        body = m.group(0)
        assert "type-select" in body or "typeId" in body, \
            "saveFilters() must include typeId (type-select value)"

    def test_save_filters_saves_status_id(self):
        html = _html()
        m = re.search(r"function saveFilters\s*\(.*?\n\}", html, re.DOTALL)
        assert m, "saveFilters() not found"
        assert "statusId" in m.group(0) or "status-select" in m.group(0), \
            "saveFilters() must include statusId"

    def test_save_filters_saves_org(self):
        html = _html()
        m = re.search(r"function saveFilters\s*\(.*?\n\}", html, re.DOTALL)
        assert m, "saveFilters() not found"
        assert "selectedOrgId" in m.group(0) or "orgId" in m.group(0), \
            "saveFilters() must include selectedOrgId"


class TestFilterRestore:
    """Task 3.2: Restore filter settings from localStorage on scr-setup load."""

    def test_restore_filters_function_exists(self):
        assert re.search(r"function restoreFilters\s*\(", _html()), \
            "restoreFilters() function not found in HTML"

    def test_restore_filters_reads_from_localstorage(self):
        html = _html()
        m = re.search(r"function restoreFilters\s*\(.*?\n\}", html, re.DOTALL)
        assert m, "restoreFilters() function body not found"
        assert "localStorage.getItem" in m.group(0), \
            "restoreFilters() must call localStorage.getItem"

    def test_load_setup_data_calls_restore_filters(self):
        html = _html()
        m = re.search(r"function loadSetupData\s*\(.*?\n\}", html, re.DOTALL)
        assert m, "loadSetupData() function body not found"
        assert "restoreFilters" in m.group(0), \
            "loadSetupData() must call restoreFilters()"

    def test_restore_filters_restores_type(self):
        html = _html()
        m = re.search(r"function restoreFilters\s*\(.*?\n\}", html, re.DOTALL)
        assert m, "restoreFilters() not found"
        body = m.group(0)
        assert "selectedTypeId" in body or "typeId" in body, \
            "restoreFilters() must restore type selection via AppState.selectedTypeId"

    def test_restore_filters_restores_org(self):
        html = _html()
        m = re.search(r"function restoreFilters\s*\(.*?\n\}", html, re.DOTALL)
        assert m, "restoreFilters() not found"
        body = m.group(0)
        assert "selectedOrgId" in body or "org-inp" in body, \
            "restoreFilters() must restore org selection"


class TestButtonConfigSave:
    """Task 3.3: Save decision buttons config to localStorage on any change."""

    def test_save_btn_cfg_function_exists(self):
        assert re.search(r"function saveBtnCfg\s*\(", _html()), \
            "saveBtnCfg() function not found in HTML"

    def test_save_btn_cfg_writes_to_localstorage(self):
        html = _html()
        m = re.search(r"function saveBtnCfg\s*\(.*?\n\}", html, re.DOTALL)
        assert m, "saveBtnCfg() function body not found"
        assert "localStorage.setItem" in m.group(0), \
            "saveBtnCfg() must call localStorage.setItem"

    def test_save_btn_cfg_saves_action_buttons(self):
        html = _html()
        m = re.search(r"function saveBtnCfg\s*\(.*?\n\}", html, re.DOTALL)
        assert m, "saveBtnCfg() not found"
        assert "actionButtons" in m.group(0), \
            "saveBtnCfg() must save AppState.actionButtons"

    def test_update_btn_calls_save_btn_cfg(self):
        html = _html()
        m = re.search(r"function updateBtn\s*\(.*?\n\}", html, re.DOTALL)
        assert m, "updateBtn() function body not found"
        assert "saveBtnCfg" in m.group(0), \
            "updateBtn() must call saveBtnCfg()"

    def test_add_btn_cfg_calls_save_btn_cfg(self):
        html = _html()
        m = re.search(r"function addBtnCfg\s*\(.*?\n\}", html, re.DOTALL)
        assert m, "addBtnCfg() function body not found"
        assert "saveBtnCfg" in m.group(0), \
            "addBtnCfg() must call saveBtnCfg()"

    def test_del_btn_calls_save_btn_cfg(self):
        html = _html()
        m = re.search(r"function delBtn\s*\(.*?\n\}", html, re.DOTALL)
        assert m, "delBtn() function body not found"
        assert "saveBtnCfg" in m.group(0), \
            "delBtn() must call saveBtnCfg()"


class TestButtonConfigRestore:
    """Task 3.4: Restore decision buttons from localStorage on scr-setup load."""

    def test_init_btn_cfg_checks_localstorage(self):
        html = _html()
        m = re.search(r"function initBtnCfg\s*\(.*?\n\}", html, re.DOTALL)
        assert m, "initBtnCfg() function body not found"
        assert "localStorage.getItem" in m.group(0), \
            "initBtnCfg() must check localStorage for saved button config"

    def test_init_btn_cfg_restores_saved_buttons(self):
        html = _html()
        m = re.search(r"function initBtnCfg\s*\(.*?\n\}", html, re.DOTALL)
        assert m, "initBtnCfg() not found"
        body = m.group(0)
        assert "actionButtons" in body and "localStorage" in body, \
            "initBtnCfg() must assign actionButtons from localStorage when available"


class TestOrgLoadingIndicator:
    """Task 3.5: Show loading indicator while organizations are being fetched."""

    def test_load_orgs_shows_loading_state(self):
        html = _html()
        m = re.search(r"function loadOrgs\s*\(.*?\n\}", html, re.DOTALL)
        assert m, "loadOrgs() function body not found"
        body = m.group(0)
        assert re.search(r'placeholder|disabled|Загрузка|loading', body, re.IGNORECASE), \
            "loadOrgs() must show a loading state on the org input before fetching"

    def test_load_orgs_clears_loading_on_done(self):
        html = _html()
        m = re.search(r"function loadOrgs\s*\(.*?\n\}", html, re.DOTALL)
        assert m, "loadOrgs() function body not found"
        body = m.group(0)
        assert re.search(r'placeholder\s*=\s*["\'].*организац|disabled\s*=\s*false|org-loading', body, re.IGNORECASE) or \
               re.search(r'org-inp.*placeholder\s*=|loading.*false', body, re.IGNORECASE), \
            "loadOrgs() must clear the loading indicator when fetch completes"
