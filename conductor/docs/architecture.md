# Architecture

> Confidence: HIGH — analyzed from reviewer.py + reviewer_html.html

## Overview

Monolithic single-file desktop app. One `.exe` = Python HTTP server + bundled HTML frontend.

```
[Browser at localhost:8765] → fetch /proxy/* → [Python ThreadingHTTPServer] → [ActiveMap REST API]
```

## Python Backend Routes

| Method | Path | Action |
|--------|------|--------|
| GET | `/` | Serve `reviewer_html.html` |
| GET | `/version` | `{"version": "2.0.0"}` |
| POST | `/login` | Auth + start `_detect_auth()` |
| GET | `/proxy/*` | Proxy → ActiveMap REST |
| POST | `/patch/{taskId}` | PATCH mutation → ActiveMap |
| POST | `/report-bug` | Save locally + GitHub Issues |

## Auth Detection

After login, tests 6 formats to find which ActiveMap accepts:
`Authorization: {raw}` → `Token {t}` → `Bearer {t}` → `Cookie: token=` → `X-Auth-Token` → `?token=`

First 2xx response wins. Stored in `Handler.auth_header_name`.

## Frontend Screen Flow

```
scr-login → scr-setup → scr-viewer → [loop] → scr-summary
```

`show(id)`: removes `.active` from all `.screen` divs, adds to target.

## State Management

**v1 (current):** 20+ global variables. **v2 target:** structured objects.

```javascript
// v2 target
var AppState = {
  tasks: [], idx: 0, decisions: {}, actionButtons: [],
  allOrgs: [], selectedOrgId: null, taskDetailCache: {},
  submitStatus: {}, submitQueue: []
};
var LightboxState = { photos: [], curIdx: 0, zoom: 1, dx: 0, dy: 0 };
```

## Submit Queue (FIFO, 400ms gap)

```javascript
submitQueue.push(item);      // enqueue
item = submitQueue.shift();  // dequeue
setTimeout(processNext, SUBMIT_GAP);  // rate limit
```

## v1 → v2 Key Changes

| Issue | v2 Fix |
|-------|--------|
| 20+ global vars | `AppState`, `LightboxState` objects |
| Silent `.catch(function(){})` | All errors surfaced to user |
| 1782-line monolith | Logical `<script>` sections |
| No settings persistence | `localStorage` for filters + buttons |
| Button race condition | Disable during PATCH, re-enable on response |
| No request logging | `logging` module → `.log` file next to .exe |
