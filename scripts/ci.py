"""The workflow reader, re-exported from the shared discipline.

`vendor/discipline/ci.py` is the one implementation - the corpus' own, copied
verbatim and pinned in `provenance/vendored-discipline.yaml`. This module stays
because the README's commands run as `python scripts/status.py` and the tests
import the reader as `ci`, and a second import path is much cheaper than a second
copy of the rules. A second copy is what this used to be: the three repositories
each read their own workflows, the copies had drifted into two different APIs,
and nothing compared them.

The extra path entry is the repository root, because when this module is imported
by `python scripts/status.py` the process' path begins at `scripts/`, and
`vendor/` is a directory beside it rather than inside it.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from vendor.discipline.ci import (  # noqa: E402,F401 - re-exported on purpose
    EXPRESSION,
    NAME,
    VERSION,
    checked_out_repositories,
    floor,
    interpreters,
    matrix_interpreters,
    order,
    runs_pytest,
    suspect,
    values_for,
    workflows,
)

__all__ = [
    "EXPRESSION",
    "NAME",
    "VERSION",
    "checked_out_repositories",
    "floor",
    "interpreters",
    "matrix_interpreters",
    "order",
    "runs_pytest",
    "suspect",
    "values_for",
    "workflows",
]
