from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.key_preset import KeyPreset
from ..types import UNSET, Unset

T = TypeVar("T", bound="Key")


@_attrs_define
class Key:
    """
    Attributes:
        id (str | Unset):
        name (str | Unset):
        prefix (str | Unset):
        last4 (str | Unset):
        preset (KeyPreset | Unset):
        secret (str | Unset): Returned once at creation only.
        created_at (datetime.datetime | Unset):
        last_used_at (datetime.datetime | Unset):
    """

    id: str | Unset = UNSET
    name: str | Unset = UNSET
    prefix: str | Unset = UNSET
    last4: str | Unset = UNSET
    preset: KeyPreset | Unset = UNSET
    secret: str | Unset = UNSET
    created_at: datetime.datetime | Unset = UNSET
    last_used_at: datetime.datetime | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        prefix = self.prefix

        last4 = self.last4

        preset: str | Unset = UNSET
        if not isinstance(self.preset, Unset):
            preset = self.preset.value

        secret = self.secret

        created_at: str | Unset = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        last_used_at: str | Unset = UNSET
        if not isinstance(self.last_used_at, Unset):
            last_used_at = self.last_used_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name
        if prefix is not UNSET:
            field_dict["prefix"] = prefix
        if last4 is not UNSET:
            field_dict["last4"] = last4
        if preset is not UNSET:
            field_dict["preset"] = preset
        if secret is not UNSET:
            field_dict["secret"] = secret
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if last_used_at is not UNSET:
            field_dict["last_used_at"] = last_used_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        name = d.pop("name", UNSET)

        prefix = d.pop("prefix", UNSET)

        last4 = d.pop("last4", UNSET)

        _preset = d.pop("preset", UNSET)
        preset: KeyPreset | Unset
        if isinstance(_preset, Unset):
            preset = UNSET
        else:
            preset = KeyPreset(_preset)

        secret = d.pop("secret", UNSET)

        _created_at = d.pop("created_at", UNSET)
        created_at: datetime.datetime | Unset
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = datetime.datetime.fromisoformat(_created_at)

        _last_used_at = d.pop("last_used_at", UNSET)
        last_used_at: datetime.datetime | Unset
        if isinstance(_last_used_at, Unset):
            last_used_at = UNSET
        else:
            last_used_at = datetime.datetime.fromisoformat(_last_used_at)

        key = cls(
            id=id,
            name=name,
            prefix=prefix,
            last4=last4,
            preset=preset,
            secret=secret,
            created_at=created_at,
            last_used_at=last_used_at,
        )

        key.additional_properties = d
        return key

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
