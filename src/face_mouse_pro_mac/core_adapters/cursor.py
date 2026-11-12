from __future__ import annotations

from face_mouse_core.config import CursorMappingConfig, SmoothingConfig
from face_mouse_core.cursor.mapping import CursorMapper
from face_mouse_core.cursor.smoothing import OneEuroFilter2D
from face_mouse_core.models import NormalizedPoint, TimestampedPoint, Vector2D


class CursorAdapter:
    def __init__(self, mapping: CursorMappingConfig | None = None, smoothing: SmoothingConfig | None = None) -> None:
        self.mapper = CursorMapper(mapping or CursorMappingConfig())
        self.filter = OneEuroFilter2D(smoothing or SmoothingConfig())

    def move(self, delta: Vector2D, timestamp: float) -> NormalizedPoint:
        mapped = self.mapper.map_offset(delta)
        target = NormalizedPoint(min(1, max(0, 0.5 + mapped.x)), min(1, max(0, 0.5 + mapped.y)))
        return self.filter.update(TimestampedPoint(timestamp, target))

    def reset(self) -> None:
        self.filter.reset()
