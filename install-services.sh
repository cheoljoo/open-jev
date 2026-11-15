#!/usr/bin/env bash
# Install systemd *user* services (auto-start at boot). No sudo needed.
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
UNITS="$HOME/.config/systemd/user"; mkdir -p "$UNITS"
for pair in "openjev:start.sh:OpenJev API (8100)" "laya:start-laya.sh:Laya API (8200)"; do
  IFS=: read -r name script desc <<<"$pair"
  sed -e "s|@DIR@|$DIR|g" -e "s|@SCRIPT@|$script|g" -e "s|@DESC@|$desc|g" deploy/service.template > "$UNITS/$name.service"
done
systemctl --user daemon-reload
systemctl --user enable --now openjev.service laya.service
loginctl enable-linger "$USER" || echo "run: sudo loginctl enable-linger $USER  (needed to start before login)"
