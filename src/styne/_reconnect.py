"""Reconnect rules shared by ``Browser.with_reconnect`` and ``AsyncBrowser.with_reconnect``."""

from __future__ import annotations

import re

from .errors import StyneError

_MESSAGE = re.compile(
    r"\btarget (page, context or browser|closed)\b"
    r"|\b(browser|connection|websocket|socket) (has been |was )?closed\b"
    r"|\bconnection (reset|refused|lost)\b"
    r"|\bwebsocket (error|is not open)\b"
    r"|\bno close frame\b|\bbroken pipe\b|\beconnreset\b",
    re.IGNORECASE,
)


def _is_closed_socket(error: BaseException) -> bool:
    if isinstance(error, (ConnectionError, EOFError)):
        return True
    if any(cls.__name__.startswith("ConnectionClosed") for cls in type(error).__mro__):
        return True
    return bool(_MESSAGE.search(str(error)))


def is_disconnect(error: BaseException) -> bool:
    """True when ``error`` or its cause says the CDP socket is gone.

    Matches connection errors, websocket ``ConnectionClosed`` errors and the Playwright close messages. Timeouts and
    errors from the Styne API are not disconnects.
    """
    current: BaseException | None = error
    for _ in range(5):
        if current is None:
            break
        if isinstance(current, StyneError):
            return False
        if _is_closed_socket(current):
            return True
        current = current.__cause__
    return False


def check_running(browser_id: str, state: str) -> None:
    if state != "running":
        raise StyneError(f"browser {browser_id} is {state or 'unknown'}, not running")


def backoff(delay: float, attempt: int) -> float:
    return delay * (attempt + 1)
