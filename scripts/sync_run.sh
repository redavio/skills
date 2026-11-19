#!/usr/bin/env bash
# Copy the canonical runner into every skill that has a scripts/ folder.
set -euo pipefail
cd "$(dirname "$0")/.."
for d in skills/*/scripts; do
  cp scripts/skill_run.py "$d/run.py"
done
echo "runner synced"
