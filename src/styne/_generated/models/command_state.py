from .._enums import StrEnum


class CommandState(StrEnum):
    EXITED = "exited"
    RUNNING = "running"
    SIGNALED = "signaled"
    TIMEOUT = "timeout"

    def __str__(self) -> str:
        return str(self.value)
