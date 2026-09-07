#!/usr/bin/env python3
"""
Generate human-readable HTML documentation for the AgoraOWL SKOS vocabularies,
with one resolvable anchor per concept.

Why this exists
---------------
Widoco documents AgoraOWL.ttl only. The vocabularies were published as raw
Turtle, so a fragment IRI such as

    https://w3id.org/AgoraOWL/vocabularies/observed-properties#ndvi

resolved to a 33 MB text file with no way to reach the concept it names. A
fragment is never sent to the server, so this cannot be fixed with a redirect:
the page the browser lands on has to resolve the fragment itself.

Two strategies, chosen by size:

  * Small vocabulary (<= --inline-limit concepts): every concept is rendered
    into the page with a real `id` attribute. The browser jumps to it natively,
    no JavaScript involved.
  * Large vocabulary (SIEX ships 82k concepts, 80k of them in a single scheme):
    the page stays small and looks the concept up in a sharded JSON index keyed
    by the first two hex digits of the SHA-1 of the fragment, so a lookup
    downloads roughly 1/256th of the vocabulary.

Usage:
    python3 scripts/generate_vocab_docs.py [--version 1.3.0] [--out build/vocab-docs]
"""

import argparse
import hashlib
import html
import json
import re
import sys
from pathlib import Path

from rdflib import Graph, Namespace, RDF, URIRef
from rdflib.namespace import DCTERMS, OWL, RDFS, SKOS

ROOT = Path(__file__).resolve().parent.parent
SHARD_DIGITS = 2


def latest_version(src: Path) -> str:
    versions = [d.name for d in src.iterdir() if d.is_dir() and re.fullmatch(r"\d+\.\d+\.\d+", d.name)]
    return sorted(versions, key=lambda v: [int(p) for p in v.split(".")])[-1]


def shard_of(fragment: str) -> str:
    return hashlib.sha1(fragment.encode("utf-8")).hexdigest()[:SHARD_DIGITS]


def literals(graph: Graph, subject, predicate) -> dict:
    """Collect literals by language tag, keeping the first value per language."""
    out: dict[str, str] = {}
    for value in graph.objects(subject, predicate):
        out.setdefault(value.language or "", str(value))
    return out


def concept_record(graph: Graph, concept: URIRef, base: str) -> dict:
    fragment = str(concept)[len(base):] if str(concept).startswith(base) else str(concept)
    record = {
        "id": fragment,
        "pref": literals(graph, concept, SKOS.prefLabel) or literals(graph, concept, RDFS.label),
        "alt": sorted({str(v) for v in graph.objects(concept, SKOS.altLabel)}),
        "def": literals(graph, concept, SKOS.definition),
        "notation": next((str(v) for v in graph.objects(concept, SKOS.notation)), None),
        "scheme": next((str(v).split("#")[-1] for v in graph.objects(concept, SKOS.inScheme)), None),
        "broader": [str(v).split("#")[-1] for v in graph.objects(concept, SKOS.broader)],
        "matches": sorted(
            str(v) for predicate in (SKOS.exactMatch, SKOS.closeMatch, SKOS.relatedMatch)
            for v in graph.objects(concept, predicate)
        ),
    }
    return record


def label_of(record: dict) -> str:
    pref = record["pref"]
    return pref.get("en") or pref.get("es") or next(iter(pref.values()), record["id"])


def render_concept(record: dict, base: str) -> str:
    pref = record["pref"]
    rows = []
    if record["notation"]:
        rows.append(("Notation", html.escape(record["notation"])))
    if pref.get("en"):
        rows.append(("Preferred label (en)", html.escape(pref["en"])))
    if pref.get("es"):
        rows.append(("Etiqueta preferida (es)", html.escape(pref["es"])))
    if record["alt"]:
        rows.append(("Alternative labels", ", ".join(html.escape(a) for a in record["alt"])))
    for lang, key in (("en", "Definition (en)"), ("es", "Definición (es)")):
        if record["def"].get(lang):
            rows.append((key, html.escape(record["def"][lang])))
    if record["scheme"]:
        rows.append(("In scheme", html.escape(record["scheme"])))
    if record["broader"]:
        rows.append(("Broader", ", ".join(
            f'<a href="#{html.escape(b)}">{html.escape(b)}</a>' for b in record["broader"])))
    if record["matches"]:
        rows.append(("Mappings", "<br>".join(
            f'<a href="{html.escape(m)}">{html.escape(m)}</a>' for m in record["matches"])))

    body = "".join(f"<tr><th>{key}</th><td>{value}</td></tr>" for key, value in rows)
    return (
        f'<section class="concept" id="{html.escape(record["id"])}">'
        f'<h3>{html.escape(label_of(record))} '
        f'<a class="anchor" href="#{html.escape(record["id"])}" title="Permalink">#</a></h3>'
        f'<p class="iri"><code>{html.escape(base + record["id"])}</code></p>'
        f"<table>{body}</table></section>"
    )


STYLE = """
:root{--fg:#1b1f23;--muted:#57606a;--bg:#fff;--card:#f6f8fa;--line:#d0d7de;--link:#0969da}
@media (prefers-color-scheme:dark){:root{--fg:#e6edf3;--muted:#9198a1;--bg:#0d1117;--card:#161b22;--line:#30363d;--link:#4493f8}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif}
main{max-width:60rem;margin:0 auto;padding:2rem 1.25rem 5rem}
h1{font-size:1.6rem;margin:0 0 .25rem}
.sub{color:var(--muted);margin:0 0 1.5rem}
a{color:var(--link)}
code{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:.85em;word-break:break-all}
.meta{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:1rem;margin-bottom:1.5rem}
.meta dl{display:grid;grid-template-columns:max-content 1fr;gap:.35rem 1rem;margin:0}
.meta dt{color:var(--muted)}.meta dd{margin:0}
#q{width:100%;padding:.6rem .8rem;font-size:1rem;border:1px solid var(--line);border-radius:8px;background:var(--bg);color:var(--fg)}
.concept{border:1px solid var(--line);border-radius:8px;padding:1rem 1.25rem;margin:1rem 0;background:var(--card);scroll-margin-top:1rem}
.concept:target,.concept.selected{outline:2px solid var(--link)}
.concept h3{margin:0 0 .25rem;font-size:1.1rem}
.anchor{text-decoration:none;color:var(--muted);font-weight:400}
.iri{margin:.1rem 0 .75rem;color:var(--muted)}
table{border-collapse:collapse;width:100%;overflow-x:auto;display:block}
th,td{text-align:left;vertical-align:top;padding:.3rem .6rem;border-top:1px solid var(--line);font-size:.92rem}
th{color:var(--muted);font-weight:600;white-space:nowrap;width:14rem}
.hint{color:var(--muted);font-size:.9rem}
"""

LOOKUP_JS = """
const SHARD_DIGITS = %(digits)d;
const BASE = %(base)s;
async function sha1hex(text){
  const buf = await crypto.subtle.digest('SHA-1', new TextEncoder().encode(text));
  return [...new Uint8Array(buf)].map(b => b.toString(16).padStart(2,'0')).join('');
}
function row(k,v){ return v ? `<tr><th>${k}</th><td>${v}</td></tr>` : ''; }
function render(rec){
  const pref = rec.pref || {};
  const title = pref.en || pref.es || rec.id;
  const matches = (rec.matches||[]).map(m => `<a href="${m}">${m}</a>`).join('<br>');
  const broader = (rec.broader||[]).map(b => `<a href="#${b}">${b}</a>`).join(', ');
  return `<section class="concept" id="${rec.id}"><h3>${title}</h3>
    <p class="iri"><code>${BASE}${rec.id}</code></p><table>
    ${row('Notation', rec.notation)}
    ${row('Preferred label (en)', pref.en)}
    ${row('Etiqueta preferida (es)', pref.es)}
    ${row('Alternative labels', (rec.alt||[]).join(', '))}
    ${row('Definition (en)', (rec.def||{}).en)}
    ${row('Definición (es)', (rec.def||{}).es)}
    ${row('In scheme', rec.scheme)}
    ${row('Broader', broader)}
    ${row('Mappings', matches)}
    </table></section>`;
}
async function lookup(fragment){
  const out = document.getElementById('result');
  if(!fragment){ out.innerHTML = '<p class="hint">Enter a concept identifier, or append it to the URL as a fragment.</p>'; return; }
  out.innerHTML = '<p class="hint">Looking up ' + fragment + '…</p>';
  try {
    const shard = (await sha1hex(fragment)).slice(0, SHARD_DIGITS);
    const data = await (await fetch(`./${%(name)s}.index/${shard}.json`)).json();
    const rec = data[fragment];
    if(rec){
      out.innerHTML = render(rec);
      // The browser evaluated :target before this element existed, so mark and
      // reveal it explicitly to match the behaviour of an inline anchor.
      const el = document.getElementById(rec.id);
      if(el){ el.classList.add('selected'); el.scrollIntoView({block:'start'}); }
    } else {
      out.innerHTML = `<p class="hint">No concept named <code>${fragment}</code> in this vocabulary.</p>`;
    }
  } catch (err) {
    out.innerHTML = `<p class="hint">Lookup failed: ${err}. The Turtle file is always available above.</p>`;
  }
}
function fromHash(){ lookup(decodeURIComponent(location.hash.replace(/^#/,'')).trim()); }
addEventListener('hashchange', fromHash);
addEventListener('DOMContentLoaded', () => {
  fromHash();
  document.getElementById('q').addEventListener('change', e => { location.hash = e.target.value.trim(); });
});
"""


def build_page(name: str, version: str, base: str, title: dict, description: dict,
               schemes: list, records: list, inline: bool) -> str:
    head = (
        f"<title>{html.escape(title.get('en') or name)} — AgoraOWL vocabulary</title>"
        f"<meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
        f"<style>{STYLE}</style>"
    )
    meta = (
        "<div class='meta'><dl>"
        f"<dt>Namespace</dt><dd><code>{html.escape(base)}</code></dd>"
        f"<dt>Version</dt><dd>{html.escape(version)}</dd>"
        f"<dt>Turtle</dt><dd><a href='./{name}.ttl'>{name}.ttl</a></dd>"
        f"<dt>Concepts</dt><dd>{len(records)}</dd>"
        + (f"<dt>Schemes</dt><dd>{html.escape(', '.join(schemes))}</dd>" if schemes else "")
        + "</dl></div>"
    )
    intro = ""
    for lang in ("en", "es"):
        if description.get(lang):
            intro += f"<p>{html.escape(description[lang])}</p>"

    if inline:
        listing = "".join(render_concept(record, base) for record in records)
        search = (
            "<p class='hint'>Every concept below has a permanent anchor: append "
            "<code>#&lt;identifier&gt;</code> to this page's URL.</p>"
        )
        script = ""
    else:
        listing = "<div id='result'></div>"
        search = (
            "<p class='hint'>This vocabulary is too large to render in one page. "
            "Append <code>#&lt;identifier&gt;</code> to the URL, or search below.</p>"
            "<input id='q' type='search' placeholder='e.g. siex_MeasurementUnit_9' autocomplete='off'>"
        )
        script = "<script>" + LOOKUP_JS % {
            "digits": SHARD_DIGITS, "base": json.dumps(base), "name": json.dumps(name)
        } + "</script>"

    return (
        "<!doctype html><html lang='en'><head>" + head + "</head><body><main>"
        f"<h1>{html.escape(title.get('en') or name)}</h1>"
        f"<p class='sub'>{html.escape(title.get('es') or '')}</p>"
        + meta + intro + search + listing + "</main>" + script + "</body></html>"
    )


def write_index(entries: list[dict], version: str, out_dir: Path) -> None:
    """Landing page for https://w3id.org/AgoraOWL/vocabularies/."""
    cards = "".join(
        f'<section class="concept"><h3><a href="./{html.escape(e["name"])}.html">'
        f'{html.escape(e["title"])}</a></h3>'
        f'<p class="iri"><code>{html.escape(e["base"])}</code></p>'
        f'<table><tr><th>Concepts</th><td>{e["concepts"]}</td></tr>'
        f'<tr><th>Schemes</th><td>{html.escape(", ".join(e["schemes"])) or "-"}</td></tr>'
        f'<tr><th>Turtle</th><td><a href="./{html.escape(e["name"])}.ttl">'
        f'{html.escape(e["name"])}.ttl</a></td></tr></table></section>'
        for e in entries
    )
    page = (
        "<!doctype html><html lang='en'><head>"
        "<title>AgoraOWL vocabularies</title>"
        "<meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
        f"<style>{STYLE}</style></head><body><main>"
        "<h1>AgoraOWL vocabularies</h1>"
        "<p class='sub'>Vocabularios de AgoraOWL</p>"
        "<div class='meta'><dl>"
        "<dt>Namespace</dt><dd><code>https://w3id.org/AgoraOWL/vocabularies/</code></dd>"
        f"<dt>Version</dt><dd>{html.escape(version)}</dd></dl></div>"
        "<p class='hint'>Concept IRIs are version independent: a concept keeps the same IRI "
        "across releases, and the versioned path is only a document location.</p>"
        + cards + "</main></body></html>"
    )
    (out_dir / "index.html").write_text(page, encoding="utf-8")
    print(f"[vocab-docs] index: {len(entries)} vocabularies")


def process(path: Path, version: str, out_dir: Path, inline_limit: int) -> dict:
    name = path.stem
    graph = Graph()
    graph.parse(path, format="turtle")

    ontology = next((s for s in graph.subjects(RDF.type, OWL.Ontology)), None)
    base = f"{ontology}#" if ontology else f"https://w3id.org/AgoraOWL/vocabularies/{name}#"
    title = literals(graph, ontology, DCTERMS.title) if ontology else {}
    description = literals(graph, ontology, DCTERMS.description) if ontology else {}
    schemes = sorted(str(s).split("#")[-1] for s in graph.subjects(RDF.type, SKOS.ConceptScheme))

    concepts = sorted(graph.subjects(RDF.type, SKOS.Concept), key=str)
    records = [concept_record(graph, concept, base) for concept in concepts]
    inline = len(records) <= inline_limit

    out_dir.mkdir(parents=True, exist_ok=True)
    page = build_page(name, version, base, title, description, schemes, records, inline)
    (out_dir / f"{name}.html").write_text(page, encoding="utf-8")

    shards = 0
    if not inline:
        index_dir = out_dir / f"{name}.index"
        index_dir.mkdir(exist_ok=True)
        buckets: dict[str, dict] = {}
        for record in records:
            buckets.setdefault(shard_of(record["id"]), {})[record["id"]] = record
        for shard, payload in buckets.items():
            (index_dir / f"{shard}.json").write_text(
                json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        shards = len(buckets)

    mode = "inline anchors" if inline else f"sharded index ({shards} shards)"
    size = (out_dir / f"{name}.html").stat().st_size // 1024
    print(f"[vocab-docs] {name}: {len(records)} concepts, {mode}, page {size} KB")
    return {"name": name, "base": base, "title": title.get("en") or name,
            "concepts": len(records), "schemes": schemes}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--version", default=None)
    parser.add_argument("--out", default=None, help="output directory (default: build/vocab-docs)")
    parser.add_argument("--inline-limit", type=int, default=500,
                        help="render every concept into the page below this many concepts")
    args = parser.parse_args()

    version = args.version or latest_version(ROOT / "src")
    vocab_dir = ROOT / "src" / version / "vocabularies"
    if not vocab_dir.is_dir():
        print(f"[vocab-docs] no vocabularies under src/{version}")
        return 0

    out_dir = Path(args.out) if args.out else ROOT / "build" / "vocab-docs"
    entries = [process(path, version, out_dir, args.inline_limit)
               for path in sorted(vocab_dir.glob("*.ttl"))]
    if entries:
        write_index(entries, version, out_dir)
    print(f"[vocab-docs] written to {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
