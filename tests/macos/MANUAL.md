# Manual macOS and hardware checks

These checks require an actual supported Mac and are not run in CI:

- Camera enumeration, switching, permission grant/deny/revoke, and disconnect/interruption recovery.
- Live preview and Vision tracking with a single face, multiple faces, partial face, and varied lighting.
- Guided neutral calibration and threshold tuning for blink and mouth gestures.
- Accessibility grant, cursor movement, left/right/double click, drag toggle/release, scroll, pause, emergency stop, and shutdown.
- Main-display boundary behavior; test with more than one display to confirm the documented main-display limitation.
- Run with a clean account and inspect camera/privacy prompts and application logs.
