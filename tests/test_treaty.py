"""The fidelity contract, as tests.

A treaty enters this repository only with: the source identified by SHA-256
against the register, units anchored to the page they came from, gaps
declared rather than silently filled, and text identical to the source's.
These tests fail while any of that is not true.
"""

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
REGISTER = ROOT / "provenance" / "treaties.yaml"


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def registry() -> dict:
    return yaml.safe_load(REGISTER.read_text(encoding="utf-8"))


def entries() -> list[dict]:
    return registry()["treaties"]


def artefacts(entry: dict) -> tuple[Path, Path]:
    directory = ROOT / "treaties" / entry["id"]
    return directory / "treaty.json", directory / "treaty.md"


def fetched_pdf(entry: dict) -> Path:
    pdf = ROOT / "sources" / Path(entry["source"]["url"]).name
    if not pdf.exists():
        pytest.skip("source PDF not fetched; run scripts/fetch.py")
    return pdf


def test_every_entry_carries_the_full_contract():
    """id, parties, title, source, rights, produces, status, gaps."""
    assert entries(), "the registry must declare at least one treaty"
    for entry in entries():
        assert entry["id"] == "-".join(
            word for word in entry["id"].split("-") if word
        ), "id must be a stable slug"
        assert len(entry["parties"]) == 2, f"{entry['id']}: two parties"
        assert entry["title"].strip()
        source = entry["source"]
        assert source["url"].startswith("https://")
        assert len(source["sha256"]) == 64
        assert source["retrieved"] == source["verified"]
        assert source["languages"] and source["pages"] > 0
        rights = entry["rights"]
        assert rights["status"] in {
            "public_domain", "open_licence",
            "licence_with_conditions", "unknown",
        }
        assert rights["redistribute"] is False, "source PDFs never committed"
        assert rights["note"].strip()
        assert entry["produces"], "a source declares what it produces"
        assert entry["status"] in {"published", "in-preparation", "unread"}
        assert isinstance(entry["gaps"], list)


def test_fetched_bytes_match_the_register():
    for entry in entries():
        pdf = fetched_pdf(entry)
        assert sha256_of(pdf) == entry["source"]["sha256"], (
            f"{entry['id']}: fetched PDF does not match the register's hash: "
            "the publisher changed the file, or this is not the source the "
            "artefact was built from"
        )


def test_published_treaties_have_their_artefacts():
    for entry in entries():
        treaty_json, treaty_md = artefacts(entry)
        if entry["status"] == "published":
            assert treaty_json.exists(), f"{entry['id']}: treaty.json missing"
            assert treaty_md.exists(), f"{entry['id']}: treaty.md missing"
        for produce in entry["produces"]:
            artefact = ROOT / produce["artefact"]
            if not artefact.exists():
                assert produce.get("how"), (
                    f"{entry['id']}: {produce['artefact']} is absent without "
                    "a declared reason"
                )


def test_units_exist_and_are_anchored():
    for entry in entries():
        treaty_json, _ = artefacts(entry)
        if not treaty_json.exists():
            pytest.skip("treaty.json not built; run scripts/build.py")
        payload = json.loads(treaty_json.read_text(encoding="utf-8"))
        assert payload["id"] == entry["id"]
        assert payload["source"]["sha256"] == entry["source"]["sha256"]
        assert (payload["page_count"] == entry["source"]["pages"]
                == len(payload["units"]))
        assert [u["page"] for u in payload["units"]] == list(
            range(1, payload["page_count"] + 1)
        ), f"{entry['id']}: every page present, in order, exactly once"


def test_units_rebuild_byte_identical():
    """The published artefacts are a function of the source bytes alone."""
    built = [e for e in entries()
             if artefacts(e)[0].exists() and fetched_pdf(e).exists()]
    if not built:
        pytest.skip("no built artefacts with fetched sources")
    before = {path: path.read_bytes()
              for entry in built for path in artefacts(entry)}
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "build.py")],
        capture_output=True, text=True, cwd=ROOT,
    )
    assert result.returncode == 0, result.stderr
    for path, content in before.items():
        assert path.read_bytes() == content, (
            f"rebuilding from the same source bytes moved {path}"
        )


def test_every_unit_speaks_or_declares_a_gap():
    """No silent blanks: an empty page is a declared gap with a reason."""
    for entry in entries():
        treaty_json, _ = artefacts(entry)
        if not treaty_json.exists():
            continue
        payload = json.loads(treaty_json.read_text(encoding="utf-8"))
        declared = payload["gaps_declared"]
        found = 0
        for unit in payload["units"]:
            assert unit["chars"] > 0 or unit["gap"] is True, (
                f"{entry['id']} page {unit['page']}: empty but no gap declared"
            )
            if unit["gap"]:
                found += 1
                assert unit["gap_reason"], (
                    f"{entry['id']} page {unit['page']}: gap without a reason"
                )
        assert found == declared, (
            f"{entry['id']}: {found} gaps in the units, {declared} declared"
        )


def test_unit_hashes_match_their_text():
    for entry in entries():
        treaty_json, _ = artefacts(entry)
        if not treaty_json.exists():
            continue
        payload = json.loads(treaty_json.read_text(encoding="utf-8"))
        for unit in payload["units"]:
            digest = hashlib.sha256(unit["text"].encode("utf-8")).hexdigest()
            assert digest == unit["sha256"], (
                f"{entry['id']} page {unit['page']}: recorded hash does not "
                "match its text"
            )
            assert unit["chars"] == len(unit["text"])


def test_markdown_is_rendered_not_edited():
    """treaty.md is treaty.json's own text, in order, byte for byte."""
    for entry in entries():
        treaty_json, treaty_md = artefacts(entry)
        if not treaty_json.exists() or not treaty_md.exists():
            continue
        payload = json.loads(treaty_json.read_text(encoding="utf-8"))
        markdown = treaty_md.read_text(encoding="utf-8")
        assert "Do not edit" in markdown, (
            f"{entry['id']}: treaty.md lacks the rendered-not-edited banner"
        )
        position = -1
        for unit in payload["units"]:
            if unit["gap"]:
                continue
            marker = f"<!-- page {unit['page']} -->"
            found = markdown.find(marker, position + 1)
            assert found > position, (
                f"{entry['id']}: page {unit['page']} missing or out of order "
                "in treaty.md"
            )
            position = found
            assert unit["text"].rstrip() in markdown, (
                f"{entry['id']}: page {unit['page']} text in treaty.md does "
                "not come from treaty.json"
            )


def test_text_is_extracted_from_the_pdf_not_typed():
    """The artefact's text is what the PDF's own page yields, byte for byte."""
    fitz = pytest.importorskip("fitz")
    for entry in entries():
        treaty_json, _ = artefacts(entry)
        pdf = fetched_pdf(entry)
        if not treaty_json.exists():
            continue
        payload = json.loads(treaty_json.read_text(encoding="utf-8"))
        document = fitz.open(pdf)
        try:
            assert document.page_count == payload["page_count"]
            for unit in payload["units"]:
                assert document[unit["page"] - 1].get_text("text") == unit["text"], (
                    f"{entry['id']} page {unit['page']}: artefact text is not "
                    "the source's"
                )
        finally:
            document.close()
