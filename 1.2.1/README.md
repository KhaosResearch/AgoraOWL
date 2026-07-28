# AgoraOWL v1.2.1

This release introduces **Symmetric App Profiling**, enabling DataApps to formally declare their output capabilities (using `:OutputProfile`) with the same precision as their input requirements. It also generalizes administrative metadata to support both Data Assets and Data Applications, reinforcing the schema-agnostic nature of the semantic layer.

This patch release corrects the DCAT 3 `DatasetSeries` hierarchy, makes technical and quality constraints composable, and aligns the validation and deployment tooling with the versioned source layout.

## v1.2.1 Highlights (Symmetric Profiling)

| Change                     | Impact                | Justification                                                                                                                     |
| -------------------------- | --------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| **Symmetric Profiling**    | Balanced I/O Modeling | Introduced `:hasOutputProfile` and `:OutputProfile` to match the existing input requirement pattern.                              |
| **Generalized Metadata**   | Unified Discovery     | Properties like `hasCertification`, `supportContact`, and `legalContact` now apply to both `ids:Resource` and `agoraowl:DataApp`. |
| **Schema-Agnostic Specs**  | Pure Semantic Layer   | Technical types and schema links are now strictly separated from `DataSpecification`, belonging only to Mappings or Constraints.  |
| **Data Type Requirements** | Precise Matchmaking   | Added `:requiresDataType` to formalize technical encoding requirements at the application input port.                             |
| **DCAT 3 Alignment**       | Interoperability      | Corrected the `DatasetSeries` hierarchy and retained support for spatial/temporal resolution and temporal coverage.              |

---

## v1.2.1 Architecture

The decoupled architecture has been matured into a symmetric four-layer model:

1. **Semantic Layer (`DataSpecification`)**: Atomic units defining the domain logic (e.g., "Air Temperature"). These contain NO technical details or schema names.
2. **Binding Layer (`FieldMapping`)**: Connects the atomic specification to a physical distribution, specifying the field name (`mapsField`), units (`qudt:Unit`), data type (`hasDataType`), and metrics.
3. **Requirement Layer (`InputProfile` / `OutputProfile`)**: Defines the semantic "ports" of an application, including optional quality and technical requirements (`requiresDataType`, `requiresUnit`, `requiresMetric`).
4. **Technical Layer (`Distribution`)**: Centralizes physical properties (format, URL, CRS) following DCAT-AP 3.0.

### Why this change?

- **Port-Based Modeling**: Allows apps to group required/produced variables by "files" or "streams" while maintaining atomic semantic links.
- **Improved Governance**: Apps can now carry the same rich metadata as datasets (certifications, DPIAs, contacts).
- **Cleaner Matchmaking**: Data types are now part of the matchmaking negotiation via explicit requirement properties.

---

<details>
<summary><b>v1.1.0 Highlights (Full Compliance)</b></summary>

| Feature                    | Description                                                             |
| -------------------------- | ----------------------------------------------------------------------- |
| **DCAT-AP-ES Compliance**  | 100% Green Validation against official Spanish Government SHACL shapes. |
| **Surgical SHACL Targets** | Prevents technical leakage on Catalogs.                                 |
| **Standardized Metadata**  | Authoritative DIR3 Agent IRIs and vCard alignment.                      |

</details>

<details>
<summary><b>v1.0.0 Highlights (Decoupled Architecture)</b></summary>

| Feature               | Description                                                      |
| --------------------- | ---------------------------------------------------------------- |
| **Field Mappings**    | Atomic reusable DataSpecifications decoupled from distributions. |
| **Profile Libraries** | Schema-agnostic semantic definitions across sectors.             |

</details>

---

## CRED and Validation

1. **Catalog** — `dcat:Catalog` aggregating data space resources
2. **Agent** — `foaf:Agent` for publishers and creators
3. **Dataset** — `dcat:Dataset` + `:DataAsset` with full DCAT-AP 3.0 metadata
4. **Distribution** — `dcat:Distribution` with access URL, format, license
5. **DataProfile & DataSpecification** — AgoraOWL semantic profiles referencing specific variables
6. **ODRL Policy** — `odrl:Offer` with permissions, prohibitions, and constraints
7. **DataService** — `dcat:DataService` with endpoint and served datasets
8. **Vocabulary-as-Dataset** — Ontology catalogued using CRED library model

| Domain                | Recommended Vocabulary                                              | URI Pattern                               |
| --------------------- | ------------------------------------------------------------------- | ----------------------------------------- |
| Agriculture (Global)  | [AGROVOC](http://aims.fao.org/aos/agrovoc/)                         | `http://aims.fao.org/aos/agrovoc/c_*`     |
| Agriculture (Spain)   | [SIEX (local)](vocabularies/siex.ttl)                               | `https://w3id.org/AgoraOWL/siex/kos/*`    |
| Observable Properties | [Observed Properties (local)](vocabularies/observed-properties.ttl) | `https://w3id.org/AgoraOWL/*`             |
| Units of Measure      | [QUDT](http://qudt.org/vocab/unit/)                                 | `http://qudt.org/vocab/unit/*`            |
| Data Quality          | [DQV](http://www.w3.org/ns/dqv#)                                    | `http://www.w3.org/ns/dqv#*`              |
| Geospatial            | [EPSG](http://www.opengis.net/def/crs/EPSG/)                        | `http://www.opengis.net/def/crs/EPSG/0/*` |

---

## Validation

Run the local validation script to verify compliance:

```powershell
.\scripts\local-validate.bat
```

Or on Linux/macOS:

```bash
bash ./scripts/local-validate.sh
```
