"""Compact AppKit dashboard. Hardware services are loaded lazily after user action."""

from __future__ import annotations

import threading

import objc  # type: ignore[import-not-found]
from AppKit import (  # type: ignore[import-not-found]
    NSBackingStoreBuffered, NSButton, NSComboBox, NSMakeRect, NSSlider, NSWindow, NSWindowStyleMaskClosable,
    NSWindowStyleMaskMiniaturizable, NSWindowStyleMaskTitled,
)
from Foundation import NSObject  # type: ignore[import-not-found]


class MainWindowController(NSObject):
    def init(self):
        self = objc.super(MainWindowController, self).init()
        if self is None:
            return None
        style = NSWindowStyleMaskTitled | NSWindowStyleMaskClosable | NSWindowStyleMaskMiniaturizable
        self.window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(NSMakeRect(0, 0, 660, 600), style, NSBackingStoreBuffered, False)
        self.window.setTitle_("Face Mouse Pro")
        self.window.center()
        self.status = self._label("Welcome. Camera and pointer control start only when you choose.", 24, 548, 600, 32)
        self.camera_button = self._button("Start Camera", "startCamera:", 24, 488, 190)
        self.refresh_button = self._button("Refresh Cameras", "refreshCameras:", 430, 488, 190)
        self.calibrate_button = self._button("Calibrate Neutral", "calibrate:", 230, 488, 190)
        self.activate_button = self._button("Enable Pointer Control", "activate:", 24, 432, 250)
        self.pause_button = self._button("Pause", "pause:", 290, 432, 120)
        self.stop_button = self._button("Emergency Stop", "stop:", 430, 432, 190)
        self.permission = self._label("Camera permission is requested when Start Camera is selected. Accessibility permission is required to activate pointer control.", 24, 360, 600, 52)
        self.camera_picker = NSComboBox.alloc().initWithFrame_(NSMakeRect(24, 305, 360, 30))
        self.camera_picker.setPlaceholderString_("Choose a camera")
        self.view.addSubview_(self.camera_picker)
        self.sensitivity = NSSlider.alloc().initWithFrame_(NSMakeRect(400, 305, 180, 28))
        self.sensitivity.setMinValue_(0.1)
        self.sensitivity.setMaxValue_(4.0)
        self.sensitivity.setDoubleValue_(1.0)
        self.sensitivity.setTarget_(self)
        self.sensitivity.setAction_(objc.selector(self.settingsChanged_, signature=b"v@:@"))
        self.view.addSubview_(self.sensitivity)
        self.sensitivity_label = self._label("Cursor sensitivity", 400, 335, 180, 24)
        self.blink_threshold = self._setting_slider(24, 250, 0.05, 0.5)
        self.mouth_threshold = self._setting_slider(330, 250, 0.05, 1.0)
        self._label("Blink threshold", 24, 277, 250, 24)
        self._label("Mouth threshold", 330, 277, 250, 24)
        from AppKit import NSImageView
        self.preview = NSImageView.alloc().initWithFrame_(NSMakeRect(24, 35, 612, 170))
        self.preview.setImageScaling_(2)
        self.view.addSubview_(self.preview)
        self.window.setContentView_(self.view)
        self.coordinator = None
        self._camera_devices = []
        from ..application.settings import SettingsStore
        self.settings_store = SettingsStore()
        try:
            self.settings = self.settings_store.load()
            self.sensitivity.setDoubleValue_(self.settings.sensitivity)
            self.blink_threshold.setDoubleValue_(self.settings.blink_threshold)
            self.mouth_threshold.setDoubleValue_(self.settings.mouth_threshold)
        except (ValueError, OSError):
            from ..application.settings import Settings
            self.settings = Settings()
        return self

    def _label(self, text, x, y, w, h):
        from AppKit import NSTextField
        if not hasattr(self, "view"):
            self.view = __import__("AppKit").NSView.alloc().initWithFrame_(NSMakeRect(0, 0, 660, 600))
        label = NSTextField.alloc().initWithFrame_(NSMakeRect(x, y, w, h))
        label.setStringValue_(text)
        label.setEditable_(False)
        label.setBordered_(False)
        label.setDrawsBackground_(False)
        self.view.addSubview_(label)
        return label

    def _button(self, title, action, x, y, width):
        button = NSButton.alloc().initWithFrame_(NSMakeRect(x, y, width, 38))
        button.setTitle_(title)
        button.setTarget_(self)
        button.setAction_(objc.selector(getattr(self, action), signature=b"v@:@"))
        self.view.addSubview_(button)
        return button

    def _setting_slider(self, x, y, minimum, maximum):
        slider = NSSlider.alloc().initWithFrame_(NSMakeRect(x, y, 250, 28))
        slider.setMinValue_(minimum)
        slider.setMaxValue_(maximum)
        slider.setTarget_(self)
        slider.setAction_(objc.selector(self.settingsChanged_, signature=b"v@:@"))
        self.view.addSubview_(slider)
        return slider

    def showWindow_(self, _sender):
        self.window.makeKeyAndOrderFront_(None)

    def startCamera_(self, _sender):
        try:
            if not self._camera_devices:
                self.refreshCameras_(None)
                if self._camera_devices:
                    self._set_status("Choose a camera, then select Start Camera again.")
                return
            from ..control.permissions import camera_authorization_status, request_camera_access
            state = camera_authorization_status()
            if state == "not_determined":
                request_camera_access(
                    lambda allowed: self.performSelectorOnMainThread_withObject_waitUntilDone_(
                        "cameraAccessResult:", bool(allowed), False
                    )
                )
                return
            if state != "authorized":
                self._set_status(f"Camera access is {state}. Enable it in System Settings → Privacy & Security → Camera.")
                return
            self._start_services()
        except Exception as exc:
            self._set_status(f"Unable to start camera: {exc}")

    def cameraAccessResult_(self, allowed):
        if allowed:
            self._start_services()
        else:
            self._set_status("Camera permission denied. Enable it in System Settings → Privacy & Security → Camera.")

    def refreshCameras_(self, _sender):
        try:
            from ..camera.avfoundation_camera import AVFoundationCamera
            self._camera_devices = AVFoundationCamera().devices()
            self.camera_picker.removeAllItems()
            for device in self._camera_devices:
                self.camera_picker.addItemWithObjectValue_(device.name)
            saved_index = next(
                (i for i, device in enumerate(self._camera_devices) if device.identifier == self.settings.camera_id),
                0 if self._camera_devices else -1,
            )
            if saved_index >= 0:
                self.camera_picker.selectItemAtIndex_(saved_index)
            self._set_status(f"Found {len(self._camera_devices)} camera(s)")
        except Exception as exc:
            self._set_status(f"Unable to enumerate cameras: {exc}")

    def _start_services(self):
        try:
            from ..camera.avfoundation_camera import AVFoundationCamera
            from ..control.quartz_mouse_controller import QuartzMouseController
            from ..tracking.vision_face_tracker import VisionFaceTracker
            from ..application.coordinator import Coordinator
            camera = AVFoundationCamera()
            self.coordinator = Coordinator(camera, VisionFaceTracker(), QuartzMouseController())
            self.coordinator.status_callback = self._set_status
            self.coordinator.preview_callback = self._update_preview
            selected = self.camera_picker.indexOfSelectedItem()
            camera_id = self._camera_devices[selected].identifier if 0 <= selected < len(self._camera_devices) else self.settings.camera_id
            self.settings.camera_id = camera_id
            self.settings_store.save(self.settings)
            from face_mouse_core.config import CursorMappingConfig
            from face_mouse_core.config import GestureConfig
            self.coordinator.cursor.mapper.config = CursorMappingConfig(
                sensitivity_x=2.2 * self.settings.sensitivity,
                sensitivity_y=2.0 * self.settings.sensitivity,
            )
            self.coordinator.gestures.detector.update_config(
                GestureConfig(
                    blink_ear_threshold=self.settings.blink_threshold,
                    mouth_mar_threshold=self.settings.mouth_threshold,
                )
            )
            threading.Thread(target=self.coordinator.start, args=(camera_id,), daemon=True).start()
        except Exception as exc:
            self._set_status(f"Unable to start services: {exc}")

    def calibrate_(self, _sender):
        self._set_status("Look straight at the camera; collecting 20 neutral face samples.")
        if self.coordinator:
            self.coordinator.calibrate_neutral(20)

    def settingsChanged_(self, _sender):
        from face_mouse_core.config import CursorMappingConfig, GestureConfig
        self.settings.sensitivity = float(self.sensitivity.doubleValue())
        self.settings.blink_threshold = float(self.blink_threshold.doubleValue())
        self.settings.mouth_threshold = float(self.mouth_threshold.doubleValue())
        try:
            self.settings_store.save(self.settings)
            if self.coordinator:
                self.coordinator.cursor.mapper.config = CursorMappingConfig(
                    sensitivity_x=2.2 * self.settings.sensitivity,
                    sensitivity_y=2.0 * self.settings.sensitivity,
                )
                self.coordinator.gestures.detector.update_config(
                    GestureConfig(
                        blink_ear_threshold=self.settings.blink_threshold,
                        mouth_mar_threshold=self.settings.mouth_threshold,
                    )
                )
        except (ValueError, OSError) as exc:
            self._set_status(f"Could not save settings: {exc}")

    def activate_(self, _sender):
        try:
            if self.coordinator is None:
                self._set_status("Start the camera and calibrate first.")
                return
            self.coordinator.activate_control()
        except PermissionError:
            from ..control.permissions import accessibility_trusted
            accessibility_trusted(prompt=True)
            self._set_status("Grant Accessibility in System Settings → Privacy & Security → Accessibility, then activate again.")
        except RuntimeError as exc:
            self._set_status(str(exc))

    def pause_(self, _sender):
        if self.coordinator:
            self.coordinator.pause()

    def stop_(self, _sender):
        if self.coordinator:
            self.coordinator.mouse.emergency_stop()
            self.coordinator.control_active = False
            self._set_status("Emergency stop — pointer disabled")

    def _set_status(self, text):
        # Status callback is invoked on the capture queue; schedule the view update on main.
        self.status.performSelectorOnMainThread_withObject_waitUntilDone_("setStringValue:", text, False)

    def _update_preview(self, sample):
        self.performSelectorOnMainThread_withObject_waitUntilDone_("renderPreview:", sample, False)

    def renderPreview_(self, sample):
        try:
            import CoreMedia
            from CoreImage import CIImage
            from AppKit import NSImage, NSCIImageRep
            pixel_buffer = CoreMedia.CMSampleBufferGetImageBuffer(sample)
            ci_image = CIImage.imageWithCVPixelBuffer_(pixel_buffer)
            rep = NSCIImageRep.imageRepWithCIImage_(ci_image)
            image = NSImage.alloc().initWithSize_(rep.size())
            image.addRepresentation_(rep)
            self.preview.performSelectorOnMainThread_withObject_waitUntilDone_("setImage:", image, False)
        except Exception:
            self._set_status("Camera active; preview unavailable")

    def shutdown(self):
        if self.coordinator:
            self.coordinator.stop()
