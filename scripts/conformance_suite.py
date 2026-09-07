#!/usr/bin/env python3
"""
AgoraOWL conformance suite.

Asserts both directions:

  * every positive example still conforms, and
  * every negative fixture is actually REJECTED by the layer that owns it.

The second half is the point. Until v1.3.0 the repository only contained
passing fixtures, so a validator that accepted everything would have looked
healthy: the ontology declared no disjointness, no functional properties and no
differentFrom axioms, which made `robot reason` incapable of failing on any
input whatsoever.

OWL fixtures are skipped (not failed) when ROBOT is unavailable. Point
AGORAOWL_ROBOT_JAR at robot.jar, or put `robot` on PATH, to run them.

Usage:
    python3 scripts/conformance_suite.py [--version 1.3.0]
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from pyshacl import validate
from rdflib import Graph, Namespace

SH = Namespace("http://www.w3.org/ns/shacl#")
ROOT = Path(__file__).resolve().parent.parent


def latest_version(src: Path) -> str:
    versions = [d.name for d in src.iterdir() if d.is_dir() and re.fullmatch(r"\d+\.\d+\.\d+", d.name)]
    return sorted(versions, key=lambda v: [int(p) for p in v.split(".")])[-1]


def load_shapes(paths: list[Path]) -> Graph:
    graph = Graph()
    for path in paths:
        if path.exists():
            graph.parse(path, format="turtle")
    return graph


def run_shacl(data_files: list[Path], shapes: Graph, ontology: Path | None, inference: str,
              advanced: bool = True) -> tuple[bool, int]:
    graph = Graph()
    for data_file in data_files:
        graph.parse(data_file, format="turtle")
    if ontology is not None:
        graph.parse(ontology, format="turtle")
    conforms, results, _ = validate(graph, shacl_graph=shapes, inference=inference, advanced=advanced)
    if not hasattr(results, "subjects"):
        raise RuntimeError(f"SHACL engine failure on {[f.name for f in data_files]}")
    violations = list(results.subjects(SH.resultSeverity, SH.Violation))
    # Judge on Violations only: sh:Warning / sh:Info results also set conforms=False
    # in pyshacl, and several v1.3.0 shapes deliberately report at Warning level.
    del conforms
    return not violations, len(violations)


def find_robot() -> list[str] | None:
    jar = os.environ.get("AGORAOWL_ROBOT_JAR")
    if jar and Path(jar).exists():
        return ["java", "-jar", jar]
    if shutil.which("robot"):
        return ["robot"]
    return None


def run_robot_reason(robot: list[str], fixture: Path, ontology: Path) -> bool:
    """Return True when the reasoner REJECTS the fixture (inconsistent/unsatisfiable)."""
    with tempfile.TemporaryDirectory() as tmp:
        catalog = Path(tmp) / "catalog.xml"
        catalog.write_text(
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<catalog xmlns="urn:oasis:names:tc:entity:xmlns:xml:catalog" prefer="public">\n'
            f'  <uri name="https://w3id.org/AgoraOWL/" uri="file:{ontology.resolve()}"/>\n'
            "</catalog>\n",
            encoding="utf-8",
        )
        result = subprocess.run(
            robot + ["reason", "--catalog", str(catalog), "--input", str(fixture),
                     "--reasoner", "hermit", "--output", str(Path(tmp) / "out.owl")],
            capture_output=True, text=True,
        )
        return result.returncode != 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--version", default=None, help="version folder under src/ (default: latest)")
    args = parser.parse_args()

    src = ROOT / "src"
    version = args.version or latest_version(src)
    base = src / version
    print(f"AgoraOWL conformance suite (v{version})")
    print("=" * 62)

    ontology = base / "AgoraOWL.ttl"
    dcat_ap_es = base / "shapes" / "compliance" / "dcat-ap-es" / "1.0.0"
    authoring = load_shapes([
        dcat_ap_es / "shacl_common_shapes.ttl", dcat_ap_es / "shacl_catalog_shape.ttl",
        dcat_ap_es / "shacl_dataset_shape.ttl", dcat_ap_es / "shacl_distribution_shape.ttl",
        dcat_ap_es / "shacl_dataservice_shape.ttl", dcat_ap_es / "shacl_mdr-vocabularies.shape.ttl",
        base / "shapes" / "edaan-shapes.ttl", base / "shapes" / "cred-alignment-shapes.ttl",
        base / "shapes" / "dcat-ap-alignment.ttl",
    ])
    connector = load_shapes([base / "shapes" / "edc-connector-shapes.ttl"])

    failures: list[str] = []
    skipped = 0

    print("\n-- positive: authoring examples MUST conform")
    for example in sorted((base / "examples").glob("*.ttl")):
        # advanced=False: the official DCAT-AP-ES shapes carry sh:sparql constraints
        # with no sh:prefixes block, so SHACL-SPARQL cannot resolve their prefixed
        # names. Those constraints are therefore never evaluated - by the upstream
        # profile's own construction, not by choice. AgoraOWL's own shapes are run
        # separately below with advanced=True so their SPARQL rules do execute.
        ok, count = run_shacl([example], authoring, ontology, "rdfs", advanced=False)
        print(f"   {'PASS' if ok else 'FAIL'}  {example.name}" + ("" if ok else f"  ({count} violations)"))
        if not ok:
            failures.append(f"positive {example.name}")

    print("\n-- positive: EDC connector projection MUST conform")
    projection = base / "examples" / "edc" / "dsp-catalog-dataset.ttl"
    if projection.exists():
        ok, count = run_shacl([projection], connector, None, "none")
        print(f"   {'PASS' if ok else 'FAIL'}  {projection.name}" + ("" if ok else f"  ({count} violations)"))
        if not ok:
            failures.append(f"positive {projection.name}")

    print("\n-- positive: AgoraOWL own shapes (SHACL-SPARQL enabled) MUST conform")
    own = load_shapes([base / "shapes" / "edaan-shapes.ttl"])
    for example in sorted((base / "examples").glob("*.ttl")):
        ok, count = run_shacl([example], own, ontology, "rdfs")
        print(f"   {'PASS' if ok else 'FAIL'}  {example.name}" + ("" if ok else f"  ({count} violations)"))
        if not ok:
            failures.append(f"positive(own) {example.name}")

    print("\n-- negative: SHACL fixtures MUST be rejected")
    combined = Graph()
    combined += own
    combined += connector
    for fixture in sorted((base / "examples" / "negative").glob("shacl-*.ttl")):
        ok, count = run_shacl([fixture], combined, None, "rdfs")
        rejected = not ok
        print(f"   {'PASS' if rejected else 'FAIL'}  {fixture.name}"
              f"  ({count} violations)" + ("" if rejected else "  <-- NOT DETECTED"))
        if not rejected:
            failures.append(f"negative {fixture.name} was not detected")

    print("\n-- negative: OWL fixtures MUST make the reasoner fail")
    robot = find_robot()
    if robot is None:
        print("   SKIP  ROBOT not found (set AGORAOWL_ROBOT_JAR or put `robot` on PATH)")
        skipped = len(list((base / "examples" / "negative").glob("owl-*.ttl")))
    else:
        for fixture in sorted((base / "examples" / "negative").glob("owl-*.ttl")):
            rejected = run_robot_reason(robot, fixture, ontology)
            print(f"   {'PASS' if rejected else 'FAIL'}  {fixture.name}"
                  + ("" if rejected else "  <-- reasoner accepted a graph it must reject"))
            if not rejected:
                failures.append(f"negative {fixture.name} was not detected")

    print("\n" + "=" * 62)
    if failures:
        print(f"[FAIL] {len(failures)} conformance failure(s):")
        for failure in failures:
            print(f"   - {failure}")
        return 1
    print(f"[OK] conformance suite passed" + (f" ({skipped} OWL fixture(s) skipped)" if skipped else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
