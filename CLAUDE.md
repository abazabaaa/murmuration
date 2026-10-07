# murmuration

## Serving the page

- Run `./bootstrap.sh` to serve this checkout on 127.0.0.1 (each worktree serves its own copy). It prints
  `http://127.0.0.1:<port>/murmuration.html`; add URL parameters as needed (`?seed=1&n=800`, see the README table).
  Re-running it is safe: if the server is already up it only prints the URL. Options: `--status`, `--stop`,
  `--port N`, `--open`. The log is in `.serve/serve.log`. The server itself is `murmuration-serve.js`.
- It uses port 8766 by default, or the next free port above it. It skips the ports in `bootstrap.sh`'s `AVOID`
  list, which other local servers use. Never stop, kill or reuse a listener this checkout's bootstrap did not start.
- Responses are sent with `Cache-Control: no-store`, so a plain reload shows edits; no `?v=` cache-busting is needed.
- The headless checks (`node murmuration-check.js`, `node murmuration-falcon.js`, `node murmuration-assets.js`) read the
  files directly and need no server. The page also works opened from file://.
