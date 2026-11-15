# vendor/ - upstream source that implements the REST APIs

Unmodified **reference copies** of the third-party source files the two APIs are built on, so the whole API can be read in one repository.
They are not imported from here at runtime: `setup.sh` installs/downloads the originals (`pip install laya`, Hugging Face checkpoint).
If you change something, change it in `server.py` / `laya_app.py` (this repo's own code) and keep these copies in sync with upstream.

| Path | Upstream | Version | License |
|---|---|---|---|
| `openjev/openjev_decide.py`, `openjev/modeling_openjev.py` | https://huggingface.co/AlexWortega/openjev (`code/`) | snapshot of 2026-11-15 | MIT (per the model card, `license: mit`; the Hub repo ships no LICENSE file) |
| `laya/serve.py`, `laya/LICENSE` | https://github.com/NandhaKishorM/laya (`laya/serve.py`, PyPI `laya`) | 0.4.32 | Apache-2.0 (full text in `laya/LICENSE`) |

## How the APIs map to source

- **openjev (:8100)** - `../server.py` (FastAPI routes) calls `vendor/openjev/openjev_decide.py` (`OpenJev.decide`), which uses `modeling_openjev.py` (`OpenJevCrossEncoder`).
- **laya (:8200)** - `vendor/laya/serve.py` defines the routes (`/health`, `/v1/route`, `/v1/systemone`, `/v1/systemone/batch`) and `create_app()`;
  `../laya_app.py` wraps it with CORS and Swagger examples.
