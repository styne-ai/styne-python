from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.wake_triggers_on_item import WakeTriggersOnItem
from ..types import UNSET, Unset

T = TypeVar("T", bound="WakeTriggers")


@_attrs_define
class WakeTriggers:
    """
    Attributes:
        on (list[WakeTriggersOnItem] | Unset):
        schedule (str | Unset):
    """

    on: list[WakeTriggersOnItem] | Unset = UNSET
    schedule: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        on: list[str] | Unset = UNSET
        if not isinstance(self.on, Unset):
            on = []
            for on_item_data in self.on:
                on_item = on_item_data.value
                on.append(on_item)

        schedule = self.schedule

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if on is not UNSET:
            field_dict["on"] = on
        if schedule is not UNSET:
            field_dict["schedule"] = schedule

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        _on = d.pop("on", UNSET)
        on: list[WakeTriggersOnItem] | Unset = UNSET
        if _on is not UNSET:
            on = []
            for on_item_data in _on:
                on_item = WakeTriggersOnItem(on_item_data)

                on.append(on_item)

        schedule = d.pop("schedule", UNSET)

        wake_triggers = cls(
            on=on,
            schedule=schedule,
        )

        wake_triggers.additional_properties = d
        return wake_triggers

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
