# Architecture

The app uses a native AppKit shell, AVFoundation frame capture, Vision face landmarks, injectable Quartz mouse events, and the shared platform-neutral core at pinned commit `7ae514e29578f09a819ae4f5bb84218049e338e5`. macOS integrations live under `camera`, `tracking`, and `control`; shared-core translations live under `core_adapters`.

Vision provides sparse, contour-based face landmarks, not MediaPipe's indexed mesh. `landmark_adapter.py` transforms Vision's face-box-relative, bottom-left coordinates to image-normalized, top-left coordinates and samples six ordered points for each eye/lip contour. This intentionally approximate mapping needs camera-specific and user-specific measurement validation before threshold tuning. Largest face wins deterministically by bounding-box area.

The capture callback and tracking work run outside AppKit's main thread. UI status changes and a throttled live camera preview are scheduled on the main thread. The pointer is inert until explicit activation, is disabled on face loss or processing failure, and releases a held button during pause/shutdown. Settings are stored under Application Support; images and landmarks are not persisted. Pointer coordinates currently target the main display.

Deviation: preview rendering and guided calibration UX are not complete in this first implementation; see roadmap.
