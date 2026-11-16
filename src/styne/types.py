"""Plain result types returned by the client."""

from __future__ import annotations

import base64
import codecs
import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional

from .errors import CommandError


@dataclass
class CommandResult:
    """The outcome of :meth:`styne.Vm.run`."""

    id: str
    state: str
    exit_code: Optional[int]
    stdout: str
    stderr: str

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> CommandResult:
        return cls(
            id=str(data.get("id", "")),
            state=str(data.get("state", "")),
            exit_code=data.get("exit_code"),
            stdout=data.get("stdout") or "",
            stderr=data.get("stderr") or "",
        )

    @property
    def ok(self) -> bool:
        """True when the command exited with code 0."""
        return self.exit_code == 0

    def check(self) -> CommandResult:
        """Return self, or raise :class:`styne.CommandError` unless the exit code is 0."""
        if not self.ok:
            raise CommandError(self)
        return self


@dataclass
class StreamEvent:
    """One piece of streamed command output: ``started``, ``stdout``, ``stderr`` or ``exit``.

    ``data`` is the decoded text for ``stdout`` and ``stderr`` and the raw JSON payload otherwise; ``bytes`` holds the
    undecoded output bytes. ``exit`` events set ``exit_code`` (``None`` when a signal ended the command), ``signal``
    and ``timed_out``.
    """

    type: str
    data: str
    exit_code: Optional[int] = None
    signal: Optional[int] = None
    timed_out: bool = False
    bytes: Optional[bytes] = None


@dataclass
class FileEntry:
    """One entry of :meth:`styne.Files.list`."""

    name: str
    path: str
    type: str
    size: Optional[int] = None

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> FileEntry:
        size = data.get("size")
        return cls(
            name=str(data.get("name", "")),
            path=str(data.get("path", "")),
            type=str(data.get("type", "")),
            size=size if isinstance(size, int) else None,
        )


@dataclass
class Control:
    """A person's hold on a browser, returned by :meth:`styne.Browser.take_control`."""

    cdp_url: str
    control_id: str
    holder: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> Control:
        holder = data.get("holder")
        return cls(
            cdp_url=str(data.get("cdp_url", "")),
            control_id=str(data.get("control_id", "")),
            holder=str(holder) if holder else None,
            raw=dict(data),
        )


class StreamDecoder:
    """Turns the SSE frames of one command stream into :class:`StreamEvent` objects.

    Output text is decoded incrementally per stream, so a multi-byte character split across frames stays whole.
    """

    def __init__(self) -> None:
        self._decoders = {name: codecs.getincrementaldecoder("utf-8")("replace") for name in ("stdout", "stderr")}

    def event(self, event_name: str, data: str) -> List[StreamEvent]:
        try:
            body = json.loads(data)
        except ValueError:
            return [StreamEvent(event_name, data)]
        if not isinstance(body, dict):
            return [StreamEvent(event_name, data)]
        if event_name in self._decoders:
            raw = base64.b64decode(str(body.get("data", "")))
            return [StreamEvent(event_name, self._decoders[event_name].decode(raw), bytes=raw)]
        if event_name == "exit":
            events = self._flush()
            signal = body.get("signal")
            events.append(
                StreamEvent(
                    "exit",
                    data,
                    exit_code=body.get("exit_code"),
                    signal=signal if isinstance(signal, int) else None,
                    timed_out=bool(body.get("timed_out")),
                )
            )
            return events
        return [StreamEvent(event_name, data)]

    def _flush(self) -> List[StreamEvent]:
        events: List[StreamEvent] = []
        for name, decoder in self._decoders.items():
            tail = decoder.decode(b"", final=True)
            if tail:
                events.append(StreamEvent(name, tail, bytes=b""))
        return events
