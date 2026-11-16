from __future__ import annotations

import asyncio
import base64
from typing import Any, Dict, List

import httpx
import pytest
from conftest import VM, make_async_client, make_client

import styne


def test_create_run_and_exit_deletes_vm() -> None:
    def handler(req: httpx.Request) -> httpx.Response:
        if req.method == "POST" and req.url.path == "/v1/vms":
            return httpx.Response(201, json=VM)
        if req.url.path == "/v1/vms/vm_1/commands":
            return httpx.Response(200, json={"id": "c1", "state": "exited", "exit_code": 3, "stdout": "hi\n"})
        return httpx.Response(204)

    client, rec = make_client(handler)
    with client.vms.create(template="base", size="small") as vm:
        result = vm.run("echo hi")
        assert (result.stdout, result.exit_code, result.ok) == ("hi\n", 3, False)
        with pytest.raises(styne.CommandError):
            result.check()
    assert rec.requests[0].headers["Authorization"] == "Bearer k"
    assert rec.requests[0].headers["User-Agent"].startswith("styne-python/")
    assert str(rec.requests[0].url) == "https://api.test/v1/vms"
    assert rec.requests[0].headers["Idempotency-Key"]
    assert "Idempotency-Key" not in rec.requests[1].headers
    assert rec.body(0) == {"template": "base", "size": "small"}
    assert rec.body(1) == {"cmd": "sh", "args": ["-c", "echo hi"]}
    assert (rec.requests[-1].method, rec.requests[-1].url.path) == ("DELETE", "/v1/vms/vm_1")


def test_run_list_form_and_options() -> None:
    client, rec = make_client(lambda r: httpx.Response(200, json={"id": "c", "state": "exited", "exit_code": 0}))
    vm = styne.Vm(client._transport, dict(VM))
    vm.run(["ls", "-l"], cwd="/tmp", env={"A": "1"}, timeout=5)
    assert rec.body() == {"cmd": "ls", "args": ["-l"], "cwd": "/tmp", "env": {"A": "1"}, "timeout_seconds": 5}
    assert "Idempotency-Key" not in rec.requests[0].headers


def test_files_ports_snapshot_fork() -> None:
    def handler(req: httpx.Request) -> httpx.Response:
        path = req.url.path
        if path.endswith("/files") and req.method == "GET":
            return httpx.Response(200, content=b"data")
        if path.endswith("/files/list"):
            return httpx.Response(200, json={"data": [{"name": "a"}]})
        if path.endswith("/ports") and req.method == "POST":
            return httpx.Response(201, json={"port": 8080, "url": "https://p", "public": True})
        if path.endswith("/snapshots"):
            return httpx.Response(201, json={"id": "snap_1", "name": "s"})
        if path.endswith("/fork"):
            return httpx.Response(201, json={"data": [VM, {**VM, "id": "vm_2"}]})
        if path.endswith(("/pause", "/resume")):
            return httpx.Response(200, json=VM)
        return httpx.Response(204)

    client, rec = make_client(handler)
    vm = styne.Vm(client._transport, dict(VM))
    assert vm.files.read("/etc/hostname") == b"data"
    assert rec.requests[-1].url.params["path"] == "/etc/hostname"
    vm.files.write("/a.txt", "hello")
    assert rec.requests[-1].content == b"hello"
    assert vm.files.list("/")[0].name == "a"
    assert vm.ports.expose(8080, public=True).url == "https://p"
    assert vm.snapshot("s").id == "snap_1"
    assert [v.id for v in vm.fork(2)] == ["vm_1", "vm_2"]
    vm.pause()
    vm.resume()


def test_browser_cdp_and_control() -> None:
    def handler(req: httpx.Request) -> httpx.Response:
        if req.method == "POST" and req.url.path == "/v1/browsers":
            return httpx.Response(201, json={"id": "br_1", "state": "running", "cdp_url": "wss://cdp/x"})
        return httpx.Response(200, json={"cdp_url": "wss://cdp/c", "control_id": "c1", "holder": "alice"})

    client, rec = make_client(handler)
    with client.browsers.create(viewport={"width": 1280, "height": 720}) as browser:
        assert browser.cdp_url == "wss://cdp/x"
        assert browser.live_view_url is None
        control = browser.take_control("alice")
        assert (control.cdp_url, control.control_id, control.holder) == ("wss://cdp/c", "c1", "alice")
    assert rec.body(1) == {"holder": "alice"}
    assert rec.requests[-1].method == "DELETE"


def test_pagination_follows_cursor() -> None:
    def handler(req: httpx.Request) -> httpx.Response:
        if req.url.params.get("cursor") == "c2":
            return httpx.Response(200, json={"data": [{**VM, "id": "vm_2"}], "next_cursor": None, "has_more": False})
        return httpx.Response(200, json={"data": [VM], "next_cursor": "c2", "has_more": True})

    client, _ = make_client(handler)
    assert [v.id for v in client.vms.list(page_size=1)] == ["vm_1", "vm_2"]


def test_stream_yields_events() -> None:
    sse = (
        'event: started\ndata: {"pid": 7}\n\n'
        'event: stdout\ndata: {"data": "YQo="}\n\n'
        'event: exit\ndata: {"exit_code": 0}\n\n'
    )
    client, rec = make_client(lambda r: httpx.Response(200, text=sse, headers={"Content-Type": "text/event-stream"}))
    vm = styne.Vm(client._transport, dict(VM))
    events = list(vm.stream("echo a"))
    assert [(e.type, e.data) for e in events] == [
        ("started", '{"pid": 7}'),
        ("stdout", "a\n"),
        ("exit", '{"exit_code": 0}'),
    ]
    assert events[2].exit_code == 0
    assert rec.requests[0].headers["Accept"] == "text/event-stream"
    assert rec.body()["stream"] is True


def test_missing_key_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("STYNE_API_KEY", raising=False)
    with pytest.raises(styne.StyneError, match="missing API key"):
        styne.Client()


def test_env_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("STYNE_API_KEY", "from-env")
    client = styne.Client()
    assert client._transport._headers["Authorization"] == "Bearer from-env"
    client.close()


def test_async_flow() -> None:
    def handler(req: httpx.Request) -> httpx.Response:
        if req.method == "POST" and req.url.path == "/v1/vms":
            return httpx.Response(201, json=VM)
        if req.url.path.endswith("/commands"):
            return httpx.Response(200, json={"id": "c", "state": "exited", "exit_code": 0, "stdout": "ok"})
        if req.url.path.endswith("/files"):
            return httpx.Response(200, content=b"txt")
        return httpx.Response(204)

    async def main() -> None:
        client, rec = make_async_client(handler)
        async with client, await client.vms.create() as vm:
            assert (await vm.run("true")).stdout == "ok"
            assert await vm.files.read_text("/x") == "txt"
        assert rec.requests[-1].method == "DELETE"

    asyncio.run(main())


def test_stream_keeps_a_split_character_whole_and_reads_exit_fields() -> None:
    first, second = base64.b64encode("é".encode()[:1]).decode(), base64.b64encode("é".encode()[1:]).decode()
    sse = (
        f'event: stdout\ndata: {{"data": "{first}"}}\n\n'
        f'event: stdout\ndata: {{"data": "{second}"}}\n\n'
        'event: exit\ndata: {"exit_code": null, "signal": 9, "timed_out": false}\n\n'
    )
    client, _ = make_client(lambda r: httpx.Response(200, text=sse, headers={"Content-Type": "text/event-stream"}))
    vm = styne.Vm(client._transport, dict(VM))
    events = list(vm.stream("printf é"))
    assert "".join(e.data for e in events if e.type == "stdout") == "é"
    assert (events[-1].exit_code, events[-1].signal, events[-1].timed_out) == (None, 9, False)


def test_stream_error_event_raises_typed_error() -> None:
    sse = 'event: error\ndata: {"error": {"code": "vm_ended", "status": 410, "message": "gone"}}\n\n'
    client, _ = make_client(lambda r: httpx.Response(200, text=sse, headers={"Content-Type": "text/event-stream"}))
    vm = styne.Vm(client._transport, dict(VM))
    with pytest.raises(styne.VmEndedError):
        list(vm.stream("x"))


def test_run_without_timeout_has_no_read_deadline() -> None:
    seen: List[Dict[str, Any]] = []

    def handler(req: httpx.Request) -> httpx.Response:
        seen.append(req.extensions["timeout"])
        return httpx.Response(200, json={"id": "c", "state": "exited", "exit_code": 0})

    client, _ = make_client(handler)
    vm = styne.Vm(client._transport, dict(VM))
    vm.run("sleep 90")
    vm.run("sleep 1", timeout=0.5)
    assert seen[0]["read"] is None
    assert seen[1]["read"] == 16.0


def test_run_input_checks() -> None:
    client, _ = make_client(lambda r: httpx.Response(200, json={}))
    vm = styne.Vm(client._transport, dict(VM))
    with pytest.raises(ValueError, match="empty"):
        vm.run([])
    with pytest.raises(ValueError, match="positive"):
        vm.run("x", timeout=0)


def test_path_segments_are_escaped() -> None:
    client, rec = make_client(lambda r: httpx.Response(200, json=VM))
    client.vms.get("a/b")
    assert rec.requests[0].url.raw_path == b"/v1/vms/a%2Fb"


def test_checkpoints_rewind_extend_templates_usage() -> None:
    def handler(req: httpx.Request) -> httpx.Response:
        path = req.url.path
        if path.endswith("/checkpoints") and req.method == "POST":
            return httpx.Response(201, json={"id": "ck_1", "label": "before"})
        if path.endswith("/checkpoints"):
            return httpx.Response(200, json={"data": [{"id": "ck_1"}]})
        if path == "/v1/templates":
            return httpx.Response(200, json={"data": [{"id": "base"}], "has_more": False})
        if path == "/v1/usage":
            return httpx.Response(200, json={"total": 1})
        return httpx.Response(200, json={**VM, "state": "paused"})

    client, rec = make_client(handler)
    vm = styne.Vm(client._transport, dict(VM))
    checkpoint = vm.checkpoints.create("before")
    assert rec.requests[-1].headers["Idempotency-Key"]
    assert [c.id for c in vm.checkpoints.list()] == ["ck_1"]
    assert vm.rewind(checkpoint).state == "paused"
    assert rec.body() == {"checkpoint": "ck_1"}
    vm.extend(60)
    assert rec.body() == {"seconds": 60}
    assert [t.id for t in client.templates.list()] == ["base"]
    assert client.usage() == {"total": 1}


def test_exit_keeps_the_original_exception() -> None:
    client, _ = make_client(lambda r: httpx.Response(500, json={"error": {"code": "x", "status": 500, "message": "m"}}))
    vm = styne.Vm(client._transport, dict(VM))
    with pytest.raises(KeyError), vm:
        raise KeyError("original")


def test_refuses_plain_http_base_url() -> None:
    with pytest.raises(styne.StyneError, match="https"):
        styne.Client("k", base_url="http://api.example.com/v1")
    styne.Client("k", base_url="http://localhost:8080/v1").close()
