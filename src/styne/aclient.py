"""Asynchronous client; the same surface as :mod:`styne.client` with ``Async`` class names and awaitable methods."""

from __future__ import annotations

import contextlib
from types import TracebackType
from typing import Any, AsyncIterator, Dict, List, Mapping, Optional, Type, Union

import httpx

from . import _ops
from ._ops import seg
from ._transport import (
    DEFAULT_MAX_RETRIES,
    DEFAULT_TIMEOUT,
    AsyncTransport,
    Request,
    resolve_api_key,
    resolve_base_url,
)
from .errors import NotFoundError, StyneError
from .models import BrowserInfo, Checkpoint, Port, Region, Snapshot, Template, VmInfo
from .types import CommandResult, Control, FileEntry, StreamDecoder, StreamEvent

Command = _ops.Command


class _AsyncResource:
    def __init__(self, transport: AsyncTransport) -> None:
        self._t = transport

    async def _json(self, request: Request) -> Dict[str, Any]:
        body: Dict[str, Any] = (await self._t.send(request)).json()
        return body

    async def _rows(self, request: Request) -> List[Dict[str, Any]]:
        return list((await self._json(request)).get("data", []))

    async def _pages(self, path: str, page_size: Optional[int]) -> AsyncIterator[Dict[str, Any]]:
        cursor: Optional[str] = None
        while True:
            page = await self._json(_ops.list_request(path, page_size, cursor))
            for item in page.get("data", []):
                yield item
            cursor = page.get("next_cursor")
            if not (page.get("has_more") and cursor):
                return


class AsyncFiles(_AsyncResource):
    """Files inside a VM."""

    def __init__(self, transport: AsyncTransport, vm_id: str) -> None:
        super().__init__(transport)
        self._vm = vm_id

    async def read(self, path: str) -> bytes:
        """Return the content of a file."""
        return (await self._t.send(_ops.file_request("GET", self._vm, path))).content

    async def read_text(self, path: str) -> str:
        """Return the content of a UTF-8 text file."""
        return (await self.read(path)).decode("utf-8")

    async def write(self, path: str, data: Union[str, bytes]) -> None:
        """Create or replace a file; ``str`` data is written as UTF-8."""
        await self._t.send(_ops.file_request("PUT", self._vm, path, _ops.as_bytes(data)))

    async def delete(self, path: str) -> None:
        """Delete a file."""
        await self._t.send(_ops.file_request("DELETE", self._vm, path))

    async def list(self, path: str = "/") -> List[FileEntry]:
        """List the entries of a directory."""
        rows = await self._rows(Request("GET", f"/vms/{seg(self._vm)}/files/list", params={"path": path}))
        return [FileEntry.from_dict(row) for row in rows]


class AsyncPorts(_AsyncResource):
    """Ports a VM serves to the internet."""

    def __init__(self, transport: AsyncTransport, vm_id: str) -> None:
        super().__init__(transport)
        self._vm = vm_id

    async def expose(self, port: int, *, public: Optional[bool] = None) -> Port:
        """Serve a port of the VM at a public URL; ``public=True`` drops the traffic token."""
        body = _ops.drop_none({"port": port, "public": public})
        return Port.from_dict(await self._json(Request("POST", f"/vms/{seg(self._vm)}/ports", json=body)))

    async def list(self) -> List[Port]:
        """Return the exposed ports."""
        return [Port.from_dict(p) for p in await self._rows(Request("GET", f"/vms/{seg(self._vm)}/ports"))]

    async def hide(self, port: int) -> None:
        """Stop serving a port."""
        await self._t.send(Request("DELETE", f"/vms/{seg(self._vm)}/ports/{seg(port)}"))


class AsyncCheckpoints(_AsyncResource):
    """Checkpoints of a VM; :meth:`AsyncVm.rewind` returns to one."""

    def __init__(self, transport: AsyncTransport, vm_id: str) -> None:
        super().__init__(transport)
        self._vm = vm_id

    async def create(self, label: Optional[str] = None) -> Checkpoint:
        """Record the VM's current state as a checkpoint."""
        body = _ops.drop_none({"label": label})
        request = Request("POST", f"/vms/{seg(self._vm)}/checkpoints", json=body, idempotent=True)
        return Checkpoint.from_dict(await self._json(request))

    async def list(self) -> List[Checkpoint]:
        """Return the VM's checkpoints."""
        rows = await self._rows(Request("GET", f"/vms/{seg(self._vm)}/checkpoints"))
        return [Checkpoint.from_dict(c) for c in rows]


class AsyncVm(_AsyncResource):
    """A running or paused virtual machine. Use it with ``async with`` to delete it on exit."""

    def __init__(self, transport: AsyncTransport, data: Dict[str, Any]) -> None:
        super().__init__(transport)
        self._data = data
        self.files = AsyncFiles(transport, self.id)
        self.ports = AsyncPorts(transport, self.id)
        self.checkpoints = AsyncCheckpoints(transport, self.id)

    @property
    def id(self) -> str:
        return str(self._data["id"])

    @property
    def state(self) -> str:
        return str(self._data.get("state", ""))

    @property
    def info(self) -> VmInfo:
        """The full typed record as last seen."""
        return VmInfo.from_dict(self._data)

    def _path(self, suffix: str = "") -> str:
        return f"/vms/{seg(self.id)}{suffix}"

    async def _update(self, request: Request) -> AsyncVm:
        self._data = await self._json(request)
        return self

    async def refresh(self) -> AsyncVm:
        """Reload the record from the API."""
        return await self._update(Request("GET", self._path()))

    async def run(
        self,
        command: Command,
        *,
        cwd: Optional[str] = None,
        env: Optional[Mapping[str, str]] = None,
        user: Optional[str] = None,
        stdin: Optional[str] = None,
        timeout: Optional[float] = None,
        detach: bool = False,
    ) -> CommandResult:
        """Run a command to exit and return its output and exit code.

        A string runs through ``sh -c``; a list is executed directly. ``timeout`` (seconds) kills the command;
        without it the call waits as long as the command runs. A command is sent once and never retried.
        """
        body = _ops.run_body(command, cwd=cwd, env=env, user=user, stdin=stdin, timeout=timeout, detach=detach)
        return CommandResult.from_dict(await self._json(_ops.run_request(body, self.id)))

    async def stream(
        self,
        command: Command,
        *,
        cwd: Optional[str] = None,
        env: Optional[Mapping[str, str]] = None,
        user: Optional[str] = None,
        stdin: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> AsyncIterator[StreamEvent]:
        """Run a command and yield its output as it arrives; raises the matching error on a server error event."""
        body = _ops.run_body(command, cwd=cwd, env=env, user=user, stdin=stdin, timeout=timeout, stream=True)
        decoder = StreamDecoder()
        async for event in self._t.stream(_ops.run_request(body, self.id)):
            if event.event == "error":
                raise _ops.stream_error(event.json())
            for item in decoder.event(event.event, event.data):
                yield item

    async def pause(self, tier: Optional[str] = None) -> AsyncVm:
        """Pause the VM; ``tier`` is ``hot``, ``standby`` or ``archived`` (server default when omitted)."""
        return await self._update(Request("POST", self._path("/pause"), json=_ops.drop_none({"tier": tier})))

    async def resume(self) -> AsyncVm:
        """Resume a paused VM."""
        return await self._update(Request("POST", self._path("/resume")))

    async def extend(self, seconds: int) -> AsyncVm:
        """Extend the VM's lifetime by ``seconds``."""
        return await self._update(Request("POST", self._path("/extend"), json={"seconds": seconds}))

    async def fork(self, count: int = 1) -> List[AsyncVm]:
        """Create ``count`` copies of this VM from its current state."""
        rows = await self._rows(Request("POST", self._path("/fork"), json={"count": count}, idempotent=True))
        return [AsyncVm(self._t, item) for item in rows]

    async def snapshot(self, name: Optional[str] = None) -> Snapshot:
        """Save the VM's state as a snapshot that new VMs can start from."""
        body = _ops.drop_none({"name": name})
        request = Request("POST", self._path("/snapshots"), json=body, idempotent=True)
        return Snapshot.from_dict(await self._json(request))

    async def rewind(self, checkpoint: Union[str, Checkpoint]) -> AsyncVm:
        """Return the VM to a checkpoint (id or object)."""
        checkpoint_id = checkpoint if isinstance(checkpoint, str) else str(checkpoint.id)
        return await self._update(Request("POST", self._path("/rewind"), json={"checkpoint": checkpoint_id}))

    async def kill(self) -> None:
        """Delete the VM."""
        await self._t.send(Request("DELETE", self._path()))

    async def __aenter__(self) -> AsyncVm:
        return self

    async def __aexit__(
        self, exc_type: Optional[Type[BaseException]], exc: Optional[BaseException], tb: Optional[TracebackType]
    ) -> None:
        with contextlib.suppress(StyneError if exc is not None else NotFoundError):
            await self.kill()

    def __repr__(self) -> str:
        return f"AsyncVm(id={self.id!r}, state={self.state!r})"


class AsyncVms(_AsyncResource):
    """Create, find and list VMs."""

    async def create(
        self,
        *,
        template: Optional[str] = None,
        snapshot: Optional[str] = None,
        size: Optional[str] = None,
        vcpus: Optional[int] = None,
        memory_mib: Optional[int] = None,
        region: Optional[str] = None,
        timeout_seconds: Optional[int] = None,
        auto_pause: Optional[bool] = None,
        auto_resume: Optional[bool] = None,
        env: Optional[Mapping[str, str]] = None,
        secure: Optional[bool] = None,
        metadata: Optional[Mapping[str, str]] = None,
        network: Optional[Mapping[str, Any]] = None,
    ) -> AsyncVm:
        """Start a VM from a template or a snapshot."""
        fields = {
            "template": template,
            "snapshot": snapshot,
            "size": size,
            "vcpus": vcpus,
            "memory_mib": memory_mib,
            "region": region,
            "timeout_seconds": timeout_seconds,
            "auto_pause": auto_pause,
            "auto_resume": auto_resume,
            "env": env,
            "secure": secure,
            "metadata": metadata,
            "network": network,
        }
        return AsyncVm(self._t, await self._json(_ops.create_vm(fields)))

    async def get(self, vm_id: str) -> AsyncVm:
        """Return a VM by id."""
        return AsyncVm(self._t, await self._json(Request("GET", f"/vms/{seg(vm_id)}")))

    async def connect(self, vm_id: str) -> AsyncVm:
        """Attach to an existing VM, resuming it if it is paused."""
        return AsyncVm(self._t, await self._json(Request("POST", f"/vms/{seg(vm_id)}/connect")))

    async def list(self, *, page_size: Optional[int] = None) -> AsyncIterator[AsyncVm]:
        """Iterate every VM of the account, fetching ``page_size`` per request."""
        async for item in self._pages("/vms", page_size):
            yield AsyncVm(self._t, item)


class AsyncSnapshots(_AsyncResource):
    """Saved VM states."""

    async def get(self, snapshot_id: str) -> Snapshot:
        """Return a snapshot by id or name."""
        return Snapshot.from_dict(await self._json(Request("GET", f"/snapshots/{seg(snapshot_id)}")))

    async def list(self, *, page_size: Optional[int] = None) -> AsyncIterator[Snapshot]:
        """Iterate every snapshot of the account."""
        async for item in self._pages("/snapshots", page_size):
            yield Snapshot.from_dict(item)

    async def delete(self, snapshot_id: str) -> None:
        """Delete a snapshot."""
        await self._t.send(Request("DELETE", f"/snapshots/{seg(snapshot_id)}"))

    async def start(self, snapshot_id: str) -> AsyncVm:
        """Create a VM from a snapshot."""
        request = Request("POST", f"/snapshots/{seg(snapshot_id)}/start", idempotent=True)
        return AsyncVm(self._t, await self._json(request))


class AsyncBrowser(_AsyncResource):
    """A cloud browser. ``cdp_url`` plugs into Playwright or Puppeteer. ``async with`` stops it."""

    def __init__(self, transport: AsyncTransport, data: Dict[str, Any]) -> None:
        super().__init__(transport)
        self._data = data

    @property
    def id(self) -> str:
        return str(self._data["id"])

    @property
    def state(self) -> str:
        return str(self._data.get("state", ""))

    @property
    def cdp_url(self) -> str:
        """``wss://`` endpoint for Playwright ``connect_over_cdp`` or Puppeteer."""
        return str(self._data["cdp_url"])

    @property
    def live_view_url(self) -> Optional[str]:
        value = self._data.get("live_view_url")
        return str(value) if value else None

    @property
    def info(self) -> BrowserInfo:
        """The full typed record as last seen."""
        return BrowserInfo.from_dict(self._data)

    def _path(self, suffix: str = "") -> str:
        return f"/browsers/{seg(self.id)}{suffix}"

    async def refresh(self) -> AsyncBrowser:
        """Reload the record from the API."""
        self._data = await self._json(Request("GET", self._path()))
        return self

    async def take_control(self, holder: Optional[str] = None) -> Control:
        """Hand the session to a person (``holder`` names them in the audit log).

        Agent input pauses until :meth:`give_back_control`.
        """
        body = _ops.drop_none({"holder": holder})
        return Control.from_dict(await self._json(Request("POST", self._path("/control"), json=body)))

    async def give_back_control(self) -> None:
        """End a person's control; agent input resumes."""
        await self._t.send(Request("DELETE", self._path("/control")))

    async def control_state(self) -> Dict[str, Any]:
        """Return who controls the browser right now."""
        return await self._json(Request("GET", self._path("/control")))

    async def stop(self) -> None:
        """Stop the browser."""
        await self._t.send(Request("DELETE", self._path()))

    async def __aenter__(self) -> AsyncBrowser:
        return self

    async def __aexit__(
        self, exc_type: Optional[Type[BaseException]], exc: Optional[BaseException], tb: Optional[TracebackType]
    ) -> None:
        with contextlib.suppress(StyneError if exc is not None else NotFoundError):
            await self.stop()

    def __repr__(self) -> str:
        return f"AsyncBrowser(id={self.id!r})"


class AsyncBrowsers(_AsyncResource):
    """Create, find and list cloud browsers."""

    async def create(
        self,
        *,
        region: Optional[str] = None,
        timeout_seconds: Optional[int] = None,
        secure: Optional[bool] = None,
        metadata: Optional[Mapping[str, Any]] = None,
        viewport: Optional[Mapping[str, int]] = None,
        proxy: Optional[str] = None,
    ) -> AsyncBrowser:
        """Start a browser."""
        fields = {
            "region": region,
            "timeout_seconds": timeout_seconds,
            "secure": secure,
            "metadata": metadata,
            "viewport": viewport,
            "proxy": proxy,
        }
        return AsyncBrowser(self._t, await self._json(_ops.create_browser(fields)))

    async def get(self, browser_id: str) -> AsyncBrowser:
        """Return a browser by id."""
        return AsyncBrowser(self._t, await self._json(Request("GET", f"/browsers/{seg(browser_id)}")))

    async def list(self, *, page_size: Optional[int] = None) -> AsyncIterator[AsyncBrowser]:
        """Iterate every browser of the account."""
        async for item in self._pages("/browsers", page_size):
            yield AsyncBrowser(self._t, item)


class AsyncRegions(_AsyncResource):
    """Regions a VM or browser can run in."""

    async def list(self) -> List[Region]:
        """Return every region."""
        return [Region.from_dict(r) for r in await self._rows(Request("GET", "/regions"))]


class AsyncTemplates(_AsyncResource):
    """Templates a VM can start from."""

    async def list(self) -> List[Template]:
        """Return every template the key can start."""
        return [Template.from_dict(t) async for t in self._pages("/templates", None)]


class AsyncClient:
    """Async entry point. Reads the key from ``STYNE_API_KEY`` and the URL from ``STYNE_BASE_URL`` when not given.

    ``http_client`` replaces the underlying ``httpx.AsyncClient`` (proxies, limits); the key, URL and user agent are
    still applied to every request.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        *,
        base_url: Optional[str] = None,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        http_client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        key, url = resolve_api_key(api_key), resolve_base_url(base_url)
        self._transport = AsyncTransport(key, url, timeout, max_retries, http_client)
        self.vms = AsyncVms(self._transport)
        self.snapshots = AsyncSnapshots(self._transport)
        self.browsers = AsyncBrowsers(self._transport)
        self.regions = AsyncRegions(self._transport)
        self.templates = AsyncTemplates(self._transport)

    async def usage(self) -> Dict[str, Any]:
        """Return the account's usage, grouped by product, key and project."""
        body: Dict[str, Any] = (await self._transport.send(Request("GET", "/usage"))).json()
        return body

    async def aclose(self) -> None:
        """Close the HTTP client (unless it was passed in)."""
        await self._transport.aclose()

    async def __aenter__(self) -> AsyncClient:
        return self

    async def __aexit__(
        self, exc_type: Optional[Type[BaseException]], exc: Optional[BaseException], tb: Optional[TracebackType]
    ) -> None:
        await self.aclose()
