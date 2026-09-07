#!/usr/bin/env python3
"""
Assert that the committed DSP catalogue projection still matches the payload it
was generated from.

The projection is a derived artefact: if someone edits the reference EDC payload
and forgets to regenerate it, the repository would ship an example that no longer
corresponds to what the connector would publish.

Usage:
    python3 scripts/check_projection_sync.py [--version 1.3.0]
"""

import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from rdflib import Graph
from rdflib.compare import to_isomorphic

ROOT = Path(__file__).resolve().parent.parent


def latest_version(src: Path) -> str:
    versions = [d.name for d in src.iterdir() if d.is_dir() and re.fullmatch(r"\d+\.\d+\.\d+", d.name)]
    return sorted(versions, key=lambda v: [int(p) for p in v.split(".")])[-1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--version", default=None)
    args = parser.parse_args()

    version = args.version or latest_version(ROOT / "src")
    base = ROOT / "src" / version
    payload = base / "examples" / "edc" / "asset-payload.jsonld"
    committed = base / "examples" / "edc" / "dsp-catalog-dataset.ttl"

    if not payload.exists() or not committed.exists():
        print(f"[SKIP] no EDC example under src/{version}")
        return 0

    with tempfile.TemporaryDirectory() as tmp:
        regenerated = Path(tmp) / "projection.ttl"
        subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "edc_catalog_projection.py"), str(payload),
             "--local-context", str(base / "context.jsonld"), "-o", str(regenerated)],
            check=True,
        )
        expected = to_isomorphic(Graph().parse(regenerated, format="turtle"))

    actual = to_isomorphic(Graph().parse(committed, format="turtle"))
    if expected != actual:
        print("[FAIL] the committed DSP projection no longer matches the payload.")
        print("       Re-run scripts/edc_catalog_projection.py and commit the result.")
        return 1

    print(f"[OK] DSP projection for v{version} is up to date")
    return 0


if __name__ == "__main__":
    sys.exit(main())
