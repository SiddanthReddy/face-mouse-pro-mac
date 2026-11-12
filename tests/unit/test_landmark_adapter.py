import pytest

from face_mouse_pro_mac.tracking.landmark_adapter import six_contour_points


def test_six_point_adapter_preserves_order_and_samples_evenly():
    source = tuple((i / 10, i / 10) for i in range(11))
    assert six_contour_points(source) == tuple((i / 10, i / 10) for i in range(0, 11, 2))


def test_short_or_out_of_range_contour_is_rejected():
    with pytest.raises(ValueError):
        six_contour_points(((0, 0),) * 5)
    with pytest.raises(ValueError):
        six_contour_points(((2, 0),) * 6)
