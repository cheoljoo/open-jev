# open-jev

Two typed-decision models behind simple REST APIs (FastAPI):

| Service | Model | Port | Script |
|---|---|---|---|
| **openjev** | [AlexWortega/openjev](https://huggingface.co/AlexWortega/openjev) `qwen3.5-4b-nli-v5` (Qwen3.5-4B NLI cross-encoder) | 8100 | `./start.sh` |
| **laya** | [NandhaKishorM/laya](https://github.com/NandhaKishorM/laya) (multilingual, non-autoregressive) | 8200 | `./start-laya.sh` |

Both expose the same `POST /v1/systemone` wire format, so a client only changes the port.
Give a *state* (text) and *questions* (`choice`, `score`, `noul`) and get a probability per option in one forward pass.

This repo contains only the glue (API server, scripts, docs). Model weights are downloaded from Hugging Face / PyPI by `setup.sh`;
**check each model's license** (openjev: MIT per model card, laya: Apache-2.0).

## Quick start

```bash
./setup.sh            # venv + deps + openjev checkpoint (~8.5 GB)
./start.sh            # http://0.0.0.0:8100/docs
./start-laya.sh       # http://0.0.0.0:8200/docs
./install-services.sh # optional: systemd user services, auto-start at boot
```

Requires Linux, Python 3.10+ and an NVIDIA GPU (tested: RTX PRO 4000 Blackwell, torch cu132, Python 3.14). Inference ~30-70 ms per request on GPU.

```bash
curl -X POST http://localhost:8100/v1/systemone -H 'Content-Type: application/json' -d '{
  "state": "We were billed twice for March. Please refund it today.",
  "questions": {"department": {"type": "choice", "instructions": "Which department?",
     "criteria": {"billing": "invoices, refunds", "other": "everything else"}}}}'
```

## Docs

- [docs/API.md](docs/API.md) - endpoints, request/response formats, examples
- [docs/DEPLOY.md](docs/DEPLOY.md) - network exposure, API keys, systemd, CORS, troubleshooting
- [docs/MODELS.md](docs/MODELS.md) - openjev vs laya, caveats
- [vendor/README.md](vendor/README.md) - upstream source files behind each REST API (reference copies, with licenses)

## Security

**By default both servers listen on 0.0.0.0 with no authentication** (anyone who can reach the host can use the GPU).
Run with `USE_KEYS=1` and a `keys.env` file to require `Authorization: Bearer <key>`, see [docs/DEPLOY.md](docs/DEPLOY.md).

## License

[MIT](LICENSE) for the code in this repository. The models are separate works under their own licenses (openjev: MIT, laya: Apache-2.0).
