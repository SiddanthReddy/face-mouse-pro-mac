from __future__ import annotations

from face_mouse_core.config import GestureConfig
from face_mouse_core.gestures.detection import GestureDetector
from face_mouse_core.gestures.types import GestureType

from ..tracking.protocol import FaceObservation


class GestureAdapter:
    """Keeps Vision measurements behind an explicit six-point core boundary."""

    def __init__(self, config: GestureConfig | None = None) -> None:
        self.detector = GestureDetector(
            config or GestureConfig(blink_ear_threshold=0.16, mouth_mar_threshold=0.30)
        )

    def update(self, face: FaceObservation | None, timestamp: float) -> GestureType:
        if face is None:
            self.detector.reset()
            return GestureType.NONE
        return self.detector.process(face.left_eye, face.right_eye, face.mouth, timestamp_seconds=timestamp)
