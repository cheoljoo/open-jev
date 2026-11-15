#!/usr/bin/env bash
# One-shot setup: venv + dependencies + openjev 4B v5 checkpoint and code (~8.5 GB download).
set -e
cd "$(dirname "$0")"
python3 -m venv .venv
.venv/bin/pip install -q -r requirements.txt
.venv/bin/python -I - <<'PY'
from huggingface_hub import snapshot_download
snapshot_download("AlexWortega/openjev", local_dir="openjev",
    allow_patterns=["README.md", "RESULTS-v5.md", "code/*.py", "modeling_openjev.py", "qwen3.5-4b-nli-v5/*"])
PY
echo "done. Run ./start.sh (openjev :8100) and ./start-laya.sh (laya :8200), or ./install-services.sh"
