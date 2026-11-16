from __future__ import annotations

import asyncio
from typing import List

import httpx
import pytest
from conftest import VM, envelope, make_async_client, make_client

import styne


@pytest.mark.parametrize(
    ("status", "code", "cls"),
    [
        (401, "unauthenticated", styne.AuthenticationError),
        (402, "payment_required", styne.PaymentRequiredError),
        (402, "plan_required", styne.PlanRequiredError),
        (403, "permission_denied", styne.PermissionDeniedError),
        (404, "not_found", styne.NotFoundError),
        (422, "idempotency_mismatch", styne.IdempotencyMismatchError),
        (429, "limit_concurrent", styne.LimitConcurrentError),
        (400, "invalid_request", styne.InvalidArgumentError),
        (410, "vm_ended", styne.VmEndedError),
        (418, "teapot", styne.APIError),
    ],
)
def test_error_envelope_maps_to_typed_error(status: int, code: str, cls: type) -> None:
    client, _ = make_client(lambda r: envelope(status, code, details={"limit": 5}, doc_url="x"))
    with pytest.raises(cls) as info:
        client.vms.get("vm_1")
    err = info.value
    assert isinstance(err, styne.APIError)
    assert (err.status, err.code, err.request_id, err.details) == (status, code, "req_9", {"limit": 5})
    assert "req_9" in str(err)


def test_error_body_without_envelope_maps_by_status() -> None:
    client, _ = make_client(
        lambda r: httpx.Response(404, json={"code": 404, "message": "gone", "error_code": "not_found"})
    )
    with pytest.raises(styne.NotFoundError, match="gone"):
        client.vms.get("vm_1")


def test_retries_429_with_retry_after_and_stable_idempotency_key(no_sleep: List[float]) -> None:
    calls = {"n": 0}

    def handler(req: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        if calls["n"] < 3:
            return httpx.Response(429, json={"error": {"code": "rate_limited"}}, headers={"Retry-After": "2"})
        return httpx.Response(201, json=VM)

    client, rec = make_client(handler)
    assert client.vms.create().id == "vm_1"
    assert no_sleep == [2.0, 2.0]
    keys = {r.headers["Idempotency-Key"] for r in rec.requests}
    assert len(rec.requests) == 3
    assert len(keys) == 1


def test_gives_up_after_max_retries() -> None:
    client, rec = make_client(lambda r: envelope(503, "unavailable"))
    with pytest.raises(styne.ServerError):
        client.vms.get("vm_1")
    assert len(rec.requests) == 3


def test_post_without_idempotency_is_not_retried() -> None:
    client, rec = make_client(lambda r: envelope(503, "unavailable"))
    vm = styne.Vm(client._transport, dict(VM))
    with pytest.raises(styne.ServerError):
        vm.run("true")
    assert len(rec.requests) == 1


def test_409_retried_only_when_in_flight() -> None:
    answers = iter([httpx.Response(409, headers={"Retry-After": "1"}, json={}), httpx.Response(201, json=VM)])
    client, rec = make_client(lambda r: next(answers))
    client.vms.create()
    assert len(rec.requests) == 2
    client2, rec2 = make_client(lambda r: envelope(409, "conflict"))
    with pytest.raises(styne.ConflictError):
        client2.vms.create()
    assert len(rec2.requests) == 1


def test_network_failure_becomes_api_connection_error() -> None:
    def boom(req: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("refused")

    client, rec = make_client(boom)
    with pytest.raises(styne.APIConnectionError):
        client.vms.get("vm_1")
    assert len(rec.requests) == 3


def test_stream_error_frame_raises() -> None:
    sse = 'event: error\ndata: {"error": {"code": "limit_concurrent", "status": 429, "message": "full"}}\n\n'
    client, _ = make_client(lambda r: httpx.Response(200, text=sse))
    vm = styne.Vm(client._transport, dict(VM))
    with pytest.raises(styne.LimitConcurrentError):
        list(vm.stream("x"))


def test_async_retry_and_error(no_sleep: List[float]) -> None:
    answers = iter([envelope(503, "unavailable"), envelope(404, "not_found")])
    client, rec = make_async_client(lambda r: next(answers))

    async def main() -> None:
        with pytest.raises(styne.NotFoundError):
            await client.vms.get("vm_1")
        assert len(rec.requests) == 2
        assert len(no_sleep) == 1

    asyncio.run(main())


def test_command_is_sent_once_on_a_network_error() -> None:
    def boom(req: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("slow")

    client, rec = make_client(boom)
    vm = styne.Vm(client._transport, dict(VM))
    with pytest.raises(styne.APITimeoutError):
        vm.run("make")
    assert len(rec.requests) == 1


def test_retried_delete_answering_404_is_success() -> None:
    answers = iter([envelope(502, "upstream_error"), envelope(404, "not_found")])
    client, rec = make_client(lambda r: next(answers))
    styne.Vm(client._transport, dict(VM)).kill()
    assert len(rec.requests) == 2


def test_custom_http_client_still_gets_key_and_url() -> None:
    seen: List[httpx.Request] = []

    def handler(req: httpx.Request) -> httpx.Response:
        seen.append(req)
        return httpx.Response(200, json=VM)

    http = httpx.Client(transport=httpx.MockTransport(handler))
    styne.Client("secret", base_url="https://api.test/v1", http_client=http).vms.get("vm_1")
    assert str(seen[0].url) == "https://api.test/v1/vms/vm_1"
    assert seen[0].headers["Authorization"] == "Bearer secret"
    assert seen[0].headers["User-Agent"].startswith("styne-python/")
