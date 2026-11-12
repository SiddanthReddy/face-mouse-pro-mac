"""Small validated JSON preference store; camera frames and biometric data are never persisted."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class Settings:
    camera_id: str | None = None
    sensitivity: float = 1.0
    blink_threshold: float = 0.16
    mouth_threshold: float = 0.30

    def validate(self) -> None:
        if not 0.1 <= self.sensitivity <= 4:
            raise ValueError("sensitivity must be between 0.1 and 4")
        if not 0.01 <= self.blink_threshold <= 1:
            raise ValueError("blink threshold must be between 0.01 and 1")
        if not 0.01 <= self.mouth_threshold <= 2:
            raise ValueError("mouth threshold must be between 0.01 and 2")


class SettingsStore:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or Path.home() / "Library" / "Application Support" / "Face Mouse Pro" / "settings.json"

    def load(self) -> Settings:
        if not self.path.exists():
            return Settings()
        data = json.loads(self.path.read_text())
        settings = Settings(**data)
        settings.validate()
        return settings

    def save(self, settings: Settings) -> None:
        settings.validate()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(asdict(settings), indent=2) + "\n")
