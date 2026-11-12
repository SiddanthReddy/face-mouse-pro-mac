from face_mouse_core.models import NormalizedPoint

from face_mouse_pro_mac.core_adapters.calibration import CalibrationAdapter
from face_mouse_pro_mac.core_adapters.cursor import CursorAdapter
from face_mouse_pro_mac.core_adapters.gestures import GestureAdapter


def test_calibration_neutral_and_deadzone():
    adapter = CalibrationAdapter(sample_target=2)
    assert adapter.add(NormalizedPoint(0.4, 0.5)) is None
    assert adapter.add(NormalizedPoint(0.6, 0.5)) == NormalizedPoint(0.5, 0.5)
    assert adapter.offset(NormalizedPoint(0.5, 0.5)).x == 0


def test_cursor_mapping_smoothing_monotonic():
    adapter = CursorAdapter()
    first = adapter.move(__import__("face_mouse_core.models", fromlist=["Vector2D"]).Vector2D(0, 0), 1.0)
    second = adapter.move(__import__("face_mouse_core.models", fromlist=["Vector2D"]).Vector2D(0.1, 0), 1.1)
    assert second.x >= first.x


def test_gesture_adapter_resets_on_face_loss():
    from face_mouse_core.gestures.types import GestureType
    assert GestureAdapter().update(None, 2.0) is GestureType.NONE
