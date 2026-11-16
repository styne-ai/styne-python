from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.signed_url_req_operation import SignedUrlReqOperation
from ..types import UNSET, Unset

T = TypeVar("T", bound="SignedUrlReq")


@_attrs_define
class SignedUrlReq:
    """
    Attributes:
        path (str):
        operation (SignedUrlReqOperation):
        expires_in (int | Unset):
    """

    path: str
    operation: SignedUrlReqOperation
    expires_in: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        path = self.path

        operation = self.operation.value

        expires_in = self.expires_in

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "path": path,
                "operation": operation,
            }
        )
        if expires_in is not UNSET:
            field_dict["expires_in"] = expires_in

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        path = d.pop("path")

        operation = SignedUrlReqOperation(d.pop("operation"))

        expires_in = d.pop("expires_in", UNSET)

        signed_url_req = cls(
            path=path,
            operation=operation,
            expires_in=expires_in,
        )

        signed_url_req.additional_properties = d
        return signed_url_req

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
