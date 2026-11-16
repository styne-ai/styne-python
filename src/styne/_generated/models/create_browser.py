from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.create_browser_metadata import CreateBrowserMetadata
    from ..models.create_browser_viewport import CreateBrowserViewport


T = TypeVar("T", bound="CreateBrowser")


@_attrs_define
class CreateBrowser:
    """
    Attributes:
        region (str | Unset):
        timeout_seconds (int | Unset):
        secure (bool | Unset):
        metadata (CreateBrowserMetadata | Unset):
        viewport (CreateBrowserViewport | Unset):
        proxy (str | Unset):
    """

    region: str | Unset = UNSET
    timeout_seconds: int | Unset = UNSET
    secure: bool | Unset = UNSET
    metadata: CreateBrowserMetadata | Unset = UNSET
    viewport: CreateBrowserViewport | Unset = UNSET
    proxy: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        region = self.region

        timeout_seconds = self.timeout_seconds

        secure = self.secure

        metadata: dict[str, Any] | Unset = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        viewport: dict[str, Any] | Unset = UNSET
        if not isinstance(self.viewport, Unset):
            viewport = self.viewport.to_dict()

        proxy = self.proxy

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if region is not UNSET:
            field_dict["region"] = region
        if timeout_seconds is not UNSET:
            field_dict["timeout_seconds"] = timeout_seconds
        if secure is not UNSET:
            field_dict["secure"] = secure
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if viewport is not UNSET:
            field_dict["viewport"] = viewport
        if proxy is not UNSET:
            field_dict["proxy"] = proxy

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.create_browser_metadata import CreateBrowserMetadata  # noqa: PLC0415
        from ..models.create_browser_viewport import CreateBrowserViewport  # noqa: PLC0415

        d = dict(src_dict)
        region = d.pop("region", UNSET)

        timeout_seconds = d.pop("timeout_seconds", UNSET)

        secure = d.pop("secure", UNSET)

        _metadata = d.pop("metadata", UNSET)
        metadata: CreateBrowserMetadata | Unset
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = CreateBrowserMetadata.from_dict(_metadata)

        _viewport = d.pop("viewport", UNSET)
        viewport: CreateBrowserViewport | Unset
        if isinstance(_viewport, Unset):
            viewport = UNSET
        else:
            viewport = CreateBrowserViewport.from_dict(_viewport)

        proxy = d.pop("proxy", UNSET)

        create_browser = cls(
            region=region,
            timeout_seconds=timeout_seconds,
            secure=secure,
            metadata=metadata,
            viewport=viewport,
            proxy=proxy,
        )

        create_browser.additional_properties = d
        return create_browser

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
