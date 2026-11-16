from .._enums import StrEnum


class WakeTriggersOnItem(StrEnum):
    HTTP = "http"
    SCHEDULE = "schedule"
    SSH = "ssh"
    TCP = "tcp"
    WEBHOOK = "webhook"

    def __str__(self) -> str:
        return str(self.value)
