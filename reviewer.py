#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ActiveMap Task Reviewer — Префектура САО"""
import json, http.server, urllib.request, urllib.error, webbrowser, threading, os, datetime, sys
import logging

VERSION = "2.0.3"
BASE_URL = "https://sao.geofsm.ru"
PORT = 8765


class AuthTimeoutError(TimeoutError):
    """Raised only when the 12s auth-format-detection wait times out — kept distinct from a
    plain socket timeout (also a TimeoutError since Python 3.10) so upstream ActiveMap slowness
    isn't misdiagnosed in logs/responses as an auth-detection problem."""
    pass

# ── GitHub Issues для баг-репортов ────────────────────────────────────────────
# Вставьте сюда Personal Access Token с правом Issues:Write
# Инструкция: github.com/settings/tokens → Fine-grained → Issues: Read+Write
# Если оставить пустым — репорты сохраняются только локально в bug_reports.jsonl
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")  # задайте переменную окружения перед запуском
GITHUB_REPO  = "Hainox/ActiveMap-Reviewer"   # ваш репозиторий
# ─────────────────────────────────────────────────────────────────────────────

def _app_dir():
    """Папка рядом с .exe или рядом с .py — используется для записи файлов."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

# ── Logging setup ─────────────────────────────────────────────────────────────
def _setup_logging():
    log_path = os.path.join(_app_dir(), "reviewer.log")
    _logger = logging.getLogger("reviewer")
    _logger.setLevel(logging.DEBUG)
    if not _logger.handlers:
        fh = logging.FileHandler(log_path, encoding="utf-8")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        _logger.addHandler(fh)
    return _logger

logger = _setup_logging()
# ─────────────────────────────────────────────────────────────────────────────

def _resource(filename):
    """Путь к bundled-ресурсу: сначала ищем рядом с exe (переопределение), потом в MEIPASS."""
    if getattr(sys, 'frozen', False):
        override = os.path.join(os.path.dirname(sys.executable), filename)
        if os.path.exists(override):
            # Старый файл, оставленный рядом с .exe (от прошлой сборки/попытки Способа 2),
            # молча выигрывает у актуальной версии, вшитой в exe — без этой записи в лог
            # "скачал новую версию, а работает по-старому" было бы невозможно диагностировать.
            logger.warning("Using %s override next to exe instead of bundled copy — "
                            "delete it if this isn't intentional.", override)
            return override
        return os.path.join(sys._MEIPASS, filename)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)

HTML_PATH = _resource("reviewer_html.html")


def detect_auth_format(token, base_url, request_fn):
    """Try 6 auth formats; return first working config dict or None.

    request_fn(url, headers) must return without raising on success, raise on failure.
    Returns: {"header_name", "header_value", "use_queryparam"} or None.
    """
    probe_url = base_url.rstrip("/") + "/rest/statuses?apiVersion=2.0&limit=1"

    for header_name, header_value in [
        ("Authorization", f"Bearer {token}"),
        ("Authorization", f"Token {token}"),
        ("Authorization", token),
        ("Cookie", f"token={token}"),
        ("X-Auth-Token", token),
    ]:
        try:
            request_fn(probe_url, {header_name: header_value})
            return {"header_name": header_name, "header_value": header_value, "use_queryparam": False}
        except Exception as e:
            logger.debug("auth probe %s failed: %s", header_name, e)

    sep = "&" if "?" in probe_url else "?"
    qp_url = probe_url + sep + f"token={token}"
    try:
        request_fn(qp_url, {})
        return {"use_queryparam": True}
    except Exception as e:
        logger.debug("auth probe queryparam failed: %s", e)

    return None


def build_authed_request(url, token, auth_config, auth_ready):
    """Build an authenticated urllib Request.

    Waits on auth_ready (up to 12s). Returns None if auth_config is None (auth failed).
    """
    auth_ready.wait(timeout=12)
    if auth_config is None:
        return None
    if auth_config.get("use_queryparam"):
        sep = "&" if "?" in url else "?"
        return urllib.request.Request(url + sep + f"token={token}")
    req = urllib.request.Request(url)
    req.add_header(auth_config["header_name"], auth_config["header_value"])
    return req


class Handler(http.server.BaseHTTPRequestHandler):
    token = None
    auth_config = None          # set by _detect_auth after login
    auth_ready = threading.Event()
    auth_epoch = 0               # bumped on every /login; a _detect_auth thread from a
                                  # superseded earlier login discards its (stale) result instead
                                  # of overwriting the newer login's auth_config

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
            except AuthTimeoutError as e:
                logger.warning("HEAD auth timeout: %s", e)
                self._send(503, json.dumps({"error": str(e)}).encode())
            except TimeoutError as e:
                logger.warning("HEAD upstream timeout: %s", e)
                self._send(504, json.dumps({"error": "Сервер ActiveMap не ответил вовремя"}).encode())
            except urllib.error.HTTPError as e:
                self.send_response(e.code); self._cors(); self.end_headers()
            except Exception as e:
                logger.error("HEAD proxy error: %s", e)
                self.send_response(500); self._cors(); self.end_headers()
        else:
            self.send_response(404); self.end_headers()

    def do_GET(self):
        p = self.path
        if p in ("/", "/index.html"): self._serve_html()
        elif p.startswith("/proxy/"): self._proxy_get(f"{BASE_URL}/rest/{p[7:]}")
        elif p == "/version": self._send(200, json.dumps({"version": VERSION}).encode())
        elif p == "/debug":
            if os.environ.get("DEBUG") == "1": self._debug_info()
            else: self.send_response(404); self.end_headers()
        elif p.startswith("/debug-task/"):
            if os.environ.get("DEBUG") == "1": self._debug_task(p[12:].split("?")[0])
            else: self.send_response(404); self.end_headers()
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
                Handler.auth_config = None
                Handler.auth_ready.clear()
                Handler.auth_epoch += 1
                logger.info("LOGIN OK token=%s...", Handler.token[:10])
                self._send(200, data)
                threading.Thread(target=self._detect_auth, args=(Handler.auth_epoch,), daemon=True).start()
        except urllib.error.HTTPError as e:
            self._send(e.code, e.read() or b'{"error":"auth failed"}')
        except Exception as e:
            logger.error("Login error: %s", e)
            self._send(500, json.dumps({"error":str(e)}).encode())

    def _detect_auth(self, epoch):
        t = Handler.token

        def request_fn(url, headers):
            req = urllib.request.Request(url)
            for k, v in headers.items():
                req.add_header(k, v)
            with urllib.request.urlopen(req, timeout=5):
                pass

        config = detect_auth_format(t, BASE_URL, request_fn)
        if epoch != Handler.auth_epoch:
            # Пока шла детекция, произошёл ещё один /login — этот результат устарел
            logger.info("AUTH detection for epoch %d discarded (current epoch %d)", epoch, Handler.auth_epoch)
            return
        Handler.auth_config = config
        if config:
            if config.get("use_queryparam"):
                logger.info("AUTH OK: queryparam ?token=")
            else:
                logger.info("AUTH OK: %s", config["header_name"])
        else:
            logger.warning("AUTH FAIL: no working format found")
        Handler.auth_ready.set()

    def _authed(self, url, data=None, method=None):
        if Handler.token:
            if not Handler.auth_ready.wait(timeout=12):
                raise AuthTimeoutError("Авторизация: превышено время ожидания (12 сек). Перезапустите приложение.")
            req = build_authed_request(url, Handler.token, Handler.auth_config, Handler.auth_ready)
            if req is None:
                # auth failed — attempt unauthenticated
                req = urllib.request.Request(url, data=data)
            elif data is not None:
                req.data = data
        else:
            req = urllib.request.Request(url, data=data)
        if method:
            req.method = method
        return req

    def _proxy_get(self, url):
        try:
            with urllib.request.urlopen(self._authed(url), timeout=20) as resp:
                content_type = resp.headers.get("Content-Type","application/json")
                body = resp.read()  # читаем ДО отправки заголовков — иначе обрыв чтения тут привёл бы
                                     # ко второму send_response() поверх уже отправленного 200
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self._cors(); self.end_headers(); self.wfile.write(body)
        except AuthTimeoutError as e:
            logger.warning("GET auth timeout: %s", e)
            self._send(503, json.dumps({"error": str(e)}).encode())
        except TimeoutError as e:
            logger.warning("GET upstream timeout: %s", e)
            self._send(504, json.dumps({"error": "Сервер ActiveMap не ответил вовремя"}).encode())
        except urllib.error.HTTPError as e: self._send(e.code, e.read() or b"{}")
        except Exception as e:
            logger.error("GET proxy error: %s", e)
            self._send(500, json.dumps({"error":str(e)}).encode())

    def _proxy_patch(self, url, body):
        try:
            req = self._authed(url, data=body, method="PATCH")
            req.add_header("Content-Type","application/json")
            with urllib.request.urlopen(req, timeout=15): self._send(200, b'{"ok":true}')
        except AuthTimeoutError as e:
            logger.warning("PATCH auth timeout: %s", e)
            self._send(503, json.dumps({"error": str(e)}).encode())
        except TimeoutError as e:
            logger.warning("PATCH upstream timeout: %s", e)
            self._send(504, json.dumps({"error": "Сервер ActiveMap не ответил вовремя"}).encode())
        except urllib.error.HTTPError as e: self._send(e.code, e.read() or b"{}")
        except Exception as e:
            logger.error("PATCH proxy error: %s", e)
            self._send(500, json.dumps({"error":str(e)}).encode())

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
            rtask = report.get("taskNumber", "")
            logger.info("BUG REPORT %s: %s", rtype, rdesc[:80])

            # 2. Отправляем в GitHub Issues если токен задан
            if GITHUB_TOKEN:
                self._send_github_issue(rtype, rdesc, rtask, report["timestamp"])

            self._send(200, b'{"ok":true}')
        except Exception as e:
            logger.error("Bug report error: %s", e)
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
                logger.info("GITHUB ISSUE #%s: %s", result.get('number'), result.get('html_url',''))
        except Exception as e:
            logger.error("GitHub issue error: %s", e)

    def _debug_task(self, task_id):
        """Возвращает сырой JSON задания для диагностики"""
        try:
            url = f"{BASE_URL}/rest/tasks/{task_id}?apiVersion=2.0"
            with urllib.request.urlopen(self._authed(url), timeout=15) as resp:
                data = resp.read()
                parsed = json.loads(data)
                logger.debug("DEBUG TASK %s keys: %s", task_id, list(parsed.keys())[:20])
                for k in ['photoCount','photosCount','photos_count','photos','attachments','countPhotos']:
                    if k in parsed:
                        logger.debug("  %s = %r", k, parsed[k])
                self._send(200, json.dumps(parsed, ensure_ascii=False, indent=2).encode())
        except Exception as e:
            logger.error("Debug task error: %s", e)
            self._send(500, json.dumps({"error": str(e)}).encode())

    def _debug_info(self):
        auth_config = Handler.auth_config
        if auth_config and auth_config.get("header_value"):
            auth_config = dict(auth_config, header_value="<redacted>")
        info = {"token":bool(Handler.token),"auth_ready":Handler.auth_ready.is_set(),
                "auth_config": auth_config}
        for ep in ["statuses?apiVersion=2.0","types?apiVersion=2.0"]:
            try:
                with urllib.request.urlopen(self._authed(f"{BASE_URL}/rest/{ep}"), timeout=10) as r:
                    info[ep] = r.read().decode()[:600]
            except Exception as e:
                info[ep] = str(e)
        self._send(200, json.dumps(info, ensure_ascii=False, indent=2).encode())

    def _serve_html(self):
        try:
            with open(HTML_PATH,"rb") as f: html=f.read()
        except Exception as e:
            logger.error("Serve HTML error: %s", e)
            html=f"<h1>Error: {e}</h1>".encode()
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
        # Фронтенд и бэкенд — один и тот же origin (localhost:PORT), CORS-заголовки приложению
        # не нужны. Раньше здесь стоял Access-Control-Allow-Origin: *, который открывал
        # авторизованные /proxy и /patch любому стороннему сайту, открытому в том же браузере.
        if code: self.send_response(code)

    def log_message(self, fmt, *args): pass

class ThreadingServer(http.server.ThreadingHTTPServer):
    daemon_threads = True
    # По умолчанию http.server разрешает SO_REUSEADDR, из-за чего на Windows вторая
    # запущенная копия .exe молча биндится на тот же порт вместо ошибки — браузер
    # затем случайно достаётся то новому, то старому процессу, и обновления версии
    # выглядят так, будто они не применились. Отключаем, чтобы вторая копия падала
    # с понятной ошибкой вместо создания второго невидимого процесса на порту.
    allow_reuse_address = False

def _running_instance_version():
    """Версия уже запущенного на PORT процесса, если он отвечает — иначе None."""
    try:
        with urllib.request.urlopen(f"http://localhost:{PORT}/version", timeout=2) as resp:
            return json.loads(resp.read()).get("version")
    except Exception:
        return None

if __name__ == "__main__":
    try:
        server = ThreadingServer(("localhost", PORT), Handler)
    except OSError:
        other_version = _running_instance_version()
        if other_version and other_version != VERSION:
            # Старая копия .exe (--noconsole, без окна/иконки) не закрылась и заняла порт —
            # её нельзя было "закрыть" обычным способом, только через Диспетчер задач.
            # Новая версия при этом молча не появлялась бы: браузер продолжал бы стучаться
            # в старый процесс. Явно предупреждаем вместо тихого открытия старой версии.
            logger.warning("Port %d held by v%s while this build is v%s", PORT, other_version, VERSION)
            print(f"Обнаружена запущенная старая копия (v{other_version}), эта копия — v{VERSION}.")
            print("Закройте старую копию через Диспетчер задач (ActiveMapReviewer.exe) и запустите заново.")
        else:
            logger.info("Port %d already in use — another instance is likely running.", PORT)
            print(f"ActiveMap Task Reviewer уже запущен — открываю http://localhost:{PORT}")
        webbrowser.open(f"http://localhost:{PORT}")
        sys.exit(0)
    logger.info("ActiveMap Task Reviewer v%s starting on port %d", VERSION, PORT)
    print(f"ActiveMap Task Reviewer v{VERSION}")
    print(f"  http://localhost:{PORT}")
    threading.Timer(1.3, lambda: webbrowser.open(f"http://localhost:{PORT}")).start()
    try: server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Server stopped.")
        print("Stopped.")
