# Deployment

## Layout

- `server.py` - openjev FastAPI app (wraps `openjev/code/openjev_decide.py`; GPU forward guarded by a lock)
- `laya_app.py` - `laya.serve.create_app()` + CORS + OpenAPI examples
- `start.sh`, `start-laya.sh` - uvicorn launchers (host/port via `OPENJEV_HOST`, `LAYA_HOST`, `LAYA_PORT`)
- `install-services.sh`, `deploy/service.template` - systemd user services

## Network exposure and keys

Both launchers bind `0.0.0.0` and are **unauthenticated by default**. To require a bearer key:

```bash
umask 077
printf 'OPENJEV_API_KEY=%s\nLAYA_API_KEY=%s\n' "$(openssl rand -hex 32)" "$(openssl rand -hex 32)" > keys.env
USE_KEYS=1 ./start.sh
USE_KEYS=1 ./start-laya.sh
```

Clients send `Authorization: Bearer <key>`. Keys are never stored by the servers, only read from the environment at startup.
With `LAYA_API_KEY` set, laya disables `/docs` and `/openapi.json`. `keys.env` is git-ignored; never commit it.
For systemd, add `Environment=USE_KEYS=1` under `[Service]` of the unit. Traffic is plain HTTP: put a TLS reverse proxy or VPN in front outside a trusted network.
Restrict who can reach ports 8100/8200 with a firewall (`sudo ufw allow from <subnet> to any port 8100,8200 proto tcp`).

## systemd (auto-start at boot)

```bash
./install-services.sh
systemctl --user status openjev laya
systemctl --user restart openjev
journalctl --user -u openjev -f
```

User services start at boot only with lingering enabled (`loginctl enable-linger $USER`). Model loading takes 1-2 minutes.
Do not run `start.sh` by hand while the service is running (port conflict).

## Troubleshooting

- `422 choice needs criteria`: `criteria` must be `{label: rubric}` for `choice`, a list for `score`.
- `400 request body must be valid JSON` on laya: empty body sent (use the examples in `/docs`).
- Connection refused from another PC: check the bind address, firewall, and that the model has finished loading (`/health`).
- Both models share one GPU; stop one service if memory runs out.
- Do not use `pkill -f` patterns that match your own shell command line.
- openjev's SGLang image serving (in the upstream repo) targets V100 and is not part of this setup; image input is not supported here.
