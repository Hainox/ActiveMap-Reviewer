"""Tests for auth detection logic — TDD RED phase.

Tests FAIL until reviewer.py exports detect_auth_format() and build_authed_request().
"""
import pytest
import urllib.error
import threading


def _http_error(code):
    return urllib.error.HTTPError(url="", code=code, msg="", hdrs=None, fp=None)


class TestDetectAuthFormat:
    """detect_auth_format(token, base_url, request_fn) → dict | None"""

    def _fn(self):
        from reviewer import detect_auth_format
        return detect_auth_format

    def test_bearer_detected(self):
        f = self._fn()
        def req(url, headers):
            return 200 if headers.get("Authorization") == "Bearer tok" else (_ for _ in ()).throw(_http_error(401))
        r = f("tok", "https://x.com", request_fn=req)
        assert r and r["header_value"] == "Bearer tok" and not r["use_queryparam"]

    def test_token_prefix_detected(self):
        f = self._fn()
        def req(url, headers):
            return 200 if headers.get("Authorization") == "Token tok" else (_ for _ in ()).throw(_http_error(401))
        r = f("tok", "https://x.com", request_fn=req)
        assert r and r["header_value"] == "Token tok"

    def test_raw_authorization_detected(self):
        f = self._fn()
        def req(url, headers):
            return 200 if headers.get("Authorization") == "tok" else (_ for _ in ()).throw(_http_error(401))
        r = f("tok", "https://x.com", request_fn=req)
        assert r and r["header_value"] == "tok"

    def test_cookie_detected(self):
        f = self._fn()
        def req(url, headers):
            return 200 if headers.get("Cookie") == "token=tok" else (_ for _ in ()).throw(_http_error(401))
        r = f("tok", "https://x.com", request_fn=req)
        assert r and r["header_name"] == "Cookie"

    def test_x_auth_token_detected(self):
        f = self._fn()
        def req(url, headers):
            return 200 if headers.get("X-Auth-Token") == "tok" else (_ for _ in ()).throw(_http_error(401))
        r = f("tok", "https://x.com", request_fn=req)
        assert r and r["header_name"] == "X-Auth-Token"

    def test_queryparam_detected(self):
        f = self._fn()
        def req(url, headers):
            return 200 if "token=tok" in url and not headers else (_ for _ in ()).throw(_http_error(401))
        r = f("tok", "https://x.com", request_fn=req)
        assert r and r["use_queryparam"] is True

    def test_all_fail_returns_none(self):
        f = self._fn()
        def req(url, headers):
            raise _http_error(401)
        assert f("bad", "https://x.com", request_fn=req) is None

    def test_bearer_priority_over_queryparam(self):
        f = self._fn()
        def req(url, headers):
            if headers.get("Authorization") == "Bearer tok": return 200
            if "token=tok" in url: return 200
            raise _http_error(401)
        r = f("tok", "https://x.com", request_fn=req)
        assert r and not r["use_queryparam"]


class TestBuildAuthedRequest:
    """build_authed_request(url, token, auth_config, auth_ready) → Request | None"""

    def _fn(self):
        from reviewer import build_authed_request
        return build_authed_request

    def test_returns_none_when_auth_failed(self):
        f = self._fn()
        ev = threading.Event(); ev.set()
        assert f("https://x.com", "tok", auth_config=None, auth_ready=ev) is None

    def test_injects_bearer_header(self):
        f = self._fn()
        ev = threading.Event(); ev.set()
        cfg = {"header_name": "Authorization", "header_value": "Bearer tok", "use_queryparam": False}
        req = f("https://x.com/api", "tok", auth_config=cfg, auth_ready=ev)
        assert req is not None
        assert req.get_header("Authorization") == "Bearer tok"

    def test_injects_queryparam(self):
        f = self._fn()
        ev = threading.Event(); ev.set()
        cfg = {"use_queryparam": True}
        req = f("https://x.com/api", "tok", auth_config=cfg, auth_ready=ev)
        assert req is not None
        assert "token=tok" in req.full_url
