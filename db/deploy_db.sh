#!/usr/bin/env bash

set -euo pipefail

echo "Installing Docker + Compose v2…"
apt-get update -y

# Add Docker's official GPG key:
apt-get install ca-certificates curl
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | \
  tee /etc/apt/sources.list.d/docker.list > /dev/null

apt-get install -y docker.io
apt-get install -y docker-compose-plugin

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
