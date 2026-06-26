# Plan: v2_rebuild_20260626

> Follow workflow.md: mark [~] when starting, [x] when done. TDD: write tests first.

---

## Phase 1: Foundation [checkpoint: a0dee51]

> Goal: Python server — structured logging, proper error handling, auth timeout UX, PATCH error passthrough.

- [x] Task 1.1: Write pytest tests for auth detection logic (6 header formats) — RED phase [5687f90]
- [x] Task 1.2: Replace `print()` with `logging` module; write to `reviewer.log` via `FileHandler` — GREEN phase [5fc01af]
- [x] Task 1.3: Replace all bare `except:` with `except Exception as e:` + `logging.error()` [a0dee51]
- [x] Task 1.4: Add auth timeout UX — after 12s wait, send error response to browser [a0dee51]
- [x] Task 1.5: Fix `POST /patch/{taskId}` — pass through ActiveMap HTTP error code on failure [a0dee51]
- [x] Task 1.6: Gate `/debug` and `/debug-task` behind `os.environ.get('DEBUG') == '1'` [a0dee51]
- [x] Task 1.7: Run coverage — target >80% for modified Python code
- [x] Task: Conductor - User Manual Verification 'Foundation' (Protocol in workflow.md)

---

## Phase 2: Frontend Refactor

> Goal: Restructure reviewer_html.html — AppState object, fix silent errors, button locking.

- [x] Task 2.1: Add section comments to HTML (`<!-- STATE -->`, `<!-- API -->`, `<!-- UI -->`, `<!-- LIGHTBOX -->`, `<!-- SUBMIT -->`) [121cfa8]
- [x] Task 2.2: Consolidate ~20 global variables into `AppState` object; update all references [66ac7ca]
- [x] Task 2.3: Extract `LightboxState` object (photos, curIdx, zoom, dx, dy)
- [ ] Task 2.4: Replace all `.catch(function(){})` with handlers that log + show user error
- [ ] Task 2.5: Add button locking — disable decision buttons on click, re-enable on PATCH response
- [ ] Task 2.6: Fix `POST /patch` — show error card with "Повторить" if PATCH fails
- [ ] Task 2.7: Manual test — navigate 20 tasks, apply decisions, verify no console errors
- [ ] Task: Conductor - User Manual Verification 'Frontend Refactor' (Protocol in workflow.md)

---

## Phase 3: Persistence

> Goal: localStorage for settings — filters and decision buttons persist between sessions.

- [ ] Task 3.1: Save filter settings to localStorage on "Начать проверку"
- [ ] Task 3.2: Restore filter settings from localStorage on scr-setup load
- [ ] Task 3.3: Save decision buttons config to localStorage on any change
- [ ] Task 3.4: Restore decision buttons from localStorage on scr-setup load
- [ ] Task 3.5: Add loading indicator while organizations are being fetched
- [ ] Task 3.6: Manual test — configure filters + buttons, restart app, verify settings restored
- [ ] Task: Conductor - User Manual Verification 'Persistence' (Protocol in workflow.md)

---

## Phase 4: Feature Completion

> Goal: Auto-pagination for tasks >500, CSV export, full session history.

- [ ] Task 4.1: Replace "500 tasks limit" warning with automatic pagination
- [ ] Task 4.2: Implement CSV export — taskId, taskNumber, decision label, status, stage, timestamp
- [ ] Task 4.3: Ensure session history includes decisions from all pages
- [ ] Task 4.4: Manual test — load >500 tasks, verify pagination works transparently
- [ ] Task: Conductor - User Manual Verification 'Feature Completion' (Protocol in workflow.md)

---

## Phase 5: QA & Release

> Goal: Full manual test, .exe build, GitHub Release v2.0.0.

- [ ] Task 5.1: Update `VERSION = "2.0.0"` in reviewer.py
- [ ] Task 5.2: Run full manual test checklist from `conductor/docs/testing-patterns.md`
- [ ] Task 5.3: Build .exe — `pyinstaller --onefile --noconsole --add-data "reviewer_html.html;." reviewer.py`
- [ ] Task 5.4: Test .exe on clean Windows machine without Python installed
- [ ] Task 5.5: Update CHANGELOG.md with v2.0.0 release notes
- [ ] Task 5.6: Create git tag `v2.0.0`, push → GitHub Actions builds Release
- [ ] Task 5.7: Verify GitHub Release contains `ActiveMapReviewer.exe` artifact
- [ ] Task: Conductor - User Manual Verification 'QA & Release' (Protocol in workflow.md)
