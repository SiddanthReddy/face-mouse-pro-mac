from pathlib import Path

from PyInstaller.utils.hooks import collect_all

ROOT = Path(SPECPATH).parent.parent
datas, binaries, hiddenimports = [], [], []
for framework in ("AVFoundation", "Vision", "Quartz", "CoreMedia", "CoreVideo", "CoreImage", "dispatch"):
    framework_datas, framework_binaries, framework_hidden = collect_all(framework)
    datas += framework_datas
    binaries += framework_binaries
    hiddenimports += framework_hidden

a = Analysis(
    [str(ROOT / "src" / "face_mouse_pro_mac" / "app.py")],
    pathex=[str(ROOT / "src")],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="Face Mouse Pro",
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=str(ROOT / "packaging" / "entitlements.plist"),
)
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name="Face Mouse Pro")
app = BUNDLE(
    coll,
    name="Face Mouse Pro.app",
    bundle_identifier="com.siddanthreddy.facemousepro",
    info_plist={
        "CFBundleName": "Face Mouse Pro",
        "CFBundleDisplayName": "Face Mouse Pro",
        "CFBundleVersion": "0.1.0",
        "CFBundleShortVersionString": "0.1.0",
        "LSMinimumSystemVersion": "13.0",
        "NSCameraUsageDescription": "Face Mouse Pro uses the camera to estimate face landmarks for hands-free pointer control. Frames are processed locally and are not saved.",
        "NSHumanReadableCopyright": "Copyright © 2026 Siddanth Reddy",
        "NSPrincipalClass": "NSApplication",
    },
)
