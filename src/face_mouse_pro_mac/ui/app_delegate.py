from __future__ import annotations

from AppKit import NSApplication  # type: ignore[import-not-found]
from Foundation import NSObject  # type: ignore[import-not-found]

from .main_window import MainWindowController


class AppDelegate(NSObject):
    def applicationDidFinishLaunching_(self, _notification):
        self.window_controller = MainWindowController.alloc().init()
        self.window_controller.showWindow_(None)
        NSApplication.sharedApplication().activateIgnoringOtherApps_(True)

    def applicationShouldTerminateAfterLastWindowClosed_(self, _app):
        return True

    def applicationWillTerminate_(self, _notification):
        if getattr(self, "window_controller", None):
            self.window_controller.shutdown()
