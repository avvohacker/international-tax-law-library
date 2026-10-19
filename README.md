# international-tax-law-library

[![library-drift](https://github.com/avvohacker/international-tax-law-library/actions/workflows/library-drift.yml/badge.svg)](https://github.com/avvohacker/international-tax-law-library/actions/workflows/library-drift.yml)
[![discipline-drift](https://github.com/avvohacker/international-tax-law-library/actions/workflows/discipline-drift.yml/badge.svg)](https://github.com/avvohacker/international-tax-law-library/actions/workflows/discipline-drift.yml)
[![revendor-discipline](https://github.com/avvohacker/international-tax-law-library/actions/workflows/revendor-discipline.yml/badge.svg)](https://github.com/avvohacker/international-tax-law-library/actions/workflows/revendor-discipline.yml)
[![python](https://img.shields.io/badge/python-3.11%2B-blue)](pyproject.toml)
[![license: all rights reserved](https://img.shields.io/badge/license-all%20rights%20reserved-lightgrey)](LICENSE)

Second layer of the family, and one of its two repositories: the bilateral tax
treaties people actually work on, contributed as they go. The family is the
[`corpus`](https://github.com/avvohacker/international-tax-law-corpus) — the rules
and the server it holds — this repository, the treaties, and the folder
[`mcp/`](https://github.com/avvohacker/international-tax-law-corpus/tree/main/mcp),
which answers from both.

## Where this fits: two repositories, and the folder that answers

Two repositories under one contract of fidelity, and the server that queries
both is committed inside the corpus:

* **corpus** ([international-tax-law-corpus](https://github.com/avvohacker/international-tax-law-corpus)) — the citable base: UN Model 2017 and 2021 plus the OECD MLI framework (mapping, signatories and parties, country positions). Closed scope, byte-reproducible, every unit traceable to its page. **State**: both editions and every view built, anti-drift control in CI; it also holds the server, under [`mcp/`](https://github.com/avvohacker/international-tax-law-corpus/tree/main/mcp).
* **library (this repository)** — the bilateral treaties people work on, contributed as they go, under the same fidelity contract (source hash, page-anchored units, declared gaps, no invention). Invitation: as you work a treaty, put it here. **State**: complete for the two treaties it holds and frozen there until the next one arrives (`uk-us-2001` US–UK 2001, `no-uk-2013` UK–Norway 2013).
* **the server, [`mcp/`](https://github.com/avvohacker/international-tax-law-corpus/tree/main/mcp) in the corpus** — not a repository of its own but a folder of the corpus: the query mind over corpus plus library, treaty questions answered from the data (as-modified verdicts, with the chain of MLI Articles behind each one), never from guesses. It was built in a standalone repository of its own, which is private now and is not where a reader should be pointed — the folder is its home. **State**: six tools answering from the two checkouts and refusing when they cannot; it is run by the corpus' workflows, over the protocol, and it installs from the folder alone, with no clone: `pip install "git+https://github.com/avvohacker/international-tax-law-corpus.git@main#subdirectory=mcp"`.

### What GitHub's own MCP server gives you, and what that folder adds

GitHub ships an MCP server that reads repositories: a file's content (through the contents API, which returns content in full up to 1 MB per file), directory listings, trees, blame, commits, code search. It reads and writes files; it does not execute them. No tool in it runs Python or a shell command, nothing committed in a repository can give it one, and it is not configured from inside a repository either — so pointed at the corpus it can hand a model every byte it needs, and the verdict still has to be reconstructed from those bytes by the model itself. What an agent should *do* with those bytes is stated in an `AGENTS.md`, which MCP clients read into the model's context ([the corpus' own](https://github.com/avvohacker/international-tax-law-corpus/blob/main/AGENTS.md) is the one this family keeps); no file in a repository is read by GitHub's MCP server as a rule, and there is none that could be.

The folder is a **second** server, not a plugin for GitHub's and not a set of instructions to it. An MCP host can be given both at once, and each answers what it is for. Reaching the one that computes verdicts takes three things, and only the first is an install:

1. **one command, no clone** — the `pip install` above, which needs Python 3.11 or newer on the machine that will run it;
2. **the two checkouts, named** — `ITL_CORPUS_ROOT` and `ITL_LIBRARY_ROOT`, because the server owns no data and answers only from what it is pointed at: this repository is passed as the second of the two, never copied into the server as code;
3. **a host that starts it** — MCP over stdio means the client launches the process when a question is asked, so it runs on the machine where those two checkouts are, while the client is asking. Nothing is precomputed and nothing is cached, which is why no answer can be stale.

A reader who installs nothing keeps everything GitHub already gives — every file, read in full — and with it the cases where the same files read to a different answer. What they do not get is a computed verdict, the citation chain that travels with it, or a refusal.

## Roadmap

1. **Corpus walks** (done) — both Model editions and the MLI layer,
   byte-reproducible, anti-drift control in CI.
2. **Library walks** (two in, frozen) — bilateral treaties enter one by one
   under the same fidelity contract; `uk-us-2001` and `no-uk-2013` are in, with
   fetch + rebuild + contract tests in CI, and nothing in this repository depends
   on a push into another one.
3. **MCP walks** (now) — the server is built and lives in the corpus, under
   `mcp/`: six tools over corpus plus library, as-modified verdicts, citations
   to units, and silence where the data is silent. It is a folder of the corpus
   rather than a repository of its own — the standalone one it was built in is
   private and is not the way in — and this library is one of the two checkouts
   it reads (`ITL_LIBRARY_ROOT`), never a copy of its code in here.
4. **OECD Model** (later) — a corpus extension once 1–3 walk; excluded today
   on scope grounds only.

## Current state: two treaties in, and frozen until the next

**Frozen** is a claim about coupling, not about attention: this repository can
stand for months and nothing a reader runs here turns red because another
repository moved. Two pins make that true, and both are commits rather than
branches, because a branch moves under the checkout meant to reproduce the bytes.

* the copy of the shared discipline under `vendor/discipline/` is compared with
the corpus **at the commit `provenance/vendored-discipline.yaml` names**, never
with its `main`. `discipline-drift` therefore answers one question — is this copy
the rules it says it is — and a push into the corpus cannot change its answer;
* whether the corpus has since moved past that commit is a different question,
and a clock asks it: `revendor-discipline` runs weekly, reports it as a notice
and writes nothing. Running that same workflow by hand is the decision to take
the change, and it opens a pull request rather than pushing, so the pin and the
bytes it claims are read before they are trusted;
* the corpus pins this repository the same way, in `mcp/provenance/library.yaml`,
so a treaty added here does not turn its CI red either. The day the pin there
should move is the day a person decides the server should answer from the new
treaty — and the note to do it travels with the treaty, not with a red badge.
That checkout can also be asked the question directly: `python -m itl_mcp.library_pin`
there compares the pin with this repository's `main` and answers with an exit
code — `0` the pin is the head, `1` it is not, `2` the remote could not be asked —
so nobody has to wait for a clock to know whether this repository has moved on.

First treaty in, as the proof that the contract works: the **US–UK income
tax convention** (signed 24 July 2001, protocol of 19 July 2002) — the most
cited bilateral treaty there is, official text published by the US
Treasury/IRS, fetched and hash-verified like every source of the corpus.
Registered in `provenance/treaties.yaml` under its own id (`uk-us-2001`),
with URL, SHA-256, retrieval date, rights note and what it produces.

Built from its bytes, one unit per page anchored to the page it came from:
`treaties/uk-us-2001/treaty.json` (39 pages, 0 gaps) and its readable view
`treaty.md`, rendered from the JSON and never edited by hand. Byte-identical
when rebuilt. The PDF itself is not committed: the hash is the contract
(`.gitignore` keeps `sources/` out).

Second treaty in, and the first between **two** states that are both parties
to the MLI: the **UK–Norway convention of 2013** (signed 14 March 2013, in
force 17 December 2013, `no-uk-2013`). Its publisher is HM Revenue & Customs
on GOV.UK, whose pages carry the Open Government Licence v3.0 and Crown
copyright; the PDF itself states no separate licence, so the register records
the publisher's stated terms rather than the file's, and keeps the file
uncommitted as always. 28 pages, 0 gaps.

It is here for a reason that is about the layer above: a treaty between two
MLI parties is the only kind the query server can answer `modified` for, and
meet its own chain of Articles against. With one treaty whose two parties are
not both MLI parties, that whole branch of the verdict had nothing to run on.

The proof is the tests, not the claim (`pytest -q`; `docs/status.md` is the
generated board and counts what is published):

* every registry entry carries the full contract (hash, dates, rights,
  declared gaps, `redistribute: false`);
* the fetched bytes match the register's SHA-256;
* every page of the source is present, in order, exactly once;
* rebuilding from the same source bytes moves nothing;
* an empty page would have to declare a gap with a reason — no silent blanks;
* `treaty.md` is `treaty.json`'s own text, in order — rendered, not edited;
* every unit's text is what the PDF's own page yields, byte for byte — typed
  nothing.

Run it:

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt   # 3.11 or newer
.venv/bin/python scripts/fetch.py    # download + hash-verify the source PDFs
.venv/bin/python scripts/build.py    # page-anchored units -> treaties/
.venv/bin/python -m pytest -q        # the contract, as tests
.venv/bin/python scripts/status.py --write   # regenerate docs/status.md
```

CI runs those three steps on the pinned 3.13 and again on the floor (3.11) and
on the newest release (3.14), because `requires-python = ">=3.11"` is a claim
and a claim nobody executes is an opinion: the fetch, the rebuild and the
contract have to hold on the oldest interpreter a reader may still have.

Two more controls hold claims that no rebuild can see, and both fail rather
than complain: `tests/test_the_floor_runs_in_ci.py` reads
`.github/workflows/library-drift.yml` and fails if the floor `pyproject.toml`
declares is not one of the interpreters the workflow runs, and
`tests/test_no_machine_traces.py` reads every file git tracks and fails if one
names a local path, the directory this checkout lives in, or the account name on
the machine that ran the check. `docs/status.md` is the board generated from the
register and the artefacts — the treaty table, the pages anchored, the
declared gaps — and `tests/test_the_status_is_current.py` fails the moment the
committed board and the command that writes it disagree.

## The fidelity contract (what every treaty must bring)

A treaty enters here only with:

* the source identified by URL and SHA-256, with retrieval date and rights note;
* units anchored to the page and position they came from;
* gaps declared (unread pages, unmeasured tables) rather than silently filled;
* no invention: text identical to the source's, structure identical to the source's.

The corpus repository shows what the contract looks like in practice
(`provenance/sources.yaml`, span ledger, byte-reproducible build); the first
treaty here follows the same pattern.

## Invitation

As you work a treaty, put it here — with its hash, its pages, and its gaps.

## Putting a treaty in

Three steps, and the third is the one that reaches into the other repository:

1. register the source in `provenance/treaties.yaml` — URL, SHA-256, retrieval
date, rights note, what it produces — and fetch it (`scripts/fetch.py`);
2. build it (`scripts/build.py`), then run the suite and regenerate the board
(`scripts/status.py --write`); the contract above is what the tests hold;
3. when the treaty should also be answerable by the server, move the corpus'
pin: its `mcp/provenance/library.yaml` names the commit this repository should
be read at, and the library is frozen here until that line is edited there, on
purpose, by a person.

## Rights

See `LICENSE`. All rights reserved; this repository is public and source-visible.
Contact avvohacker@gmail.com before any reuse beyond reading. Text-and-data mining and
AI/ML training rights, including generative training, are expressly reserved;
see `TDM.md`. Third-party rights in future treaty sources remain with their
holders and are not affected by it.
