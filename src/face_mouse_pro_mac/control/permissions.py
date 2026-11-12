"""macOS camera and Accessibility permission checks."""

import sys


def camera_authorization_status() -> str:
    if sys.platform != "darwin":
        return "unavailable"
    import AVFoundation  # type: ignore[import-not-found]

    values = {0: "not_determined", 1: "restricted", 2: "denied", 3: "authorized"}
    status = AVFoundation.AVCaptureDevice.authorizationStatusForMediaType_(AVFoundation.AVMediaTypeVideo)
    return values.get(int(status), "unknown")


def request_camera_access(callback) -> None:
    if sys.platform != "darwin":
        callback(False)
        return
    import AVFoundation  # type: ignore[import-not-found]

    AVFoundation.AVCaptureDevice.requestAccessForMediaType_completionHandler_(
        AVFoundation.AVMediaTypeVideo, callback
    )


def accessibility_trusted(prompt: bool = False) -> bool:
    if sys.platform != "darwin":
        return False
    import Quartz  # type: ignore[import-not-found]

    options = {Quartz.kAXTrustedCheckOptionPrompt: True} if prompt else None
    return bool(Quartz.AXIsProcessTrustedWithOptions(options))
