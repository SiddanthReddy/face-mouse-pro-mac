from face_mouse_pro_mac.application.coordinator import Coordinator
from face_mouse_pro_mac.tracking.protocol import FaceObservation


class Camera:
    def start(self, callback, device_id=None): self.callback = callback
    def stop(self): pass


class Tracker:
    def observe(self, frame, timestamp): return frame


class RecordingMouse:
    def __init__(self): self.positions = []; self.paused = True
    def move(self, x, y): self.positions.append((x, y))
    def click(self, button="left", count=1): pass
    def pause(self): self.paused = True
    def resume(self): self.paused = False
    def emergency_stop(self): self.paused = True
    def close(self): self.paused = True


def observation(x, timestamp):
    eye = ((0.1, 0.1), (0.2, 0.1), (0.3, 0.1), (0.4, 0.1), (0.5, 0.1), (0.6, 0.1))
    mouth = ((0.1, 0.1), (0.2, 0.1), (0.3, 0.1), (0.4, 0.1), (0.5, 0.1), (0.6, 0.1))
    return FaceObservation(timestamp, (x, 0.5), eye, eye, mouth, (x, 0.5))


def test_calibrated_observation_pipeline_moves_only_after_explicit_activation():
    camera, mouse = Camera(), RecordingMouse()
    coordinator = Coordinator(camera, Tracker(), mouse)
    coordinator.start()
    coordinator.calibrate_neutral(2)
    camera.callback(observation(0.5, 1.0), 1.0)
    camera.callback(observation(0.5, 1.1), 1.1)
    assert mouse.positions == []
    coordinator.activate_control()
    camera.callback(observation(0.7, 1.2), 1.2)
    assert len(mouse.positions) == 1
    coordinator.stop()
