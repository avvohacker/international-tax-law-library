#!/usr/bin/env python3
"""Fetch the registered treaty sources and verify them against the register.

provenance/treaties.yaml declares, per treaty, the official URL and the
SHA-256 of the exact bytes the extraction runs on. This downloads exactly
those bytes and fails loudly when an hash does not come back, so a publisher
swap is a red test rather than a quiet rebuild over different content.
"""

import hashlib
import sys
import urllib.request
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("PyYAML is required: pip install -r requirements.txt")

ROOT = Path(__file__).resolve().parent.parent
REGISTER = ROOT / "provenance" / "treaties.yaml"
RETRIES = 3
TIMEOUT = 120


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download(url: str, destination: Path) -> None:
    request = urllib.request.Request(url, headers={"User-Agent": "itlc-library/0"})
    last_error: Exception | None = None
    for attempt in range(1, RETRIES + 1):
        try:
            with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
                destination.write_bytes(response.read())
            return
        except Exception as error:  # noqa: BLE001 - retried, then re-raised
            last_error = error
            print(f"  attempt {attempt}/{RETRIES} failed: {error}")
    raise RuntimeError(f"download failed after {RETRIES} attempts: {url}") from last_error


def main() -> int:
    register = yaml.safe_load(REGISTER.read_text(encoding="utf-8"))
    cache = ROOT / "sources"
    cache.mkdir(exist_ok=True)
    failures = 0
    for entry in register["treaties"]:
        source = entry["source"]
        target = cache / Path(source["url"]).name
        expected = source["sha256"]
        if target.exists() and sha256_of(target) == expected:
            print(f"OK   {entry['id']} (cached, hash verified)")
            continue
        print(f"GET  {entry['id']} <- {source['url']}")
        download(source["url"], target)
        actual = sha256_of(target)
        if actual != expected:
            failures += 1
            print(f"FAIL {entry['id']}: sha256 mismatch\n"
                  f"     expected {expected}\n"
                  f"     actual   {actual}", file=sys.stderr)
        else:
            print(f"OK   {entry['id']} (downloaded, hash verified)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
