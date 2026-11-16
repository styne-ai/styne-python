from __future__ import annotations

import json
from typing import Any, Callable, Dict, List

import httpx
import pytest

import styne

VM = {"id": "vm_1", "state": "running", "created_at": "2026-11-16T10:00:00Z", "ports": []}


class Recorder:
    """Records requests and answers them through a handler."""

    def __init__(self, handler: Callable[[httpx.Request], httpx.Response]) -> None:
        self.handler = handler
        self.requests: List[httpx.Request] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        return self.handler(request)

    def body(self, index: int = -1) -> Dict[str, Any]:
        data: Dict[str, Any] = json.loads(self.requests[index].content)
        return data


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch: pytest.MonkeyPatch) -> List[float]:
    delays: List[float] = []
    monkeypatch.setattr("styne._transport.time.sleep", delays.append)

    async def fake_sleep(seconds: float) -> None:
        delays.append(seconds)

    monkeypatch.setattr("styne._transport.asyncio.sleep", fake_sleep)
    return delays


def make_client(handler: Callable[[httpx.Request], httpx.Response]) -> tuple[styne.Client, Recorder]:
    rec = Recorder(handler)
    http = httpx.Client(transport=httpx.MockTransport(rec))
    return styne.Client("k", base_url="https://api.test/v1", http_client=http), rec


def make_async_client(handler: Callable[[httpx.Request], httpx.Response]) -> tuple[styne.AsyncClient, Recorder]:
    rec = Recorder(handler)
    http = httpx.AsyncClient(transport=httpx.MockTransport(rec))
    return styne.AsyncClient("k", base_url="https://api.test/v1", http_client=http), rec


def envelope(status: int, code: str, message: str = "nope", **extra: Any) -> httpx.Response:
    body = {"error": {"code": code, "status": status, "message": message, "request_id": "req_9", **extra}}
    return httpx.Response(status, json=body, headers={"X-Request-Id": "req_9"})
