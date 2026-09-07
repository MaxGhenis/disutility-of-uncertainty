#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
audit_python="${AUDIT_PYTHON:-/Users/maxghenis/disutility-of-uncertainty-calibration-20260907/.venv/bin/python}"
"$audit_python" scripts/audit.py
"$audit_python" scripts/sensitivity.py
"$audit_python" scripts/verify_native_arithmetic.py
"$audit_python" scripts/report.py
"$audit_python" -m pytest tests -q -o addopts=''
