"""Apple Vision face landmark detector with stable largest-face selection."""

from __future__ import annotations

from __future__ import annotations

import sys

from .landmark_adapter import six_contour_points, vision_points_to_image
from .protocol import FaceObservation


class VisionFaceTracker:
    def __init__(self) -> None:
        if sys.platform != "darwin":
            raise RuntimeError("Apple Vision is available only on macOS")
        import Vision  # type: ignore[import-not-found]

        self.Vision = Vision
        self._handler = Vision.VNSequenceRequestHandler.alloc().init()
        self._request = Vision.VNDetectFaceLandmarksRequest.alloc().init()
        self._last_timestamp = -1.0

    def observe(self, frame: object, timestamp_seconds: float) -> FaceObservation | None:
        if timestamp_seconds < self._last_timestamp:
            raise ValueError("frame timestamps must be monotonic")
        self._last_timestamp = timestamp_seconds
        result = self._handler.performRequests_onCMSampleBuffer_error_([self._request], frame, None)
        succeeded = result[0] if isinstance(result, tuple) else result
        if not succeeded:
            return None
        faces = self._request.results() or []
        if not faces:
            return None
        face = max(faces, key=lambda item: item.boundingBox().size.width * item.boundingBox().size.height)
        landmarks = face.landmarks()
        if (
            landmarks is None
            or landmarks.leftEye() is None
            or landmarks.rightEye() is None
            or landmarks.outerLips() is None
            or landmarks.nose() is None
        ):
            return None
        bbox = face.boundingBox()
        try:
            left = six_contour_points(vision_points_to_image(landmarks.leftEye().normalizedPoints(), bbox))
            right = six_contour_points(vision_points_to_image(landmarks.rightEye().normalizedPoints(), bbox))
            mouth = six_contour_points(vision_points_to_image(landmarks.outerLips().normalizedPoints(), bbox))
            nose_points = vision_points_to_image(landmarks.nose().normalizedPoints(), bbox)
            if not nose_points:
                return None
            nose = (
                sum(point[0] for point in nose_points) / len(nose_points),
                sum(point[1] for point in nose_points) / len(nose_points),
            )
        except (ValueError, TypeError, AttributeError):
            return None
        center = (bbox.origin.x + bbox.size.width / 2, 1 - (bbox.origin.y + bbox.size.height / 2))
        return FaceObservation(timestamp_seconds, center, left, right, mouth, nose)
