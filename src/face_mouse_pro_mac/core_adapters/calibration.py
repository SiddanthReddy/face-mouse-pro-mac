from __future__ import annotations

from face_mouse_core.calibration.algorithms import CalibrationAccumulator, relative_offset
from face_mouse_core.models import NormalizedPoint, Vector2D


class CalibrationAdapter:
    def __init__(self, sample_target: int = 20) -> None:
        self.accumulator = CalibrationAccumulator(sample_target)
        self.neutral: NormalizedPoint | None = None

    def add(self, point: NormalizedPoint) -> NormalizedPoint | None:
        result = self.accumulator.add_sample(point)
        if result is not None:
            self.neutral = result
        return result

    def offset(self, point: NormalizedPoint) -> Vector2D:
        return relative_offset(point, self.neutral)
