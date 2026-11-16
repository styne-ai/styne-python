from .._enums import StrEnum


class PauseTier(StrEnum):
    ARCHIVED = "archived"
    HOT = "hot"
    STANDBY = "standby"

    def __str__(self) -> str:
        return str(self.value)
