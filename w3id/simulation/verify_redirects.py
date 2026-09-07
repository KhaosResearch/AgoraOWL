#!/usr/bin/env python3
"""
Verify the proposed w3id.org redirection rules before opening a pull request
against perma-id/w3id.org.

Builds an Apache 2.4 container configured the way w3id.org configures itself
(per-directory .htaccess, mod_rewrite, AllowOverride All), serves
w3id/AgoraOWL/.htaccess from it, and asserts the exact Location header returned
for every path and Accept header in expectations.tsv.

Nothing is installed on the host and the container is removed on exit.

Usage:
    python3 w3id/simulation/verify_redirects.py
    python3 w3id/simulation/verify_redirects.py --keep     # leave it running
    python3 w3id/simulation/verify_redirects.py --port 8099
"""

import argparse
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
IMAGE = "agoraowl-w3id-sim"
CONTAINER = "agoraowl-w3id-sim"
GH = "https://khaosresearch.github.io/AgoraOWL"


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, **kwargs)


def free_port() -> int:
    """Ask the OS for an unused port so a busy 8088 does not fail the run."""
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def docker_available() -> bool:
    return run(["docker", "info"]).returncode == 0


def build_and_start(port: int, htaccess: Path | None) -> None:
    if htaccess is not None:
        target = HERE / "AgoraOWL" / ".htaccess"
        target.write_text(htaccess.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"[sim] using rules from {htaccess}")
    print(f"[sim] building {IMAGE} ...")
    result = run(["docker", "build", "-q", "-t", IMAGE, str(HERE)])
    if result.returncode != 0:
        sys.exit(f"[sim] build failed:\n{result.stderr}")
    run(["docker", "rm", "-f", CONTAINER])
    print(f"[sim] starting container on port {port} ...")
    result = run(["docker", "run", "-d", "--name", CONTAINER, "-p", f"{port}:80", IMAGE])
    if result.returncode != 0:
        sys.exit(f"[sim] run failed:\n{result.stderr}")


def wait_ready(port: int, timeout: float = 30.0) -> None:
    opener = urllib.request.build_opener(NoRedirect)
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            opener.open(f"http://127.0.0.1:{port}/", timeout=2)
            return
        except urllib.error.HTTPError:
            return
        except Exception:
            time.sleep(0.4)
    sys.exit("[sim] container did not become ready")


def request(port: int, path: str, accept: str, agent: str) -> tuple[int, str | None]:
    opener = urllib.request.build_opener(NoRedirect)
    req = urllib.request.Request(f"http://127.0.0.1:{port}{path}",
                                 headers={"Accept": accept, "User-Agent": agent})
    try:
        response = opener.open(req, timeout=10)
        return response.status, response.headers.get("Location")
    except urllib.error.HTTPError as err:
        return err.code, err.headers.get("Location")


def load_expectations() -> list[dict]:
    rows = []
    with open(HERE / "expectations.tsv", encoding="utf-8") as handle:
        for line in handle:
            if line.startswith("#") or not line.strip():
                continue
            path, accept, agent, expected, note = (line.rstrip("\n").split("\t") + [""] * 5)[:5]
            rows.append({"path": path, "accept": accept, "agent": agent,
                         "expected": expected.replace("GH", GH, 1), "note": note})
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--port", type=int, default=0, help="0 = pick a free port automatically")
    parser.add_argument("--keep", action="store_true", help="do not remove the container on exit")
    parser.add_argument("--htaccess", type=Path, default=None,
                        help="rules to test (default: the proposed w3id/AgoraOWL/.htaccess)")
    parser.add_argument("--gh-pages", type=Path, default=None,
                        help="local copy of the gh-pages tree; also assert every redirect target exists")
    parser.add_argument("--baseline", action="store_true",
                        help="test the rules currently live at perma-id/w3id.org instead")
    args = parser.parse_args()

    if not docker_available():
        sys.exit("[sim] docker is not available")

    rules = args.htaccess
    if args.baseline:
        rules = HERE / "baseline.htaccess"
        if not rules.exists():
            sys.exit(f"[sim] {rules} not found. Fetch it with:\n"
                     "  curl -sSL -o w3id/simulation/baseline.htaccess "
                     "https://raw.githubusercontent.com/perma-id/w3id.org/master/ids/AgoraOWL/.htaccess")
    port = args.port or free_port()
    build_and_start(port, rules)
    try:
        wait_ready(port)
        rows = load_expectations()
        print(f"[sim] checking {len(rows)} redirection contracts\n")
        failures = []
        for row in rows:
            status, location = request(port, row["path"], row["accept"], row["agent"])
            ok = (location == row["expected"]) and status in (301, 302, 303, 307, 308)
            mark = "PASS" if ok else "FAIL"
            short = row["path"].replace("/AgoraOWL", "")
            print(f"  {mark}  {short:52} Accept: {row['accept'][:34]:34} -> {status} {location or '(none)'}")
            if not ok:
                failures.append((row, status, location))
                print(f"        expected: {row['expected']}")
            elif args.gh_pages is not None:
                # A rule that points at a file the deployment never produces is
                # just a 404 with extra steps.
                rel = location[len(GH) + 1:].split("#", 1)[0]
                if not (args.gh_pages / rel).exists():
                    failures.append((row, status, location))
                    print(f"        MISSING TARGET: {args.gh_pages / rel}")

        print("\n" + "=" * 70)
        if failures:
            print(f"[FAIL] {len(failures)} of {len(rows)} contracts not satisfied")
            return 1
        print(f"[OK] all {len(rows)} redirection contracts satisfied")
        return 0
    finally:
        # Always restore the proposed rules into the build context.
        proposed = HERE.parent / "AgoraOWL" / ".htaccess"
        (HERE / "AgoraOWL" / ".htaccess").write_text(proposed.read_text(encoding="utf-8"), encoding="utf-8")
        if args.keep:
            print(f"[sim] container kept: docker rm -f {CONTAINER}")
        else:
            run(["docker", "rm", "-f", CONTAINER])
            print("[sim] container removed")


if __name__ == "__main__":
    sys.exit(main())
