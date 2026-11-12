"""AppKit entry point."""

import sys


def main() -> None:
    if sys.platform != "darwin":
        raise SystemExit("Face Mouse Pro for macOS requires macOS 13 or newer")
    from AppKit import NSApplication  # type: ignore[import-not-found]

    from .ui.app_delegate import AppDelegate

    app = NSApplication.sharedApplication()
    app.setActivationPolicy_(0)
    delegate = AppDelegate.alloc().init()
    app.setDelegate_(delegate)
    app.run()


if __name__ == "__main__":
    main()
