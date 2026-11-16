from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="CiJob")


@_attrs_define
class CiJob:
    """
    Attributes:
        id (str | Unset):
        state (str | Unset):
        repo (str | Unset):
        command (str | Unset):
        runner (str | Unset):
    """

    id: str | Unset = UNSET
    state: str | Unset = UNSET
    repo: str | Unset = UNSET
    command: str | Unset = UNSET
    runner: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        state = self.state

        repo = self.repo

        command = self.command

        runner = self.runner

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if state is not UNSET:
            field_dict["state"] = state
        if repo is not UNSET:
            field_dict["repo"] = repo
        if command is not UNSET:
            field_dict["command"] = command
        if runner is not UNSET:
            field_dict["runner"] = runner

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        state = d.pop("state", UNSET)

        repo = d.pop("repo", UNSET)

        command = d.pop("command", UNSET)

        runner = d.pop("runner", UNSET)

        ci_job = cls(
            id=id,
            state=state,
            repo=repo,
            command=command,
            runner=runner,
        )

        ci_job.additional_properties = d
        return ci_job

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
