# AgoraOWL v1.3.0

**Theme: make the validation layers actually validate, and make the ontology safe to merge.**

v1.2.1 was syntactically clean and passed every check in this repository. The
problem was what those checks could not see. This release closes four gaps found
by auditing the ontology against external tooling (ROBOT OWL 2 profile
validation, HermiT, a diff against the authoritative DCAT / DCMI / ODRL / FOAF
documents) and against real connector payloads from a running Eclipse EDC
deployment.

| Change | Why it was needed |
| --- | --- |
| **OWL 2 DL conformance** | v1.2.1 had 13 DL profile violations. `robot validate-profile --profile DL` failed, so strict OWL tooling either rejected the ontology or silently dropped axioms. |
| **Discriminating axioms** | v1.2.1 declared zero disjointness, zero functional properties and zero `differentFrom`. No reasoner could detect any modelling error: `robot reason` was a smoke test that could not fail on any input. |
| **Third-party alignment split out** | v1.2.1 asserted ~110 `rdfs:domain`/`rdfs:range` axioms over DCAT, DCMI, ODRL and FOAF properties. 16 of them contradicted the source vocabulary. Anyone merging AgoraOWL with the real ODRL inherited `odrl:permission range odrl:Rule`, collapsing the Permission/Prohibition/Duty distinction that policy engines depend on. |
| **Executable matchmaking semantics** | The normative table in `docs/ARCHITECTURE.md` referenced terms that did not exist and left "constraint cannot be evaluated" undefined - a case AgoraOWL's own reference example falls into. |
| **EDC connector profile** | Nothing in the repository described, or validated, the graph a partner actually receives over the Dataspace Protocol. |

---

## What is in this folder

| File | Role |
| --- | --- |
| `AgoraOWL.ttl` | The core ontology. **OWL 2 DL conformant.** Asserts no logical axiom over any third-party property. |
| `alignment.ttl` | **New.** Optional, opt-in module holding the corrected third-party `domain`/`range` axioms. The core does not import it. |
| `context.jsonld` | **New.** The JSON-LD context. Publish it at `https://w3id.org/AgoraOWL/context.jsonld`. |
| `shapes/edaan-shapes.ttl` | Authoring shapes. Extended to cover the 9 classes and the governance properties that had no shape at all in v1.2.1. |
| `shapes/edc-connector-shapes.ttl` | **New.** The wire profile: validates the `dcat:Dataset` an EDC connector publishes over DSP. Self-contained. |
| `shapes/idsa-shapes.ttl` | **Rewritten.** The v1.2.1 file contained zero shapes and 26 imports of files that do not exist. |
| `shapes/compliance/dcat-ap-es/` | Official Spanish Government shapes, unchanged. |
| `examples/edc/` | **New.** A reference EDC Management API payload and the DSP catalogue projection it produces. |
| `examples/negative/` | **New.** Fixtures that MUST be rejected, one per validation layer. |

---

## 1. OWL 2 DL conformance

```bash
robot validate-profile --profile DL --input src/1.3.0/AgoraOWL.ttl
# OWL 2 DL Profile Report: [Ontology and imports closure in profile]
```

The 13 violations in v1.2.1 came from two causes, both fixed:

* `dct:modified` was declared both `owl:AnnotationProperty` and
  `owl:DatatypeProperty`. Annotation/data punning is forbidden in OWL 2 DL. The
  data property declaration is gone.
* `rdfs:Resource` and `rdfs:Datatype` were declared as `owl:Class` and used as
  ranges of `odrl:action`, `odrl:leftOperand`, `odrl:operator`, `dcat:accessURL`,
  `dcat:endpointURL`, `:hasDataType` and `:requiresDataType`. Using reserved
  vocabulary as a class is not OWL 2 DL. Ranges now point at the real classes,
  or are omitted and enforced in SHACL.

The core **and** core + `alignment.ttl` are both DL conformant.

## 2. The OWL layer can now fail

New in the core: `owl:AllDisjointClasses` over
`{DataSpecification, FieldMapping, DataProfile, DataConstraint, Metric}` and over
`{DataAsset, DataApp}`, `InputProfile owl:disjointWith OutputProfile`, and ten
functional properties (`mapsToSpecification`, `mapsField`, `hasUnit`,
`hasDataType`, `hasObservableProperty`, `hasFeatureOfInterest`, `metricType`,
`metricValue`, `constraintValue`, `constraintOperator`).

`examples/negative/owl-*.ttl` are graphs that HermiT must reject. They pass under
v1.2.1 and fail under v1.3.0 - which is the point.

**SHACL remains the normative validation layer.** OWL reasoning is a schema
coherence check, not a data validation mechanism, and this release stops the
repository from presenting it as one.

## 3. Alignment is opt-in

```bash
# core only - no axioms over anyone else's properties
robot merge --input src/1.3.0/AgoraOWL.ttl ...

# with the restated third-party axioms
robot merge --input src/1.3.0/AgoraOWL.ttl --input src/1.3.0/alignment.ttl ...
```

Corrections applied while moving (each diffed against the authoritative
document): `odrl:permission` → `odrl:Permission`, `odrl:prohibition` →
`odrl:Prohibition`, `odrl:obligation` → `odrl:Duty`, `odrl:action` →
`odrl:Action`, `odrl:leftOperand` → `odrl:LeftOperand`, `odrl:operator` →
`odrl:Operator`, `odrl:assigner` → `odrl:Party`, `dcat:mediaType` →
`dct:MediaType`. Dropped because the source refutes them: `dct:format domain`,
`foaf:name domain`, `dct:accrualPeriodicity domain`.

## 4. Matchmaking is now executable

New terms: `:ConstraintEnforcement` with `:Mandatory` / `:Preferred`,
`:constraintEnforcement`, `:requiresFormat`, `:requiresMediaType`,
`:UnitIntervalMetric`, plus the `:Consistency` and `:Duplication` metric types
that real connector quality blobs already emit.

A constraint that cannot be evaluated because the candidate publishes no
evidence rejects the match when it is `:Mandatory`, and only lowers the ranking
otherwise. The default is `:Preferred`. See `docs/ARCHITECTURE.md` §6.1.

## 5. Eclipse EDC connector profile

An EDC asset and the DCAT dataset a partner receives are **not the same graph**.
In the DSP catalogue the connector types the node `dcat:Dataset` and lifts every
`edc:properties` entry to a direct predicate of it, so shapes targeting
`dcat:Dataset` never fire on a Management API payload.

```bash
# turn a Management API payload into the graph partners actually see
python3 scripts/edc_catalog_projection.py src/1.3.0/examples/edc/asset-payload.jsonld \
        --local-context src/1.3.0/context.jsonld -o /tmp/catalog.ttl
```

Two EDC behaviours are load-bearing and are documented inline in
`examples/edc/asset-payload.jsonld`:

* A payload whose `@context` does not include the official EDC management
  context, or whose `@type` is not `Asset`, expands to **exactly one triple**.
  The semantic annotation is silently discarded. Put the semantic type
  *alongside*: `"@type": ["Asset", "agoraowl:DataAsset"]`.
* Language tags and datatypes are lost on **scalar** asset properties
  (`JsonValueToGenericTypeTransformer` keeps only the `@value`). They survive
  inside nested node objects, which is why the AgoraOWL subtree round-trips
  intact. Do not expect DCAT-AP-ES multilingual conformance from the DSP
  catalogue output.

Verified against Eclipse EDC Connector v0.18.0.

### Registering AgoraOWL as a dataspace profile (EDC 0.18+)

```properties
edc.dataspace.profiles.agora.name=agora
edc.dataspace.profiles.agora.protocol.version=2025-1
edc.dataspace.profiles.agora.protocol.binding=http
edc.dataspace.profiles.agora.protocol.namespace=https://w3id.org/dspace/2025/1/
edc.dataspace.profiles.agora.jsonld.context.urls=https://w3id.org/dspace/2025/1/context.jsonld,https://w3id.org/AgoraOWL/context.jsonld
```

EDC registers those contexts and uses them to compact outgoing DSP messages, so
partners receive readable, resolvable AgoraOWL terms. `jsonLdContextsUrl` does
not exist before 0.18.

---

## Validation

```bash
python3 scripts/check_rdf.py             # syntax
python3 scripts/validate_shacl.py        # SHACL, all profiles
python3 scripts/conformance_suite.py     # positives AND negatives
bash    scripts/local-validate.sh        # everything, in Docker
```

`conformance_suite.py` is the one that matters: it asserts that the positive
examples conform **and** that every fixture in `examples/negative/` is rejected
by the layer that owns it. Set `AGORAOWL_ROBOT_JAR` to run the OWL fixtures.

### Known limitation of the upstream DCAT-AP-ES shapes

The official DCAT-AP-ES shape files carry `sh:sparql` constraints with no
`sh:prefixes` block. Prefixed names in those queries cannot be resolved, so those
particular constraints are not evaluated by any conformant SHACL-SPARQL engine.
This is upstream and is not patched here; AgoraOWL's own shapes declare their
prefixes properly and do execute.
