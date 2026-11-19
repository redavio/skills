"""Repo integrity: skills.json is current, every skill meets the standard, runners are identical."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_index_current_and_skills_valid():
    r = subprocess.run([sys.executable, "scripts/build_index.py", "--check"], cwd=ROOT, capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr


def test_runners_identical():
    canon = (ROOT / "scripts" / "skill_run.py").read_text()
    for run in ROOT.glob("skills/*/scripts/run.py"):
        assert run.read_text() == canon, f"{run} differs: run scripts/sync_run.sh"


def test_every_job_skill_has_the_sections():
    for f in ROOT.glob("skills/*/SKILL.md"):
        text = f.read_text()
        assert "## Getting the data" in text, f
        if "stage: cadence" in text or "stage: role" in text:
            continue
        for h in ("## Needs", "## If something is missing", "## Method", "## Output"):
            assert h in text, f"{f.parent.name} missing {h}"
