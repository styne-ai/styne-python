from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.create_vm_env import CreateVmEnv
    from ..models.create_vm_lifecycle import CreateVmLifecycle
    from ..models.create_vm_metadata import CreateVmMetadata
    from ..models.network import Network


T = TypeVar("T", bound="CreateVm")


@_attrs_define
class CreateVm:
    """Name a template, a snapshot or a size; none = default size.

    Attributes:
        template (str | Unset):
        snapshot (str | Unset):
        size (str | Unset):
        vcpus (int | Unset):
        memory_mib (int | Unset):
        region (str | Unset):
        timeout_seconds (int | Unset):
        auto_pause (bool | Unset):
        auto_resume (bool | Unset):
        lifecycle (CreateVmLifecycle | Unset):
        network (Network | Unset):
        env (CreateVmEnv | Unset):
        secure (bool | Unset):
        metadata (CreateVmMetadata | Unset):
    """

    template: str | Unset = UNSET
    snapshot: str | Unset = UNSET
    size: str | Unset = UNSET
    vcpus: int | Unset = UNSET
    memory_mib: int | Unset = UNSET
    region: str | Unset = UNSET
    timeout_seconds: int | Unset = UNSET
    auto_pause: bool | Unset = UNSET
    auto_resume: bool | Unset = UNSET
    lifecycle: CreateVmLifecycle | Unset = UNSET
    network: Network | Unset = UNSET
    env: CreateVmEnv | Unset = UNSET
    secure: bool | Unset = UNSET
    metadata: CreateVmMetadata | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        template = self.template

        snapshot = self.snapshot

        size = self.size

        vcpus = self.vcpus

        memory_mib = self.memory_mib

        region = self.region

        timeout_seconds = self.timeout_seconds

        auto_pause = self.auto_pause

        auto_resume = self.auto_resume

        lifecycle: dict[str, Any] | Unset = UNSET
        if not isinstance(self.lifecycle, Unset):
            lifecycle = self.lifecycle.to_dict()

        network: dict[str, Any] | Unset = UNSET
        if not isinstance(self.network, Unset):
            network = self.network.to_dict()

        env: dict[str, Any] | Unset = UNSET
        if not isinstance(self.env, Unset):
            env = self.env.to_dict()

        secure = self.secure

        metadata: dict[str, Any] | Unset = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if template is not UNSET:
            field_dict["template"] = template
        if snapshot is not UNSET:
            field_dict["snapshot"] = snapshot
        if size is not UNSET:
            field_dict["size"] = size
        if vcpus is not UNSET:
            field_dict["vcpus"] = vcpus
        if memory_mib is not UNSET:
            field_dict["memory_mib"] = memory_mib
        if region is not UNSET:
            field_dict["region"] = region
        if timeout_seconds is not UNSET:
            field_dict["timeout_seconds"] = timeout_seconds
        if auto_pause is not UNSET:
            field_dict["auto_pause"] = auto_pause
        if auto_resume is not UNSET:
            field_dict["auto_resume"] = auto_resume
        if lifecycle is not UNSET:
            field_dict["lifecycle"] = lifecycle
        if network is not UNSET:
            field_dict["network"] = network
        if env is not UNSET:
            field_dict["env"] = env
        if secure is not UNSET:
            field_dict["secure"] = secure
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.create_vm_env import CreateVmEnv  # noqa: PLC0415
        from ..models.create_vm_lifecycle import CreateVmLifecycle  # noqa: PLC0415
        from ..models.create_vm_metadata import CreateVmMetadata  # noqa: PLC0415
        from ..models.network import Network  # noqa: PLC0415

        d = dict(src_dict)
        template = d.pop("template", UNSET)

        snapshot = d.pop("snapshot", UNSET)

        size = d.pop("size", UNSET)

        vcpus = d.pop("vcpus", UNSET)

        memory_mib = d.pop("memory_mib", UNSET)

        region = d.pop("region", UNSET)

        timeout_seconds = d.pop("timeout_seconds", UNSET)

        auto_pause = d.pop("auto_pause", UNSET)

        auto_resume = d.pop("auto_resume", UNSET)

        _lifecycle = d.pop("lifecycle", UNSET)
        lifecycle: CreateVmLifecycle | Unset
        if isinstance(_lifecycle, Unset):
            lifecycle = UNSET
        else:
            lifecycle = CreateVmLifecycle.from_dict(_lifecycle)

        _network = d.pop("network", UNSET)
        network: Network | Unset
        if isinstance(_network, Unset):
            network = UNSET
        else:
            network = Network.from_dict(_network)

        _env = d.pop("env", UNSET)
        env: CreateVmEnv | Unset
        if isinstance(_env, Unset):
            env = UNSET
        else:
            env = CreateVmEnv.from_dict(_env)

        secure = d.pop("secure", UNSET)

        _metadata = d.pop("metadata", UNSET)
        metadata: CreateVmMetadata | Unset
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = CreateVmMetadata.from_dict(_metadata)

        create_vm = cls(
            template=template,
            snapshot=snapshot,
            size=size,
            vcpus=vcpus,
            memory_mib=memory_mib,
            region=region,
            timeout_seconds=timeout_seconds,
            auto_pause=auto_pause,
            auto_resume=auto_resume,
            lifecycle=lifecycle,
            network=network,
            env=env,
            secure=secure,
            metadata=metadata,
        )

        create_vm.additional_properties = d
        return create_vm

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
