from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class FaceObservation:
    timestamp_seconds: float
    face_center: tuple[float, float]
    left_eye: tuple[tuple[float, float], ...]
    right_eye: tuple[tuple[float, float], ...]
    mouth: tuple[tuple[float, float], ...]
    nose_point: tuple[float, float]


class FaceTracker(Protocol):
    def observe(self, frame: object, timestamp_seconds: float) -> FaceObservation | None: ...
