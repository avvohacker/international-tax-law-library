# international-tax-law-library

Second layer of the corpus-library-MCP trilogy: the bilateral tax treaties
people actually work on, contributed as they go.

## Where this fits: corpus, library, mcp

Three layers, three repositories, one contract of fidelity:

* **corpus** ([international-tax-law-corpus](https://github.com/avvohacker/international-tax-law-corpus)) — the citable base: UN Model 2017 and 2021 plus the OECD MLI framework. Closed scope, byte-reproducible, every unit traceable to its page.
* **library (this repository)** — the bilateral treaties people work on, contributed as they go: each treaty enters with the same fidelity contract (source hash, page-anchored units, declared gaps, no invention).
* **mcp** ([international-tax-law-mcp](https://github.com/avvohacker/international-tax-law-mcp)) — the query mind over corpus plus library: treaty questions answered from the data (as-modified verdicts), never from guesses.

## Current state: scaffold

No treaties yet. This repository currently holds only its own contract:
this README, `LICENSE`, and `TDM.md`. That is deliberate — an empty library
with its rules stated is better than a library with treaties of unknown
provenance.

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
Contact via GitHub before any reuse beyond reading. Text-and-data mining and
AI/ML training rights, including generative training, are expressly reserved;
see `TDM.md`. Third-party rights in future treaty sources remain with their
holders and are not affected by it.
