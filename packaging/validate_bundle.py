"""Validate plist syntax and required usage text without building a signed app."""

import plistlib
from pathlib import Path

path = Path(__file__).with_name("Info.plist")
data = plistlib.loads(path.read_bytes())
assert data["CFBundleIdentifier"]
assert data["NSCameraUsageDescription"]
assert data["LSMinimumSystemVersion"] == "13.0"
spec_path = path.with_name("FaceMousePro.spec")
compile(spec_path.read_text(), str(spec_path), "exec")
print("Bundle plist validated")
