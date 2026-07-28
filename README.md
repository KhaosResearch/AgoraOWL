# AgoraOWL: An ontology for annotating data-space assets aligned with IDSA and BIGOWL

[![Deploy Ontology to GitHub Pages](https://github.com/KhaosResearch/AgoraOWL/actions/workflows/deploy-docs.yml/badge.svg)](https://github.com/KhaosResearch/AgoraOWL/actions/workflows/deploy-docs.yml)
[![Docs](https://img.shields.io/badge/docs-GitHub%20Pages-1f6feb)](https://khaosresearch.github.io/AgoraOWL/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-green.svg)](LICENSE)
[![Ontology Version](https://img.shields.io/badge/stable-1.2.1-blue.svg)](src/1.2.1/)
[![PURL](https://img.shields.io/badge/purl-w3id.org-blue)](https://w3id.org/AgoraOWL/)
[![SHACL Validation](https://img.shields.io/badge/SHACL-Conformant-success)](src/1.2.1/shapes/edaan-shapes.ttl)
[![DCAT-AP-ES Alignment](https://img.shields.io/badge/DCAT--AP--ES-Alignment-brightgreen.svg)](https://github.com/datosgobes/DCAT-AP-ES)

> **Sectoral Semantic Interoperability for Data Spaces**: Decoupling domain logic from technical schemas to enable automated matchmaking.

---

## 🚀 Overview

**AgoraOWL** is a lightweight ontology designed to operationalize Data Spaces. It bridges the gap between the **IDSA Information Model** (governance) and **BIGOWL** (analytical workflows), enabling:

- **DCAT-AP-ES 1.0.0 & DCAT 3.0 Alignment**: Standardized metadata and local SHACL shapes for validating the supported profile.
- **Symmetric App Profiling**: Formalized Input and Output ports for DataApps, enabling automated pipeline chaining.
- **Decoupled Architecture**: Semantic `DataSpecification` is linked to physical `Distribution` through `FieldMappings`, preventing schema leakage.
- **Technical Matchmaking**: Support for unit-aware, quality-aware, and data-type-aware constraints for formal interoperability.

---

## ⚡ Quickstart (Minimal Example)

Annotate a Data Asset and a Data App using the decoupled model:

```turtle
@prefix : <https://w3id.org/AgoraOWL/> .
@prefix dcat: <http://www.w3.org/ns/dcat#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix qudt: <http://qudt.org/vocab/unit/> .

# 1. Semantic Layer: Define WHAT the data is
:TemperatureSpec a :DataSpecification ;
    rdfs:label "Air Temperature Specification"@en .

# 2. Binding Layer: Map it to a physical field
:MyDataset a :DataAsset, dcat:Dataset ;
    dcat:distribution [
        a dcat:Distribution ;
        :hasFieldMapping [
            a :FieldMapping ;
            :mapsToSpecification :TemperatureSpec ;
            :mapsField "temp_celsius" ;
            :hasUnit qudt:DEG_C ;
            :hasDataType xsd:float
        ]
    ] .

# 3. Requirement Layer: Define what an App needs
:MyAnalysisApp a :DataApp ;
    :hasInputProfile [
        a :InputProfile ;
        :hasDataSpecification :TemperatureSpec ;
        :hasConstraint [
            a :DataConstraint ;
            :constraintMetricType :Accuracy ;
            :requiresUnit qudt:DEG_C ;
            :constraintOperator :GreaterOrEqual ;
            :constraintValue "0.95"^^xsd:decimal
        ]
    ] .
```

---

## 🇪🇸 Strategic Alignment (Spanish Framework)

AgoraOWL reinforces the **[Marco de Interoperabilidad Técnico (MIT)](https://cred.digital.gob.es/content/dam/cred/img/docs/MarcoInteroperabilidadTecnico.pdf)** by:

- **Sectoral Semantic Interoperability**: By decoupling _technical mapping_ from _domain semantics_, AgoraOWL allow assets to reuse the same semantic library even if their physical schemas differ.
- **SIEX & FEGA Support**: Includes native SKOS alignments for Spanish agricultural catalogs, ensuring immediate operationality in the national context.

---

## 📘 Documentation

- **[Architecture Guide](docs/ARCHITECTURE.md)**: High-level view of the 4-layer model.
- **[Semantic Profiling Guide](docs/semantic-profiling-guide.md)**: Detailed matchmaking rules.
- **[Interoperability Examples (ES)](docs/INTEROPERABILITY_EXAMPLES_ES.md)**: Real-world Spanish scenarios.
- **[Interactive Documentation (WIDOCO)](https://khaosresearch.github.io/AgoraOWL/v1.2.1/index.html)**.

---

## 🛠️ Validation

Ensure your instances conform to AgoraOWL and DCAT-AP-ES rules:

```bash
# Verify using Docker-powered local suite
bash ./scripts/local-validate.sh
```

---

© 2026 [Khaos Research Group](https://khaos.uma.es/). Licensed under the **Apache License 2.0**.
