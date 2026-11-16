from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.plan_limits import PlanLimits
    from ..models.plan_overage import PlanOverage


T = TypeVar("T", bound="Plan")


@_attrs_define
class Plan:
    """
    Attributes:
        id (str | Unset):
        name (str | Unset):
        price_usd_month (float | Unset):
        limits (PlanLimits | Unset):
        overage (PlanOverage | Unset):
    """

    id: str | Unset = UNSET
    name: str | Unset = UNSET
    price_usd_month: float | Unset = UNSET
    limits: PlanLimits | Unset = UNSET
    overage: PlanOverage | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        price_usd_month = self.price_usd_month

        limits: dict[str, Any] | Unset = UNSET
        if not isinstance(self.limits, Unset):
            limits = self.limits.to_dict()

        overage: dict[str, Any] | Unset = UNSET
        if not isinstance(self.overage, Unset):
            overage = self.overage.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name
        if price_usd_month is not UNSET:
            field_dict["price_usd_month"] = price_usd_month
        if limits is not UNSET:
            field_dict["limits"] = limits
        if overage is not UNSET:
            field_dict["overage"] = overage

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.plan_limits import PlanLimits  # noqa: PLC0415
        from ..models.plan_overage import PlanOverage  # noqa: PLC0415

        d = dict(src_dict)
        id = d.pop("id", UNSET)

        name = d.pop("name", UNSET)

        price_usd_month = d.pop("price_usd_month", UNSET)

        _limits = d.pop("limits", UNSET)
        limits: PlanLimits | Unset
        if isinstance(_limits, Unset):
            limits = UNSET
        else:
            limits = PlanLimits.from_dict(_limits)

        _overage = d.pop("overage", UNSET)
        overage: PlanOverage | Unset
        if isinstance(_overage, Unset):
            overage = UNSET
        else:
            overage = PlanOverage.from_dict(_overage)

        plan = cls(
            id=id,
            name=name,
            price_usd_month=price_usd_month,
            limits=limits,
            overage=overage,
        )

        plan.additional_properties = d
        return plan

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
