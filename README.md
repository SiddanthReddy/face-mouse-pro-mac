# Face Mouse Pro for macOS

Hands-free pointer control experiment built with AppKit, AVFoundation, Apple Vision, Quartz, and the shared [face-mouse-pro-core](https://github.com/SiddanthReddy/face-mouse-pro-core). Camera images are processed locally and are not recorded.

> Early implementation: face tracking and an opt-in pointer pipeline are present. The sparse Vision contour adapter is an approximation and needs real-user calibration. Review the limitations before enabling pointer control.

## Features

- Native AppKit dashboard and explicit camera/pointer activation controls.
- AVFoundation camera discovery/capture on a capture queue; Vision face landmark requests.
- Deterministic largest-face selection, timestamp validation, normalized coordinate conversion.
- Shared-core gesture, calibration, cursor mapping, deadzone and One Euro smoothing adapters.
- Quartz pointer, click, double click, right click, drag, scrolling, pause, emergency stop, and release on shutdown.
- Persistent validated preferences; no frame or landmark persistence.

## Requirements and installation

macOS 13 or newer and Python 3.11. From a clone:

```sh
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[macos,dev]'
face-mouse-pro-mac
```

The core dependency is pinned to commit `7ae514e29578f09a819ae4f5bb84218049e338e5`.

## Setup and use

Select **Start Camera** to request camera access and begin tracking. Follow the on-screen status. Calibrate while looking at the camera, then explicitly choose **Enable Pointer Control**. Grant Accessibility access in System Settings when prompted, return to the app, and activate again. **Pause** releases held buttons; **Emergency Stop** disables pointer injection. Face loss pauses control and requires an explicit reactivation.

Read [installation](docs/INSTALLATION.md), [permissions](docs/PERMISSIONS.md), and [architecture](docs/ARCHITECTURE.md) before use. Initial screenshots are intentionally omitted until captured from the running macOS app.

## Testing and development

```sh
pytest -q
ruff check src tests
mypy src
python -m compileall -q src tests
```

See [testing](docs/TESTING.md) and [development](docs/DEVELOPMENT.md). Automated tests use mocks and never post system mouse events.

## Packaging

`sh packaging/build_macos.sh` prepares an app bundle using PyInstaller. See [packaging notes](docs/INSTALLATION.md#packaging). This project has not been Developer ID signed or notarized.

## Limitations and roadmap

Vision eye and lip contours are sparse and differ from MediaPipe mesh indices; the adapter samples the contours into the shared core's six-point contract. Thresholds are provisional, and there are no accuracy claims. Guided multipoint calibration, end-to-end manual testing, signed distribution, and notarization are future milestones. Pointer coordinates currently map to the main display; multi-display selection remains future work.
