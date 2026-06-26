# Tech Stack

> Confirmed by user. Auto-detected stack (JS/React) overridden: project is Python + vanilla HTML.

## Languages

- **Python 3.8+** — backend, HTTP server, proxy, auth logic (stdlib only, no pip)
- **JavaScript ES6** — vanilla JS frontend (single HTML file, no build step)
- **HTML5 / CSS3** — UI markup and styles (inline in reviewer_html.html)

## Frameworks

- **None** — Python stdlib only; no Django/Flask/FastAPI
- **No JS framework** — vanilla JS, no React/Vue/Angular

## Database

- **None** — stateless application
- `bug_reports.jsonl` — local append-only log (JSON Lines format)
- `localStorage` (v2) — browser storage for user settings persistence

## Infrastructure

- **Hosting:** localhost:8765 (desktop app, no cloud)
- **Distribution:** GitHub Releases (single .exe file)
- **CI/CD:** GitHub Actions (`windows-latest`) — build .exe + upload to release on `v*` tag

## Key Libraries

| Library | Source | Purpose |
|---------|--------|---------|
| `http.server` | Python stdlib | ThreadingHTTPServer — serve HTML + handle API |
| `urllib.request` | Python stdlib | HTTP client for proxying to ActiveMap API |
| `threading` | Python stdlib | Background auth detection, server threading |
| `json` | Python stdlib | Request/response serialization |
| `webbrowser` | Python stdlib | Open browser on app start |
| `logging` | Python stdlib | v2: structured logging to file |
| PyInstaller 6.x | pip (build only) | Package Python + HTML into single .exe |

## Architecture Decisions

### Decision 1: Python stdlib only (no pip runtime deps)

**Date:** 2026-06-15

**Decision:** Use only Python standard library for runtime. PyInstaller allowed only as build tool.

**Rationale:** Zero-install requirement — the .exe must work without any prerequisites. External dependencies complicate PyInstaller builds and can cause import errors on target machines.

### Decision 2: Single-file HTML frontend

**Date:** 2026-06-15

**Decision:** All frontend code in one `reviewer_html.html` file, embedded in .exe.

**Rationale:** Simplest distribution — no npm build step, no asset pipeline. Acceptable for a small internal tool.

**v2 note:** File grew to 1782 lines — split into logical `<script>` sections while staying in single file.

### Decision 3: Python as CORS proxy

**Date:** 2026-06-15

**Decision:** Python server proxies all ActiveMap API calls from browser frontend.

**Rationale:** ActiveMap API (sao.geofsm.ru) does not allow CORS from browser origins. Python proxy strips/adds auth headers transparently.

### Decision 4: Multi-format auth detection

**Date:** 2026-06-15

**Decision:** After login, test 6 auth header formats to find which one ActiveMap accepts.

**Rationale:** Different versions of ActiveMap API use different auth schemes. Auto-detection removes need for manual configuration.

## Development Environment

### Prerequisites

- Python 3.11+
- Git

### Setup

```bash
# Run in development
python reviewer.py
# Browser opens at http://localhost:8765

# Build .exe (requires PyInstaller)
pip install pyinstaller
pyinstaller --onefile --noconsole --add-data "reviewer_html.html;." reviewer.py
```

### CI/CD (GitHub Actions)

Build triggers on push to `master` or tag `v*`. Artifact: `ActiveMapReviewer.exe`.
