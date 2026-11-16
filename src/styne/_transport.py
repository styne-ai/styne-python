"""HTTP transports (sync and async) with retries, idempotency keys and error mapping."""

from __future__ import annotations

import asyncio
import json
import os
import random
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Dict, Iterator, List, Mapping, Optional, Union
from urllib.parse import urlsplit

import httpx

from ._version import __version__
from .errors import APIConnectionError, APITimeoutError, StyneError, error_from_payload

DEFAULT_BASE_URL = "https://api.styne.ai/v1"
DEFAULT_TIMEOUT = 60.0
DEFAULT_MAX_RETRIES = 2
_RETRY_STATUS = frozenset({408, 409, 429, 500, 502, 503, 504})
_MAX_BACKOFF = 8.0
_LOCAL_HOSTS = frozenset({"localhost", "127.0.0.1", "::1"})

# A long-running call (a command without its own timeout, an output stream) waits for the answer without a read
# deadline; only connecting is bounded.
NO_READ_TIMEOUT = httpx.Timeout(None, connect=10.0)

Timeout = Union[float, httpx.Timeout, None]


@dataclass
class Request:
    """One API call, independent of sync or async execution.

    ``idempotent`` marks a POST the server deduplicates by Idempotency-Key; only such a POST is retried.
    """

    method: str
    path: str
    params: Optional[Mapping[str, Any]] = None
    json: Any = None
    content: Optional[bytes] = None
    headers: Dict[str, str] = field(default_factory=dict)
    idempotent: bool = False
    timeout: Timeout = None


@dataclass
class Event:
    """One server-sent event."""

    event: str
    data: str
    id: Optional[str] = None

    def json(self) -> Any:
        return json.loads(self.data)


def resolve_api_key(api_key: Optional[str]) -> str:
    key = api_key or os.environ.get("STYNE_API_KEY")
    if not key:
        raise StyneError("missing API key: pass api_key= or set STYNE_API_KEY")
    return key


def resolve_base_url(base_url: Optional[str]) -> str:
    url = (base_url or os.environ.get("STYNE_BASE_URL") or DEFAULT_BASE_URL).rstrip("/")
    parts = urlsplit(url)
    if parts.scheme != "https" and not (parts.scheme == "http" and parts.hostname in _LOCAL_HOSTS):
        raise StyneError(f"base URL must use https (http only for localhost): {url}")
    return url


def _clean(params: Optional[Mapping[str, Any]]) -> Optional[Dict[str, Any]]:
    if params is None:
        return None
    return {k: (str(v).lower() if isinstance(v, bool) else v) for k, v in params.items() if v is not None}


def _retry_after(response: httpx.Response) -> Optional[float]:
    raw = response.headers.get("retry-after")
    if raw is None:
        return None
    try:
        return max(0.0, float(raw))
    except ValueError:
        return None


def _delay(attempt: int, retry_after: Optional[float]) -> float:
    if retry_after is not None:
        return min(retry_after, 60.0)
    return random.uniform(0, min(_MAX_BACKOFF, 0.5 * 2**attempt))


def _may_retry(request: Request) -> bool:
    return request.method != "POST" or request.idempotent


def _is_retryable(request: Request, response: httpx.Response) -> bool:
    if response.status_code not in _RETRY_STATUS or not _may_retry(request):
        return False
    if response.status_code == 409:
        return request.idempotent and response.headers.get("retry-after") is not None
    return True


def _connection_error(exc: httpx.TransportError) -> APIConnectionError:
    message = str(exc) or type(exc).__name__
    if isinstance(exc, httpx.TimeoutException):
        return APITimeoutError(message)
    return APIConnectionError(message)


def _raise_for_error(response: httpx.Response) -> None:
    if response.status_code < 400:
        return
    try:
        payload = response.json()
    except ValueError:
        payload = None
    raise error_from_payload(
        response.status_code,
        payload,
        request_id=response.headers.get("x-request-id"),
        retry_after=_retry_after(response),
    )


def _gone_after_retry(request: Request, response: httpx.Response, attempt: int) -> bool:
    """A retried DELETE that answers 404: the earlier attempt already deleted the object."""
    return request.method == "DELETE" and attempt > 0 and response.status_code == 404


class _Base:
    def __init__(self, api_key: str, base_url: str, max_retries: int) -> None:
        self.max_retries = max_retries
        self._base = base_url.rstrip("/")
        self._headers = {"Authorization": f"Bearer {api_key}", "User-Agent": f"styne-python/{__version__}"}

    def _prepare(self, request: Request) -> Dict[str, Any]:
        headers = {**self._headers, **request.headers}
        if request.idempotent and request.method == "POST":
            headers.setdefault("Idempotency-Key", str(uuid.uuid4()))
        kwargs: Dict[str, Any] = {
            "method": request.method,
            "url": f"{self._base}/{request.path.lstrip('/')}",
            "params": _clean(request.params),
            "headers": headers,
        }
        if request.json is not None:
            kwargs["json"] = request.json
        if request.content is not None:
            kwargs["content"] = request.content
        if request.timeout is not None:
            kwargs["timeout"] = request.timeout
        return kwargs

    def _prepare_stream(self, request: Request) -> Dict[str, Any]:
        kwargs = self._prepare(request)
        kwargs["headers"]["Accept"] = "text/event-stream"
        kwargs["timeout"] = NO_READ_TIMEOUT
        return kwargs


class _SseParser:
    """Assembles events from SSE lines."""

    def __init__(self) -> None:
        self._event = "message"
        self._data: List[str] = []
        self._id: Optional[str] = None

    def feed(self, line: str) -> Optional[Event]:
        if line == "":
            return self.flush()
        if line.startswith(":"):
            return None
        name, _, value = line.partition(":")
        value = value[1:] if value.startswith(" ") else value
        if name == "event":
            self._event = value
        elif name == "data":
            self._data.append(value)
        elif name == "id":
            self._id = value
        return None

    def flush(self) -> Optional[Event]:
        event = Event(self._event, "\n".join(self._data), self._id) if self._data else None
        self._event, self._data = "message", []
        return event


def parse_sse(lines: Iterator[str]) -> Iterator[Event]:
    parser = _SseParser()
    for line in lines:
        event = parser.feed(line)
        if event:
            yield event
    event = parser.flush()
    if event:
        yield event


async def _aparse_sse(lines: AsyncIterator[str]) -> AsyncIterator[Event]:
    parser = _SseParser()
    async for line in lines:
        event = parser.feed(line)
        if event:
            yield event
    event = parser.flush()
    if event:
        yield event


class SyncTransport(_Base):
    def __init__(
        self, api_key: str, base_url: str, timeout: float, max_retries: int, http_client: Optional[httpx.Client] = None
    ) -> None:
        super().__init__(api_key, base_url, max_retries)
        self._owns_client = http_client is None
        self.http = http_client or httpx.Client(timeout=timeout)

    def send(self, request: Request) -> httpx.Response:
        kwargs = self._prepare(request)
        for attempt in range(self.max_retries + 1):
            try:
                response = self.http.request(**kwargs)
            except httpx.TransportError as exc:
                if attempt < self.max_retries and _may_retry(request):
                    time.sleep(_delay(attempt, None))
                    continue
                raise _connection_error(exc) from exc
            if attempt < self.max_retries and _is_retryable(request, response):
                time.sleep(_delay(attempt, _retry_after(response)))
                continue
            if not _gone_after_retry(request, response, attempt):
                _raise_for_error(response)
            return response
        raise AssertionError("unreachable")

    def stream(self, request: Request) -> Iterator[Event]:
        kwargs = self._prepare_stream(request)
        try:
            with self.http.stream(**kwargs) as response:
                if response.status_code >= 400:
                    response.read()
                    _raise_for_error(response)
                yield from parse_sse(response.iter_lines())
        except httpx.TransportError as exc:
            raise _connection_error(exc) from exc

    def close(self) -> None:
        if self._owns_client:
            self.http.close()


class AsyncTransport(_Base):
    def __init__(
        self,
        api_key: str,
        base_url: str,
        timeout: float,
        max_retries: int,
        http_client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        super().__init__(api_key, base_url, max_retries)
        self._owns_client = http_client is None
        self.http = http_client or httpx.AsyncClient(timeout=timeout)

    async def send(self, request: Request) -> httpx.Response:
        kwargs = self._prepare(request)
        for attempt in range(self.max_retries + 1):
            try:
                response = await self.http.request(**kwargs)
            except httpx.TransportError as exc:
                if attempt < self.max_retries and _may_retry(request):
                    await asyncio.sleep(_delay(attempt, None))
                    continue
                raise _connection_error(exc) from exc
            if attempt < self.max_retries and _is_retryable(request, response):
                await asyncio.sleep(_delay(attempt, _retry_after(response)))
                continue
            if not _gone_after_retry(request, response, attempt):
                _raise_for_error(response)
            return response
        raise AssertionError("unreachable")

    async def stream(self, request: Request) -> AsyncIterator[Event]:
        kwargs = self._prepare_stream(request)
        try:
            async with self.http.stream(**kwargs) as response:
                if response.status_code >= 400:
                    await response.aread()
                    _raise_for_error(response)
                async for event in _aparse_sse(response.aiter_lines()):
                    yield event
        except httpx.TransportError as exc:
            raise _connection_error(exc) from exc

    async def aclose(self) -> None:
        if self._owns_client:
            await self.http.aclose()


__all__ = [
    "DEFAULT_BASE_URL",
    "NO_READ_TIMEOUT",
    "AsyncTransport",
    "Event",
    "Request",
    "SyncTransport",
    "parse_sse",
    "resolve_api_key",
    "resolve_base_url",
]
