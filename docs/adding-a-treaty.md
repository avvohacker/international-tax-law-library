# Adding a treaty: from the official source to the corpus' pin

One treaty is a register entry, two committed artefacts, and — only if the
server should answer from it — one line in the corpus. This is the order that
works, with the command that proves each step. Nothing here is typed by hand
except the register entry: the text is the PDF's, the readable view is rendered,
and every number on the board is computed.

The rule underneath all of it: **a gap is an answer**. A page with no extractable
text is published as a declared gap with a reason. It is never skipped, never
filled from another edition, and never OCR-guessed. A treaty that cannot be read
is `unread`, with the reason, and that is a finished entry too.

## 0. The source, and the right to read it

Take the text from the **publisher's own site** — the tax administration, the
foreign ministry, the official gazette — not from an aggregator, a law firm's
mirror or a scan somebody uploaded. Record the page you found it on, not only the
file's URL: the note has to say how you know this is the text.

```bash
mkdir -p sources
curl -fL --retry 3 -o sources/<file-name>.pdf '<official url>'
shasum -a 256 sources/<file-name>.pdf     # macOS
sha256sum sources/<file-name>.pdf         # Linux
```

Three things go into the entry and nowhere else:

* the **SHA-256 of these exact bytes** — the hash, not the file, is the contract;
* the **rights**: `public_domain`, `open_licence`, `licence_with_conditions` or
  `unknown`, with the licence the publisher states and the date you checked it.
  `unknown` is a legitimate value; guessing it is not;
* `redistribute` stays **false**. The PDF is never committed — `sources/` is
  ignored — and a treaty enters the repository as the extraction plus the hash.

If the publisher's page states terms for the site rather than the file, record
that: the note has to say which of the two the claim is about. `no-uk-2013` in
the register is the example — GOV.UK's Open Government Licence is the site's
statement, and the entry says so.

## 1. The register entry

Append to `provenance/treaties.yaml`. The header of that file is the schema, and
`tests/test_treaty.py` holds every field of it.

```yaml
  - id: <party-a>-<party-b>-<signature-year>   # alphabetical party order
    parties:
      - <canonical English name>
      - <canonical English name>
    title: >-
      <the treaty's official title, as published>
    source:
      url: <official url, https>
      publisher: <who published it>
      sha256: <64 hex characters>
      retrieved: YYYY-MM-DD
      verified: YYYY-MM-DD      # the test requires this to equal `retrieved`
      languages: [English]
      pages: <the page count you will check the build against>
    rights:
      status: public_domain | open_licence | licence_with_conditions | unknown
      redistribute: false
      note: >-
        <what the publisher states, and the date and page you checked it on>
    produces:
      - artefact: treaties/<id>/treaty.json
        how: >-
          scripts/build.py reads the fetched PDF as one unit per page, each
          anchored to its page number, and writes treaty.json;
          tests/test_treaty.py rebuilds it and compares byte for byte.
      - artefact: treaties/<id>/treaty.md
        how: >-
          rendered from treaty.json by scripts/build.py, never edited by hand.
    status: published | in-preparation | unread   # `unread` needs a reason
    gaps: []                                       # or each gap with its reason
```

`pages` is not decoration: the build refuses a document whose page count differs
from it, so a publisher's re-upload that drops a page is a red run and not a
quietly shorter treaty.

## 2. Fetch, and let the hash disagree with you

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/fetch.py
```

Every entry is downloaded or reused from `sources/`, and each is hashed against
the register. `FAIL … sha256 mismatch` means the bytes are not the ones the entry
names: either you edited the entry after downloading, or the publisher replaced
the file. Download it again and compare by eye before touching the hash — a hash
updated to match whatever came back turns the contract into a formality.

## 3. Build, and look at the gaps

```bash
.venv/bin/python scripts/build.py
```

The command prints, per treaty, the pages read and the gaps declared. Read that
line with the PDF open at one page you know: the text in `treaty.json` is the
PDF's own, extracted in document order, never typed. `0 gaps` on a scanned
document is a symptom, not a success — check a page.

* every page appears exactly once, in order, anchored to its page number;
* a page with no extractable text is a gap with `gap_reason`, and
  `tests/test_treaty.py` fails if one is blank without a reason;
* `treaties/<id>/treaty.md` is rendered from the JSON. Editing it is editing a
  view: the next build overwrites it, and `test_markdown_is_rendered_not_edited`
  says so before the build does.

## 4. The contract, as tests

```bash
.venv/bin/python -m pytest -q
```

What fails, and what it means:

| failure | what it is telling you |
|---|---|
| `test_every_entry_carries_the_full_contract` | a field is missing, `retrieved != verified`, or `redistribute` is not `false` |
| `test_fetched_bytes_match_the_register` | the PDF in `sources/` is not the registered one |
| `test_published_treaties_have_their_artefacts` | the entry says `published` and a file is missing, or a `produces` entry has no `how` |
| `test_units_exist_and_are_anchored` | pages differ from `source.pages`, or the units are not one per page in order |
| `test_units_rebuild_byte_identical` | the build is not a function of the bytes alone |
| `test_every_unit_speaks_or_declares_a_gap` | a blank page was published without a reason |
| `test_unit_hashes_match_their_text` | a unit's declaration disagrees with its own text |
| `test_markdown_is_rendered_not_edited` | `treaty.md` was edited by hand |

On this machine the three tests that need the PDFs skip when `sources/` is empty.
A skip is green: in CI the fetch runs first, and the same tests run for real.

## 5. The board

```bash
.venv/bin/python scripts/status.py --write
```

`docs/status.md` is generated and never edited: `tests/test_the_status_is_current.py`
compares the committed file with what this command writes. It counts treaties,
pages, gaps, sources and interpreters, and it prints a declared treaty that was
not built instead of omitting it.

## 6. Making the server answer from it (the corpus)

The library finishes here. The server is a folder of the corpus, and it reads a
**commit of this repository**, named in the corpus' `mcp/provenance/library.yaml`.
So adding a treaty does not change what the server answers until that pin moves —
by design, because moving the pin is the decision.

```bash
# 1. has the library moved past the pin?
cd <corpus>/mcp
python -m itl_mcp.library_pin        # 0 same, 1 moved (prints both commits), 2 cannot tell

# 2. move the pin: edit `commit:` to the library commit that holds the new treaty
#    mcp/provenance/library.yaml

# 3. re-earn the answers the new bytes change
python -m itl_mcp.drift              # names what moved, from what to what
python -m pytest -q

# 4. commit the pin and the answers together
```

If `drift` names a moved verdict for the new treaty, that is the control working:
the answers are recomputed from the data every time, and the recorded facts say
which ones changed. If it names answers for a treaty you did not add, the pin is
pointing at the wrong commit — that is what the negative rehearsal showed: pinning
to the library as it was *before* a treaty makes `drift` name every answer about it.

## 7. What CI does with it

| run | what it proves |
|---|---|
| `library-drift` | fetch, rebuild and the contract, on 3.13 and again on 3.11 and 3.14; the board is what the command writes; no machine trace in any tracked file |
| `discipline-drift` | the vendored copy of the shared rules still equals the corpus at the commit its pin names — a push into the corpus cannot turn it red |
| `revendor-discipline` (weekly) | reports whether the corpus has moved past that pin, and writes nothing |
| `mcp-drift` (in the corpus) | the server's recorded answers, read from the library **at the commit the corpus pins**; a schedule job reports whether the pin is behind, as a notice |

## Checklist

- [ ] the source is the publisher's own, and the note says how that was checked
- [ ] `sha256` is the hash of the bytes that were built, not of a redownload
- [ ] `retrieved` equals `verified`
- [ ] `pages` matches the PDF and the build
- [ ] every gap is declared with a reason; no page is silently blank
- [ ] `treaty.md` was not edited
- [ ] `pytest -q` green, `status.py --write` run and committed
- [ ] the corpus pin moved in a commit of its own, with the answers re-earned
- [ ] `python -m itl_mcp.drift` run **after** the pin moved, and its line is in the report
