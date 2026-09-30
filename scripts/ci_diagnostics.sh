#!/usr/bin/env bash
set -u

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="$ROOT_DIR/output/logs"
DIAG_DIR="$ROOT_DIR/output/diagnostics"
mkdir -p "$LOG_DIR" "$DIAG_DIR"

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
LOG_FILE="$LOG_DIR/workflow_${STAMP}.log"

# Send every line from this script to both GitHub Actions console and a file.
exec > >(tee -a "$LOG_FILE") 2>&1

set -x

echo "============================================================"
echo "SMART LEARNING LAB - CI DIAGNOSTIC SCRIPT"
echo "Started UTC: $(date -u)"
echo "Started IST: $(TZ=Asia/Kolkata date)"
echo "Run: ${GITHUB_RUN_NUMBER:-local}"
echo "Run ID: ${GITHUB_RUN_ID:-local}"
echo "Event: ${GITHUB_EVENT_NAME:-local}"
echo "Ref: ${GITHUB_REF:-local}"
echo "SHA: ${GITHUB_SHA:-local}"
echo "Python: $(python --version 2>&1 || true)"
echo "============================================================"

STATUS=0

if ! python -m compileall -q app; then
  echo "ERROR: Python compilation failed."
  STATUS=1
fi

if ! python -m unittest discover -s tests -v; then
  echo "ERROR: Smoke tests failed."
  STATUS=1
fi

if ! python -u -m app.run_agent --dry-run; then
  echo "ERROR: Dry-run blog generation failed."
  STATUS=1
fi

cat > "$DIAG_DIR/run_result.txt" <<RESULT
Smart Learning Lab diagnostic result
UTC: $(date -u)
IST: $(TZ=Asia/Kolkata date)
Status: $STATUS
Run: ${GITHUB_RUN_NUMBER:-local}
RESULT

find "$ROOT_DIR/output" -maxdepth 3 -type f -printf '%p | %s bytes\n' | sort || true

echo "============================================================"
echo "CI DIAGNOSTIC SCRIPT FINISHED WITH STATUS=$STATUS"
echo "Log file: $LOG_FILE"
echo "============================================================"

exit "$STATUS"
