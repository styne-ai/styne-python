from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Template")


@_attrs_define
class Template:
    """
    Attributes:
        id (str | Unset):
        aliases (list[str] | Unset):
        vcpus (int | Unset):
        memory_mib (int | Unset):
        regions (list[str] | Unset):
    """

    id: str | Unset = UNSET
    aliases: list[str] | Unset = UNSET
    vcpus: int | Unset = UNSET
    memory_mib: int | Unset = UNSET
    regions: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        aliases: list[str] | Unset = UNSET
        if not isinstance(self.aliases, Unset):
            aliases = self.aliases

        vcpus = self.vcpus

        memory_mib = self.memory_mib

        regions: list[str] | Unset = UNSET
        if not isinstance(self.regions, Unset):
            regions = self.regions

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if aliases is not UNSET:
            field_dict["aliases"] = aliases
        if vcpus is not UNSET:
            field_dict["vcpus"] = vcpus
        if memory_mib is not UNSET:
            field_dict["memory_mib"] = memory_mib
        if regions is not UNSET:
            field_dict["regions"] = regions

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        aliases = cast(list[str], d.pop("aliases", UNSET))

        vcpus = d.pop("vcpus", UNSET)

        memory_mib = d.pop("memory_mib", UNSET)

        regions = cast(list[str], d.pop("regions", UNSET))

        template = cls(
            id=id,
            aliases=aliases,
            vcpus=vcpus,
            memory_mib=memory_mib,
            regions=regions,
        )

        template.additional_properties = d
        return template

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
