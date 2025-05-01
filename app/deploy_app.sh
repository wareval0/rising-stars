#!/usr/bin/env bash
set -euo pipefail

echo "Installing Docker + Compose v2…"
apt-get update -y

echo "Installing prerequisites…"
apt-get install -y ca-certificates curl

echo "Adding Docker's official GPG key…"
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
     -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc

echo "Setting up Docker's repository…"
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] \
  https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
  | tee /etc/apt/sources.list.d/docker.list > /dev/null

echo "Updating package index with the new repo…"
apt-get update -y

echo "Installing Docker and Compose plugin…"
apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

echo "Enabling Docker service…"
systemctl enable --now docker

echo "Adding user $(whoami) to docker group…"
usermod -aG docker "$(whoami)"

echo "Deploying app container…"
docker compose -f /rising-stars/app/docker-compose.yaml up -d

echo -e "\nApp is running.\n"
