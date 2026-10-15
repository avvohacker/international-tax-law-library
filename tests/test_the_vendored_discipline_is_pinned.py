"""The shared discipline is vendored here, and the pin is what holds it.

`vendor/discipline/` is not this repository's own code: it is the corpus' rules -
what may not be committed about a machine, how a workflow is read, what a status
board owes a reader - copied verbatim, and `provenance/vendored-discipline.yaml`
says which bytes traveled and where they came from. Two ways that can stop being
true, and all three are checked here:

  * the copy can be edited in place, which silently gives this repository a rule
    of its own - the state the three copies were in when a hand comparison found
    them three wordings, three exemption lists and two different readers;
  * the pin can be left behind by a copy that moved, in which case the register
    describes a repository that no longer exists;
  * the pin's own claim can be about the wrong kind of thing: a `source_commit`
    that names a branch or a tag is not a pin, because that ref moves under the
    checkout meant to reproduce it, so the register would say which bytes
    travelled only for the moment it was written.

Any of them is a red run rather than a surprise. The one way that cannot be
checked from here is checked where the other checkouts are: whether this copy still
equals the corpus' *current* rules is what the `discipline` job of this
repository's workflow asks against the corpus' own working copy, and
`test_the_workflow_runs_the_control_that_asks_it` is what stops that job from
being deleted while every test here stays green.

The rule is then *run* here, not only hashed: equal bytes are not the same as a
rule that passes.
"""
import hashlib
import re
from pathlib import Path

import yaml

from vendor.discipline import board, machine_traces

ROOT = Path(__file__).resolve().parent.parent
VENDORED = ROOT / "vendor" / "discipline"
PIN = ROOT / "provenance" / "vendored-discipline.yaml"
SOURCE_REPOSITORY = "https://github.com/avvohacker/international-tax-law-corpus"
SOURCE_PATH = "harness/discipline"
# What a pin may name as the commit it came from: a git object id, and nothing
# else. `main` is not one, and a tag is not one either.
COMMIT = re.compile(r"^[0-9a-f]{40}([0-9a-f]{24})?$")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def copies() -> dict[str, bytes]:
    """The vendored files, as bytes, keyed by name."""
    return {path.name: path.read_bytes() for path in sorted(VENDORED.glob("*.py"))}


def pinned() -> dict:
    return yaml.safe_load(PIN.read_text(encoding="utf-8")) or {}


def drift(copies: dict[str, bytes], pin: dict) -> list[str]:
    """Every way these bytes are not what the pin declares.

    Taking the copies as an argument rather than reading the tree is what lets
    `test_the_checker_can_fail` hand it a copy somebody edited: a checker that
    can only be tested on a repository that is already correct proves nothing.
    """
    stated = pin.get("files") or {}
    problems: list[str] = []
    for name in sorted(set(stated) | set(copies)):
        if name not in copies:
            problems.append(f"{name}: pinned, and there is no such file under "
                            f"{VENDORED.relative_to(ROOT)}/")
        elif name not in stated:
            problems.append(f"{name}: here, and the pin does not name it")
        elif stated[name] != digest(copies[name]):
            problems.append(f"{name}: the pin declares {stated[name][:12]}, and "
                            f"the copy here is {digest(copies[name])[:12]}")
    if pin.get("source") != SOURCE_REPOSITORY:
        problems.append(f"the pin names the source {pin.get('source')!r}, and the "
                        f"discipline comes from {SOURCE_REPOSITORY}")
    if pin.get("source_path") != SOURCE_PATH:
        problems.append(f"the pin names the source path {pin.get('source_path')!r}, "
                        f"and the discipline lives at {SOURCE_PATH}")
    stated_commit = pin.get("source_commit")
    if not stated_commit:
        problems.append("the pin does not say which commit was vendored")
    elif not COMMIT.match(str(stated_commit)):
        problems.append(
            f"the pin names {stated_commit!r} as the commit it was vendored from, "
            f"and that is a ref rather than a commit: a branch or a tag moves "
            f"under the checkout meant to reproduce these bytes")
    return problems


def test_the_vendored_discipline_is_the_bytes_the_pin_declares():
    """A copy nobody re-vendored is a rule of this repository's own invention."""
    problems = drift(copies(), pinned())
    assert not problems, (
        "the vendored discipline and its pin disagree:\n  "
        + "\n  ".join(problems)
        + "\n  re-vendor with `python scripts/vendor-discipline.py --into .` from "
          "the corpus")


def test_the_checker_can_fail():
    """The positive control, because every test above is an `assert not`."""
    here = copies()
    name = sorted(here)[0]

    edited = dict(here)
    edited[name] = here[name] + b"\n# an edit nobody re-vendored\n"
    problems = drift(edited, pinned())
    assert problems and any(name in problem for problem in problems), problems

    missing = dict(here)
    missing.pop(name)
    problems = drift(missing, pinned())
    assert problems and any(name in problem for problem in problems), problems

    unfixed = dict(pinned())
    unfixed["files"] = {key: "0" * 64 for key in (pinned().get("files") or {})}
    assert drift(here, unfixed), "a pin whose hashes are all wrong was accepted"

    moved = dict(pinned())
    moved["source_commit"] = "main"
    assert drift(here, moved), (
        "a pin naming a branch instead of a commit was accepted: it describes "
        "whatever that branch held when it was read, and not these bytes")
    tagged = dict(pinned())
    tagged["source_commit"] = "v1.0.0"
    assert drift(here, tagged), "a pin naming a tag instead of a commit was accepted"


def test_the_board_rule_holds_here():
    """The rule the three layers share about the document they print."""
    assert board.problems(ROOT) == []


def test_the_rule_holds_here_as_ci_sees_it():
    """Equal bytes are not a rule that passes: the scan is run, not hashed."""
    problems = machine_traces.problems(
        ROOT, user="runner", checkout="international-tax-law-library")
    assert not problems, "\n  ".join(["the rule fails on this checkout:"] + problems)


def test_the_workflow_runs_the_control_that_compares_the_copy_with_the_corpus():
    """The check that needs three checkouts cannot be a test; it must be a run."""
    workflows = sorted((ROOT / ".github" / "workflows").glob("*.y*ml"))
    text = "\n".join(path.read_text(encoding="utf-8") for path in workflows)
    assert workflows, "this repository has no workflow, so nothing runs at all"
    assert "discipline-drift.py" in text, (
        "no workflow step runs the corpus' discipline drift control: the copy in "
        "vendor/ would go on being compared with nothing, and every test in this "
        "file would stay green while it did")
