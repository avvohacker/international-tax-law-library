"""Nothing this repository commits may describe the machine it was built on.

The corpus states the rule as invariant F14, and states why: a committed
`derived/index.json` once carried an absolute path into the builder's home
directory. The class is wider than the artefacts a pipeline writes, so this file
holds every file git tracks in the library to it: the register, the page-anchored
artefacts, the scripts and these tests.

The rule itself is not written here. It is `vendor/discipline/machine_traces.py`,
copied verbatim from the corpus and pinned in
`provenance/vendored-discipline.yaml`, because the three repositories kept three
copies of it and the copies had drifted apart before anything compared them. The
copy this file replaced is also why the sharing is worth the plumbing: the
compatibility jobs found it red on itself, because its positive control wrote a
machine root whole and the scan then read its own sample as a leak - a defect
invisible from a desk, and invisible in the other two copies of the same rule.

What stays here is the library's own half of the rule: the samples a treaty
catalogue uses (a path written with a placeholder is not a path to a machine),
and the identity this repository's CI runs under, reproduced below on a desk.
"""
from pathlib import Path

from vendor.discipline import machine_traces

ROOT = Path(__file__).resolve().parent.parent


def test_no_committed_file_carries_a_machine_trace():
    """The whole tracked tree, read the way the rule is meant to read it."""
    problems = machine_traces.problems(ROOT)
    assert not problems, (
        "a committed file describes the machine it was built on:\n  "
        + "\n  ".join(problems[:12]))


def test_the_library_passes_the_rule_as_the_ci_account_sees_it():
    """The identity of the compatibility jobs, reproduced on a desk.

    CI checks this repository out under its own project name and runs as an
    account whose name is an ordinary English word. Nothing on a desk is called
    that, so a rule that collides with the repositories' own prose cannot be seen
    here unless the identity is stated. It is stated instead.
    """
    problems = machine_traces.problems(
        ROOT, user="runner", checkout="international-tax-law-library")
    assert not problems, (
        "the library is red under the identity its own CI runs as:\n  "
        + "\n  ".join(problems[:12]))


def test_the_detector_catches_every_trace_it_claims_to():
    """The positive control: a detector that never fires proves nothing."""
    checkout = "a-clone-called-something-else"
    user = "somebody"
    samples = (
        ("an absolute home path", "/" + "Users" + "/somebody/treaty.json"),
        ("a machine-local root",
         "/" + "private" + "/var" + "/folders" + "/x/y/treaty.md"),
        ("a Windows home path",
         "C:" + "\\" + "Users" + "\\" + "somebody" + "\\treaty.json"),
        ("a file:// URL naming a local path", "file:" + "///tmp/treaty.json"),
        ("the directory this checkout lives in",
         "cloned into a-clone-called-something-else"),
        ("the account name on this machine", "built on somebody's laptop"),
    )
    for expectation, sample in samples:
        found = machine_traces.traces_in(sample, checkout=checkout, user=user,
                                         project="international-tax-law-library")
        assert any(expectation in hit for hit in found), (
            f"the detector no longer catches {expectation}: {sample!r} -> {found}")


def test_a_ci_accounts_home_path_is_still_a_trace():
    """The exemption is the account name, never the path that carries it."""
    text = "/" + "home" + "/" + "runner" + "/work/library/treaties/uk-us-2001"
    found = machine_traces.traces_in(text, checkout=None, user="runner")
    assert found, "the path rule stopped catching a CI account's home directory"


def test_the_exempt_accounts_are_declared_where_an_exemption_can_be_reviewed():
    """A list that grows without a second edit is a list that grows by accident."""
    assert machine_traces.CI_ACCOUNTS == frozenset({"runner", "github-actions"}), (
        "the accounts exempt from the name rule changed: the rule's own docstring "
        "and the corpus' SPEC state the reason, and the copy here is pinned")


def test_the_detector_leaves_the_declarations_alone():
    """Naming the owner and the contact is the point of these lines."""
    text = ("Copyright (c) 2026 somebody <somebody@example.com> - project\n"
            "Contact somebody@example.com before any reuse beyond reading.\n"
            "repository: somebody/international-tax-law-corpus\n"
            "badge: https://github.com/somebody/international-tax-law-library\n")
    assert not machine_traces.traces_in(text, checkout="international-tax-law-library",
                                        user="somebody",
                                        project="international-tax-law-library")


def test_a_checkout_named_after_the_project_is_not_a_trace():
    """CI clones into the project's own name, and that name is not a machine."""
    text = "the library repository international-tax-law-library"
    assert not machine_traces.traces_in(text, checkout="international-tax-law-library",
                                        user=None, project="international-tax-law-library")
    assert machine_traces.traces_in(text, checkout="intl", user=None,
                                    project="international-tax-law-library") == []


def test_a_placeholder_for_a_local_path_is_not_a_trace():
    """A document may say where a local path *would* be, without naming one."""
    evidence = '"' + "/" + "Users" + "/<someone>/treaty.pdf" + '"'
    assert not machine_traces.traces_in(evidence, checkout="x", user=None)
