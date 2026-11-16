from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Literal, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.browser_metadata import BrowserMetadata


T = TypeVar("T", bound="Browser")


@_attrs_define
class Browser:
    """
    Attributes:
        id (str):
        state (str):
        cdp_url (str): wss:// endpoint for playwright connect_over_cdp or puppeteer.connect; embeds a session-scoped
            token.
        object_ (Literal['browser'] | Unset):
        region (str | Unset):
        live_view_url (str | Unset):
        expires_at (datetime.datetime | Unset):
        created_at (datetime.datetime | Unset):
        metadata (BrowserMetadata | Unset):
    """

    id: str
    state: str
    cdp_url: str
    object_: Literal["browser"] | Unset = UNSET
    region: str | Unset = UNSET
    live_view_url: str | Unset = UNSET
    expires_at: datetime.datetime | Unset = UNSET
    created_at: datetime.datetime | Unset = UNSET
    metadata: BrowserMetadata | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        state = self.state

        cdp_url = self.cdp_url

        object_ = self.object_

        region = self.region

        live_view_url = self.live_view_url

        expires_at: str | Unset = UNSET
        if not isinstance(self.expires_at, Unset):
            expires_at = self.expires_at.isoformat()

        created_at: str | Unset = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        metadata: dict[str, Any] | Unset = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "state": state,
                "cdp_url": cdp_url,
            }
        )
        if object_ is not UNSET:
            field_dict["object"] = object_
        if region is not UNSET:
            field_dict["region"] = region
        if live_view_url is not UNSET:
            field_dict["live_view_url"] = live_view_url
        if expires_at is not UNSET:
            field_dict["expires_at"] = expires_at
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.browser_metadata import BrowserMetadata  # noqa: PLC0415

        d = dict(src_dict)
        id = d.pop("id")

        state = d.pop("state")

        cdp_url = d.pop("cdp_url")

        object_ = cast(Literal["browser"] | Unset, d.pop("object", UNSET))
        if object_ != "browser" and not isinstance(object_, Unset):
            raise ValueError(f"object must match const 'browser', got '{object_}'")

        region = d.pop("region", UNSET)

        live_view_url = d.pop("live_view_url", UNSET)

        _expires_at = d.pop("expires_at", UNSET)
        expires_at: datetime.datetime | Unset
        if isinstance(_expires_at, Unset):
            expires_at = UNSET
        else:
            expires_at = datetime.datetime.fromisoformat(_expires_at)

        _created_at = d.pop("created_at", UNSET)
        created_at: datetime.datetime | Unset
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = datetime.datetime.fromisoformat(_created_at)

        _metadata = d.pop("metadata", UNSET)
        metadata: BrowserMetadata | Unset
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = BrowserMetadata.from_dict(_metadata)

        browser = cls(
            id=id,
            state=state,
            cdp_url=cdp_url,
            object_=object_,
            region=region,
            live_view_url=live_view_url,
            expires_at=expires_at,
            created_at=created_at,
            metadata=metadata,
        )

        browser.additional_properties = d
        return browser

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
