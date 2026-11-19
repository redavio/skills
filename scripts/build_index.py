#!/usr/bin/env python3
"""Build skills.json from every skill's SKILL.md frontmatter (the single source of truth).

  python3 scripts/build_index.py          write skills.json
  python3 scripts/build_index.py --check  fail if skills.json is stale or a skill breaks the standard
Standard checks: name matches the folder, lowercase letters/digits/hyphens, <= 64 chars;
description present and <= 1024 chars; metadata has role, stage, summary, needs.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO_URL = "https://github.com/redavio/skills"
STAGES = ["role", "status", "set-up", "run", "review", "cadence"]


def frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        raise ValueError(f"{path}: no YAML frontmatter")
    out, sub = {}, None
    for line in m.group(1).splitlines():
        if not line.strip():
            continue
        if line.startswith("  ") and sub is not None:
            k, v = line.strip().split(":", 1)
            out[sub][k.strip()] = v.strip().strip('"')
            continue
        k, v = line.split(":", 1)
        k, v = k.strip(), v.strip()
        if v == "":
            out[k], sub = {}, k
        else:
            out[k], sub = v.strip('"'), None
    return out


def build() -> tuple[list, list]:
    skills, errs = [], []
    for f in sorted(ROOT.glob("skills/*/SKILL.md")):
        d = f.parent.name
        try:
            fm = frontmatter(f)
        except ValueError as e:
            errs.append(str(e)); continue
        name, desc, meta = fm.get("name", ""), fm.get("description", ""), fm.get("metadata", {})
        if name != d:
            errs.append(f"{d}: name '{name}' must match the folder")
        if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name) or len(name) > 64:
            errs.append(f"{d}: name must be lowercase letters, digits and single hyphens, <= 64 chars")
        if not desc or len(desc) > 1024:
            errs.append(f"{d}: description missing or over 1024 characters ({len(desc)})")
        for k in ("role", "stage", "summary", "needs"):
            if not meta.get(k):
                errs.append(f"{d}: metadata.{k} missing")
        if meta.get("stage") and meta["stage"] not in STAGES:
            errs.append(f"{d}: stage must be one of {STAGES}")
        skills.append({"name": name, "role": meta.get("role"), "stage": meta.get("stage"),
                       "description": meta.get("summary"), "needs": [n.strip() for n in meta.get("needs", "").split(";") if n.strip()],
                       "path": f"skills/{d}", "has_scripts": (f.parent / "scripts").is_dir(),
                       "install": f"npx skills add redavio/skills --skill {name}",
                       "zip": f"dist/{name}.zip"})
    skills.sort(key=lambda s: (s["role"] or "", STAGES.index(s["stage"]) if s["stage"] in STAGES else 99))
    return skills, errs


def index(skills):
    return {"repo": REPO_URL, "standard": "https://agentskills.io", "license": "MIT",
            "roles": {"paid-search-lead": "Demand capture on Google and Microsoft Ads: Search, AI Max, Performance Max."},
            "stages": STAGES, "skills": skills}


if __name__ == "__main__":
    skills, errs = build()
    data = json.dumps(index(skills), indent=2) + "\n"
    target = ROOT / "skills.json"
    if "--check" in sys.argv:
        if not target.exists() or target.read_text() != data:
            errs.append("skills.json is stale: run python3 scripts/build_index.py")
        if errs:
            print("\n".join(errs)); sys.exit(1)
        print(f"{len(skills)} skills OK"); sys.exit(0)
    if errs:
        print("\n".join(errs)); sys.exit(1)
    target.write_text(data)
    print(f"skills.json: {len(skills)} skills")
