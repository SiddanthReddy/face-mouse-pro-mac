"""Camera abstraction used by the application and test doubles."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class CameraDevice:
    identifier: str
    name: str


class Camera(Protocol):
    def devices(self) -> list[CameraDevice]: ...
    def start(self, callback: Callable[[object, float], None], device_id: str | None = None) -> None: ...
    def stop(self) -> None: ...
