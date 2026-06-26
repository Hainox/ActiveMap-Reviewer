# Naming Conventions

> Confidence: HIGH — analyzed from reviewer.py + reviewer_html.html

## Python (reviewer.py)

| Construct | Convention | Example |
|-----------|-----------|---------|
| Functions | `snake_case` | `do_GET()`, `_handle_login()`, `_detect_auth()` |
| Private methods | `_snake_case` | `_proxy_get()`, `_authed()`, `_send()` |
| Classes | `PascalCase` | `Handler`, `ThreadingServer` |
| Variables | `snake_case` | `token`, `auth_header_name`, `auth_use_queryparam` |
| Constants | `UPPER_SNAKE_CASE` | `VERSION`, `BASE_URL`, `PORT`, `GITHUB_TOKEN` |

```python
VERSION = "2.0.0"
BASE_URL = "https://sao.geofsm.ru"

class Handler(BaseHTTPRequestHandler):
    def do_GET(self): ...
    def _handle_login(self, body): ...
    def _detect_auth(self): ...
```

## JavaScript (reviewer_html.html)

| Construct | Convention | Example |
|-----------|-----------|---------|
| Functions | `camelCase` | `doLogin()`, `loadSetupData()`, `renderTaskCard()` |
| Variables | `camelCase` | `tasks`, `selectedOrgId`, `taskDetailCache` |
| True constants | `UPPER_SNAKE_CASE` | `SUBMIT_GAP`, `ZOOM_STEPS` |
| State objects | `camelCase` (mutable) | `submitStatus`, `decisions`, `actionButtons` |

```javascript
const SUBMIT_GAP = 400;
const ZOOM_STEPS = [1, 1.25, 1.5, 2, 2.5, 3, 4, 5, 6, 8];

var AppState = { tasks: [], idx: 0, decisions: {}, actionButtons: [] };

function loadSetupData() { }
function renderTaskCard(task) { }
```

## HTML DOM IDs

Pattern: `kebab-case` with semantic prefix.

| Prefix | Scope | Examples |
|--------|-------|---------|
| `scr-` | Screen containers | `scr-login`, `scr-setup`, `scr-viewer` |
| `li-` | Login inputs | `li-login`, `li-pass` |
| `tc-` | Task card elements | `tc-num`, `tc-photos` |
| `btn-` | Buttons | `btn-skip`, `btn-finish` |

## CSS Classes

Pattern: `kebab-case`, BEM-like.

```css
.task-card { }
.decision-area { }
.btn.btn-primary { }
.screen.active { }
```

## v2 Rule

`UPPER_SNAKE_CASE` only for true immutable constants. Mutable state objects use `camelCase`.
