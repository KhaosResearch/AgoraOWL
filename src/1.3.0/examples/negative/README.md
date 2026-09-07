# Negative conformance fixtures (v1.3.0)

Up to v1.2.1 every fixture in this repository was expected to PASS. A suite that
only contains passing cases cannot distinguish a working validator from a
vacuous one: when these fixtures were first written, `robot reason` could not
fail on *any* input because the ontology declared no disjointness, no functional
properties and no `differentFrom` axioms.

Each file below is a known-bad graph together with the layer that must reject it
and the expected message. `scripts/conformance_suite.py` asserts that the
positive examples still conform AND that every fixture here is rejected.

| Fixture | Layer | Must be rejected because |
| --- | --- | --- |
| `owl-disjoint-layers.ttl` | OWL (HermiT) | one node is both a `DataSpecification` and a `FieldMapping` |
| `owl-two-specifications.ttl` | OWL (HermiT) | a `FieldMapping` maps to two provably different specifications |
| `shacl-spec-without-property.ttl` | SHACL | a `DataSpecification` with no `hasObservableProperty` |
| `shacl-mapping-without-field.ttl` | SHACL | a `FieldMapping` with no `mapsField` |
| `shacl-metric-out-of-scale.ttl` | SHACL | a completeness metric published as `93` instead of `0.93` |
| `shacl-non-canonical-unit.ttl` | SHACL | `hasUnit` pointing at `http://www.qudt.org/...` instead of `http://qudt.org/...` |
| `shacl-denormalised-semantics.ttl` | SHACL | `mapsField` copied up to the dataset node for search faceting |
| `shacl-threshold-without-operator.ttl` | SHACL | a `constraintValue` with no `constraintOperator` |
