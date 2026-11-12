#!/bin/sh
set -eu
python packaging/app_bundle_config.py
echo "Built dist/Face Mouse Pro.app. The app is not Developer ID signed or notarized."
