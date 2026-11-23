#!/usr/bin/env bash
# Serve this folder over HTTP (loopback only) so the demos open in a browser,
# incl. over SSH. Ctrl-C to stop.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
PORT="${1:-8777}"
echo "Serving $(pwd) on 127.0.0.1:${PORT} (loopback only)"
echo "  local:  http://localhost:${PORT}/"
echo "  remote: ssh -L ${PORT}:localhost:${PORT} <host>  then open http://localhost:${PORT}/"
exec python3 -m http.server "${PORT}" --bind 127.0.0.1
