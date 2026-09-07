# AgoraOWL

**Persistent identifier (PID) home** for the AgoraOWL ontology and related resources.

This directory hosts the redirection rules (via `.htaccess`) that resolve the PID
<https://w3id.org/AgoraOWL> and its associated versions, vocabularies and
distribution artefacts.

Targets are served from GitHub Pages: **`https://khaosresearch.github.io/AgoraOWL/`**

## Resolvable resources

### Ontology

| PID | `Accept` | Resolves to |
| --- | --- | --- |
| `https://w3id.org/AgoraOWL` | `text/html` | `latest/index-en.html` |
| `https://w3id.org/AgoraOWL` | `text/turtle` | `latest/ontology.ttl` |
| `https://w3id.org/AgoraOWL` | `application/rdf+xml` | `latest/ontology.owl` |
| `https://w3id.org/AgoraOWL` | `application/n-triples` | `latest/ontology.nt` |
| `https://w3id.org/AgoraOWL` | `application/ld+json` | `latest/ontology.jsonld` |
| `https://w3id.org/AgoraOWL/1.3.0` | any of the above | the same, for that version |

### Terms

| PID | `Accept` | Resolves to |
| --- | --- | --- |
| `https://w3id.org/AgoraOWL/DataApp` | `text/html` | `latest/index-en.html#DataApp` |
| `https://w3id.org/AgoraOWL/DataApp` | `text/turtle` | `latest/ontology.ttl` |

The RDF branch is **new**: previously a term IRI returned `404` for every RDF
media type while the browser branch worked, so a term could not be dereferenced
by a machine.

### Vocabularies

Concept IRIs are **version independent**. A concept keeps the same IRI across
releases; the versioned path is only a document location.

| PID | `Accept` | Resolves to |
| --- | --- | --- |
| `https://w3id.org/AgoraOWL/vocabularies/` | `text/html` | `latest/vocabularies/index.html` |
| `https://w3id.org/AgoraOWL/vocabularies/observed-properties` | `text/html` | `latest/vocabularies/observed-properties.html` |
| `https://w3id.org/AgoraOWL/vocabularies/observed-properties` | `text/turtle` | `latest/vocabularies/observed-properties.ttl` |
| `https://w3id.org/AgoraOWL/1.3.0/vocabularies/siex` | `text/html` | `1.3.0/vocabularies/siex.html` |
| `https://w3id.org/AgoraOWL/vocabularies/siex.ttl` | any | `latest/vocabularies/siex.ttl` |

A **fragment is never sent to the server**, so a redirect cannot resolve
`#ndvi` by itself: the landing page has to. That is why browsers now get the
generated HTML documentation, which carries one anchor per concept (and, for
SIEX's 82 240 concepts, a sharded client-side index):

    https://w3id.org/AgoraOWL/vocabularies/observed-properties#ndvi

### Distribution artefacts

| PID | Resolves to | Used by |
| --- | --- | --- |
| `https://w3id.org/AgoraOWL/context.jsonld` | `latest/context.jsonld` | Eclipse EDC 0.18+ `edc.dataspace.profiles.*.jsonld.context.urls` |
| `https://w3id.org/AgoraOWL/alignment.ttl` | `latest/alignment.ttl` | optional third-party alignment module |
| `https://w3id.org/AgoraOWL/1.3.0/context.jsonld` | that version | |

## Verifying changes to these rules

Do not iterate against this repository. The AgoraOWL repository ships a
simulator that runs these exact rules inside Apache 2.4 configured the way
w3id.org configures it, and asserts the `Location` header for every path and
`Accept` combination:

```bash
python3 w3id/simulation/verify_redirects.py                  # proposed rules
python3 w3id/simulation/verify_redirects.py --baseline       # rules currently live here
python3 w3id/simulation/verify_redirects.py --gh-pages DIR   # also assert targets exist
```

At the time of the AgoraOWL 1.3.0 proposal the live rules satisfied 14 of 33
contracts and the proposed rules satisfied 33 of 33.

## Scope

**AgoraOWL** is an ontology aligned with **IDSA** and connected to **BIGOWL**
(Data, Algorithms, Problems, Workflows). It models data assets, data apps,
profiles and workflows, using modular SKOS vocabularies for domains, data types
and observed properties.

## Maintainers

- Martín J. Salvachúa ([@MartinM10](https://github.com/MartinM10)) — `<martinjs@uma.es>` — `<martin.salvachua1@gmail.com>`
