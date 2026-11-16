from .._enums import StrEnum


class VmState(StrEnum):
    ENDED = "ended"
    PAUSED = "paused"
    RUNNING = "running"
    STARTING = "starting"

    def __str__(self) -> str:
        return str(self.value)
