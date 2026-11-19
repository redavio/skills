#!/usr/bin/env bash
# Build one ZIP per skill into dist/, ready to upload to Claude.ai (Settings > Capabilities > Skills)
# or to unzip into any Agent Skills client. Skills with a scripts/ folder get the shared math
# (shared/perfos) and ad platform scripts (shared/ads_scripts) bundled in scripts/_vendor,
# so each ZIP works on its own.
#   bash scripts/zip_skills.sh            all skills
#   bash scripts/zip_skills.sh volume-gate audit
set -euo pipefail
cd "$(dirname "$0")/.."
rm -rf dist && mkdir -p dist
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
names=("$@")
if [ ${#names[@]} -eq 0 ]; then
  names=()
  for d in skills/*/; do names+=("$(basename "$d")"); done
fi
for name in "${names[@]}"; do
  src="skills/$name"
  [ -f "$src/SKILL.md" ] || { echo "no skill: $name" >&2; exit 1; }
  rsync -a --exclude '__pycache__' --exclude '.DS_Store' "$src/" "$tmp/$name/"
  if [ -d "$src/scripts" ]; then
    mkdir -p "$tmp/$name/scripts/_vendor"
    rsync -a --exclude '__pycache__' shared/perfos "$tmp/$name/scripts/_vendor/"
    rsync -a --exclude '__pycache__' shared/ads_scripts "$tmp/$name/scripts/_vendor/"
    cp LICENSE "$tmp/$name/LICENSE"
  fi
  (cd "$tmp" && zip -qr "$OLDPWD/dist/$name.zip" "$name")
done
echo "${#names[@]} skill ZIPs in dist/"
