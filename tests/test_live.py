"""Runs against the real API. Needs STYNE_API_KEY (a test account); skipped otherwise."""

from __future__ import annotations

import asyncio
import json
import os
import uuid
from typing import Iterator

import pytest

import styne

pytestmark = [
    pytest.mark.live,
    pytest.mark.skipif(not os.environ.get("STYNE_API_KEY"), reason="STYNE_API_KEY not set"),
]


@pytest.fixture(scope="module")
def client() -> Iterator[styne.Client]:
    with styne.Client() as c:
        yield c


@pytest.fixture()
def vm(client: styne.Client) -> Iterator[styne.Vm]:
    with client.vms.create(size="small", timeout_seconds=300) as created:
        yield created


def test_run_and_stream(vm: styne.Vm) -> None:
    result = vm.run("echo hello").check()
    assert result.stdout.strip() == "hello"
    assert vm.run("exit 3").exit_code == 3
    events = list(vm.stream("echo out; echo err >&2"))
    assert [e.type for e in events if e.type != "stdout" and e.type != "stderr"] == ["started", "exit"]
    assert "".join(e.data for e in events if e.type == "stdout") == "out\n"
    assert "".join(e.data for e in events if e.type == "stderr") == "err\n"
    assert events[-1].exit_code == 0


def test_files(vm: styne.Vm) -> None:
    vm.files.write("/tmp/live/a.txt", "data")
    vm.files.write("/tmp/live/b.bin", bytes(range(256)))
    assert vm.files.read_text("/tmp/live/a.txt") == "data"
    assert vm.files.read("/tmp/live/b.bin") == bytes(range(256))
    assert sorted(e.name for e in vm.files.list("/tmp/live")) == ["a.txt", "b.bin"]
    vm.files.delete("/tmp/live/a.txt")
    assert [e.name for e in vm.files.list("/tmp/live")] == ["b.bin"]


def test_ports(vm: styne.Vm) -> None:
    port = vm.ports.expose(8080)
    assert str(port.url).startswith("https://8080-")
    assert [p.port for p in vm.ports.list()] == [8080]
    vm.ports.hide(8080)
    assert vm.ports.list() == []


def test_snapshot_and_fork(client: styne.Client, vm: styne.Vm) -> None:
    vm.files.write("/root/marker", "kept")
    snapshot = vm.snapshot("live-test")
    snapshot_id = str(snapshot.id)
    try:
        assert snapshot_id in [s.id for s in client.snapshots.list()]
        with client.snapshots.start(snapshot_id) as restored:
            assert restored.files.read_text("/root/marker") == "kept"
    finally:
        client.snapshots.delete(snapshot_id)
    forks = vm.fork(1)
    try:
        assert len(forks) == 1
        assert forks[0].run("cat /root/marker").stdout == "kept"
    finally:
        for fork in forks:
            fork.kill()


def test_pause_and_resume(vm: styne.Vm) -> None:
    vm.run("echo persisted > /root/state")
    assert vm.pause().state == "paused"
    assert vm.resume().state == "running"
    assert vm.run("cat /root/state").stdout.strip() == "persisted"


def test_browser_cdp_and_takeover(client: styne.Client) -> None:
    websockets = pytest.importorskip("websockets.sync.client")
    with client.browsers.create(timeout_seconds=300) as browser:
        assert browser.cdp_url.startswith("wss://")
        with websockets.connect(browser.cdp_url, open_timeout=30) as ws:
            ws.send(json.dumps({"id": 1, "method": "Browser.getVersion"}))
            reply = json.loads(ws.recv(timeout=30))
        assert "product" in reply["result"]
        link = browser.take_control("live-test")
        assert link.cdp_url.startswith("wss://")
        browser.give_back_control()


def test_regions(client: styne.Client) -> None:
    assert client.regions.list()


def test_not_found_is_typed(client: styne.Client) -> None:
    with pytest.raises(styne.NotFoundError) as info:
        client.vms.get("vm_does_not_exist")
    assert info.value.request_id


def test_bad_key_is_typed() -> None:
    with styne.Client(api_key="sk_invalid", max_retries=0) as bad, pytest.raises(styne.AuthenticationError):
        list(bad.vms.list())


def test_idempotent_create_replays(client: styne.Client) -> None:
    key = f"live-test-{uuid.uuid4()}"
    first = client._transport.send(_create(key)).json()
    try:
        second = client._transport.send(_create(key)).json()
        assert second["id"] == first["id"]
    finally:
        client.vms.get(first["id"]).kill()


def _create(key: str) -> styne._transport.Request:
    from styne._transport import Request

    return Request(
        "POST",
        "/vms",
        json={"template": "small", "timeout_seconds": 120},
        headers={"Idempotency-Key": key},
        idempotent=True,
    )


def test_async_client() -> None:
    async def go() -> str:
        async with styne.AsyncClient() as c, await c.vms.create(size="small", timeout_seconds=300) as vm:
            return (await vm.run("echo async")).stdout.strip()

    assert asyncio.run(go()) == "async"
