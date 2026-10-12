"""Make this repository and its `scripts/` importable from the tests.

`scripts/` is not a package: the commands in the README run as
`python scripts/build.py`, from the repository root, which is why `scripts/ci.py`
is imported as `ci`. A test that holds the CI's own declaration against the
floor has to read the same module the status board reads, so this file puts both
directories on `sys.path` once rather than in every test.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

for entry in (ROOT, ROOT / "scripts"):
    if str(entry) not in sys.path:
        sys.path.insert(0, str(entry))
