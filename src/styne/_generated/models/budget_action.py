from .._enums import StrEnum


class BudgetAction(StrEnum):
    BLOCK = "block"
    NOTIFY = "notify"

    def __str__(self) -> str:
        return str(self.value)
