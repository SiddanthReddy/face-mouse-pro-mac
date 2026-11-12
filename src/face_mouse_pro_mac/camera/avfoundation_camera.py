"""AVFoundation capture. Frames are delivered on its capture queue, never AppKit's UI thread."""

from __future__ import annotations

import threading
import time
from collections.abc import Callable
from typing import Protocol, cast

from .protocol import CameraDevice


class _NSObjectInstance(Protocol):
    def init(self) -> _NSObjectInstance: ...


class _NSObjectClass(Protocol):
    def alloc(self) -> _NSObjectInstance: ...


class AVFoundationCamera:
    def __init__(self) -> None:
        if __import__("sys").platform != "darwin":
            raise RuntimeError("AVFoundation camera capture is available only on macOS")
        import AVFoundation  # type: ignore[import-not-found]
        import CoreMedia  # type: ignore[import-not-found]
        import dispatch  # type: ignore[import-not-found]
        import Foundation  # type: ignore[import-not-found]

        self.AVFoundation = AVFoundation
        self.CoreMedia = CoreMedia
        self.Foundation = Foundation
        self.dispatch = dispatch
        self.session = None
        self.output = None
        self.delegate: _NSObjectInstance | None = None
        self.error_callback = lambda _message: None
        self._notification_tokens: list[object] = []
        self._lock = threading.RLock()

    def devices(self) -> list[CameraDevice]:
        av = self.AVFoundation
        discovery = av.AVCaptureDeviceDiscoverySession.discoverySessionWithDeviceTypes_mediaType_position_(
            [av.AVCaptureDeviceTypeBuiltInWideAngleCamera, av.AVCaptureDeviceTypeExternal],
            av.AVMediaTypeVideo,
            av.AVCaptureDevicePositionUnspecified,
        )
        return [CameraDevice(str(d.uniqueID()), str(d.localizedName())) for d in discovery.devices()]

    def start(self, callback: Callable[[object, float], None], device_id: str | None = None) -> None:
        with self._lock:
            if self.session is not None:
                return
            av = self.AVFoundation
            devices = av.AVCaptureDevice.devicesWithMediaType_(av.AVMediaTypeVideo)
            device = next((d for d in devices if not device_id or str(d.uniqueID()) == device_id), None)
            if device is None:
                raise RuntimeError("No matching camera is available")
            session = av.AVCaptureSession.alloc().init()
            input_device, error = av.AVCaptureDeviceInput.deviceInputWithDevice_error_(device, None)
            if input_device is None:
                raise RuntimeError(f"Unable to open camera: {error}")
            output = av.AVCaptureVideoDataOutput.alloc().init()
            output.setAlwaysDiscardsLateVideoFrames_(True)
            def capture_output(_delegate, _out, sample, _connection):
                callback(sample, time.monotonic())

            def capture_dropped_sample(_delegate, _out, _sample, _connection):
                return

            delegate_class = cast(
                _NSObjectClass,
                type(
                    "Delegate",
                    (self.Foundation.NSObject,),
                    {
                        "captureOutput_didOutputSampleBuffer_fromConnection_": capture_output,
                        "captureOutput_didDropSampleBuffer_fromConnection_": capture_dropped_sample,
                    },
                ),
            )
            self.delegate = delegate_class.alloc().init()
            self._queue = self.dispatch.dispatch_queue_create("com.siddanthreddy.facemousepro.capture", None)
            output.setSampleBufferDelegate_queue_(self.delegate, self._queue)
            if not session.canAddInput_(input_device) or not session.canAddOutput_(output):
                raise RuntimeError("Camera session rejected its input or video output")
            session.addInput_(input_device)
            session.addOutput_(output)
            self.session, self.output = session, output
            center = self.Foundation.NSNotificationCenter.defaultCenter()
            self._notification_tokens = [
                center.addObserverForName_object_queue_usingBlock_(
                    av.AVCaptureSessionWasInterruptedNotification, session, None,
                    lambda _note: self.error_callback("Camera session was interrupted"),
                ),
                center.addObserverForName_object_queue_usingBlock_(
                    av.AVCaptureSessionRuntimeErrorNotification, session, None,
                    lambda note: self.error_callback(f"Camera session error: {note.userInfo()}"),
                ),
            ]
            session.startRunning()

    def stop(self) -> None:
        with self._lock:
            center = self.Foundation.NSNotificationCenter.defaultCenter()
            for token in self._notification_tokens:
                center.removeObserver_(token)
            self._notification_tokens.clear()
            if self.output is not None:
                self.output.setSampleBufferDelegate_queue_(None, None)
            if self.session is not None and self.session.isRunning():
                self.session.stopRunning()
            self.session = self.output = self.delegate = None
