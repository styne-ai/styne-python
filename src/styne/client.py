"""Synchronous client."""

from __future__ import annotations

import contextlib
import time
from types import TracebackType
from typing import Any, Callable, Dict, Iterator, List, Mapping, Optional, Type, TypeVar, Union

import httpx

from . import _ops
from ._ops import seg
from ._reconnect import backoff, check_running
from ._reconnect import is_disconnect as _is_disconnect
from ._transport import (
    DEFAULT_MAX_RETRIES,
    DEFAULT_TIMEOUT,
    Request,
    SyncTransport,
    resolve_api_key,
    resolve_base_url,
    resolve_region,
)
from .errors import NotFoundError, StyneError
from .models import BrowserInfo, Checkpoint, Port, Region, Snapshot, Template, VmInfo
from .types import CommandResult, Control, FileEntry, StreamDecoder, StreamEvent

Command = _ops.Command


T = TypeVar("T")


class _Resource:
    def __init__(self, transport: SyncTransport) -> None:
        self._t = transport

    def _json(self, request: Request) -> Dict[str, Any]:
        body: Dict[str, Any] = self._t.send(request).json()
        return body

    def _rows(self, request: Request) -> List[Dict[str, Any]]:
        return list(self._json(request).get("data", []))

    def _pages(self, path: str, page_size: Optional[int]) -> Iterator[Dict[str, Any]]:
        cursor: Optional[str] = None
        while True:
            page = self._json(_ops.list_request(path, page_size, cursor))
            yield from page.get("data", [])
            cursor = page.get("next_cursor")
            if not (page.get("has_more") and cursor):
                return


class Files(_Resource):
    """Files inside a VM."""

    def __init__(self, transport: SyncTransport, vm_id: str) -> None:
        super().__init__(transport)
        self._vm = vm_id

    def read(self, path: str) -> bytes:
        """Return the content of a file."""
        return self._t.send(_ops.file_request("GET", self._vm, path)).content

    def read_text(self, path: str) -> str:
        """Return the content of a UTF-8 text file."""
        return self.read(path).decode("utf-8")

    def write(self, path: str, data: Union[str, bytes]) -> None:
        """Create or replace a file; ``str`` data is written as UTF-8."""
        self._t.send(_ops.file_request("PUT", self._vm, path, _ops.as_bytes(data)))

    def delete(self, path: str) -> None:
        """Delete a file."""
        self._t.send(_ops.file_request("DELETE", self._vm, path))

    def list(self, path: str = "/") -> List[FileEntry]:
        """List the entries of a directory."""
        rows = self._rows(Request("GET", f"/vms/{seg(self._vm)}/files/list", params={"path": path}))
        return [FileEntry.from_dict(row) for row in rows]


class Ports(_Resource):
    """Ports a VM serves to the internet."""

    def __init__(self, transport: SyncTransport, vm_id: str) -> None:
        super().__init__(transport)
        self._vm = vm_id

    def expose(self, port: int, *, public: Optional[bool] = None) -> Port:
        """Serve a port of the VM at a public URL; ``public=True`` drops the traffic token."""
        body = _ops.drop_none({"port": port, "public": public})
        return Port.from_dict(self._json(Request("POST", f"/vms/{seg(self._vm)}/ports", json=body)))

    def list(self) -> List[Port]:
        """Return the exposed ports."""
        return [Port.from_dict(p) for p in self._rows(Request("GET", f"/vms/{seg(self._vm)}/ports"))]

    def hide(self, port: int) -> None:
        """Stop serving a port."""
        self._t.send(Request("DELETE", f"/vms/{seg(self._vm)}/ports/{seg(port)}"))


class Checkpoints(_Resource):
    """Checkpoints of a VM; :meth:`Vm.rewind` returns to one."""

    def __init__(self, transport: SyncTransport, vm_id: str) -> None:
        super().__init__(transport)
        self._vm = vm_id

    def create(self, label: Optional[str] = None) -> Checkpoint:
        """Record the VM's current state as a checkpoint."""
        body = _ops.drop_none({"label": label})
        request = Request("POST", f"/vms/{seg(self._vm)}/checkpoints", json=body, idempotent=True)
        return Checkpoint.from_dict(self._json(request))

    def list(self) -> List[Checkpoint]:
        """Return the VM's checkpoints."""
        return [Checkpoint.from_dict(c) for c in self._rows(Request("GET", f"/vms/{seg(self._vm)}/checkpoints"))]


class Vm(_Resource):
    """A running or paused virtual machine. Use it as a context manager to delete it on exit."""

    def __init__(self, transport: SyncTransport, data: Dict[str, Any]) -> None:
        super().__init__(transport)
        self._data = data
        self.files = Files(transport, self.id)
        self.ports = Ports(transport, self.id)
        self.checkpoints = Checkpoints(transport, self.id)

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

    def _update(self, request: Request) -> Vm:
        self._data = self._json(request)
        return self

    def refresh(self) -> Vm:
        """Reload the record from the API."""
        return self._update(Request("GET", self._path()))

    def run(
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
        return CommandResult.from_dict(self._json(_ops.run_request(body, self.id)))

    def stream(
        self,
        command: Command,
        *,
        cwd: Optional[str] = None,
        env: Optional[Mapping[str, str]] = None,
        user: Optional[str] = None,
        stdin: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> Iterator[StreamEvent]:
        """Run a command and yield its output as it arrives; raises the matching error on a server error event."""
        body = _ops.run_body(command, cwd=cwd, env=env, user=user, stdin=stdin, timeout=timeout, stream=True)
        decoder = StreamDecoder()
        for event in self._t.stream(_ops.run_request(body, self.id)):
            if event.event == "error":
                raise _ops.stream_error(event.json())
            yield from decoder.event(event.event, event.data)

    def pause(self, tier: Optional[str] = None) -> Vm:
        """Pause the VM; ``tier`` is ``hot``, ``standby`` or ``archived`` (server default when omitted)."""
        return self._update(Request("POST", self._path("/pause"), json=_ops.drop_none({"tier": tier})))

    def resume(self) -> Vm:
        """Resume a paused VM."""
        return self._update(Request("POST", self._path("/resume")))

    def extend(self, seconds: int) -> Vm:
        """Extend the VM's lifetime by ``seconds``."""
        return self._update(Request("POST", self._path("/extend"), json={"seconds": seconds}))

    def fork(self, count: int = 1) -> List[Vm]:
        """Create ``count`` copies of this VM from its current state."""
        rows = self._rows(Request("POST", self._path("/fork"), json={"count": count}, idempotent=True))
        return [Vm(self._t, item) for item in rows]

    def snapshot(self, name: Optional[str] = None) -> Snapshot:
        """Save the VM's state as a snapshot that new VMs can start from."""
        body = _ops.drop_none({"name": name})
        return Snapshot.from_dict(self._json(Request("POST", self._path("/snapshots"), json=body, idempotent=True)))

    def rewind(self, checkpoint: Union[str, Checkpoint]) -> Vm:
        """Return the VM to a checkpoint (id or object)."""
        checkpoint_id = checkpoint if isinstance(checkpoint, str) else str(checkpoint.id)
        return self._update(Request("POST", self._path("/rewind"), json={"checkpoint": checkpoint_id}))

    def kill(self) -> None:
        """Delete the VM."""
        self._t.send(Request("DELETE", self._path()))

    def __enter__(self) -> Vm:
        return self

    def __exit__(
        self, exc_type: Optional[Type[BaseException]], exc: Optional[BaseException], tb: Optional[TracebackType]
    ) -> None:
        with contextlib.suppress(StyneError if exc is not None else NotFoundError):
            self.kill()

    def __repr__(self) -> str:
        return f"Vm(id={self.id!r}, state={self.state!r})"


class Vms(_Resource):
    """Create, find and list VMs."""

    def create(
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
    ) -> Vm:
        """Start a VM from a template or a snapshot."""
        fields = {
            "template": template,
            "snapshot": snapshot,
            "size": size,
            "vcpus": vcpus,
            "memory_mib": memory_mib,
            "region": region or (None if snapshot else self._t.region),
            "timeout_seconds": timeout_seconds,
            "auto_pause": auto_pause,
            "auto_resume": auto_resume,
            "env": env,
            "secure": secure,
            "metadata": metadata,
            "network": network,
        }
        return Vm(self._t, self._json(_ops.create_vm(fields)))

    def get(self, vm_id: str) -> Vm:
        """Return a VM by id."""
        return Vm(self._t, self._json(Request("GET", f"/vms/{seg(vm_id)}")))

    def connect(self, vm_id: str) -> Vm:
        """Attach to an existing VM, resuming it if it is paused."""
        return Vm(self._t, self._json(Request("POST", f"/vms/{seg(vm_id)}/connect")))

    def list(self, *, page_size: Optional[int] = None) -> Iterator[Vm]:
        """Iterate every VM of the account, fetching ``page_size`` per request."""
        for item in self._pages("/vms", page_size):
            yield Vm(self._t, item)


class Snapshots(_Resource):
    """Saved VM states."""

    def get(self, snapshot_id: str) -> Snapshot:
        """Return a snapshot by id or name."""
        return Snapshot.from_dict(self._json(Request("GET", f"/snapshots/{seg(snapshot_id)}")))

    def list(self, *, page_size: Optional[int] = None) -> Iterator[Snapshot]:
        """Iterate every snapshot of the account."""
        for item in self._pages("/snapshots", page_size):
            yield Snapshot.from_dict(item)

    def delete(self, snapshot_id: str) -> None:
        """Delete a snapshot."""
        self._t.send(Request("DELETE", f"/snapshots/{seg(snapshot_id)}"))

    def start(self, snapshot_id: str) -> Vm:
        """Create a VM from a snapshot."""
        return Vm(self._t, self._json(Request("POST", f"/snapshots/{seg(snapshot_id)}/start", idempotent=True)))


class Browser(_Resource):
    """A cloud browser. ``cdp_url`` plugs into Playwright or Puppeteer. Context manager stops it."""

    def __init__(self, transport: SyncTransport, data: Dict[str, Any]) -> None:
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

    def refresh(self) -> Browser:
        """Reload the record from the API."""
        self._data = self._json(Request("GET", self._path()))
        return self

    def with_reconnect(
        self,
        connect: Callable[[str], Any],
        run: Callable[[Any, int], T],
        *,
        max_reconnects: int = 5,
        delay: float = 0.5,
        is_disconnect: Callable[[BaseException], bool] = _is_disconnect,
    ) -> T:
        """Call ``run(browser, attempt)`` and, when the CDP socket closes, connect again and call it again.

        ``connect`` turns the current ``cdp_url`` into your client's browser object, for example
        ``playwright.chromium.connect_over_cdp``. The browser, its pages and their state live on the server and
        survive a closed socket, so make ``run`` continue from ``context.pages``; ``attempt`` counts from 0.
        ``run`` starts again from the top, so it must be safe to repeat, and it owns the browser object it is
        given (close it if you need to). ``delay`` is in seconds; the wait before reconnect n is ``delay * n``.
        ``is_disconnect`` decides which errors mean a closed socket. Other errors, and the last one after
        ``max_reconnects`` tries, are raised unchanged.
        """
        attempt = 0
        while True:
            check_running(self.id, self.refresh().state)
            try:
                return run(connect(self.cdp_url), attempt)
            except Exception as error:
                if attempt >= max_reconnects or not is_disconnect(error):
                    raise
            time.sleep(backoff(delay, attempt))
            attempt += 1

    def take_control(self, holder: Optional[str] = None) -> Control:
        """Hand the session to a person (``holder`` names them in the audit log).

        Agent input pauses until :meth:`give_back_control`.
        """
        body = _ops.drop_none({"holder": holder})
        return Control.from_dict(self._json(Request("POST", self._path("/control"), json=body)))

    def give_back_control(self) -> None:
        """End a person's control; agent input resumes."""
        self._t.send(Request("DELETE", self._path("/control")))

    def control_state(self) -> Dict[str, Any]:
        """Return who controls the browser right now."""
        return self._json(Request("GET", self._path("/control")))

    def stop(self) -> None:
        """Stop the browser."""
        self._t.send(Request("DELETE", self._path()))

    def __enter__(self) -> Browser:
        return self

    def __exit__(
        self, exc_type: Optional[Type[BaseException]], exc: Optional[BaseException], tb: Optional[TracebackType]
    ) -> None:
        with contextlib.suppress(StyneError if exc is not None else NotFoundError):
            self.stop()

    def __repr__(self) -> str:
        return f"Browser(id={self.id!r})"


class Browsers(_Resource):
    """Create, find and list cloud browsers."""

    def create(
        self,
        *,
        region: Optional[str] = None,
        timeout_seconds: Optional[int] = None,
        secure: Optional[bool] = None,
        metadata: Optional[Mapping[str, Any]] = None,
        viewport: Optional[Mapping[str, int]] = None,
        proxy: Optional[str] = None,
    ) -> Browser:
        """Start a browser."""
        fields = {
            "region": region or self._t.region,
            "timeout_seconds": timeout_seconds,
            "secure": secure,
            "metadata": metadata,
            "viewport": viewport,
            "proxy": proxy,
        }
        return Browser(self._t, self._json(_ops.create_browser(fields)))

    def get(self, browser_id: str) -> Browser:
        """Return a browser by id."""
        return Browser(self._t, self._json(Request("GET", f"/browsers/{seg(browser_id)}")))

    def list(self, *, page_size: Optional[int] = None) -> Iterator[Browser]:
        """Iterate every browser of the account."""
        for item in self._pages("/browsers", page_size):
            yield Browser(self._t, item)


class Regions(_Resource):
    """Regions a VM or browser can run in."""

    def list(self) -> List[Region]:
        """Return every region."""
        return [Region.from_dict(r) for r in self._rows(Request("GET", "/regions"))]


class Templates(_Resource):
    """Templates a VM can start from."""

    def list(self) -> List[Template]:
        """Return every template the key can start."""
        return [Template.from_dict(t) for t in self._pages("/templates", None)]


class Client:
    """Entry point. Reads the key from ``STYNE_API_KEY`` and the URL from ``STYNE_BASE_URL`` when not given.

    ``region`` (``ash`` or ``ams``; ``STYNE_REGION``) picks the regional API host. Default: ``ash``.

    ``http_client`` replaces the underlying ``httpx.Client`` (proxies, limits); the key, URL and user agent are
    still applied to every request.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        *,
        base_url: Optional[str] = None,
        region: Optional[str] = None,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        http_client: Optional[httpx.Client] = None,
    ) -> None:
        key, url = resolve_api_key(api_key), resolve_base_url(base_url, region)
        chosen = resolve_region(region)
        self._transport = SyncTransport(key, url, timeout, max_retries, http_client)
        self._transport.region = chosen
        self.vms = Vms(self._transport)
        self.snapshots = Snapshots(self._transport)
        self.browsers = Browsers(self._transport)
        self.regions = Regions(self._transport)
        self.templates = Templates(self._transport)

    def usage(self) -> Dict[str, Any]:
        """Return the account's usage, grouped by product, key and project."""
        body: Dict[str, Any] = self._transport.send(Request("GET", "/usage")).json()
        return body

    def close(self) -> None:
        """Close the HTTP client (unless it was passed in)."""
        self._transport.close()

    def __enter__(self) -> Client:
        return self

    def __exit__(
        self, exc_type: Optional[Type[BaseException]], exc: Optional[BaseException], tb: Optional[TracebackType]
    ) -> None:
        self.close()
