# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.1](https://github.com/KhaosResearch/AgoraOWL/compare/v1.3.0...v1.3.1) (2026-09-11)


### Fixed

* **context:** add the 17 agoraowl: terms missing from the JSON-LD context ([03cfa74](https://github.com/KhaosResearch/AgoraOWL/commit/03cfa74ac2232633e9415189c6aa6fe6c935c127))
* **context:** remove the invalid empty-string term definition ([55fd54b](https://github.com/KhaosResearch/AgoraOWL/commit/55fd54b695cd2346418fd677bf9da0e0e2ae454e))
* **w3id:** add missing Turtle fallback for term IRIs; trim description comment ([a174f14](https://github.com/KhaosResearch/AgoraOWL/commit/a174f1459424f2ba16e4716f0888f23533bc43ce))
* **w3id:** cut README down to Scope and Maintainers only ([5671e8b](https://github.com/KhaosResearch/AgoraOWL/commit/5671e8b50ce372b338f583056a81dd08f47ca3b8))
* **w3id:** drop the .htaccess Contact block, now redundant with README ([4a958af](https://github.com/KhaosResearch/AgoraOWL/commit/4a958afe01036fac8003e778689527adb7d8a306))
* **w3id:** trim README/.htaccess to the previously-approved format ([58e4411](https://github.com/KhaosResearch/AgoraOWL/commit/58e44119fd59913a9cb5c008c658f0b991783e40))
* **w3id:** trim README/.htaccess to the previously-approved format ([a22de0d](https://github.com/KhaosResearch/AgoraOWL/commit/a22de0da538cab67c8a2cf8eba2ce0a16397df30))


### Changed

* **deploy-docs:** allow republishing an existing version on demand ([85b349f](https://github.com/KhaosResearch/AgoraOWL/commit/85b349f2a4e536c6f16615a024ad726a81894924))

## [1.3.0](https://github.com/KhaosResearch/AgoraOWL/compare/v1.2.1...v1.3.0) (2026-09-07)


### Added

* **ci:** publish alignment module, JSON-LD context, and vocabulary docs ([88d1cd6](https://github.com/KhaosResearch/AgoraOWL/commit/88d1cd6d0635e9e54a6221a212b9433f6a359878))
* **ontology:** release v1.3.0 with OWL 2 DL conformance and executable matchmaking ([18b284f](https://github.com/KhaosResearch/AgoraOWL/commit/18b284f9f853b96fd736146e7721ad897310862e))
* **tooling:** add conformance suite, EDC projection, and vocabulary docs generator ([0b7a671](https://github.com/KhaosResearch/AgoraOWL/commit/0b7a6717c0f8fa38b1995f0d385806f81e22a257))
* **w3id:** add PID resolution rules and redirection verification harness ([fff48fd](https://github.com/KhaosResearch/AgoraOWL/commit/fff48fdd984c620df1a00ed375f7a33be1878ea2))


### Fixed

* **compat:** correct stale file paths in ISA testbed config ([4fcf4ea](https://github.com/KhaosResearch/AgoraOWL/commit/4fcf4ea5cb6c9b2494069b39e31cb8e01bd8ecd7))


### Changed

* **architecture:** correct the branching model to match actual practice ([daaaad4](https://github.com/KhaosResearch/AgoraOWL/commit/daaaad47f6c076fb93793c647a391d1d42d44d57))
* update architecture, guides, citation and landing page for v1.3.0 ([ee701b1](https://github.com/KhaosResearch/AgoraOWL/commit/ee701b1c45d29fa10edf65a2c66103460d632adc))
* validate OWL 2 DL profile, SHACL, and conformance suite on every PR ([c253f00](https://github.com/KhaosResearch/AgoraOWL/commit/c253f00cbc602925fdd1f5c1ff6c37b9ff6753a1))

## [1.2.1](https://github.com/KhaosResearch/AgoraOWL/compare/v1.2.0...v1.2.1) (2026-07-28)


### Fixed

* **ci:** preserve nested shape/example dirs and validate shape file refs ([aa2c16c](https://github.com/KhaosResearch/AgoraOWL/commit/aa2c16cd89b4b08b48219661b31649f45a1a51f3))
* **ontology:** release v1.2.1 with DCAT3 alignment and OWL modeling fixes ([d7f1e08](https://github.com/KhaosResearch/AgoraOWL/commit/d7f1e087fcd06064746a9ecd67cd082a897b0f71))


### Changed

* **release:** correct release-please manifest drift back to v1.2.0 ([217102a](https://github.com/KhaosResearch/AgoraOWL/commit/217102ab2a30db56a30a911c448f8e4d8c3b4329))

## [1.2.0](https://github.com/KhaosResearch/AgoraOWL/compare/v1.1.0...v1.2.0) (2026-03-26)

### Added

- **Ontology**: Added `:requiresDataType` to `DataConstraint` for formalizing technical data type requirements.
- **Ontology**: Symmetric profiling architecture for `DataApp` using `:hasInputProfile` and `:hasOutputProfile`.
- **Ontology**: Promotions of `:OutputProfile` to a proper class for balanced I/O modeling.
- **Ontology**: **DCAT 3 Compliance**: Added `dct:temporal` and `dcat:inSeries` object properties.
- **Ontology**: **DCAT 3 Compliance**: Added `dct:PeriodOfTime` and `dcat:DatasetSeries` classes.
- **Ontology**: **DCAT 3 Compliance**: Updated and standardized `dcat:spatialResolutionInDegrees`, `dcat:spatialResolutionInMeters`, and `dcat:temporalResolution` properties.

### Changed

- **Ontology**: Refactored `:OutputProfile` and `:InputProfile` to use `minCardinality 1` for `hasDataSpecification`.
- **Ontology**: Generalized administrative metadata domains for both `ids:Resource` and `:DataApp`.
- **Ontology**: Updated `hasFieldMapping` labels to "field mapping" for consistency.
- **Ontology**: Enforced `FieldMapping` as the primary domain for `hasDataType`.
- **metadata**: update v1.2.0 description and publisher URI to Khaos Research Group ([990ccb0](https://github.com/KhaosResearch/AgoraOWL/commit/990ccb0ff1e4028d28b21b2d32415dc9e45163b7))
- **ontology**: implement DataProfile superclass hierarchy (R12) ([36a71b2](https://github.com/KhaosResearch/AgoraOWL/commit/36a71b26999a03d233c43efd0c1aded845abef47))
- **release**: update documentation, citation, and security policy for v1.2.0 ([ef15a4c](https://github.com/KhaosResearch/AgoraOWL/commit/ef15a4ce54788b80bb8b8b47a176835338d37d49))

### Deprecated

- **Ontology**: Deprecated legacy properties `requiresProfile` and `producesProfile`.
- **Ontology**: Deprecated technical properties (`hasSchemaType`, `conformsToSchema`) on `DataSpecification`.

## [1.1.0](https://github.com/KhaosResearch/AgoraOWL/compare/v1.0.0...v1.1.0) (2026-03-26)

### Added

- **Compliance**: Full DCAT-AP-ES 1.0.0 and DCAT 3.0 compliance.
- **Validation**: Integrated official Spanish Government validation tools (Docker + `validate-local.sh`).
- **Shapes**: New specialized SHACL shapes for Spanish Data Office (CRED) and official vocabularies.
- **Metadata**: Standardized DIR3-compliant URIs for Agents and vCard alignment for ContactPoints.
- **ci**: add official DCAT-AP-ES 1.0.0 validation suite and docker environment ([048eafb](https://github.com/KhaosResearch/AgoraOWL/commit/048eafb4a7c4649fb5eeb40171b6e6a9af96fc5a))
- **compliance**: achieve full DCAT-AP-ES 1.0.0 compliance and add official validation infrastructure ([67cda14](https://github.com/KhaosResearch/AgoraOWL/commit/67cda14e6226f287f74c31b29c316ea041e40bf3))
- **v1.1.0**: align documentation and ontology with v1.1.0 standards ([1fe3531](https://github.com/KhaosResearch/AgoraOWL/commit/1fe3531dd45d7fc1b3c0d7d5d367b9166af50428))

### Fixed

- **SHACL**: Resolved URI collisions and refined technical distribution targets.
- **Consistency**: Added mandatory spatial and temporal fields to test suites for full validation.
- align v1.1.0 docs, ontology notes and release tooling ([edab072](https://github.com/KhaosResearch/AgoraOWL/commit/edab072c63974ca84edc2dc6bf605d9c0b7dd350))

### Changed

- **Architecture**: Refactored DataSpecifications into atomic reusable units, decoupled from technical distribution details via FieldMappings.

## [1.0.0] - 2026-03-12

### Added

- **Architecture**: Decoupled DataSpecifications from technical distributions via FieldMappings.
- **Library Model**: Enabled "Profile Libraries" for schema-agnostic semantic definitions.

### Changed

- **Matchmaking**: Upgraded to Matchmaking 2.0 with unit-aware constraints.

## [0.9.0](https://github.com/KhaosResearch/AgoraOWL/compare/v0.8.1...v0.9.0) (2026-03-13)

### ⚠ BREAKING CHANGES

- Decoupled property declarations from subjects in matchmaking through the introduction of FeatureOfInterest. DataAssets and DataProfiles now require FOI associations for accurate semantic discovery.

### Added

- incorporate Feature of Interest (SOSA/SSN) and release v0.9.0 ([df651a2](https://github.com/KhaosResearch/AgoraOWL/commit/df651a2776b77a00d78ef588998636f132e8f103))

### Fixed

- **shacl:** align shapes with dcat:theme and fix test distribution requirements ([38c83b8](https://github.com/KhaosResearch/AgoraOWL/commit/38c83b8a1e5285a237fc827f33f2ba536eb86b75))

### Changed

- enrich documentation and examples with FOI and dcat:theme ([3a011f1](https://github.com/KhaosResearch/AgoraOWL/commit/3a011f14d4ecb54fc76f0b85d86bd7ee64041c1e))

## [0.8.1](https://github.com/KhaosResearch/AgoraOWL/compare/v0.8.0...v0.8.1) (2026-03-10)

### Fixed

- add Spanish labels to observed-properties and update examples for release v0.8.1 ([641d927](https://github.com/KhaosResearch/AgoraOWL/commit/641d9271281f691281e0905daaba1e43fa56b881))
- add Spanish labels to observed-properties and update examples for release v0.8.1 ([11f78e1](https://github.com/KhaosResearch/AgoraOWL/commit/11f78e1c71fcb9e44f4821d2c07bdadd492c5524))

## [0.8.0] - 2026-03-04

### ⚠ BREAKING CHANGES

- **ontology:** major update for CRED (Spanish Data Office) and UNE 0087:2025 alignment.
- Added mandatory hierarchy: `dcat:Catalog` -> `dcat:Dataset` -> `dcat:Distribution`.
- Enforced `xsd:nonNegativeInteger` for `dcat:byteSize`.

### Added

- **ontology:** alignment with DCAT-AP 3.0, ODRL 2.2, and FOAF.
- **shapes:** created `src/0.8.0/shapes/cred-alignment-shapes.ttl` for SHACL validation of CRED entities.
- **classes:** added `dcat:Catalog`, `dcat:DataService`, `dcat:Resource`, `odrl:Policy`, etc.
- **properties:** added 25 Object Properties and 6 Data Properties from CRED recommendation.

### Changed

- **hierarchy:** established `dcat:Catalog subClassOf dcat:Dataset`, `dcat:Dataset subClassOf dcat:Resource`.
- **metadata:** updated ontology version to 0.8.0.

## [0.7.0] - 2026-02-24

### Added

- **ontology:** full integration with QUDT units.
- **ontology:** introduced `measuresProperty` for metrics.
- **vocabularies:** integrated SIEX (Spain) agricultural catalogs.

## [0.6.1](https://github.com/KhaosResearch/AgoraOWL/compare/v0.6.0...v0.6.1) (2026-02-18)

### Fixed

- **ontology:** refine metric definitions and cleanup vocabularies ([d7290d6](https://github.com/KhaosResearch/AgoraOWL/commit/d7290d6eb5b106e68456c9c51ccca20b4ad347b1))

## [0.6.0] (2026-02-17)

### Added

- **ontology:** v0.6.0 release with Zero-Local policy and DQV alignment ([a2c365e](https://github.com/KhaosResearch/AgoraOWL/commit/a2c365ec18e24b90e755e8c811abe2ceb356cf73))

## [0.5.0] (2026-01-30)

### ⚠ BREAKING CHANGES

- Align with BIGOWL and enforce external vocabularies.

### Added

- **ontology:** release v0.5.0 with DQV alignment ([8f5913c](https://github.com/KhaosResearch/AgoraOWL/commit/8f5913c77ada43f09efcd4e37860465fd1b966d3))

## [0.4.1] - 2026-01-12

### Fixed

- **OWL Restriction Bug**: Removed incorrect `owl:minCardinality` restriction on `:DataAsset`.

## [0.4.0] - 2025-12-22

### Changed

- **Profile Conformance (BREAKING)**: `:conformsToProfile` property domain changed from `ids:Resource` to `dcat:Distribution`.

## [0.3.2] - 2025-12-16

### Added

- **`:MetricType` class**: New class for standardized metric type vocabulary.

## [0.3.1] - 2025-11-28

### Added

- **[MULTILINGUAL]** Added Spanish translations (`@es`) for all labels and comments.

## [0.3.0] - 2025-11-19

### Added

- **[PROVENANCE]** Added `prov:wasGeneratedBy` and `prov:wasDerivedFrom`.

## [0.2.1] - 2025-11-10

### Added

- Added bibliographic metadata and architecture diagram link.

## [0.2.0] - 2025-11-10

### Changed

- **Model Unification**: Unified "Profile-based Model" and "Direct Semantic Model".

## [0.1.0] - 2025-11-05

### Added

- **Initial Modular CI/CD**: Added SHACL validation and robot consistency checks.

## [0.0.1] - 2025-11-03

### Added

- **Initial Ontology**: First version of AgoraOWL with basic DataProfile model.

[Unreleased]: https://github.com/KhaosResearch/AgoraOWL/compare/v1.2.0...HEAD
[1.2.0]: https://github.com/KhaosResearch/AgoraOWL/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/KhaosResearch/AgoraOWL/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/KhaosResearch/AgoraOWL/compare/v0.9.0...v1.0.0
[0.9.0]: https://github.com/KhaosResearch/AgoraOWL/compare/v0.8.1...v0.9.0
[0.8.1]: https://github.com/KhaosResearch/AgoraOWL/compare/v0.8.0...v0.8.1
[0.8.0]: https://github.com/KhaosResearch/AgoraOWL/compare/v0.7.0...v0.8.0
[0.7.0]: https://github.com/KhaosResearch/AgoraOWL/compare/v0.6.1...v0.7.0
[0.6.1]: https://github.com/KhaosResearch/AgoraOWL/compare/v0.6.0...v0.6.1
[0.6.0]: https://github.com/KhaosResearch/AgoraOWL/compare/v0.5.0...v0.6.0
[0.5.0]: https://github.com/KhaosResearch/AgoraOWL/compare/v0.4.1...v0.5.0
[0.4.1]: https://github.com/KhaosResearch/AgoraOWL/compare/v0.4.0...v0.4.1
[0.4.0]: https://github.com/KhaosResearch/AgoraOWL/compare/v0.3.2...v0.4.0
[0.3.2]: https://github.com/KhaosResearch/AgoraOWL/compare/v0.3.1...v0.3.2
[0.3.1]: https://github.com/KhaosResearch/AgoraOWL/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/KhaosResearch/AgoraOWL/compare/v0.2.1...v0.3.0
[0.2.1]: https://github.com/KhaosResearch/AgoraOWL/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/KhaosResearch/AgoraOWL/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/KhaosResearch/AgoraOWL/compare/v0.0.1...v0.1.0
[0.0.1]: https://github.com/KhaosResearch/AgoraOWL/releases/tag/v0.0.1
