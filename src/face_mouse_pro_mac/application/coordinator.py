"""Lifecycle and safe gating between camera, tracker and the opt-in pointer."""

from __future__ import annotations

import logging

from face_mouse_core.models import NormalizedPoint

from ..camera.protocol import Camera
from ..control.quartz_mouse_controller import MouseController
from ..core_adapters.calibration import CalibrationAdapter
from ..core_adapters.cursor import CursorAdapter
from ..core_adapters.gestures import GestureAdapter
from ..tracking.protocol import FaceTracker

log = logging.getLogger(__name__)


class Coordinator:
    def __init__(self, camera: Camera, tracker: FaceTracker, mouse: MouseController) -> None:
        self.camera, self.tracker, self.mouse = camera, tracker, mouse
        self.gestures, self.calibration, self.cursor = GestureAdapter(), CalibrationAdapter(), CursorAdapter()
        self.running = False
        self.control_active = False
        self.calibration_sampling = False
        self.status_callback = lambda _text: None
        self.preview_callback = lambda _frame: None
        self._last_preview_timestamp = -1.0
        self._dragging = False
        if hasattr(camera, "error_callback"):
            camera.error_callback = self.camera_failure

    def start(self, camera_id: str | None = None) -> None:
        self.running = True
        try:
            self.camera.start(self._on_frame, camera_id)
        except Exception as exc:
            self.camera_failure(f"Camera startup failed: {exc}")
            return
        if self.running:
            self.status_callback("Camera active — center your face")

    def activate_control(self) -> None:
        if self.calibration.neutral is None or self.calibration_sampling:
            raise RuntimeError("Complete neutral calibration before enabling pointer control")
        self.mouse.resume()
        self.control_active = True
        self.status_callback("Pointer control active")

    def pause(self) -> None:
        self.mouse.pause()
        self.control_active = False
        self._dragging = False
        self.status_callback("Paused")

    def stop(self) -> None:
        self.running = False
        self.control_active = False
        try:
            self.mouse.close()
        finally:
            self.camera.stop()

    def _on_frame(self, frame: object, timestamp: float) -> None:
        if not self.running:
            return
        try:
            if timestamp - self._last_preview_timestamp >= 0.1:
                self._last_preview_timestamp = timestamp
                self.preview_callback(frame)
            observation = self.tracker.observe(frame, timestamp)
            if observation is None:
                self.mouse.pause()
                self.control_active = False
                self._dragging = False
                self.gestures.update(None, timestamp)
                self.status_callback("Face not detected — pointer paused")
                return
            if self.calibration_sampling:
                result = self.add_calibration_sample(NormalizedPoint(*observation.nose_point))
                if result is not None:
                    self.calibration_sampling = False
                    self.status_callback("Neutral calibration complete")
                else:
                    sample_count = self.calibration.accumulator.sample_count
                    self.status_callback(f"Calibrating neutral — {sample_count}/20")
            if self.control_active:
                neutral_offset = self.calibration.offset(NormalizedPoint(*observation.nose_point))
                point = self.cursor.move(neutral_offset, timestamp)
                self.mouse.move(point.x, point.y)
                self.status_callback(f"Tracking — {point.x:.2f}, {point.y:.2f}")
            gesture = self.gestures.update(observation, timestamp)
            if gesture.value == "left_click":
                self.mouse.click()
            elif gesture.value == "right_click":
                self.mouse.click("right")
            elif gesture.value == "double_click":
                self.mouse.click(count=2)
            elif gesture.value == "drag_toggle":
                if self._dragging:
                    end_drag = getattr(self.mouse, "end_drag", None)
                    if end_drag:
                        end_drag()
                    self._dragging = False
                else:
                    begin_drag = getattr(self.mouse, "begin_drag", None)
                    if begin_drag:
                        begin_drag()
                        self._dragging = True
        except Exception:
            log.exception("Tracking frame failed; stopping pointer events")
            self.mouse.emergency_stop()
            self.control_active = False
            self.status_callback("Tracking error — pointer stopped")

    def camera_failure(self, message: str) -> None:
        self.running = False
        self.control_active = False
        self._dragging = False
        self.mouse.emergency_stop()
        try:
            self.camera.stop()
        except Exception:
            log.exception("Camera cleanup failed after capture error")
        self.status_callback(f"{message} — pointer stopped")

    def calibrate_neutral(self, target_samples: int = 20) -> None:
        self.calibration = CalibrationAdapter(target_samples)
        self.calibration_sampling = True

    def add_calibration_sample(self, point: NormalizedPoint) -> NormalizedPoint | None:
        return self.calibration.add(point)
