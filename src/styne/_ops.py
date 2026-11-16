"""Request builders shared by the sync and async clients."""

from __future__ import annotations

import math
from typing import Any, Dict, List, Mapping, Optional, Sequence, Union
from urllib.parse import quote

from ._transport import NO_READ_TIMEOUT, Request
from .errors import error_from_payload

Command = Union[str, Sequence[str]]

# Extra seconds the HTTP call waits beyond a command's own timeout, so the server's answer arrives first.
_RUN_SLACK_SECONDS = 15


def seg(value: Union[str, int]) -> str:
    """One URL path segment, escaped."""
    return quote(str(value), safe="")


def drop_none(fields: Mapping[str, Any]) -> Dict[str, Any]:
    return {k: v for k, v in fields.items() if v is not None}


def timeout_seconds(timeout: Optional[float]) -> Optional[int]:
    if timeout is None:
        return None
    if timeout <= 0:
        raise ValueError("timeout must be positive")
    return math.ceil(timeout)


def run_body(
    command: Command,
    *,
    cwd: Optional[str],
    env: Optional[Mapping[str, str]],
    user: Optional[str],
    stdin: Optional[str],
    timeout: Optional[float],
    detach: bool = False,
    stream: bool = False,
) -> Dict[str, Any]:
    if isinstance(command, str):
        cmd, args = "sh", ["-c", command]
    else:
        parts: List[str] = list(command)
        if not parts:
            raise ValueError("command is empty")
        cmd, args = parts[0], parts[1:]
    return drop_none(
        {
            "cmd": cmd,
            "args": args or None,
            "cwd": cwd,
            "env": dict(env) if env else None,
            "user": user,
            "stdin": stdin,
            "timeout_seconds": timeout_seconds(timeout),
            "detach": True if detach else None,
            "stream": True if stream else None,
        }
    )


def run_request(body: Dict[str, Any], vm_id: str) -> Request:
    """POST a command. Never retried: the server does not deduplicate commands."""
    seconds = body.get("timeout_seconds")
    http_timeout = float(seconds + _RUN_SLACK_SECONDS) if seconds else NO_READ_TIMEOUT
    return Request("POST", f"/vms/{seg(vm_id)}/commands", json=body, timeout=http_timeout)


def stream_error(payload: Any) -> Exception:
    inner = payload.get("error") if isinstance(payload, dict) else None
    status = inner.get("status") if isinstance(inner, dict) else None
    return error_from_payload(status if isinstance(status, int) else 500, payload)


def create_vm(fields: Mapping[str, Any]) -> Request:
    return Request("POST", "/vms", json=drop_none(fields), idempotent=True)


def create_browser(fields: Mapping[str, Any]) -> Request:
    return Request("POST", "/browsers", json=drop_none(fields), idempotent=True)


def list_request(path: str, page_size: Optional[int], cursor: Optional[str]) -> Request:
    return Request("GET", path, params={"limit": page_size, "cursor": cursor})


def file_request(method: str, vm_id: str, path: str, content: Optional[bytes] = None) -> Request:
    return Request(method, f"/vms/{seg(vm_id)}/files", params={"path": path}, content=content)


def as_bytes(data: Union[str, bytes]) -> bytes:
    return data.encode("utf-8") if isinstance(data, str) else data
