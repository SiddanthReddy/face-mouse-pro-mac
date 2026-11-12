from face_mouse_pro_mac.application.coordinator import Coordinator
from face_mouse_core.models import NormalizedPoint


class FakeCamera:
    def __init__(self): self.callback = None
    def start(self, callback, device_id=None): self.callback = callback
    def stop(self): self.callback = None


class FakeTracker:
    def observe(self, frame, timestamp): return None


class FakeMouse:
    def __init__(self): self.paused = True; self.stopped = False
    def move(self, x, y): raise AssertionError("face loss should suppress movement")
    def click(self, button="left", count=1): raise AssertionError("face loss should suppress clicks")
    def pause(self): self.paused = True
    def resume(self): self.paused = False
    def emergency_stop(self): self.stopped = True
    def close(self): self.stopped = True


def test_face_loss_safely_pauses_and_shutdown_releases_resources():
    camera, mouse = FakeCamera(), FakeMouse()
    coordinator = Coordinator(camera, FakeTracker(), mouse)
    coordinator.start()
    coordinator.calibration.neutral = NormalizedPoint(0.5, 0.5)
    coordinator.activate_control()
    camera.callback(object(), 1.0)
    assert not coordinator.control_active
    assert mouse.paused
    coordinator.stop()
    assert camera.callback is None
    assert mouse.stopped
