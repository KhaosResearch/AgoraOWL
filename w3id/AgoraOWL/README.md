# AgoraOWL

**Persistent identifier (PID) home** for the AgoraOWL ontology and related resources.

This directory hosts the redirection rules (via `.htaccess`) that resolve the PID
<https://w3id.org/AgoraOWL> and its associated versions, vocabularies, and distribution artefacts.

## 🔗 Resolvable Resources

The redirection rules point to the ontology documentation and files hosted on GitHub Pages:
**`https://khaosresearch.github.io/AgoraOWL/`**

### Main Ontology (Latest & Versioned)

The base PID <https://w3id.org/AgoraOWL> redirects to the **latest** version. Specific versions can be accessed via `/<version>` (e.g., <https://w3id.org/AgoraOWL/1.3.0>).

- **HTML Docs (for browsers):**
  - `https://w3id.org/AgoraOWL/` (Redirects to latest docs)
  - `https://w3id.org/AgoraOWL/1.3.0/` (Redirects to versioned docs)
- **Terms (for browsers and RDF tools):**
  - `https://w3id.org/AgoraOWL/DataApp` (Redirects to the term's section, or to the ontology document for RDF `Accept` types)

- **RDF Serializations (for tools, using `Accept` header):**
  - **Turtle (.ttl):** `https://khaosresearch.github.io/AgoraOWL/latest/ontology.ttl`
  - **RDF/XML (.owl):** `https://khaosresearch.github.io/AgoraOWL/latest/ontology.owl`
  - **N-Triples (.nt):** `https://khaosresearch.github.io/AgoraOWL/latest/ontology.nt`
  - **JSON-LD (.jsonld):** `https://khaosresearch.github.io/AgoraOWL/latest/ontology.jsonld`

### Modular Vocabularies

Vocabulary PIDs are resolvable with or without a version segment; concept IRIs
stay stable across releases. For example:
<https://w3id.org/AgoraOWL/vocabularies/observed-properties>

This PID redirects to the generated documentation (for browsers) or the raw
`.ttl` file (for tools):

- `https://khaosresearch.github.io/AgoraOWL/latest/vocabularies/observed-properties.html`
- `https://khaosresearch.github.io/AgoraOWL/1.3.0/vocabularies/siex.ttl`

### Distribution Artefacts

- `https://w3id.org/AgoraOWL/context.jsonld` — the JSON-LD context, used by Eclipse EDC connectors.
- `https://w3id.org/AgoraOWL/alignment.ttl` — an optional module aligning AgoraOWL terms with third-party vocabularies.

## 📦 Content Negotiation

The `.htaccess` provides content negotiation based on the `Accept` header:

- `text/html` → HTML documentation (e.g., `.../latest/index-en.html`)
- `text/turtle` → Turtle file (e.g., `.../latest/ontology.ttl`)
- `application/rdf+xml` → RDF/XML file (e.g., `.../latest/ontology.owl`)
- `application/n-triples` → N-Triples file (e.g., `.../latest/ontology.nt`)
- `application/ld+json` → JSON-LD file (e.g., `.../latest/ontology.jsonld`)
- Default/Fallback → Turtle file (e.g., `.../latest/ontology.ttl`)

## 🧭 Scope

**AgoraOWL** is an ontology aligned with **IDSA** and connected to **BIGOWL** (Data, Algorithms, Problems, Workflows).
It models data assets, data apps, profiles, and workflows, using modular SKOS vocabularies for domains, data types, and observed properties.

## 👥 Maintainers

- Martín J. Salvachúa ([@MartinM10](https://github.com/MartinM10)) - `<martinjs@uma.es>` - `<martin.salvachua1@gmail.com>`
