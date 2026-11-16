from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="FilePerm")


@_attrs_define
class FilePerm:
    """
    Attributes:
        path (str):
        mode (str | Unset):
        owner (str | Unset):
        group (str | Unset):
    """

    path: str
    mode: str | Unset = UNSET
    owner: str | Unset = UNSET
    group: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        path = self.path

        mode = self.mode

        owner = self.owner

        group = self.group

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "path": path,
            }
        )
        if mode is not UNSET:
            field_dict["mode"] = mode
        if owner is not UNSET:
            field_dict["owner"] = owner
        if group is not UNSET:
            field_dict["group"] = group

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        path = d.pop("path")

        mode = d.pop("mode", UNSET)

        owner = d.pop("owner", UNSET)

        group = d.pop("group", UNSET)

        file_perm = cls(
            path=path,
            mode=mode,
            owner=owner,
            group=group,
        )

        file_perm.additional_properties = d
        return file_perm

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
