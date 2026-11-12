# Installation and packaging

Use macOS 13+, Python 3.11, and create a project venv. Install `.[macos,dev]` and launch `face-mouse-pro-mac`. Install through the Git pin in `pyproject.toml`; do not edit the shared-core checkout to develop this app.

## Packaging

Run `sh packaging/build_macos.sh` on macOS. PyInstaller bundles Python and attempts collection of PyObjC frameworks. The resulting app may receive an ad-hoc signature from PyInstaller, but it is not Developer ID signed or notarized; macOS privacy APIs may require additional signing configuration. Do not bypass Gatekeeper. No icon is included yet. Validate on a clean macOS account before distribution.
