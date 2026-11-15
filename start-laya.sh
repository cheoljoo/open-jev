#!/usr/bin/env bash
# Usage: ./start-laya.sh   Public (no key) on all interfaces. For auth: USE_KEYS=1 ./start-laya.sh
cd "$(dirname "$0")"
[ "$USE_KEYS" = 1 ] && { set -a; . ./keys.env; set +a; }
exec .venv/bin/python -m uvicorn laya_app:app --host "${LAYA_HOST:-0.0.0.0}" --port "${LAYA_PORT:-8200}"
