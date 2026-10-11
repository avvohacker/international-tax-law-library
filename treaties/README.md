# treaties/

One directory per treaty, named by its registry id
(`<party-a>-<party-b>-<signature-year>`, alphabetical party order):

```
treaties/<id>/
  treaty.json  — the page-anchored extraction (units traceable to page
                 and position, gaps declared, no invention)
  treaty.md    — the readable view, rendered from treaty.json, never edited
```

Two treaties here: `uk-us-2001/` (US–UK income tax convention, 2001) and
`no-uk-2013/` (UK–Norway convention, 2013). A treaty appears only together
with its `provenance/treaties.yaml` entry
(source hash, rights note, gaps); the directory without the registry entry
— or the entry without the directory — is an error, not a half-published
treaty.

Source PDFs live under `sources/` (local only, gitignored) and are never
committed.
