#!/usr/bin/env python3
"""
AgoraOWL SHACL validation script.

By default this validates the ontology and AgoraOWL-authored examples for the
latest version under `src/`. Official DCAT-AP-ES reference RDF examples can be
included explicitly with `--include-official-examples`.

Note: the official DCAT-AP-ES examples are expected to fail under this flag.
See the "Fallos esperados con --include-official-examples" section in
src/<version>/shapes/compliance/dcat-ap-es/README.md for why (RDFS entailment
of dcat:Catalog as a dcat:Dataset, and external-vocabulary dependencies the
standalone examples intentionally omit) -- it is not a regression.
"""

import re
import sys
from pathlib import Path

try:
    from pyshacl import validate
    from rdflib import Graph, Namespace
except ImportError:
    print("[FAIL] Please install dependencies: pip install rdflib pyshacl")
    sys.exit(1)

SH = Namespace("http://www.w3.org/ns/shacl#")


def should_include_official_examples(argv: list[str]) -> bool:
    """Include official DCAT-AP-ES RDF examples only when explicitly requested."""
    return "--include-official-examples" in argv


def find_latest_version(src_dir: Path) -> str | None:
    """Find the latest semver version folder in src/."""
    versions: list[str] = []
    if not src_dir.exists():
        return None
    for item in src_dir.iterdir():
        if item.is_dir() and re.match(r"^\d+\.\d+\.\d+$", item.name):
            versions.append(item.name)
    if not versions:
        return None
    versions.sort(key=lambda version: [int(part) for part in version.split(".")])
    return versions[-1]


def validate_file(
    data_file: Path,
    shape_files: list[Path],
    ontology_file: Path,
    vocab_files: list[Path] | None = None,
    fmt: str = "turtle",
) -> bool:
    """Validate a single data file against SHACL shapes."""
    print(f"\nValidating: {data_file.name} (Format: {fmt})")

    report_dir = Path("validation_reports")
    report_dir.mkdir(exist_ok=True)
    report_file = report_dir / f"report_{data_file.stem}.txt"

    data_graph = Graph()
    data_graph.parse(str(data_file), format=fmt)

    merged_graph = Graph()
    merged_graph += data_graph
    merged_graph.parse(str(ontology_file), format="turtle")

    if vocab_files:
        for vocab in vocab_files:
            if vocab.exists():
                merged_graph.parse(str(vocab), format="turtle")

    shapes_graph = Graph()
    for shape_file in shape_files:
        if shape_file.exists():
            shapes_graph.parse(str(shape_file), format="turtle")

    _, results_graph, results_text = validate(
        merged_graph,
        shacl_graph=shapes_graph,
        ont_graph=None,
        inference="rdfs",
        debug=False,
    )

    violations = list(results_graph.subjects(SH.resultSeverity, SH.Violation))
    is_success = len(violations) == 0

    with open(report_file, "w", encoding="utf-8") as handle:
        handle.write(results_text)

    if is_success:
        print("   [OK] Success (No Violations)")
    else:
        print(f"   [FAIL] Failed ({len(violations)} Violations found)")
    
    print(f"      Report saved to: {report_file}")

    return is_success


def main() -> None:
    """Run SHACL validation for the latest version."""
    script_dir = Path(__file__).parent.resolve()
    root_dir = script_dir.parent
    src_dir = root_dir / "src"

    version = find_latest_version(src_dir)
    if not version:
        print("[FAIL] No version folder found in src/")
        sys.exit(1)

    include_official_examples = should_include_official_examples(sys.argv[1:])

    print(f"AgoraOWL SHACL Validation (v{version})")
    print("=" * 50)

    version_dir = src_dir / version
    ontology_file = version_dir / "AgoraOWL.ttl"

    shape_dir = version_dir / "shapes" / "compliance" / "dcat-ap-es" / "1.0.0"
    shape_files = [
        shape_dir / "shacl_common_shapes.ttl",
        shape_dir / "shacl_catalog_shape.ttl",
        shape_dir / "shacl_dataset_shape.ttl",
        shape_dir / "shacl_distribution_shape.ttl",
        shape_dir / "shacl_dataservice_shape.ttl",
        shape_dir / "shacl_mdr-vocabularies.shape.ttl",
        version_dir / "shapes" / "edaan-shapes.ttl",
        version_dir / "shapes" / "idsa-shapes.ttl",
        version_dir / "shapes" / "cred-alignment-shapes.ttl",
        version_dir / "shapes" / "dcat-ap-alignment.ttl",
    ]

    missing_shapes = [shape for shape in shape_files if not shape.exists()]
    if missing_shapes:
        print("[FAIL] Missing SHACL shape files:")
        for shape in missing_shapes:
            print(f"   - {shape}")
        sys.exit(1)

    vocab_files: list[Path] = []
    major, minor, _ = map(int, version.split("."))
    if major == 0 and minor < 6:
        vocab_dir = version_dir / "vocabularies"
        vocab_names = [
            "metric-types.ttl",
            "observed-properties.ttl",
            "agro-vocab.ttl",
            "datatype-scheme.ttl",
            "data-theme.ttl",
            "crs-vocab.ttl",
            "access-rights.ttl",
        ]
        vocab_files = [vocab_dir / name for name in vocab_names]

    examples_dir = version_dir / "examples"
    official_examples_dir = examples_dir / "dcat-ap-es" / "rdf" / "1.0.0"

    data_files: list[tuple[Path, str]] = [
        (ontology_file, "turtle"),
        (examples_dir / "test-consistency.ttl", "turtle"),
        (examples_dir / "eo-instances.ttl", "turtle"),
        (examples_dir / "cred-asset-example.ttl", "turtle"),
        (examples_dir / "energy-example.ttl", "turtle"),
    ]

    if include_official_examples and official_examples_dir.exists():
        for rdf_file in official_examples_dir.glob("*.rdf"):
            data_files.append((rdf_file, "xml"))

    all_valid = True
    for data_file, fmt in data_files:
        if data_file.exists() and not validate_file(data_file, shape_files, ontology_file, vocab_files, fmt):
            all_valid = False

    print("\n" + "=" * 50)
    if all_valid:
        print(f"[OK] All SHACL validations passed for v{version}!")
        sys.exit(0)

    print(f"[FAIL] Some SHACL validations failed for v{version}.")
    sys.exit(1)


if __name__ == "__main__":
    main()
