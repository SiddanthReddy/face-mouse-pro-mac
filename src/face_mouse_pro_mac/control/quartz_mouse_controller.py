"""Injectable, opt-in Quartz pointer controller. Never enabled implicitly."""

from __future__ import annotations

import sys
from typing import Protocol


class MouseController(Protocol):
    def move(self, x: float, y: float) -> None: ...
    def click(self, button: str = "left", count: int = 1) -> None: ...
    def pause(self) -> None: ...
    def resume(self) -> None: ...
    def emergency_stop(self) -> None: ...
    def close(self) -> None: ...


class QuartzMouseController:
    def __init__(self, enabled: bool = False) -> None:
        if sys.platform != "darwin":
            raise RuntimeError("Quartz mouse control is available only on macOS")
        import Quartz  # type: ignore[import-not-found]

        self.q = Quartz
        self.enabled = False
        self.paused = True
        self._held: set[int] = set()
        if enabled:
            self.resume()

    def resume(self) -> None:
        from .permissions import accessibility_trusted

        if not accessibility_trusted():
            raise PermissionError("Accessibility permission is not granted; enable it in System Settings")
        self.enabled, self.paused = True, False

    def pause(self) -> None:
        self.paused = True
        self._release_buttons()

    def move(self, x: float, y: float) -> None:
        if not self.enabled or self.paused:
            return
        q = self.q
        # Normalized points are mapped to the main display bounds. Quartz bounds
        # reflect display placement, including a non-zero origin where present.
        bounds = q.CGDisplayBounds(q.CGMainDisplayID())
        x = bounds.origin.x + min(1.0, max(0.0, x)) * max(0, bounds.size.width - 1)
        y = bounds.origin.y + min(1.0, max(0.0, y)) * max(0, bounds.size.height - 1)
        event = q.CGEventCreateMouseEvent(None, q.kCGEventMouseMoved, (x, y), q.kCGMouseButtonLeft)
        q.CGEventPost(q.kCGHIDEventTap, event)

    def click(self, button: str = "left", count: int = 1) -> None:
        if not self.enabled or self.paused:
            return
        q = self.q
        mapping = {"left": (q.kCGMouseButtonLeft, q.kCGEventLeftMouseDown, q.kCGEventLeftMouseUp),
                   "right": (q.kCGMouseButtonRight, q.kCGEventRightMouseDown, q.kCGEventRightMouseUp)}
        if button not in mapping:
            raise ValueError("button must be left or right")
        btn, down, up = mapping[button]
        pos = q.CGEventGetLocation(q.CGEventCreate(None))
        for _ in range(max(1, min(count, 2))):
            q.CGEventPost(q.kCGHIDEventTap, q.CGEventCreateMouseEvent(None, down, pos, btn))
            q.CGEventPost(q.kCGHIDEventTap, q.CGEventCreateMouseEvent(None, up, pos, btn))

    def right_click(self) -> None:
        self.click("right")

    def scroll(self, delta: int) -> None:
        if self.enabled and not self.paused:
            self.q.CGEventPost(self.q.kCGHIDEventTap, self.q.CGEventCreateScrollWheelEvent(None, self.q.kCGScrollEventUnitLine, 1, delta))

    def begin_drag(self) -> None:
        if self.enabled and not self.paused:
            q = self.q
            event = q.CGEventCreateMouseEvent(None, q.kCGEventLeftMouseDown, q.CGEventGetLocation(q.CGEventCreate(None)), q.kCGMouseButtonLeft)
            q.CGEventPost(q.kCGHIDEventTap, event)
            self._held.add(q.kCGMouseButtonLeft)

    def end_drag(self) -> None:
        self._release_buttons()

    def _release_buttons(self) -> None:
        q = self.q
        for button in tuple(self._held):
            event_type = q.kCGEventLeftMouseUp if button == q.kCGMouseButtonLeft else q.kCGEventRightMouseUp
            q.CGEventPost(q.kCGHIDEventTap, q.CGEventCreateMouseEvent(None, event_type, q.CGEventGetLocation(q.CGEventCreate(None)), button))
            self._held.discard(button)

    def emergency_stop(self) -> None:
        self._release_buttons()
        self.paused, self.enabled = True, False

    def close(self) -> None:
        self.emergency_stop()
