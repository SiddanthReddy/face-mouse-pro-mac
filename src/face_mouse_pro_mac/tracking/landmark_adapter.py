"""Convert Vision's sparse, face-relative contours to the core's six-point metric contract.

Vision landmark coordinates are normalized within a face bounding box with a bottom-left origin.
This adapter emits image-normalized, top-left-origin coordinates. For each eye it uses six evenly
spaced contour samples; the shared EAR metric interprets samples 0/3 as corners and 1/2/4/5 as
vertical pairs. For the mouth, six contour samples are similarly provided to the shared MAR metric.
This is an explicit approximation, not MediaPipe mesh equivalence; thresholds require per-user tuning.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol


class _Point(Protocol):
    x: float
    y: float


class _Size(Protocol):
    width: float
    height: float


class _Rectangle(Protocol):
    origin: _Point
    size: _Size


def six_contour_points(points: Sequence[tuple[float, float]]) -> tuple[tuple[float, float], ...]:
    if len(points) < 6:
        raise ValueError("Vision contour must have at least six points")
    # Uniformly sample the ordered contour including its endpoints.
    last = len(points) - 1
    result = tuple(points[round(index * last / 5)] for index in range(6))
    if any(not (0 <= x <= 1 and 0 <= y <= 1) for x, y in result):
        raise ValueError("converted landmarks must be normalized")
    return result


def vision_points_to_image(points: Sequence[_Point], bbox: _Rectangle) -> tuple[tuple[float, float], ...]:
    x0, y0, width, height = bbox.origin.x, bbox.origin.y, bbox.size.width, bbox.size.height
    converted = []
    for point in points:
        x = x0 + float(point.x) * width
        y = 1.0 - (y0 + float(point.y) * height)
        if not (0 <= x <= 1 and 0 <= y <= 1):
            raise ValueError("Vision landmark falls outside normalized image")
        converted.append((x, y))
    return tuple(converted)
