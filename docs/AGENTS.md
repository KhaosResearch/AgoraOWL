# AI Agent Operational Guide (AGENTS.md)

> [!IMPORTANT]
> This file is the primary entry point for AI Coding Agents. Follow these guidelines to maintain architectural integrity and consistent development across versions.

## 1. Context Recovery (Start Here)

When starting a session or resuming work, perform these checks to establish current state:

1.  **Current Version**: Check `owl:versionInfo` in `src/<latest-version>/AgoraOWL.ttl`.
2.  **Recent Changes**: Read `CHANGELOG.md` to understand what was implemented in the last few increments.
3.  **Critical Feedback**: Review the latest release notes and open issues for pending semantic fixes or architectural debts.
4.  **Active Version Path**: Documentation and source code reside in `src/<version>/`.

## 2. Technical Commandments

Adhere to these rules in every edit:

- **Structure over Content**: Prefer external authoritative concepts for mature domains (e.g., Agriculture, Units).
- **External-First (v0.6.0+)**: Use external normative IRIs (AGROVOC, EU Data Themes, DQV, PROV) by default; add local bridge vocabularies only when they improve discoverability, acronyms, or mappings.
- **Matchmaking Integrity**: Always maintain the triangular link: `DataAsset` ↔ `[FieldMapping → DataSpecification]` ↔ `[InputProfile → DataSpecification]`.
- **Validation First**: Every change to `.ttl` files MUST be validated using `scripts/local-validate.bat` (Windows).

## 3. Standard Procedures

### Procedure A: Generating a New Version (e.g., 1.0.0 → 1.1.0)

1.  **Folder Hierarchy**:
    - Duplicate the latest version folder: `cp -r src/1.0.0/ src/1.1.0/`
2.  **Ontology Metadata**:
    - Update `owl:versionIRI` to `.../1.0.0`
    - Update `owl:versionInfo` to `1.0.0`
    - Update `owl:priorVersion` to `.../0.9.0`
3.  **Global Updates**:
    - Update `CITATION.cff` and root `README.md`.
    - Update `src/index.html` (Available Versions grid and Latest badge).
4.  **Documentation**:
    - Update the version-specific `README.md` and `index.html` inside the new folder.

### Procedure B: Adding a New Metric or Property

1.  **Ontology**: Add definition to `AgoraOWL.ttl`.
2.  **Alignment**: Map it to DQV (`dqv:Metric` / `dqv:QualityMeasurement`) or PROV (`prov:Activity`) if applicable.
3.  **SHACL**: Add a targeted shape in `shapes/edaan-shapes.ttl` or the relevant compliance-shape directory.
4.  **Example**: Update `examples/` to demonstrate the new property.

### Check scripts

check if the `scripts/` files are updated with the new property or metric.

### Check docs

check if the `docs/` files are updated with the new property or metric.

## 4. Semantic Mapping Reference

| Concept                | External Standard / Base Class    |
| :--------------------- | :-------------------------------- |
| **Quality Metric**     | `dqv:QualityMeasurement`          |
| **Metric Definition**  | `dqv:Metric`                      |
| **Field Mapping**      | `agoraowl:FieldMapping`           |
| **Data Specification** | `agoraowl:DataSpecification`      |
| **Data App**           | `ids:DataApp` / `bigwf:Component` |
| **Data Asset**         | `ids:Resource` / `dcat:Dataset`   |
| **Lineage**            | `prov:generatedAtTime`            |
| **Format**             | `dct:format` (MIME or URI)        |

### DCAT-AP-ES Compliance Schema

![DCAT All Attributes Diagram](assets/dcat-all-attributes.svg)
_Reference diagram for Full DCAT-AP-ES 1.0.0 compliance._

## 5. Troubleshooting for AI Agents

- **rdflib errors**: Usually caused by non-UTF-8 characters. Ensure encoding is explicit.
- **SHACL Violation**: Check if `ids:fileName` is missing in `ids:Artifact`, or if `ids:representation` (it does not exist) is missing in `ids:DataResource`.
- **Symlink Issues**: Under Windows, be careful with symlinks; prefer updating the actual versioned file.

---

_Created for AI Agents, maintained by humans._
