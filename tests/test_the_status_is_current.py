"""The status board, held against the repository and against itself.

`docs/status.md` is the document a reader is told to trust without reading the
code, and it is generated - so there are two ways it can lie: by being older
than the repository it describes, and by printing a number that contradicts the
table under it. Both are checked here, and both are the same rule the treaty
artefacts obey: a generated document is the command's output, never an edit.

One property no passing board can show is checked too. The board must not
describe the machine that built it: a clone called `library` in CI,
`intl-library` in one checkout and anything else on another desk has to print
the *project's* name, or one repository produces three different documents and
none of them says which project it is about.
"""

import re
import shutil
from pathlib import Path

import pytest
import yaml

import status

ROOT = Path(__file__).resolve().parent.parent

# Rendering the board reads the register and every built artefact, so it is
# done once for the whole file rather than once per test.
BOARD = status.render(ROOT)

TREATIES_SUMMARY = re.compile(r"^- treaties: (\d+) declared, (\d+) published, "
                              r"(\d+) declared not built", re.M)
PAGES_SUMMARY = re.compile(r"^- pages: (\d+) anchored, (\d+) declared gaps", re.M)
SOURCES_SUMMARY = re.compile(r"^- sources: (\d+) registered, (\d+) of them "
                             r"redistributable", re.M)


def _clone(tmp_path: Path) -> Path:
    """A checkout of this repository under a name that is nobody's project."""
    clone = tmp_path / "a-clone-called-something-else"
    clone.mkdir()
    shutil.copy(ROOT / "pyproject.toml", clone / "pyproject.toml")
    (clone / "provenance").mkdir()
    shutil.copy(ROOT / "provenance" / "treaties.yaml",
                clone / "provenance" / "treaties.yaml")
    shutil.copytree(ROOT / "treaties", clone / "treaties")
    return clone


def _table_rows(text: str) -> list[list[str]]:
    """The treaty table, as cells: id, status, parties, pages, gaps, publisher."""
    rows = []
    for line in text.splitlines():
        cells = [cell.strip() for cell in line.split("|")]
        if len(cells) == 8 and cells[1].startswith("`") and cells[1].endswith("`"):
            rows.append(cells[1:7])
    return rows


def test_the_committed_board_is_what_the_command_writes():
    """`python scripts/status.py --write` is the only author of this file."""
    committed = (ROOT / "docs" / "status.md").read_text(encoding="utf-8")
    assert committed == BOARD, (
        "docs/status.md is not what `python scripts/status.py --write` writes "
        "now: regenerate it rather than editing it")


def test_the_summary_counts_the_table_below_it():
    """Every number in the summary is a count of rows the board itself shows."""
    summary = TREATIES_SUMMARY.search(BOARD)
    assert summary, "the board no longer prints a treaties summary line"
    declared, published, pending = (int(group) for group in summary.groups())
    rows = _table_rows(BOARD)
    assert declared == len(rows), "the summary counts treaties the table does not list"
    assert published == sum(1 for row in rows if row[3] != "-"), (
        "the summary's published count is not the table's")
    assert pending == declared - published


def test_the_pages_summary_is_the_table_s_own_pages():
    summary = PAGES_SUMMARY.search(BOARD)
    assert summary, "the board no longer prints a pages summary line"
    anchored, gaps = (int(group) for group in summary.groups())
    rows = _table_rows(BOARD)
    assert anchored == sum(int(row[3]) for row in rows if row[3].isdigit())
    assert gaps == sum(int(row[4]) for row in rows if row[4].isdigit())


def test_the_sources_summary_is_the_register_s_own_flags():
    """The line about the sources is read from `rights.redistribute`, not typed."""
    register = yaml.safe_load(
        (ROOT / "provenance" / "treaties.yaml").read_text(encoding="utf-8"))
    summary = SOURCES_SUMMARY.search(BOARD)
    assert summary, "the board no longer prints a sources summary line"
    registered, redistributable = (int(group) for group in summary.groups())
    assert registered == len(register["treaties"])
    assert redistributable == sum(
        1 for entry in register["treaties"]
        if entry["rights"]["redistribute"] is True)


def test_the_board_names_the_project_not_the_directory(tmp_path):
    """A clone on a desk prints the project, not the desk."""
    text = status.render(_clone(tmp_path))
    assert "a-clone-called-something-else" not in text
    assert "`international-tax-law-library`" in text


def test_a_treaty_with_no_artefact_is_reported_not_omitted(tmp_path):
    """The board reads the artefacts; it does not repeat the register's hope."""
    clone = _clone(tmp_path)
    gone = sorted(path.name for path in (clone / "treaties").iterdir()
                  if path.is_dir())[0]
    (clone / "treaties" / gone / "treaty.json").unlink()

    text = status.render(clone)
    summary = TREATIES_SUMMARY.search(text)
    assert summary, "the board no longer prints a treaties summary line"
    assert int(summary.group(3)) == 1, "the unbuilt treaty is not counted as pending"
    assert f"**`{gone}`**" in text, "the unbuilt treaty is not named with its reason"


def test_a_missing_register_is_a_stated_failure(tmp_path):
    """An empty board is the most convincing lie; a missing register is not one."""
    with pytest.raises(FileNotFoundError):
        status.render(tmp_path)
