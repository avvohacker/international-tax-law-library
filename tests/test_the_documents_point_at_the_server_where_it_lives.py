"""The prose that points a reader at the server must point at where it lives.

The server is a folder of the corpus, `mcp/`, and the way in is the command that
installs it from that subfolder: no clone, and this repository passed to it as a
library root rather than copied into it. Two documents here make that promise to a
reader who will act on it — `README.md`, which sets out the family, and
`AGENTS.md`, which tells an agent what to run. A promise in prose is worth what
the check behind it is worth, and this is the check that was missing: the README
kept pointing at the standalone repository the server was built in, which is
private now and is not a way in. The corpus' own README had already been through
that repair; this one had not, and nothing here would have said so.

So the command is held here word for word, and the standalone repository may not
appear at all. The rule is a function of the text rather than of the file, so the
positive control below can hand it the two drifts it exists for: a link to the
standalone repository, and a sentence that keeps the promise while losing the
command.
"""
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent

# The documents a reader is sent to: what the project is, and what an agent
# working in it should do.
DOCUMENTS = ("README.md", "AGENTS.md")

# The only way in: the server, installed from the corpus' own subfolder, at main.
COMMAND = ('pip install "git+https://github.com/avvohacker/'
           'international-tax-law-corpus.git@main#subdirectory=mcp"')

# The repository the server was built in, private now: a reader sent there gets
# nothing, which is the failure this file refuses.
STANDALONE = "international-tax-law-mcp"


def problems(text: str) -> list[str]:
    """Every way one document sends a reader to the wrong place."""
    found: list[str] = []
    if COMMAND not in text:
        found.append("it does not give the command that installs the server from "
                     f"the corpus' subfolder: {COMMAND}")
    if STANDALONE in text:
        lines = [line.strip() for line in text.splitlines() if STANDALONE in line]
        found.append("it names the standalone server repository, which is private "
                     "and is not where a reader should be sent: "
                     + " | ".join(lines[:3]))
    return found


@pytest.mark.parametrize("name", DOCUMENTS)
def test_the_document_points_at_the_server_in_the_corpus(name: str) -> None:
    """The command is there, word for word, and the private repository is not."""
    path = ROOT / name
    assert path.is_file(), f"{name} is missing, and a reader is sent to it"
    found = problems(path.read_text(encoding="utf-8"))
    assert not found, "\n  ".join([f"{name}:"] + found)


def test_the_check_can_fail() -> None:
    """The positive control: a rule that cannot be broken proves nothing."""
    good = (f"* **the server** — reach it with `{COMMAND}`, and pass the two roots: "
            f"this repository is the library root.\n")
    assert problems(good) == []

    from_the_root = good.replace("corpus.git@main#subdirectory=mcp", "corpus.git@main")
    assert problems(from_the_root), (
        "a document that installs the server from the corpus' own root, and not "
        "from its subfolder, was accepted")

    standalone = good + (f"* **mcp** ([{STANDALONE}]"
                         f"(https://github.com/avvohacker/{STANDALONE}))"
                         f" — the query mind over both\n")
    assert any(STANDALONE in problem for problem in problems(standalone)), (
        f"a document that sends a reader to the private repository was accepted: "
        f"{problems(standalone)}")
