# international-tax-law-library

Second layer of the corpus-library-MCP trilogy: the bilateral tax treaties
people actually work on, contributed as they go.

## Where this fits: corpus, library, mcp

Three layers, three repositories, one contract of fidelity:

* **corpus** ([international-tax-law-corpus](https://github.com/avvohacker/international-tax-law-corpus)) — the citable base: UN Model 2017 and 2021 plus the OECD MLI framework (mapping, signatories and parties, country positions). Closed scope, byte-reproducible, every unit traceable to its page. **State**: both editions and every view built, anti-drift control in CI.
* **library (this repository)** — the bilateral treaties people work on, contributed as they go, under the same fidelity contract (source hash, page-anchored units, declared gaps, no invention). Invitation: as you work a treaty, put it here. **State**: contract walking — two treaties in (`uk-us-2001` US–UK 2001, `no-uk-2013` UK–Norway 2013).
* **mcp** ([international-tax-law-mcp](https://github.com/avvohacker/international-tax-law-mcp)) — the query mind over corpus plus library: treaty questions answered from the data (as-modified verdicts, with the chain of MLI Articles behind each one), never from guesses. **State**: server — seven tools answering from the two checkouts and refusing when they cannot; tested over the protocol in CI.

## Roadmap

1. **Corpus walks** (done) — both Model editions and the MLI layer,
   byte-reproducible, anti-drift control in CI.
2. **Library walks** (now) — bilateral treaties enter one by one under the
   same fidelity contract; the first is in (`uk-us-2001`) as the proof, with
   fetch + rebuild + contract tests in CI.
3. **MCP walks** (now) — this server is built: seven tools over corpus plus
   library, as-modified verdicts, citations to units, and silence where the
   data is silent.
4. **OECD Model** (later) — a corpus extension once 1–3 walk; excluded today
   on scope grounds only.

## Current state: the contract is walking, with two treaties

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

## Rights

See `LICENSE`. All rights reserved; this repository is public and source-visible.
Contact avvohacker@gmail.com before any reuse beyond reading. Text-and-data mining and
AI/ML training rights, including generative training, are expressly reserved;
see `TDM.md`. Third-party rights in future treaty sources remain with their
holders and are not affected by it.
