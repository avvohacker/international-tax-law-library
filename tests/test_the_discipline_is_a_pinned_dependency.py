"""The shared discipline arrives as a dependency pinned to a tag, not a copy.

`itl-discipline` is the corpus' implementation of the rules this family shares -
what may not be committed about a machine, how a workflow is read, what a status
board owes a reader. It used to be copied into `vendor/discipline/` and pinned by
hash in `provenance/vendored-discipline.yaml`; both are gone, and with them the
drift between a copy and its source: there is nothing here to compare with the
corpus, because there is nothing here to freeze.

What can still go wrong is the pin, and that is what this file holds:

  * the requirement must name a **tag**, not a branch. A branch moves under a
    checkout, so a repository that says it holds these rules while the rules
    change beneath it has the defect the pinned copy had, only harder to see: no
    line of this repository changes when it happens;
  * the distribution must really expose what this repository reads from it - the
    workflow reader (`ci`), the machine-trace rule, the board rule - so a package
    that renamed or dropped one is a red run here rather than an import error in a
    reader's checkout.

The rule is then *run*, not only imported: a package that imports and refuses
nothing proves nothing, and the run under this repository's CI identity is where
it was, in `tests/test_no_machine_traces.py`.
"""
import re
from pathlib import Path

from itl_discipline import board, ci, machine_traces

ROOT = Path(__file__).resolve().parent.parent
REQUIREMENTS = ROOT / "requirements.txt"

# `name @ url#subdirectory=path`, the form requirements.txt uses for a package
# that is not on an index.
REQUIREMENT = re.compile(
    r"^\s*itl-discipline\s*@\s*(?P<url>\S+?)#subdirectory=(?P<path>\S+)\s*$", re.M)
# A ref that cannot move: a version tag, `v1.2.3` or `discipline-v1.2.3`. A ref
# with a slash is a branch (`user/thing`) and a bare word is one too (`main`).
TAG = re.compile(r"^[A-Za-z0-9._-]*v?\d+\.\d+(\.\d+)?$")
CORPUS = "github.com/avvohacker/international-tax-law-corpus"
PACKAGE_PATH = "discipline"


def problems(text: str) -> list[str]:
    """Every way the requirement fails to pin the discipline to fixed bytes."""
    found: list[str] = []
    match = REQUIREMENT.search(text)
    if not match:
        found.append("requirements.txt does not name `itl-discipline @ <url>"
                     "#subdirectory=<path>`: the shared rules are not installed at "
                     "all, and every import of them is about to fail")
        return found

    url, path = match.group("url"), match.group("path")
    if CORPUS not in url:
        found.append(f"the discipline is fetched from {url!r}, and it comes from "
                     f"{CORPUS}, which owns it")
    if not url.startswith("git+https://"):
        found.append(f"the requirement points at {url!r}, which is not a git URL: "
                     f"only a git ref pins bytes")
    if "@" not in url:
        found.append(f"{url!r} names no ref at all, so which rules arrive is "
                     f"whatever the default branch holds when pip runs")
    elif not TAG.match(url.rsplit("@", 1)[1]):
        found.append(f"the pin is {url!r}, whose ref is not a version tag: a "
                     f"branch or another moving ref changes the rules under this "
                     f"checkout without a line of this repository changing")
    if path != PACKAGE_PATH:
        found.append(f"the package is read from {path!r}, and the corpus publishes "
                     f"it under `{PACKAGE_PATH}/`")
    return found


def test_the_discipline_is_pinned_to_a_tag():
    """Not `@main`: the difference between a pin and a promise."""
    found = problems(REQUIREMENTS.read_text(encoding="utf-8"))
    assert not found, "\n  ".join(["requirements.txt:"] + found)


def test_the_installed_discipline_exposes_what_this_repository_reads():
    """A package that renamed one of these is a red run here, not in a checkout."""
    # The reader is what `scripts/status.py` and the floor test call through
    # `scripts/ci.py`; the rule is what the machine-trace test runs; the board rule
    # is the one the generated document under `docs/` obeys.
    assert callable(ci.floor), "the reader lost `floor`: the floor test cannot read"
    assert callable(ci.interpreters), "the reader lost `interpreters`"
    assert callable(machine_traces.problems), "the machine-trace rule is not callable"
    assert callable(board.problems), "the board rule is not callable"


def test_the_board_rule_holds_here():
    """The rule the three layers share about the document they print."""
    assert board.problems(ROOT) == []


def test_the_check_can_fail():
    """The positive control: a check that cannot fail proves nothing."""
    good = ("itl-discipline @ git+https://github.com/avvohacker/"
            "international-tax-law-corpus.git@discipline-v1.0.0"
            "#subdirectory=discipline\n")
    assert problems(good) == []

    branch = good.replace("discipline-v1.0.0", "main")
    assert problems(branch), "a requirement pinned to a branch was accepted"

    missing = "PyYAML==6.0.3\n"
    assert problems(missing), "a requirements.txt without the discipline was accepted"

    elsewhere = good.replace("#subdirectory=discipline",
                             "#subdirectory=harness/discipline")
    assert problems(elsewhere), "a package read from another path was accepted"

    other_owner = good.replace("avvohacker", "somebody")
    assert problems(other_owner), "a package from another repository was accepted"
