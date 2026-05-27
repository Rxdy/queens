#!/usr/bin/env bash
# deploy-rasp.sh — Script de déploiement pour Raspberry Pi (Raspbian/Debian)
# Usage : bash deploy-rasp.sh

set -euo pipefail

REPO_URL="https://github.com/Rxdy/queens.git"
APP_DIR="$HOME/queens"

echo "========================================"
echo " Queens — déploiement Raspberry Pi"
echo "========================================"

# ── 1. Docker ─────────────────────────────────────────────────────────────────
if ! command -v docker &>/dev/null; then
  echo "[1/4] Installation de Docker..."
  curl -fsSL https://get.docker.com | sh
  sudo usermod -aG docker "$USER"
  echo "      Docker installé. Lance 'newgrp docker' ou reconnecte-toi avant de relancer ce script."
  exit 0
else
  echo "[1/4] Docker déjà installé : $(docker --version)"
fi

# ── 2. Cloner ou mettre à jour le dépôt ───────────────────────────────────────
if [[ -z "$REPO_URL" ]]; then
  echo ""
  echo "ERREUR : renseigne REPO_URL dans ce script avant de le lancer."
  exit 1
fi

if [[ -d "$APP_DIR/.git" ]]; then
  echo "[2/4] Mise à jour du dépôt..."
  git -C "$APP_DIR" pull
else
  echo "[2/4] Clonage du dépôt..."
  git clone "$REPO_URL" "$APP_DIR"
fi

cd "$APP_DIR"

# ── 3. Build et lancement ─────────────────────────────────────────────────────
echo "[3/4] Build et démarrage des conteneurs (prod)..."
docker compose -f docker-compose.prod.yml up -d --build

echo "[4/4] État des services :"
docker compose -f docker-compose.prod.yml ps

echo ""
echo "✅  Application disponible sur http://$(hostname -I | awk '{print $1}')"
echo ""
echo "══════════════════════════════════════════════════════════════"
echo " Étape suivante : rendre accessible depuis internet"
echo " → installe cloudflared : bash cloudflare-tunnel.sh"
echo "══════════════════════════════════════════════════════════════"
