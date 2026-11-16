from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.run_command_env import RunCommandEnv


T = TypeVar("T", bound="RunCommand")


@_attrs_define
class RunCommand:
    """
    Attributes:
        cmd (str):
        args (list[str] | Unset):
        cwd (str | Unset):
        env (RunCommandEnv | Unset):
        user (str | Unset):
        stdin (str | Unset):
        timeout_seconds (int | Unset):
        detach (bool | Unset):
        stream (bool | Unset):
    """

    cmd: str
    args: list[str] | Unset = UNSET
    cwd: str | Unset = UNSET
    env: RunCommandEnv | Unset = UNSET
    user: str | Unset = UNSET
    stdin: str | Unset = UNSET
    timeout_seconds: int | Unset = UNSET
    detach: bool | Unset = UNSET
    stream: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        cmd = self.cmd

        args: list[str] | Unset = UNSET
        if not isinstance(self.args, Unset):
            args = self.args

        cwd = self.cwd

        env: dict[str, Any] | Unset = UNSET
        if not isinstance(self.env, Unset):
            env = self.env.to_dict()

        user = self.user

        stdin = self.stdin

        timeout_seconds = self.timeout_seconds

        detach = self.detach

        stream = self.stream

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "cmd": cmd,
            }
        )
        if args is not UNSET:
            field_dict["args"] = args
        if cwd is not UNSET:
            field_dict["cwd"] = cwd
        if env is not UNSET:
            field_dict["env"] = env
        if user is not UNSET:
            field_dict["user"] = user
        if stdin is not UNSET:
            field_dict["stdin"] = stdin
        if timeout_seconds is not UNSET:
            field_dict["timeout_seconds"] = timeout_seconds
        if detach is not UNSET:
            field_dict["detach"] = detach
        if stream is not UNSET:
            field_dict["stream"] = stream

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.run_command_env import RunCommandEnv  # noqa: PLC0415

        d = dict(src_dict)
        cmd = d.pop("cmd")

        args = cast(list[str], d.pop("args", UNSET))

        cwd = d.pop("cwd", UNSET)

        _env = d.pop("env", UNSET)
        env: RunCommandEnv | Unset
        if isinstance(_env, Unset):
            env = UNSET
        else:
            env = RunCommandEnv.from_dict(_env)

        user = d.pop("user", UNSET)

        stdin = d.pop("stdin", UNSET)

        timeout_seconds = d.pop("timeout_seconds", UNSET)

        detach = d.pop("detach", UNSET)

        stream = d.pop("stream", UNSET)

        run_command = cls(
            cmd=cmd,
            args=args,
            cwd=cwd,
            env=env,
            user=user,
            stdin=stdin,
            timeout_seconds=timeout_seconds,
            detach=detach,
            stream=stream,
        )

        run_command.additional_properties = d
        return run_command

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
