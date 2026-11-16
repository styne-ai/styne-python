from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.create_key_preset import CreateKeyPreset
from ..types import UNSET, Unset

T = TypeVar("T", bound="CreateKey")


@_attrs_define
class CreateKey:
    """
    Attributes:
        name (str):
        preset (CreateKeyPreset | Unset):
    """

    name: str
    preset: CreateKeyPreset | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        preset: str | Unset = UNSET
        if not isinstance(self.preset, Unset):
            preset = self.preset.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
            }
        )
        if preset is not UNSET:
            field_dict["preset"] = preset

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        _preset = d.pop("preset", UNSET)
        preset: CreateKeyPreset | Unset
        if isinstance(_preset, Unset):
            preset = UNSET
        else:
            preset = CreateKeyPreset(_preset)

        create_key = cls(
            name=name,
            preset=preset,
        )

        create_key.additional_properties = d
        return create_key

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
