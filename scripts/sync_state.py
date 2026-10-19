"""Copy src/newproj/state.py into the template, byte for byte (docs/DECISIONS.md, D-002).

Run from anywhere: uv run python scripts/sync_state.py
"""

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "src" / "newproj" / "state.py"
TARGET = ROOT / "template" / ".agents" / "skills" / "resume" / "scripts" / "state.py"

if __name__ == "__main__":
    shutil.copyfile(SOURCE, TARGET)
    print(f"Copied {SOURCE.relative_to(ROOT).as_posix()} to {TARGET.relative_to(ROOT).as_posix()}")
