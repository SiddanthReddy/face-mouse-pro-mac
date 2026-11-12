# Development

Use Python 3.11 and the project venv. Keep AVFoundation, Vision, AppKit, and Quartz code in platform-specific packages. Keep reusable math in the pinned shared core and adapt provider-specific coordinate contracts at explicit boundaries. All observation timestamps use `time.monotonic()` seconds. Do not commit camera frames or biometric observations. CI runs on macOS and validates code and mocks, not physical camera/permission behavior.
