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

echo "Deploying App container…"
APP_DIR=/rising-stars/app
docker compose -f "$APP_DIR/docker-compose.yaml" up -d

echo -e "Worker is running.\n"
