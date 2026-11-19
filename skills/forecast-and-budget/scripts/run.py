#!/usr/bin/env python3
"""Run the playbook math or an ad platform script from inside a skill.

  python3 <skill>/scripts/run.py perfos <command> [options]   the math, e.g. perfos gate --help
  python3 <skill>/scripts/run.py ads <script> [options]       e.g. ads google_report search_terms --days 28

The shared code is found in, in order: $REDAVIO_SKILLS_SHARED; this skill's scripts/_vendor
(ZIP download); the repo's shared/ folder (git clone or npx skills install from the repo);
an installed perfos package (pip install "git+https://github.com/redavio/skills#subdirectory=shared").
This file is identical in every skill; edit scripts/skill_run.py at the repo root, then run
scripts/sync_run.sh.
"""
import os
import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def roots():
    env = os.environ.get("REDAVIO_SKILLS_SHARED")
    if env:
        yield Path(env)
    yield HERE / "_vendor"
    for p in [HERE, *HERE.parents]:
        yield p / "shared"


def find(sub):
    for r in roots():
        if (r / sub).is_dir():
            return r
    return None


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ("perfos", "ads"):
        sys.exit(__doc__)
    kind, rest = sys.argv[1], sys.argv[2:]
    if kind == "perfos":
        root = find("perfos")
        if root:
            sys.path.insert(0, str(root))
        try:
            from perfos import cli
        except ImportError:
            sys.exit('perfos not found. pip install "git+https://github.com/redavio/skills#subdirectory=shared" '
                     "or download this skill as a ZIP (it bundles the math).")
        cli.main(rest)
        return
    root = find("ads_scripts")
    if not root or not rest:
        sys.exit("Ad platform scripts not found (or no script named). They ship in the repo's shared/ads_scripts "
                 "and inside each skill ZIP.")
    script = root / "ads_scripts" / (rest[0] if rest[0].endswith(".py") else rest[0] + ".py")
    if not script.exists():
        sys.exit(f"No script {script.name}. Available: " +
                 ", ".join(sorted(p.stem for p in (root / 'ads_scripts').glob('*.py') if not p.stem.startswith('_'))))
    sys.path.insert(0, str(root))
    sys.argv = [str(script), *rest[1:]]
    runpy.run_path(str(script), run_name="__main__")


if __name__ == "__main__":
    main()
