from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.error_error_origin import ErrorErrorOrigin
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.error_error_details import ErrorErrorDetails


T = TypeVar("T", bound="ErrorError")


@_attrs_define
class ErrorError:
    """
    Attributes:
        code (str):
        status (int):
        message (str):
        request_id (str):
        origin (ErrorErrorOrigin | Unset):
        details (ErrorErrorDetails | Unset):
        doc_url (str | Unset):
    """

    code: str
    status: int
    message: str
    request_id: str
    origin: ErrorErrorOrigin | Unset = UNSET
    details: ErrorErrorDetails | Unset = UNSET
    doc_url: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        code = self.code

        status = self.status

        message = self.message

        request_id = self.request_id

        origin: str | Unset = UNSET
        if not isinstance(self.origin, Unset):
            origin = self.origin.value

        details: dict[str, Any] | Unset = UNSET
        if not isinstance(self.details, Unset):
            details = self.details.to_dict()

        doc_url = self.doc_url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "code": code,
                "status": status,
                "message": message,
                "request_id": request_id,
            }
        )
        if origin is not UNSET:
            field_dict["origin"] = origin
        if details is not UNSET:
            field_dict["details"] = details
        if doc_url is not UNSET:
            field_dict["doc_url"] = doc_url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.error_error_details import ErrorErrorDetails  # noqa: PLC0415

        d = dict(src_dict)
        code = d.pop("code")

        status = d.pop("status")

        message = d.pop("message")

        request_id = d.pop("request_id")

        _origin = d.pop("origin", UNSET)
        origin: ErrorErrorOrigin | Unset
        if isinstance(_origin, Unset):
            origin = UNSET
        else:
            origin = ErrorErrorOrigin(_origin)

        _details = d.pop("details", UNSET)
        details: ErrorErrorDetails | Unset
        if isinstance(_details, Unset):
            details = UNSET
        else:
            details = ErrorErrorDetails.from_dict(_details)

        doc_url = d.pop("doc_url", UNSET)

        error_error = cls(
            code=code,
            status=status,
            message=message,
            request_id=request_id,
            origin=origin,
            details=details,
            doc_url=doc_url,
        )

        error_error.additional_properties = d
        return error_error

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
