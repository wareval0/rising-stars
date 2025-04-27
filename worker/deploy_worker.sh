#!/usr/bin/env bash

set -euo pipefail

echo "Installing Docker + Compose v2…"
apt-get update -y
apt-get install -y docker.io
apt-get install docker-compose-plugin

echo "Enabling Docker service…"
systemctl enable --now docker

echo "Adding user $(whoami) to docker group…"
if id "ubuntu" &>/dev/null; then
  usermod -aG docker ubuntu
fi

echo "Deploying Worker container…"
cd "$(dirname "$0")"
docker compose up -d

echo -e "Worker is running.\n"
