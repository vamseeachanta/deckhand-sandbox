#!/usr/bin/env bash
# view.sh — tiny viewer "app" for the rendered marketing demos.
# Serves this folder over HTTP so the MP4/GIF/HTML open in a browser even when
# file:// links and xdg-open don't work (e.g. over SSH). Ctrl-C to stop.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
PORT="${1:-8777}"
echo "Serving $(pwd) on 127.0.0.1:${PORT} (loopback only — not exposed to the LAN)"
echo "  local:  http://localhost:${PORT}/"
echo "  remote: ssh -L ${PORT}:localhost:${PORT} <host>   then open http://localhost:${PORT}/"
echo "  (Ctrl-C to stop)"
exec python3 -m http.server "${PORT}" --bind 127.0.0.1
