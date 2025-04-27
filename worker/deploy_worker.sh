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

echo "Creating folder for Worker data…"
mkdir -p /opt/rising-stars-worker
cp "$(dirname "$0")/docker-compose.yaml" /opt/rising-stars-worker/

cd /opt/rising-stars-worker

echo "Starting Worker container…"
docker compose up -d

echo -e "Worker is running.\n"
