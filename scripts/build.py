#!/usr/bin/env python3
"""Read the registered treaty PDFs as page-anchored units and publish them.

For every treaty in provenance/treaties.yaml:

* ``treaties/<id>/treaty.json`` — one unit per page, each anchored to the
  page number it came from, with its own text hash; text extracted by rule
  (PyMuPDF, document order), never typed. An empty page is published as a
  declared gap with its reason instead of being skipped.
* ``treaties/<id>/treaty.md``   — the readable view, rendered from
  treaty.json and never edited by hand.

The build refuses to run when the fetched PDF does not match the register:
the artefacts are a function of registered bytes alone.
"""

import hashlib
import json
import sys
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError:  # pragma: no cover
    sys.exit("PyMuPDF is required: pip install -r requirements.txt")

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("PyYAML is required: pip install -r requirements.txt")

ROOT = Path(__file__).resolve().parent.parent
REGISTER = ROOT / "provenance" / "treaties.yaml"


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build(pdf: Path) -> tuple[dict, list[dict]]:
    document = fitz.open(pdf)
    units = []
    for index in range(document.page_count):
        text = document[index].get_text("text")
        units.append({
            "page": index + 1,
            "chars": len(text),
            "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "gap": text.strip() == "" or None,
            "gap_reason": ("no extractable text on this page"
                           if text.strip() == "" else None),
            "text": text,
        })
    document.close()
    return units, units


def render_markdown(payload: dict) -> str:
    lines = [
        f"# {payload['title']}",
        "",
        f"*Source*: {payload['source']['url']}  ",
        f"*SHA-256*: `{payload['source']['sha256']}`  ",
        f"*Pages*: {payload['page_count']} · *Gaps*: {payload['gaps_declared']}",
        "",
        "<!-- Rendered from treaty.json by scripts/build.py.",
        "     Do not edit: every change belongs in the source PDF. -->",
        "",
    ]
    for unit in payload["units"]:
        lines.append(f"<a id=\"page-{unit['page']}\"></a>")
        lines.append(f"<!-- page {unit['page']} -->")
        lines.append("")
        if unit["gap"]:
            lines.append(f"> **Gap (page {unit['page']})**: "
                         f"{unit['gap_reason']}.")
        else:
            lines.append(unit["text"].rstrip())
        lines.append("")
    return "\n".join(lines) + "\n"


def main() -> int:
    register = yaml.safe_load(REGISTER.read_text(encoding="utf-8"))
    failures = 0
    for entry in register["treaties"]:
        source = entry["source"]
        pdf = ROOT / "sources" / Path(source["url"]).name
        if not pdf.exists():
            print(f"missing {pdf}; run scripts/fetch.py first", file=sys.stderr)
            failures += 1
            continue
        actual = sha256_of(pdf)
        if actual != source["sha256"]:
            print(f"sha256 mismatch for {pdf}\n"
                  f"  expected {source['sha256']}\n  actual   {actual}",
                  file=sys.stderr)
            failures += 1
            continue
        units, _ = build(pdf)
        gaps = [u for u in units if u["gap"]]
        if len(units) != source["pages"]:
            print(f"{entry['id']}: read {len(units)} pages, register says "
                  f"{source['pages']}", file=sys.stderr)
            failures += 1
            continue
        payload = {
            "id": entry["id"],
            "parties": entry["parties"],
            "title": entry["title"].strip(),
            "source": {
                "url": source["url"],
                "sha256": source["sha256"],
                "retrieved": str(source["retrieved"]),
                "pages": source["pages"],
            },
            "page_count": len(units),
            "gaps_declared": len(gaps),
            "units": units,
        }
        directory = ROOT / "treaties" / entry["id"]
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "treaty.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=1, sort_keys=True)
            + "\n", encoding="utf-8")
        (directory / "treaty.md").write_text(render_markdown(payload),
                                             encoding="utf-8")
        print(f"wrote {entry['id']}: {len(units)} pages, {len(gaps)} gaps")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
