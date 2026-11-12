import pytest

from face_mouse_pro_mac.application.settings import Settings, SettingsStore


def test_settings_round_trip(tmp_path):
    store = SettingsStore(tmp_path / "nested" / "settings.json")
    settings = Settings(camera_id="device-1", sensitivity=1.7)
    store.save(settings)
    assert store.load() == settings


def test_invalid_settings_rejected():
    with pytest.raises(ValueError):
        Settings(sensitivity=99).validate()
