#!/usr/bin/env bash
# Usage: ./start.sh [port]   Public (no key) on all interfaces. For auth: USE_KEYS=1 ./start.sh
cd "$(dirname "$0")"
[ "$USE_KEYS" = 1 ] && { set -a; . ./keys.env; set +a; }
exec .venv/bin/python -m uvicorn server:app --host "${OPENJEV_HOST:-0.0.0.0}" --port "${1:-8100}"
