from .._enums import StrEnum


class VmPauseTierType2Type1(StrEnum):
    ARCHIVED = "archived"
    HOT = "hot"
    STANDBY = "standby"

    def __str__(self) -> str:
        return str(self.value)
