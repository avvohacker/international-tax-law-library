"""The workflow reader, from the shared discipline.

`itl-discipline` is the one implementation - the corpus' own, installed at the tag
`requirements.txt` names rather than copied into `vendor/discipline/` and pinned by
hash. This module stays because the README's commands run as `python
scripts/status.py` and the tests import the reader as `ci`, and a second import
path is much cheaper than a second copy of the rules. A second copy is what this
used to be: each layer read its own workflows, the copies had drifted into two
different APIs, and nothing compared them.

The path entry this module used to add is gone with the copy: `vendor/` was a
directory beside `scripts/` rather than inside it, and an installed package needs
no help to be found.
"""
from itl_discipline.ci import (  # noqa: F401 - re-exported on purpose
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
