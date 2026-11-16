from .._enums import StrEnum


class TicketReqKind(StrEnum):
    CDP = "cdp"
    LIVE_VIEW = "live_view"
    PTY = "pty"

    def __str__(self) -> str:
        return str(self.value)
