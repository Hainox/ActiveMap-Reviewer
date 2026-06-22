#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ActiveMap Task Reviewer — Префектура САО"""
import json, http.server, urllib.request, urllib.error, webbrowser, threading, os, datetime, sys

VERSION = "1.2.0"
BASE_URL = "https://sao.geofsm.ru"
PORT = 8765

# ── GitHub Issues для баг-репортов ────────────────────────────────────────────
# Вставьте сюда Personal Access Token с правом Issues:Write
# Инструкция: github.com/settings/tokens → Fine-grained → Issues: Read+Write
# Если оставить пустым — репорты сохраняются только локально в bug_reports.jsonl
GITHUB_TOKEN = ""  # вставьте токен вручную перед запуском, не храните в репозитории
GITHUB_REPO  = "Hainox/ActiveMap-Reviewer"   # ваш репозиторий
# ─────────────────────────────────────────────────────────────────────────────

def _app_dir():
    """Папка рядом с .exe или рядом с .py — используется для записи файлов."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def _resource(filename):
    """Путь к bundled-ресурсу: сначала ищем рядом с exe (переопределение), потом в MEIPASS."""
    if getattr(sys, 'frozen', False):
        override = os.path.join(os.path.dirname(sys.executable), filename)
        if os.path.exists(override):
            return override
        return os.path.join(sys._MEIPASS, filename)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)

HTML_PATH = _resource("reviewer_html.html")

class Handler(http.server.BaseHTTPRequestHandler):
    token = None
    auth_use_queryparam = False
    auth_header_name  = "Authorization"
    auth_header_value = None
    auth_ready = threading.Event()

    def do_OPTIONS(self):
        self._cors(200); self.end_headers()

    def do_HEAD(self):
        p = self.path
        if p.startswith("/proxy/"):
            url = f"{BASE_URL}/rest/{p[7:]}"
            try:
                with urllib.request.urlopen(self._authed(url), timeout=10) as resp:
                    self.send_response(resp.status)
                    self.send_header("Content-Type", resp.headers.get("Content-Type","application/octet-stream"))
                    self.send_header("Content-Length", resp.headers.get("Content-Length","0"))
                    self._cors(); self.end_headers()
            except urllib.error.HTTPError as e:
                self.send_response(e.code); self._cors(); self.end_headers()
            except:
                self.send_response(500); self._cors(); self.end_headers()
        else:
            self.send_response(404); self.end_headers()

    def do_GET(self):
        p = self.path
        if p in ("/", "/index.html"): self._serve_html()
        elif p.startswith("/proxy/"): self._proxy_get(f"{BASE_URL}/rest/{p[7:]}")
        elif p == "/version": self._send(200, json.dumps({"version": VERSION}).encode())
        elif p == "/debug": self._debug_info()
        elif p.startswith("/debug-task/"): self._debug_task(p[12:].split("?")[0])
        else: self.send_response(404); self.end_headers()

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(n) if n else b"{}"
        p = self.path
        if p == "/login": self._handle_login(body)
        elif p.startswith("/patch/"): self._proxy_patch(f"{BASE_URL}/rest/tasks/{p[7:]}?apiVersion=2.0", body)
        elif p == "/report-bug": self._handle_bug_report(body)
        else: self.send_response(404); self.end_headers()

    def _handle_login(self, body):
        try:
            req = urllib.request.Request(
                f"{BASE_URL}/rest/auth/by-login?apiVersion=2.0",
                data=body, headers={"Content-Type":"application/json"}, method="POST")
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = resp.read()
                parsed = json.loads(data)
                Handler.token = parsed.get("token","")
                Handler.auth_header_value = None
                Handler.auth_use_queryparam = False
                Handler.auth_ready.clear()
                print(f"  [LOGIN OK] {Handler.token[:10]}...")
                self._send(200, data)
                threading.Thread(target=self._detect_auth, daemon=True).start()
        except urllib.error.HTTPError as e:
            self._send(e.code, e.read() or b'{"error":"auth failed"}')
        except Exception as e:
            self._send(500, json.dumps({"error":str(e)}).encode())

    def _detect_auth(self):
        url = f"{BASE_URL}/rest/statuses?apiVersion=2.0&limit=1"
        t = Handler.token
        def ok(u, h=None):
            try:
                r = urllib.request.Request(u)
                for k,v in (h or {}).items(): r.add_header(k,v)
                with urllib.request.urlopen(r, timeout=5) as resp: return resp.status==200
            except: return False
        for k,v in [("Authorization",t),("Authorization",f"Token {t}"),
                    ("Authorization",f"Bearer {t}"),("Cookie",f"token={t}"),("X-Auth-Token",t)]:
            if ok(url,{k:v}):
                Handler.auth_header_name=k; Handler.auth_header_value=v
                Handler.auth_use_queryparam=False
                print(f"  [AUTH OK] {k}"); Handler.auth_ready.set(); return
        if ok(f"{url}&token={t}"):
            Handler.auth_use_queryparam=True; print("  [AUTH OK] ?token="); Handler.auth_ready.set(); return
        print("  [AUTH FAIL]"); Handler.auth_ready.set()

    def _authed(self, url, data=None, method=None):
        if Handler.token:
            Handler.auth_ready.wait(timeout=12)
            if Handler.auth_use_queryparam:
                url += ("&" if "?" in url else "?") + f"token={Handler.token}"
                req = urllib.request.Request(url, data=data)
            else:
                req = urllib.request.Request(url, data=data)
                if Handler.auth_header_value:
                    req.add_header(Handler.auth_header_name, Handler.auth_header_value)
        else:
            req = urllib.request.Request(url, data=data)
        if method: req.method = method
        return req

    def _proxy_get(self, url):
        try:
            with urllib.request.urlopen(self._authed(url), timeout=20) as resp:
                self.send_response(200)
                self.send_header("Content-Type", resp.headers.get("Content-Type","application/json"))
                self._cors(); self.end_headers(); self.wfile.write(resp.read())
        except urllib.error.HTTPError as e: self._send(e.code, e.read() or b"{}")
        except Exception as e: self._send(500, json.dumps({"error":str(e)}).encode())

    def _proxy_patch(self, url, body):
        try:
            req = self._authed(url, data=body, method="PATCH")
            req.add_header("Content-Type","application/json")
            with urllib.request.urlopen(req, timeout=15): self._send(200, b'{"ok":true}')
        except urllib.error.HTTPError as e: self._send(e.code, e.read() or b"{}")
        except Exception as e: self._send(500, json.dumps({"error":str(e)}).encode())

    def _handle_bug_report(self, body):
        """Сохраняет отчёт об ошибке локально и отправляет в GitHub Issues (если задан токен)"""
        try:
            report = json.loads(body)
            report["timestamp"] = datetime.datetime.now().isoformat()
            report["version"] = VERSION

            # 1. Всегда сохраняем локально как резерв
            log_path = os.path.join(_app_dir(), "bug_reports.jsonl")
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(report, ensure_ascii=False) + "\n")

            rtype = report.get("type", "Прочее")
            rdesc = str(report.get("description", ""))
            rtask = report.get("task_no", "")
            print(f"  [BUG REPORT] {rtype}: {rdesc[:80]}")

            # 2. Отправляем в GitHub Issues если токен задан
            if GITHUB_TOKEN:
                self._send_github_issue(rtype, rdesc, rtask, report["timestamp"])

            self._send(200, b'{"ok":true}')
        except Exception as e:
            self._send(500, json.dumps({"error": str(e)}).encode())

    def _send_github_issue(self, rtype, description, task_no, timestamp):
        """Создаёт Issue в GitHub репозитории"""
        try:
            title = f"[{rtype}] {description[:80]}"
            body_lines = [
                f"**Тип:** {rtype}",
                f"**Описание:** {description}",
            ]
            if task_no:
                body_lines.append(f"**Задание:** {task_no}")
            body_lines += [
                f"**Версия:** {VERSION}",
                f"**Время:** {timestamp}",
                "",
                "*Отправлено автоматически из ActiveMap Reviewer*",
            ]
            payload = json.dumps({
                "title": title,
                "body": "\n".join(body_lines),
                "labels": ["bug"]
            }).encode("utf-8")

            req = urllib.request.Request(
                f"https://api.github.com/repos/{GITHUB_REPO}/issues",
                data=payload,
                headers={
                    "Authorization": f"token {GITHUB_TOKEN}",
                    "Accept": "application/vnd.github+json",
                    "Content-Type": "application/json",
                    "X-GitHub-Api-Version": "2022-11-28",
                },
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                result = json.loads(resp.read())
                print(f"  [GITHUB ISSUE] #{result.get('number')} создан: {result.get('html_url','')}")
        except Exception as e:
            print(f"  [GITHUB ISSUE ERROR] {e}")

    def _debug_task(self, task_id):
        """Возвращает сырой JSON задания для диагностики"""
        try:
            url = f"{BASE_URL}/rest/tasks/{task_id}?apiVersion=2.0"
            with urllib.request.urlopen(self._authed(url), timeout=15) as resp:
                data = resp.read()
                parsed = json.loads(data)
                # Печатаем ключи и первые значения в терминал
                print(f"\n[DEBUG TASK {task_id}] keys: {list(parsed.keys())[:20]}")
                for k in ['photoCount','photosCount','photos_count','photos','attachments','countPhotos']:
                    if k in parsed:
                        print(f"  {k} = {repr(parsed[k])[:200]}")
                self._send(200, json.dumps(parsed, ensure_ascii=False, indent=2).encode())
        except Exception as e:
            self._send(500, json.dumps({"error": str(e)}).encode())

    def _debug_info(self):
        info = {"token":bool(Handler.token),"auth_ready":Handler.auth_ready.is_set(),
                "auth_qp":Handler.auth_use_queryparam,"header":Handler.auth_header_name}
        for ep in ["statuses?apiVersion=2.0","types?apiVersion=2.0"]:
            try:
                with urllib.request.urlopen(self._authed(f"{BASE_URL}/rest/{ep}"), timeout=10) as r:
                    info[ep] = r.read().decode()[:600]
            except Exception as e: info[ep] = str(e)
        self._send(200, json.dumps(info, ensure_ascii=False, indent=2).encode())

    def _serve_html(self):
        try:
            with open(HTML_PATH,"rb") as f: html=f.read()
        except Exception as e: html=f"<h1>Error: {e}</h1>".encode()
        self.send_response(200)
        self.send_header("Content-Type","text/html; charset=utf-8")
        self.send_header("Content-Length",str(len(html)))
        self.send_header("Cache-Control","no-store, no-cache, must-revalidate")
        self._cors(); self.end_headers(); self.wfile.write(html)

    def _send(self, code, data, ct="application/json; charset=utf-8"):
        self.send_response(code)
        self.send_header("Content-Type",ct)
        self._cors(); self.end_headers(); self.wfile.write(data)

    def _cors(self, code=None):
        if code: self.send_response(code)
        self.send_header("Access-Control-Allow-Origin","*")
        self.send_header("Access-Control-Allow-Methods","GET,POST,PATCH,OPTIONS")
        self.send_header("Access-Control-Allow-Headers","Content-Type,Authorization")

    def log_message(self, fmt, *args): pass

class ThreadingServer(http.server.ThreadingHTTPServer):
    daemon_threads = True

if __name__ == "__main__":
    server = ThreadingServer(("localhost", PORT), Handler)
    print(f"ActiveMap Task Reviewer v{VERSION}")
    print(f"  http://localhost:{PORT}")
    threading.Timer(1.3, lambda: webbrowser.open(f"http://localhost:{PORT}")).start()
    try: server.serve_forever()
    except KeyboardInterrupt: print("Stopped.")
