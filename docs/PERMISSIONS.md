# Permissions

Camera permission is requested when the user selects Start Camera. A denial must be changed in System Settings → Privacy & Security → Camera. The app does not attempt to capture until the camera service starts.

Quartz event injection requires Accessibility permission. Selecting Enable Pointer Control checks trust and opens no automatic grant; macOS must be allowed by the user under System Settings → Privacy & Security → Accessibility. `AXIsProcessTrustedWithOptions` can show the system prompt, but prompting does not grant access. Restart or re-activate after granting.

Permission prompts and actual physical devices cannot be validated by ordinary CI tests.
