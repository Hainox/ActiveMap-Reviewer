# AGENTS.md

## Unwritten
- Shipping: the product is `reviewer.py` (stdlib HTTP server and proxy on port 8765) plus `reviewer_html.html`, bundled by PyInstaller into `ActiveMapReviewer.exe`. Pushing a `v*.*.*` tag builds the exe and publishes a GitHub Release. A release bumps `VERSION` in `reviewer.py` and adds a dated `CHANGELOG.md` entry; notable ones also get a line in README «История версий».
- Checks: `python -m pytest tests/ -v` from the root; CI also runs `py_compile reviewer.py` on Ubuntu and Windows. Local exe build: `build.bat`.
- Gotchas: CI fails if top-level `VERSION`, `PORT` (a literal number), or `BASE_URL` disappear from `reviewer.py`, or if `reviewer_html.html` loses ids `scr-login`, `scr-setup`, `scr-viewer`, `scr-summary`, `lb`, `bug-modal`, `app-version`, `tc-title`, `tc-photos`, `decision-btns` or functions `doLogin`, `renderTask`, `openLb`, `showBugReport`, `lbApplyTransform`. Tests also regex-match `var AppState = {` in the HTML. The ActiveMap API paginates with `&page=` and silently ignores `offset`; stop on the response `count` (v2.0.4 fix). Opening the HTML via `file://` breaks everything; run `python reviewer.py`. A second running copy exits instead of sharing port 8765.
- Conventions: UI text, README, and CHANGELOG are in Russian. Style guides live in `conductor/code_styleguides/`, architecture notes in `conductor/docs/`.
- Why: runtime is Python stdlib only and the frontend is one vanilla-JS HTML file, so the exe needs no install; do not add pip runtime dependencies or a JS build step to it. The Python server exists because ActiveMap does not allow browser CORS. The Next.js app in `app/` is a design-system stub and is not shipped in the exe.
- Off-limits: `bug_reports.jsonl` holds internal data and stays untracked. The committed binaries and docs (`VersionManager.exe`, `admin_manual_activemap_gis.pdf`, `ActiveMap Messages.lnk`) and the `MAP` gitlink (no `.gitmodules`) are human-owned; leave them alone.

## Pointers
- **Writing** or reviewing code: apply `CODING_STANDARDS.md`; project config and linters win where they disagree.
- **Security**-sensitive change (auth, permissions, untrusted input, secrets): read `docs/agents/security.md` first.
- **Committing** or opening a PR: follow `docs/agents/git.md`.
- **Risky** change (spans modules, migrates data, alters a public API): propose a phased plan and get approval before editing.
- **Done** means you ran the project's own check commands and they are green, or you named the ones you could not run.
