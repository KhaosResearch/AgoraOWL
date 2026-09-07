# w3id redirection simulator

Runs the **proposed** `w3id/AgoraOWL/.htaccess` inside an Apache 2.4 container
configured the way `w3id.org` configures it (per-directory `.htaccess`,
`mod_rewrite`, `AllowOverride All`), and asserts the `Location` header returned
for every URL and `Accept` header combination AgoraOWL cares about.

The point is to open **one** pull request against `perma-id/w3id.org` and know
it is right, instead of iterating against a repository we do not control.

```bash
python3 w3id/simulation/verify_redirects.py            # build, run, assert, clean up
python3 w3id/simulation/verify_redirects.py --keep     # leave the container running
```

Nothing is installed on the host: the image is built from `httpd:2.4-alpine`,
the container is removed on exit, and the image can be dropped with
`docker rmi agoraowl-w3id-sim`.

`expectations.tsv` is the contract. Each row is
`request path`, `Accept header`, `User-Agent`, `expected Location` (or `404`).

## Fragment resolution (end to end, with a real browser)

`verify_redirects.py` can only check the `Location` header. It cannot check
whether

    https://w3id.org/AgoraOWL/vocabularies/observed-properties#ndvi

actually lands on the NDVI section, because **a fragment is never sent to the
server**. What happens is a three-step chain and every step can break:

1. the browser drops the fragment and requests the fragment-less URL,
2. w3id answers `303` pointing at the documentation page,
3. the browser re-applies the fragment to the redirect target (RFC 7231
   §7.1.2: a `Location` without a fragment inherits the original one) and
   scrolls to the matching element.

```bash
python3 w3id/simulation/verify_fragments.py
```

This drives a real headless Chrome over the DevTools protocol against the
proposed rules plus a local copy of the gh-pages tree, and reports the final
URL, the element the fragment selected and its rendered label. It covers both
vocabulary strategies (inline anchors, and the sharded client-side index SIEX
needs for its 82 240 concepts) and asserts the other half of the contract too:
a client sending `Accept: text/turtle` gets the whole Turtle document.

The rules under test are byte-identical to `w3id/AgoraOWL/.htaccess` except that
the absolute target base is rewritten to a local path, so the redirect can be
followed without standing up TLS for `khaosresearch.github.io`.

Requires `google-chrome` (or `chromium`) on `PATH` and the `websocket-client`
Python package. Nothing is installed: Chrome runs headless against a throwaway
profile in a temporary directory that is deleted on exit.
