from .._enums import StrEnum


class SignedUrlReqOperation(StrEnum):
    DOWNLOAD = "download"
    UPLOAD = "upload"

    def __str__(self) -> str:
        return str(self.value)
