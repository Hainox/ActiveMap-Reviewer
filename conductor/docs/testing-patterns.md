# Testing Patterns

> Confidence: HIGH — analyzed from reviewer.py + reviewer_html.html

## Current State (v1)

- **Automated tests:** 0% — no pytest, no Jest
- **Testing approach:** Manual browser testing only
- **Logging:** `print()` statements, no levels or rotation

## Error Handling Rules (v2)

### Python — Never swallow exceptions silently

```python
# Bad (v1 pattern to eliminate)
except:
    return False

# Good
except urllib.error.HTTPError as e:
    self._send(e.code, e.read() or b'{}')
except Exception as e:
    logging.error(f"Proxy error: {e}")
    self._send(500, json.dumps({"error": str(e)}).encode())
```

### JavaScript — Never silent catch

```javascript
// Bad (v1 pattern to eliminate)
.catch(function(){})

// Good
.catch(function(e) {
  console.error('[load error]', e);
  showError('Не удалось загрузить данные: ' + e.message);
})
```

## Logging (v2)

Replace `print()` with Python `logging` module:

```python
logging.basicConfig(
  level=logging.INFO,
  format='%(asctime)s [%(levelname)s] %(message)s',
  handlers=[
    logging.FileHandler(_app_dir() / 'reviewer.log'),
    logging.StreamHandler()
  ]
)

logging.info(f"[LOGIN OK] token={token[:8]}...")
logging.error(f"[PATCH FAIL] taskId={task_id}: {e}")
```

## v2 Testing Strategy

### Unit Tests (pytest)

```python
# tests/test_auth.py
def test_detect_bearer_token(): ...
def test_format_error_response(): ...
```

### Smoke Test

```python
def test_version_endpoint():
    r = requests.get('http://localhost:8765/version')
    assert r.status_code == 200
    assert r.json()['version'] == VERSION
```

## Manual Test Checklist

Before each release:
- [ ] Login with valid credentials
- [ ] Filter by work type + status + stage + org
- [ ] Load 50+ tasks, navigate with ←/→ and hotkeys
- [ ] Open lightbox, zoom in/out, pan
- [ ] Apply decision button, verify PATCH sent
- [ ] Submit bug report, verify bug_reports.jsonl written
- [ ] Verify settings persist after restart (localStorage)
- [ ] Build .exe and run on clean Windows machine
