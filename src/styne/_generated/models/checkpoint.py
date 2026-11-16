from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Checkpoint")


@_attrs_define
class Checkpoint:
    """
    Attributes:
        id (str | Unset):
        label (str | Unset):
        step (int | Unset):
        follows (None | str | Unset):
        snapshot (str | Unset):
        created_at (datetime.datetime | Unset):
    """

    id: str | Unset = UNSET
    label: str | Unset = UNSET
    step: int | Unset = UNSET
    follows: None | str | Unset = UNSET
    snapshot: str | Unset = UNSET
    created_at: datetime.datetime | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        label = self.label

        step = self.step

        follows: None | str | Unset
        if isinstance(self.follows, Unset):
            follows = UNSET
        else:
            follows = self.follows

        snapshot = self.snapshot

        created_at: str | Unset = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if label is not UNSET:
            field_dict["label"] = label
        if step is not UNSET:
            field_dict["step"] = step
        if follows is not UNSET:
            field_dict["follows"] = follows
        if snapshot is not UNSET:
            field_dict["snapshot"] = snapshot
        if created_at is not UNSET:
            field_dict["created_at"] = created_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        label = d.pop("label", UNSET)

        step = d.pop("step", UNSET)

        def _parse_follows(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        follows = _parse_follows(d.pop("follows", UNSET))

        snapshot = d.pop("snapshot", UNSET)

        _created_at = d.pop("created_at", UNSET)
        created_at: datetime.datetime | Unset
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = datetime.datetime.fromisoformat(_created_at)

        checkpoint = cls(
            id=id,
            label=label,
            step=step,
            follows=follows,
            snapshot=snapshot,
            created_at=created_at,
        )

        checkpoint.additional_properties = d
        return checkpoint

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
