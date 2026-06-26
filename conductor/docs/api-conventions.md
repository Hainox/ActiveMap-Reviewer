# API Conventions

> Confidence: HIGH — analyzed from reviewer.py + reviewer_html.html

## Internal Routes (Python server)

| Method | Path | Request | Response |
|--------|------|---------|---------|
| GET | `/version` | — | `{"version": "2.0.0"}` |
| POST | `/login` | `{"login": "...", "password": "..."}` | `{"token": "..."}` |
| GET | `/proxy/*` | — | Proxied JSON from ActiveMap |
| POST | `/patch/{taskId}` | `{"status_id": X, "stage": "..."}` | `{"ok": true}` |
| POST | `/report-bug` | `{"type": "...", "description": "...", "taskNumber": "..."}` | `{"ok": true}` |

## External API (ActiveMap)

All `/proxy/*` requests → `/rest/*` at `sao.geofsm.ru`.

Always include `?apiVersion=2.0` on all ActiveMap requests.

```
/proxy/tasks?apiVersion=2.0&limit=500&type_id=X&onlyStatus=Y
/proxy/tasks/{id}?apiVersion=2.0
/proxy/organizations?apiVersion=2.0&limit=500&offset=N
```

## PATCH Mutation Format

```javascript
fetch('/patch/' + taskId, {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    status_id: btn.statusId,
    statusId: btn.statusId,  // duplicate for API compat
    stage: btn.stageId       // "in_progress" | "completed"
  })
})
```

## Error Handling

Python: pass through upstream HTTP errors; wrap exceptions in `{"error": "..."}`.

JavaScript: always check `r.ok` before parsing, surface errors to user — never silent catch.

```javascript
fetch('/proxy/tasks?' + params)
  .then(r => { if (!r.ok) throw new Error(r.status); return r.json(); })
  .catch(e => showError('Ошибка: ' + e.message));
```

## Bug Report Schema

```json
{
  "type": "bug",
  "description": "...",
  "taskNumber": "12345",
  "version": "2.0.0",
  "timestamp": "2026-06-26T09:00:00Z"
}
```

Saved to `bug_reports.jsonl` (append-only). Optional: GitHub Issues via `GITHUB_TOKEN`.

## v2 Fixes

- `POST /patch/{taskId}` must pass through ActiveMap error code on failure (currently always returns `{"ok": true}`)
- `/debug` and `/debug-task` endpoints must be gated behind env var check
- Add `X-Request-ID` header for request correlation
