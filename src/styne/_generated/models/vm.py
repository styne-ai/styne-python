from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Literal, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.vm_pause_tier_type_1 import VmPauseTierType1
from ..models.vm_pause_tier_type_2_type_1 import VmPauseTierType2Type1
from ..models.vm_pause_tier_type_3_type_1 import VmPauseTierType3Type1
from ..models.vm_state import VmState
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.port import Port
    from ..models.vm_metadata import VmMetadata


T = TypeVar("T", bound="Vm")


@_attrs_define
class Vm:
    """
    Attributes:
        id (str):
        state (VmState):
        created_at (datetime.datetime):
        object_ (Literal['vm'] | Unset):
        pause_tier (None | Unset | VmPauseTierType1 | VmPauseTierType2Type1 | VmPauseTierType3Type1):
        region (str | Unset):
        template (str | Unset):
        size (str | Unset):
        vcpus (int | Unset):
        memory_mib (int | Unset):
        timeout_seconds (int | Unset):
        expires_at (datetime.datetime | Unset):
        metadata (VmMetadata | Unset):
        ports (list[Port] | Unset):
    """

    id: str
    state: VmState
    created_at: datetime.datetime
    object_: Literal["vm"] | Unset = UNSET
    pause_tier: None | Unset | VmPauseTierType1 | VmPauseTierType2Type1 | VmPauseTierType3Type1 = UNSET
    region: str | Unset = UNSET
    template: str | Unset = UNSET
    size: str | Unset = UNSET
    vcpus: int | Unset = UNSET
    memory_mib: int | Unset = UNSET
    timeout_seconds: int | Unset = UNSET
    expires_at: datetime.datetime | Unset = UNSET
    metadata: VmMetadata | Unset = UNSET
    ports: list[Port] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        state = self.state.value

        created_at = self.created_at.isoformat()

        object_ = self.object_

        pause_tier: None | str | Unset
        if isinstance(self.pause_tier, Unset):
            pause_tier = UNSET
        elif isinstance(self.pause_tier, VmPauseTierType1):
            pause_tier = self.pause_tier.value
        elif isinstance(self.pause_tier, VmPauseTierType2Type1):
            pause_tier = self.pause_tier.value
        elif isinstance(self.pause_tier, VmPauseTierType3Type1):
            pause_tier = self.pause_tier.value
        else:
            pause_tier = self.pause_tier

        region = self.region

        template = self.template

        size = self.size

        vcpus = self.vcpus

        memory_mib = self.memory_mib

        timeout_seconds = self.timeout_seconds

        expires_at: str | Unset = UNSET
        if not isinstance(self.expires_at, Unset):
            expires_at = self.expires_at.isoformat()

        metadata: dict[str, Any] | Unset = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        ports: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.ports, Unset):
            ports = []
            for ports_item_data in self.ports:
                ports_item = ports_item_data.to_dict()
                ports.append(ports_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "state": state,
                "created_at": created_at,
            }
        )
        if object_ is not UNSET:
            field_dict["object"] = object_
        if pause_tier is not UNSET:
            field_dict["pause_tier"] = pause_tier
        if region is not UNSET:
            field_dict["region"] = region
        if template is not UNSET:
            field_dict["template"] = template
        if size is not UNSET:
            field_dict["size"] = size
        if vcpus is not UNSET:
            field_dict["vcpus"] = vcpus
        if memory_mib is not UNSET:
            field_dict["memory_mib"] = memory_mib
        if timeout_seconds is not UNSET:
            field_dict["timeout_seconds"] = timeout_seconds
        if expires_at is not UNSET:
            field_dict["expires_at"] = expires_at
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if ports is not UNSET:
            field_dict["ports"] = ports

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.port import Port  # noqa: PLC0415
        from ..models.vm_metadata import VmMetadata  # noqa: PLC0415

        d = dict(src_dict)
        id = d.pop("id")

        state = VmState(d.pop("state"))

        created_at = datetime.datetime.fromisoformat(d.pop("created_at"))

        object_ = cast(Literal["vm"] | Unset, d.pop("object", UNSET))
        if object_ != "vm" and not isinstance(object_, Unset):
            raise ValueError(f"object must match const 'vm', got '{object_}'")

        def _parse_pause_tier(
            data: object,
        ) -> None | Unset | VmPauseTierType1 | VmPauseTierType2Type1 | VmPauseTierType3Type1:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                pause_tier_type_1 = VmPauseTierType1(data)

                return pause_tier_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, str):
                    raise TypeError()
                pause_tier_type_2_type_1 = VmPauseTierType2Type1(data)

                return pause_tier_type_2_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, str):
                    raise TypeError()
                pause_tier_type_3_type_1 = VmPauseTierType3Type1(data)

                return pause_tier_type_3_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | VmPauseTierType1 | VmPauseTierType2Type1 | VmPauseTierType3Type1, data)

        pause_tier = _parse_pause_tier(d.pop("pause_tier", UNSET))

        region = d.pop("region", UNSET)

        template = d.pop("template", UNSET)

        size = d.pop("size", UNSET)

        vcpus = d.pop("vcpus", UNSET)

        memory_mib = d.pop("memory_mib", UNSET)

        timeout_seconds = d.pop("timeout_seconds", UNSET)

        _expires_at = d.pop("expires_at", UNSET)
        expires_at: datetime.datetime | Unset
        if isinstance(_expires_at, Unset):
            expires_at = UNSET
        else:
            expires_at = datetime.datetime.fromisoformat(_expires_at)

        _metadata = d.pop("metadata", UNSET)
        metadata: VmMetadata | Unset
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = VmMetadata.from_dict(_metadata)

        _ports = d.pop("ports", UNSET)
        ports: list[Port] | Unset = UNSET
        if _ports is not UNSET:
            ports = []
            for ports_item_data in _ports:
                ports_item = Port.from_dict(ports_item_data)

                ports.append(ports_item)

        vm = cls(
            id=id,
            state=state,
            created_at=created_at,
            object_=object_,
            pause_tier=pause_tier,
            region=region,
            template=template,
            size=size,
            vcpus=vcpus,
            memory_mib=memory_mib,
            timeout_seconds=timeout_seconds,
            expires_at=expires_at,
            metadata=metadata,
            ports=ports,
        )

        vm.additional_properties = d
        return vm

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
