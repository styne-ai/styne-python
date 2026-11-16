"""Marker for fields the server did not send."""

from typing import Literal

from attrs import define


@define
class Unset:
    def __bool__(self) -> Literal[False]:
        return False


UNSET: Unset = Unset()

__all__ = ["UNSET", "Unset"]
