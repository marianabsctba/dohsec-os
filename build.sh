#!/bin/bash
# Gera a ISO do D'OH!Sec OS. Precisa de Debian (ou WSL Debian) com sudo.
# O build roda numa pasta do filesystem Linux: chroot em /mnt/c (NTFS) nao funciona.
set -euo pipefail

SRC="$(cd "$(dirname "$0")" && pwd)"
WORK="${DOHSEC_WORK:-$HOME/dohsec-build}"
ISO=dohsec-os-amd64.hybrid.iso

if ! command -v lb >/dev/null 2>&1; then
  sudo apt-get update
  sudo apt-get install -y live-build
fi

# Copia a config limpa para a pasta de trabalho (o cache de pacotes e mantido)
mkdir -p "$WORK"
cd "$WORK"
sudo lb clean 2>/dev/null || true
sudo rm -rf auto config
cp -r "$SRC/auto" "$SRC/config" .

# Permissoes corretas (arquivos vindos do Windows chegam todos como 777)
find auto config -type d -exec chmod 755 {} +
find config -type f -exec chmod 644 {} +
chmod 755 auto/* config/hooks/live/*.hook.chroot config/includes.chroot/usr/local/bin/*

lb config
sudo lb build

cp "$WORK/$ISO" "$SRC/"
echo "ISO pronta: $SRC/$ISO"
