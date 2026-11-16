from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.pause_tier import PauseTier
from ..types import UNSET, Unset

T = TypeVar("T", bound="Pause")


@_attrs_define
class Pause:
    """
    Attributes:
        tier (PauseTier | Unset):  Default: PauseTier.HOT.
    """

    tier: PauseTier | Unset = PauseTier.HOT
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        tier: str | Unset = UNSET
        if not isinstance(self.tier, Unset):
            tier = self.tier.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if tier is not UNSET:
            field_dict["tier"] = tier

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        _tier = d.pop("tier", UNSET)
        tier: PauseTier | Unset
        if isinstance(_tier, Unset):
            tier = UNSET
        else:
            tier = PauseTier(_tier)

        pause = cls(
            tier=tier,
        )

        pause.additional_properties = d
        return pause

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
