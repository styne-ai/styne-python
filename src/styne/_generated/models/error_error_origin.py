from .._enums import StrEnum


class ErrorErrorOrigin(StrEnum):
    AGENT = "agent"
    CLIENT = "client"
    CUSTOMER_LIMIT = "customer_limit"
    GUEST = "guest"
    INFRASTRUCTURE = "infrastructure"
    UNKNOWN = "unknown"

    def __str__(self) -> str:
        return str(self.value)
