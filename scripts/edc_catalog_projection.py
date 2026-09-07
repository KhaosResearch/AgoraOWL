#!/usr/bin/env python3
"""
Project an EDC Management API asset payload onto the DCAT dataset that the
connector publishes over the Dataspace Protocol, so it can be SHACL-validated.

Why this exists
---------------
An EDC asset and the DCAT dataset a partner receives are not the same graph:

  * `edc:properties` is a container. In the DSP catalog EDC lifts every entry to
    a direct predicate of the dataset node and types the node `dcat:Dataset`
    (see JsonObjectFromDatasetTransformer / DatasetResolverImpl in the Connector).
  * Language tags and datatypes are LOST on scalar asset properties: EDC's
    JsonValueToGenericTypeTransformer keeps only the `@value`. Nested node
    objects survive verbatim.
  * `edc:dataAddress` is internal and never published; the catalog carries
    `dcat:distribution` instead.

Validating the Management API representation therefore tells you nothing about
what partners actually see. This script produces the graph that matters.

Usage:
    python3 scripts/edc_catalog_projection.py <payload.jsonld> [-o out.ttl] [--keep-language-tags]
"""

import argparse
import json
import sys
from pathlib import Path

from rdflib import Graph, URIRef, Literal, BNode, Namespace, RDF
from rdflib.namespace import DCAT, DCTERMS, XSD

EDC = Namespace("https://w3id.org/edc/v0.0.1/ns/")
AGORAOWL = Namespace("https://w3id.org/AgoraOWL/")
CONTEXT_IRI = "https://w3id.org/AgoraOWL/context.jsonld"


def load_payload(path: Path, local_context: Path | None) -> dict:
    """Read the payload, optionally substituting the AgoraOWL context with a local copy."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload.pop("_comment", None)
    if local_context and local_context.exists():
        inline = json.loads(local_context.read_text(encoding="utf-8"))["@context"]
        contexts = payload.get("@context")
        if isinstance(contexts, list):
            payload["@context"] = [inline if c == CONTEXT_IRI else c for c in contexts]
    return payload


def strip_scalar_annotations(graph: Graph, asset: URIRef) -> Graph:
    """Reproduce EDC's loss of @language / @type on scalar asset properties.

    Only top-level literals are affected. Values inside nested node objects go
    through JsonValueToGenericTypeTransformer.toJavaType(), which stores the
    expanded JSON-LD verbatim, so their language tags and datatypes survive.
    """
    stripped = Graph()
    for subject, predicate, obj in graph:
        if subject == asset and isinstance(obj, Literal) and (obj.language or obj.datatype):
            obj = Literal(str(obj))
        stripped.add((subject, predicate, obj))
    return stripped


def project(payload: dict, keep_language_tags: bool) -> Graph:
    """Build the dcat:Dataset graph that EDC would publish over DSP."""
    source = Graph()
    source.parse(data=json.dumps(payload), format="json-ld")

    asset = URIRef(payload["@id"])
    out = Graph()
    out.bind("agoraowl", AGORAOWL)
    out.bind("dcat", DCAT)
    out.bind("dct", DCTERMS)

    # The DSP catalog types the node dcat:Dataset and keeps any additional
    # semantic types the publisher declared.
    out.add((asset, RDF.type, DCAT.Dataset))
    for extra_type in source.objects(asset, RDF.type):
        if extra_type != EDC.Asset:
            out.add((asset, RDF.type, extra_type))

    # Lift edc:properties onto the dataset node.
    lifted = 0
    for container in source.objects(asset, EDC.properties):
        for predicate, obj in source.predicate_objects(container):
            out.add((asset, predicate, obj))
            lifted += 1

    # Carry over the whole nested subtree reachable from the lifted values.
    seen: set = set()
    frontier = [obj for _, obj in out.predicate_objects(asset) if isinstance(obj, (BNode, URIRef))]
    while frontier:
        node = frontier.pop()
        if node in seen:
            continue
        seen.add(node)
        for predicate, obj in source.predicate_objects(node):
            out.add((node, predicate, obj))
            if isinstance(obj, (BNode, URIRef)):
                frontier.append(obj)

    # dataAddress is internal: the catalog exposes a dcat:Distribution instead.
    for address in source.objects(asset, EDC.dataAddress):
        base_url = next(source.objects(address, EDC.baseUrl), None)
        distribution = URIRef(f"{asset}/distribution")
        out.add((asset, DCAT.distribution, distribution))
        out.add((distribution, RDF.type, DCAT.Distribution))
        if base_url is not None:
            out.add((distribution, DCAT.accessURL, URIRef(str(base_url))))
        for prop in (DCTERMS.format, DCAT.mediaType, DCTERMS.license):
            for value in out.objects(asset, prop):
                out.add((distribution, prop, value))

    if not keep_language_tags:
        out = strip_scalar_annotations(out, asset)

    print(f"[projection] lifted {lifted} properties from edc:properties onto {asset}", file=sys.stderr)
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("payload", type=Path, help="EDC Management API asset payload (JSON-LD)")
    parser.add_argument("-o", "--output", type=Path, help="Turtle output file (default: stdout)")
    parser.add_argument("--local-context", type=Path, default=None,
                        help="Local copy of the AgoraOWL context to use instead of the published URL")
    parser.add_argument("--keep-language-tags", action="store_true",
                        help="Do NOT reproduce EDC's loss of @language/@type on scalar properties")
    args = parser.parse_args()

    payload = load_payload(args.payload, args.local_context)
    graph = project(payload, args.keep_language_tags)
    turtle = graph.serialize(format="turtle")

    if args.output:
        args.output.write_text(turtle, encoding="utf-8")
        print(f"[projection] wrote {len(graph)} triples to {args.output}", file=sys.stderr)
    else:
        print(turtle)


if __name__ == "__main__":
    main()
