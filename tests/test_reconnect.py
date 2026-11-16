from __future__ import annotations

import asyncio
from typing import Any, List

import httpx
import pytest
from conftest import make_async_client, make_client

import styne
from styne._reconnect import is_disconnect


def _handler(states: List[str]) -> Any:
    def handle(request: httpx.Request) -> httpx.Response:
        state = states.pop(0) if len(states) > 1 else states[0]
        return httpx.Response(200, json={"id": "br_1", "state": state, "cdp_url": "wss://run.test/cdp"})

    return handle


def _browser(states: List[str]) -> styne.Browser:
    client, _ = make_client(_handler(states))
    return styne.Browser(client._transport, {"id": "br_1", "state": "running", "cdp_url": "wss://x"})


class ConnectionClosedError(Exception):
    """Stands in for websockets.exceptions.ConnectionClosedError."""


def _chained() -> BaseException:
    try:
        try:
            raise ConnectionResetError("reset")
        except ConnectionResetError as inner:
            raise RuntimeError("navigation failed") from inner
    except RuntimeError as outer:
        return outer


def test_is_disconnect_matches_closed_sockets_only() -> None:
    assert is_disconnect(ConnectionResetError("reset"))
    assert is_disconnect(EOFError())
    assert is_disconnect(RuntimeError("Target page, context or browser has been closed"))
    assert is_disconnect(RuntimeError("WebSocket error: connection closed"))
    assert is_disconnect(ConnectionClosedError("no close frame received or sent"))
    assert is_disconnect(_chained())
    assert not is_disconnect(RuntimeError("selector #go not found"))
    assert not is_disconnect(RuntimeError("payment dialog not open"))
    assert not is_disconnect(RuntimeError("homepage closed for maintenance"))
    assert not is_disconnect(TimeoutError("Timeout 30000ms exceeded"))
    assert not is_disconnect(KeyError("closed_at"))
    assert not is_disconnect(styne.NotFoundError("page closed", status=404))


def test_reconnects_after_a_closed_socket(no_sleep: List[float]) -> None:
    browser = _browser(["running"])
    urls: List[str] = []
    seen: List[int] = []

    def run(page: str, attempt: int) -> str:
        seen.append(attempt)
        if attempt < 2:
            raise ConnectionResetError("socket closed")
        return page

    assert browser.with_reconnect(lambda url: urls.append(url) or "b", run, delay=0.25) == "b"
    assert seen == [0, 1, 2]
    assert len(urls) == 3
    assert no_sleep == [0.25, 0.5]


def test_other_errors_are_raised_at_once(no_sleep: List[float]) -> None:
    browser = _browser(["running"])
    with pytest.raises(ValueError, match="bad selector"):
        browser.with_reconnect(lambda url: url, lambda b, n: (_ for _ in ()).throw(ValueError("bad selector")))
    assert no_sleep == []


def test_gives_up_after_max_reconnects(no_sleep: List[float]) -> None:
    browser = _browser(["running"])
    attempts: List[int] = []

    def run(b: Any, attempt: int) -> None:
        attempts.append(attempt)
        raise EOFError()

    with pytest.raises(EOFError):
        browser.with_reconnect(lambda url: url, run, max_reconnects=2)
    assert attempts == [0, 1, 2]


def test_stops_when_the_browser_is_no_longer_running() -> None:
    browser = _browser(["running", "stopped"])

    def run(b: Any, attempt: int) -> None:
        raise ConnectionResetError("gone")

    with pytest.raises(styne.StyneError, match="stopped, not running"):
        browser.with_reconnect(lambda url: url, run)


def test_async_reconnects_after_a_closed_socket(no_sleep: List[float]) -> None:
    client, _ = make_async_client(
        lambda request: httpx.Response(200, json={"id": "br_1", "state": "running", "cdp_url": "wss://c"})
    )
    browser = styne.AsyncBrowser(client._transport, {"id": "br_1", "state": "running", "cdp_url": "wss://x"})

    async def connect(url: str) -> str:
        return url

    async def run(b: str, attempt: int) -> str:
        if attempt == 0:
            raise RuntimeError("Browser has been closed")
        return f"{b}:{attempt}"

    assert asyncio.run(browser.with_reconnect(connect, run)) == "wss://c:1"
    assert no_sleep == [0.5]


def test_reconnect_uses_the_refreshed_url_and_a_custom_classifier() -> None:
    browser = _browser(["running"])
    urls: List[str] = []

    def run(b: str, attempt: int) -> str:
        if attempt == 0:
            raise RuntimeError("renderer crashed")
        return b

    result = browser.with_reconnect(
        lambda url: urls.append(url) or url,
        run,
        is_disconnect=lambda error: "crashed" in str(error),
    )
    assert result == "wss://run.test/cdp"
    assert urls == ["wss://run.test/cdp"] * 2


def test_max_reconnects_zero_never_reconnects() -> None:
    browser = _browser(["running"])
    runs: List[int] = []

    def run(b: Any, attempt: int) -> None:
        runs.append(attempt)
        raise EOFError()

    with pytest.raises(EOFError):
        browser.with_reconnect(lambda url: url, run, max_reconnects=0)
    assert runs == [0]


def test_refresh_failure_is_raised_not_retried() -> None:
    client, _ = make_client(
        lambda request: httpx.Response(404, json={"error": {"code": "not_found", "status": 404, "message": "x"}})
    )
    browser = styne.Browser(client._transport, {"id": "br_1", "state": "running", "cdp_url": "wss://x"})
    with pytest.raises(styne.NotFoundError):
        browser.with_reconnect(lambda url: url, lambda b, n: b)
