from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.update_vm_metadata import UpdateVmMetadata


T = TypeVar("T", bound="UpdateVm")


@_attrs_define
class UpdateVm:
    """
    Attributes:
        timeout_seconds (int | Unset):
        metadata (UpdateVmMetadata | Unset):
        auto_pause (bool | Unset):
    """

    timeout_seconds: int | Unset = UNSET
    metadata: UpdateVmMetadata | Unset = UNSET
    auto_pause: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        timeout_seconds = self.timeout_seconds

        metadata: dict[str, Any] | Unset = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        auto_pause = self.auto_pause

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if timeout_seconds is not UNSET:
            field_dict["timeout_seconds"] = timeout_seconds
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if auto_pause is not UNSET:
            field_dict["auto_pause"] = auto_pause

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.update_vm_metadata import UpdateVmMetadata  # noqa: PLC0415

        d = dict(src_dict)
        timeout_seconds = d.pop("timeout_seconds", UNSET)

        _metadata = d.pop("metadata", UNSET)
        metadata: UpdateVmMetadata | Unset
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = UpdateVmMetadata.from_dict(_metadata)

        auto_pause = d.pop("auto_pause", UNSET)

        update_vm = cls(
            timeout_seconds=timeout_seconds,
            metadata=metadata,
            auto_pause=auto_pause,
        )

        update_vm.additional_properties = d
        return update_vm

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
