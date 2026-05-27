#!/usr/bin/env bash
# cloudflare-tunnel.sh — Expose l'app sur internet via Cloudflare Tunnel (gratuit)
# Prérequis : avoir un compte Cloudflare (gratuit) sur https://dash.cloudflare.com
# Usage : bash cloudflare-tunnel.sh

set -euo pipefail

echo "================================================"
echo " Cloudflare Tunnel — installation & configuration"
echo "================================================"

# ── 1. Installer cloudflared ──────────────────────────────────────────────────
if ! command -v cloudflared &>/dev/null; then
  echo "[1/3] Installation de cloudflared..."
  ARCH=$(dpkg --print-architecture)   # arm64 ou armhf selon ton Rasp
  curl -fsSL "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-${ARCH}.deb" \
    -o /tmp/cloudflared.deb
  sudo dpkg -i /tmp/cloudflared.deb
  rm /tmp/cloudflared.deb
else
  echo "[1/3] cloudflared déjà installé : $(cloudflared --version)"
fi

# ── 2. Authentification Cloudflare (ouvre un lien dans ton navigateur) ────────
echo ""
echo "[2/3] Authentification Cloudflare..."
echo "      Un lien va s'afficher. Ouvre-le dans ton navigateur et autorise cloudflared."
echo ""
cloudflared tunnel login

# ── 3. Créer et lancer un tunnel Quick (URL temporaire, sans domaine) ─────────
echo ""
echo "[3/3] Lancement du tunnel (port 80 → internet)..."
echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  URL publique affichée ci-dessous (format .trycloudflare.com)║"
echo "║  Partage-la pour accéder à l'app depuis n'importe où.        ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Quick tunnel : aucune config, aucun domaine requis, URL générée automatiquement
cloudflared tunnel --url http://localhost:80
