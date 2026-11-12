"""PyInstaller configuration helper; run with `python packaging/app_bundle_config.py`."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def build() -> None:
    from PyInstaller.__main__ import run
    run([str(ROOT / "packaging" / "FaceMousePro.spec")])


if __name__ == "__main__":
    build()
