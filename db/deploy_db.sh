#!/usr/bin/env bash

set -euo pipefail

echo "Installing Docker + Compose v2…"
apt-get update -y
apt-get install -y docker.io docker-compose-plugin

echo "Enabling Docker service…"
systemctl enable --now docker

echo "Adding user $(whoami) to docker group…"
if id "ubuntu" &>/dev/null; then
  usermod -aG docker ubuntu
fi

echo "Creating folder for DB data…"
mkdir -p /opt/rising-stars-db
cp "$(dirname "$0")/docker-compose.yaml" /opt/rising-stars-db/

cd /opt/rising-stars-db

echo "Starting DB container…"
docker compose up -d

echo -e "Database is running on the port 5432.\n"
