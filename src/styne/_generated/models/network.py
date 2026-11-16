from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Network")


@_attrs_define
class Network:
    """
    Attributes:
        allow_internet_access (bool | Unset):
        allow_out (list[str] | Unset):
        deny_out (list[str] | Unset):
    """

    allow_internet_access: bool | Unset = UNSET
    allow_out: list[str] | Unset = UNSET
    deny_out: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        allow_internet_access = self.allow_internet_access

        allow_out: list[str] | Unset = UNSET
        if not isinstance(self.allow_out, Unset):
            allow_out = self.allow_out

        deny_out: list[str] | Unset = UNSET
        if not isinstance(self.deny_out, Unset):
            deny_out = self.deny_out

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if allow_internet_access is not UNSET:
            field_dict["allow_internet_access"] = allow_internet_access
        if allow_out is not UNSET:
            field_dict["allow_out"] = allow_out
        if deny_out is not UNSET:
            field_dict["deny_out"] = deny_out

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        allow_internet_access = d.pop("allow_internet_access", UNSET)

        allow_out = cast(list[str], d.pop("allow_out", UNSET))

        deny_out = cast(list[str], d.pop("deny_out", UNSET))

        network = cls(
            allow_internet_access=allow_internet_access,
            allow_out=allow_out,
            deny_out=deny_out,
        )

        network.additional_properties = d
        return network

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
