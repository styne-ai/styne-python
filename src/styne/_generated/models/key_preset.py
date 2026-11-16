from .._enums import StrEnum


class KeyPreset(StrEnum):
    BROWSERS = "browsers"
    CI = "ci"
    FULL = "full"
    READ_ONLY = "read-only"
    VMS = "vms"

    def __str__(self) -> str:
        return str(self.value)
