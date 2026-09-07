#!/usr/bin/env python3
"""
End-to-end proof that a concept fragment resolves all the way to its section.

    https://w3id.org/AgoraOWL/vocabularies/observed-properties#ndvi

A fragment is never sent to the server, so this cannot be verified with curl.
What actually happens is a three-step chain, and every step can break:

  1. the browser drops the fragment and requests the fragment-less URL,
  2. w3id answers 303 to the documentation page,
  3. the browser re-applies the fragment to the redirect target
     (RFC 7231 section 7.1.2: a Location without a fragment inherits the
     original one) and scrolls to the matching element.

This script drives a real headless Chrome over the DevTools protocol against
the proposed rules and a local copy of the gh-pages tree, and reports the final
URL, the element the fragment selected, and its rendered label.

It also covers the SIEX path, where the concept is not in the page at all and
is fetched from a sharded JSON index at runtime.

The rules under test are byte-identical to w3id/AgoraOWL/.htaccess except that
the absolute target base is rewritten to a local path, so the redirect can be
followed without standing up TLS for khaosresearch.github.io.

Usage:
    python3 w3id/simulation/verify_fragments.py
"""

import json
import shutil
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import websocket  # websocket-client

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
IMAGE = "agoraowl-w3id-sim"
CONTAINER = "agoraowl-w3id-e2e"
REMOTE_BASE = "https://khaosresearch.github.io/AgoraOWL"
LOCAL_BASE = "/gh"

CASES = [
    ("/AgoraOWL/vocabularies/observed-properties#ndvi", "ndvi",
     "unversioned PID resolves to latest and lands on the concept"),
    ("/AgoraOWL/vocabularies/observed-properties#soilMoisture", "soilMoisture",
     "another concept in the same document"),
    ("/AgoraOWL/1.3.0/vocabularies/observed-properties#ndwi", "ndwi",
     "versioned PID lands on that version's page"),
    ("/AgoraOWL/latest/vocabularies/observed-properties#repiloIncidence", "repiloIncidence",
     "explicit 'latest' segment"),
    ("/AgoraOWL/vocabularies/siex#siex_MeasurementUnit_9", "siex_MeasurementUnit_9",
     "82k-concept vocabulary, resolved from the sharded index at runtime"),
    ("/AgoraOWL/vocabularies/siex#siex_CropVariety_1-1460", "siex_CropVariety_1-1460",
     "deep concept in the largest scheme"),
]

PROBE = """
(() => {
  const t = document.querySelector(':target') || document.querySelector('.concept.selected') || document.getElementById(%s);
  const h = t ? t.querySelector('h3') : null;
  return JSON.stringify({
    href: location.href,
    title: document.title,
    found: !!t,
    id: t ? t.id : null,
    label: h ? h.textContent.replace(/#$/, '').trim() : null,
    highlighted: !!(document.querySelector(':target') || document.querySelector('.concept.selected'))
  });
})()
"""


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def build_gh_tree(dest: Path) -> str:
    """Reproduce what .github/workflows/deploy-docs.yml publishes."""
    version = sorted(
        (d.name for d in (ROOT / "src").iterdir()
         if d.is_dir() and d.name[0].isdigit() and d.name.count(".") == 2),
        key=lambda v: [int(p) for p in v.split(".")])[-1]
    vocab_docs = ROOT / "build" / "vocab-docs"
    if not vocab_docs.is_dir():
        print("[e2e] generating vocabulary documentation first ...")
        subprocess.run([sys.executable, str(ROOT / "scripts" / "generate_vocab_docs.py")], check=True)

    target = dest / version / "vocabularies"
    target.mkdir(parents=True)
    for ttl in (ROOT / "src" / version / "vocabularies").glob("*.ttl"):
        shutil.copy(ttl, target / ttl.name)
    shutil.copytree(vocab_docs, target, dirs_exist_ok=True)
    for artefact in ("alignment.ttl", "context.jsonld"):
        source = ROOT / "src" / version / artefact
        if source.exists():
            shutil.copy(source, dest / version / artefact)
    shutil.copytree(dest / version, dest / "latest")
    print(f"[e2e] local gh-pages tree built from src/{version} (+ latest)")
    return version


def localised_rules(dest: Path) -> None:
    rules = (ROOT / "w3id" / "AgoraOWL" / ".htaccess").read_text(encoding="utf-8")
    dest.mkdir(parents=True, exist_ok=True)
    (dest / ".htaccess").write_text(rules.replace(REMOTE_BASE, LOCAL_BASE), encoding="utf-8")


def start_container(port: int, rules_dir: Path, gh_dir: Path) -> None:
    if run(["docker", "images", "-q", IMAGE]).stdout.strip() == "":
        print(f"[e2e] building {IMAGE} ...")
        result = run(["docker", "build", "-q", "-t", IMAGE, str(HERE)])
        if result.returncode != 0:
            sys.exit(f"[e2e] build failed:\n{result.stderr}")
    run(["docker", "rm", "-f", CONTAINER])
    result = run(["docker", "run", "-d", "--name", CONTAINER, "-p", f"{port}:80",
                  "-v", f"{rules_dir}:/usr/local/apache2/htdocs/AgoraOWL:ro",
                  "-v", f"{gh_dir}:/usr/local/apache2/htdocs/gh:ro", IMAGE])
    if result.returncode != 0:
        sys.exit(f"[e2e] run failed:\n{result.stderr}")


def wait_http(port: int, timeout: float = 30) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        with socket.socket() as sock:
            if sock.connect_ex(("127.0.0.1", port)) == 0:
                time.sleep(0.5)
                return
        time.sleep(0.3)
    sys.exit("[e2e] container did not become ready")


class Chrome:
    def __init__(self, profile: Path):
        self.port = free_port()
        binary = shutil.which("google-chrome") or shutil.which("chromium") or shutil.which("chromium-browser")
        if not binary:
            sys.exit("[e2e] no Chrome/Chromium found on PATH")
        self.proc = subprocess.Popen(
            [binary, "--headless=new", "--disable-gpu", "--no-sandbox", "--no-first-run",
             f"--remote-debugging-port={self.port}", f"--user-data-dir={profile}", "about:blank"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.ws = self._attach()
        self.msg_id = 0

    def _attach(self):
        import urllib.request
        deadline = time.time() + 30
        while time.time() < deadline:
            try:
                targets = json.loads(urllib.request.urlopen(
                    f"http://127.0.0.1:{self.port}/json/list", timeout=2).read())
                pages = [t for t in targets if t.get("type") == "page"]
                if pages:
                    # Chrome rejects the DevTools handshake when an Origin header is present.
                    return websocket.create_connection(
                        pages[0]["webSocketDebuggerUrl"], timeout=30, suppress_origin=True)
            except Exception:
                time.sleep(0.4)
        sys.exit("[e2e] could not attach to Chrome")

    def call(self, method: str, params: dict | None = None) -> dict:
        self.msg_id += 1
        self.ws.send(json.dumps({"id": self.msg_id, "method": method, "params": params or {}}))
        while True:
            message = json.loads(self.ws.recv())
            if message.get("id") == self.msg_id:
                return message.get("result", {})

    def visit(self, url: str, fragment: str) -> dict:
        # A fresh document each time, so a stale :target cannot mask a failure.
        self.call("Page.navigate", {"url": "about:blank"})
        time.sleep(0.15)
        self.call("Page.navigate", {"url": url})
        deadline = time.time() + 15
        last = {}
        while time.time() < deadline:
            time.sleep(0.35)
            result = self.call("Runtime.evaluate",
                               {"expression": PROBE % json.dumps(fragment), "returnByValue": True})
            value = result.get("result", {}).get("value")
            if value:
                last = json.loads(value)
                if last.get("found"):
                    return last
        return last

    def close(self):
        try:
            self.ws.close()
        finally:
            self.proc.terminate()


def main() -> int:
    if run(["docker", "info"]).returncode != 0:
        sys.exit("[e2e] docker is not available")

    workdir = Path(tempfile.mkdtemp(prefix="agoraowl-e2e-"))
    profile = workdir / "chrome-profile"
    gh_dir = workdir / "gh"
    rules_dir = workdir / "AgoraOWL"
    chrome = None
    port = free_port()
    try:
        build_gh_tree(gh_dir)
        localised_rules(rules_dir)
        start_container(port, rules_dir, gh_dir)
        wait_http(port)
        print(f"[e2e] apache on 127.0.0.1:{port}, rules from w3id/AgoraOWL/.htaccess\n")

        chrome = Chrome(profile)
        failures = []
        for path, fragment, note in CASES:
            url = f"http://127.0.0.1:{port}{path}"
            info = chrome.visit(url, fragment)
            ok = info.get("found") and info.get("id") == fragment
            print(f"  {'PASS' if ok else 'FAIL'}  {path}")
            print(f"        final URL : {info.get('href')}")
            print(f"        selected  : id={info.get('id')}  highlighted={info.get('highlighted')}")
            print(f"        renders   : {info.get('label')}")
            print(f"        ({note})")
            if not ok:
                failures.append(path)

        # The other half of the contract: a non-browser client asks for the same
        # PID and must get the whole Turtle document, with the concept in it.
        print()
        import urllib.request
        from rdflib import Graph, URIRef
        rdf_cases = [
            ("/AgoraOWL/vocabularies/observed-properties", "ndvi"),
            ("/AgoraOWL/1.3.0/vocabularies/observed-properties", "ndwi"),
        ]
        for path, fragment in rdf_cases:
            request = urllib.request.Request(f"http://127.0.0.1:{port}{path}",
                                             headers={"Accept": "text/turtle", "User-Agent": "curl/8"})
            with urllib.request.urlopen(request, timeout=15) as response:
                body = response.read().decode("utf-8")
                final = response.geturl()
            graph = Graph()
            graph.parse(data=body, format="turtle")
            concept = URIRef(f"https://w3id.org/AgoraOWL/vocabularies/observed-properties#{fragment}")
            present = (concept, None, None) in graph
            ok = final.endswith(".ttl") and present
            print(f"  {'PASS' if ok else 'FAIL'}  {path}   Accept: text/turtle")
            print(f"        final URL : {final}")
            print(f"        parsed    : {len(graph)} triples, {concept.split('#')[-1]} present={present}")
            if not ok:
                failures.append(path + " (turtle)")

        print("\n" + "=" * 72)
        if failures:
            print(f"[FAIL] {len(failures)} of {len(CASES)} fragments did not resolve")
            return 1
        print(f"[OK] all {len(CASES)} fragments resolve to their section, and the Turtle branch serves the full document")
        return 0
    finally:
        if chrome:
            chrome.close()
        run(["docker", "rm", "-f", CONTAINER])
        shutil.rmtree(workdir, ignore_errors=True)
        print("[e2e] container removed, temporary files deleted")


if __name__ == "__main__":
    sys.exit(main())
