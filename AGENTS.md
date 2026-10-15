# AGENTS.md — how to work in this repository

Repo-level instructions for any coding agent working here. They are the rules
that are easy to break by being helpful; the READMEs say what the project is.

## What this is

The bilateral tax treaties people work on, contributed as they go, under one
contract of fidelity: the source identified by URL and SHA-256, one unit per page
anchored to the page it came from, the gaps declared rather than filled, and no
invention. This is the library layer; the family is two repositories and one
folder — the [`corpus`](https://github.com/avvohacker/international-tax-law-corpus)
(the UN Model editions and the OECD MLI material, and the server, under its
`mcp/`), this repository (the bilateral treaties), and the folder `mcp/`, which
answers from both checkouts.

## The two rules that decide almost everything

**A gap is an answer.** Where the data does not hold something — a page this
library declares it could not read, a table the reader could not measure, a
provision the source prints in a shape the reading does not recognise — the answer
*is* the gap, named, with the reader's own reason. Do not fill it by analogy with
a document that does hold it, do not read a `null` as a "no", and do not report a
page the pipeline could not read as a finding about the treaty. `null`,
`undecidable`, `NOT-EVALUATED` and a declared gap are outputs of this project, not
defects in it.

**No claim without the bytes.** Every statement about a treaty names the artefact,
the page and the hash it was verified against. A citation to a page that does not
carry the fact is worse than no citation: it is the failure mode this repository
exists to make impossible. Where the corpus and the library disagree, report both.

## Ask the server, or read the file

Both are correct, for different questions, and the line between them is worth
holding:

* **Reading is right** for what the files say: what a treaty's text is, what a
  page contains, what the register says about a source. GitHub's own MCP server is
  a fine reader for that — it returns a file in full up to 1 MB through the
  contents API, and every committed file here is far below that. What it is not is
  a way to run anything: it executes no code and no shell, and no file in a
  repository changes what it does. What an agent should *do* is stated in this
  file, which MCP clients read into a model's context — not by the MCP server.
* **The server is right** where the answer needs a rule the files do not state:
  what the MLI does to one of these treaties and by which chain of Articles,
  whether a treaty falls inside a reservation, which edition is silent on an
  Article, and what any of it was verified against. Those are the six tools of the
  corpus' `mcp/`, and
  [its README](https://github.com/avvohacker/international-tax-law-corpus/blob/main/mcp/README.md)
  names the rule each one applies.

That server is a **second** one, not a plugin for GitHub's and not a set of
instructions to it: it is installed from the corpus' subfolder and started by the
MCP host, and this repository is one of the two checkouts it reads. A refusal from
it is an answer: relay it with its reason rather than answering around it.

## Starting the server, with this repository as the library root

```bash
pip install "git+https://github.com/avvohacker/international-tax-law-corpus.git@main#subdirectory=mcp"
export ITL_CORPUS_ROOT=/path/to/the/corpus/checkout
export ITL_LIBRARY_ROOT=/path/to/this/checkout
itl-mcp                      # speaks MCP over stdio
```

It owns no data and answers only from those two checkouts; with either missing it
exits naming the one it wants. None of it is copied in here: the server takes this
repository as an argument.

## House rules

* **Generated files are not edited by hand.** `docs/status.md` is written by
  `python scripts/status.py --write`, and `treaties/<id>/treaty.md` is rendered
  from `treaty.json` by `python scripts/build.py`; a test compares each with what
  its command writes. Hand-editing one turns a check into a copy of itself.
* **A treaty enters only with its whole contract.** `provenance/treaties.yaml`
  holds the URL, the SHA-256 of the exact bytes read, the retrieval date, the
  rights note (`redistribute` is never true here), what the source produces and
  where, and the gaps. A page that could not be read is declared with a reason in
  the artefact rather than quietly left out of a page count.
* **The source PDFs are never committed.** They are fetched, hashed and read
  locally under `sources/` (gitignored), and the hash in the register is the
  contract: `python scripts/fetch.py` downloads exactly the registered bytes and
  fails on a mismatch.
* **Vendored copies are never edited either.** `vendor/discipline/` is the
  corpus' own implementation of the rules the family shares — what may not be
  committed about a machine, how a workflow is read, and what a status board owes
  a reader — copied verbatim and pinned in `provenance/vendored-discipline.yaml`.
  Both halves are written by the corpus' `scripts/vendor-discipline.py` and never
  by hand: re-vendor, never patch a copy. The manual `revendor-discipline`
  workflow runs that writer from the corpus' own main and opens a pull request
  with the result, and `library-drift`'s `discipline` job is what stays red until
  it is merged.
* **No machine traces.** No absolute path of the machine that built anything, no
  user name, no host name, in code, comments, documents, fixtures or commit
  messages (invariant F14). The rule is implemented once, in
  `vendor/discipline/machine_traces.py`, and the tests run it under the CI account
  as well, because neither the account nor the checkout name is visible from a
  desk.
* **Prose here is dense on purpose.** It states what is known, by what check, and
  what is not: do not soften a limitation into a promise, and do not delete a
  stated defect.

## Checking your work

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/fetch.py           # download + hash-verify the sources
.venv/bin/python scripts/build.py           # page-anchored units -> treaties/
                                            # (a clean rebuild must move nothing)
.venv/bin/python -m pytest -q               # the contract, as tests
.venv/bin/python scripts/status.py --write  # regenerate docs/status.md

# the rules the three layers share, run from a corpus checkout beside this one,
# which is how this repository's own `discipline` job runs it:
cd ../international-tax-law-corpus
python scripts/discipline-drift.py --corpus . \
      --library ../international-tax-law-library --mcp mcp
```

A red check is a finding, not an obstacle: say which fact moved and why, or say
that the check could not run. Both are better than a green run that checked
nothing.
