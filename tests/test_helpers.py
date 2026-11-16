from __future__ import annotations

import pytest

import styne
from styne import _ops, _transport, aclient, client, errors, types


def test_ops_run_body_string_and_list() -> None:
    body = _ops.run_body("ls -l", cwd=None, env=None, user=None, stdin=None, timeout=None)
    assert body == {"cmd": "sh", "args": ["-c", "ls -l"]}
    body = _ops.run_body(["echo"], cwd="/w", env=None, user="u", stdin="in", timeout=2.5, detach=True)
    assert body == {"cmd": "echo", "cwd": "/w", "user": "u", "stdin": "in", "timeout_seconds": 3, "detach": True}


def test_ops_requests() -> None:
    assert _ops.create_vm({"size": "s", "region": None}).json == {"size": "s"}
    assert _ops.create_browser({}).idempotent
    assert _ops.list_request("/vms", 5, None).params == {"limit": 5, "cursor": None}
    assert _ops.file_request("PUT", "vm_1", "/a", b"x").content == b"x"
    assert _ops.as_bytes("é") == "é".encode()
    assert _ops.run_request({"timeout_seconds": 10}, "vm_1").timeout == 25
    assert _ops.run_request({}, "vm_1").timeout is _transport.NO_READ_TIMEOUT
    assert not _ops.run_request({}, "vm_1").idempotent


def test_sse_parser_handles_comments_ids_and_multiline_data() -> None:
    lines = [": ping", "id: 7", "event: stdout", "data: a", "data: b", "", "data: tail"]
    events = list(_transport.parse_sse(iter(lines)))
    assert [(e.event, e.data, e.id) for e in events] == [("stdout", "a\nb", "7"), ("message", "tail", "7")]


def test_transport_helpers() -> None:
    assert _transport._clean({"a": True, "b": None, "c": 1}) == {"a": "true", "c": 1}
    assert _transport.resolve_api_key("k") == "k"
    assert _transport._delay(0, 3.0) == 3.0
    assert 0 <= _transport._delay(5, None) <= 8.0


def test_error_helpers() -> None:
    err = errors.error_from_payload(500, "not json", request_id="r")
    assert isinstance(err, errors.ServerError)
    assert (err.code, err.request_id) == ("unknown", "r")
    assert isinstance(errors.error_from_payload(409, {}), errors.ConflictError)
    assert issubclass(errors.APITimeoutError, errors.APIConnectionError)
    assert issubclass(errors.PlanRequiredError, errors.PaymentRequiredError)
    assert issubclass(errors.LimitConcurrentError, errors.RateLimitError)


def test_stream_decoder_and_command_result() -> None:
    decoder = types.StreamDecoder()
    assert decoder.event("exit", "not json")[0].exit_code is None
    assert decoder.event("stdout", "raw text")[0].data == "raw text"
    result = types.CommandResult.from_dict({"id": "c", "state": "exited", "exit_code": 1, "stderr": "bad"})
    with pytest.raises(errors.CommandError, match="bad"):
        result.check()


def test_sync_and_async_clients_expose_the_same_methods() -> None:
    sync = client.Client("k")
    asyn = aclient.AsyncClient("k")
    for name in ("vms", "snapshots", "browsers", "regions", "templates"):
        assert type(getattr(asyn, name)).__name__ == "Async" + type(getattr(sync, name)).__name__
    for sync_cls, async_cls in [
        (styne.Vm, styne.AsyncVm),
        (styne.Browser, styne.AsyncBrowser),
        (styne.Files, styne.AsyncFiles),
        (styne.Ports, styne.AsyncPorts),
        (styne.Checkpoints, styne.AsyncCheckpoints),
    ]:
        public = {n for n in vars(sync_cls) if not n.startswith("_")}
        assert public == {n for n in vars(async_cls) if not n.startswith("_")}
    sync.close()


def test_region_resolution_precedence(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("STYNE_BASE_URL", raising=False)
    monkeypatch.delenv("STYNE_REGION", raising=False)
    assert _transport.resolve_base_url(None) == "https://ash.api.styne.ai/v1"
    monkeypatch.setenv("STYNE_REGION", "ams")
    assert _transport.resolve_base_url(None) == "https://ams.api.styne.ai/v1"
    assert _transport.resolve_base_url(None, "ash") == "https://ash.api.styne.ai/v1"
    assert _transport.resolve_base_url(None, "eu") == "https://ams.api.styne.ai/v1"
    assert _transport.resolve_base_url(None, "us-east") == "https://ash.api.styne.ai/v1"
    monkeypatch.setenv("STYNE_BASE_URL", "https://api.styne.ai/v1/")
    assert _transport.resolve_base_url(None, "ams") == "https://api.styne.ai/v1"
    assert _transport.resolve_base_url("https://x.example.com", "ams") == "https://x.example.com"


def test_region_unknown_lists_choices() -> None:
    with pytest.raises(errors.StyneError, match="ash, ams"):
        _transport.resolve_base_url(None, "mars")


def test_client_region_option(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("STYNE_BASE_URL", raising=False)
    monkeypatch.delenv("STYNE_REGION", raising=False)
    with client.Client("k", region="ams") as c:
        assert c._transport._base == "https://ams.api.styne.ai/v1"
    with client.Client("k") as c:
        assert c._transport._base == "https://ash.api.styne.ai/v1"


def test_chosen_region_is_the_default_of_a_create(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("STYNE_BASE_URL", raising=False)
    monkeypatch.delenv("STYNE_REGION", raising=False)
    with client.Client("k") as c:
        assert c._transport.region is None
    with client.Client("k", region="eu") as c:
        assert c._transport.region == "ams"
    monkeypatch.setenv("STYNE_REGION", "us-east")
    with client.Client("k") as c:
        assert c._transport.region == "ash"
        assert c.browsers._t.region == "ash"


@pytest.mark.parametrize(
    ("alias", "region"),
    [("us-east", "ash"), ("ASHBURN", "ash"), (" eu ", "ams"), ("eu-central", "ams"), ("ams", "ams")],
)
def test_region_aliases_match_the_api(alias: str, region: str) -> None:
    assert _transport.region_name(alias) == region


def test_snapshot_create_keeps_the_snapshot_region() -> None:
    import json

    import httpx
    from conftest import make_async_client, make_client

    def handle(request: httpx.Request) -> httpx.Response:
        return httpx.Response(201, json={"id": "vm_1", "state": "running"})

    c, rec = make_client(handle)
    c._transport.region = "ams"
    c.vms.create(snapshot="snap_1")
    c.vms.create(template="small")
    c.vms.create(snapshot="snap_1", region="ash")
    assert [json.loads(r.content).get("region") for r in rec.requests] == [None, "ams", "ash"]

    ac, arec = make_async_client(handle)
    ac._transport.region = "ams"

    async def go() -> None:
        await ac.vms.create(snapshot="snap_1")
        await ac.vms.create(template="small")

    import asyncio

    asyncio.run(go())
    assert [json.loads(r.content).get("region") for r in arec.requests] == [None, "ams"]


def test_https_error_does_not_echo_credentials() -> None:
    with pytest.raises(errors.StyneError) as excinfo:
        _transport.resolve_base_url("http://user:secret@example.com/v1?token=abc")
    assert "secret" not in str(excinfo.value)
    assert "token" not in str(excinfo.value)
    assert "example.com" in str(excinfo.value)
