#!/bin/bash
# Gera o D'OH!Sec OS: ./build.sh iso (padrao), ./build.sh wsl ou ./build.sh disco (VMware).
# Em Debian roda direto; em outro Linux (ex.: WSL Ubuntu) monta um chroot Debian
# com scripts/debian-builder.sh e roda la dentro.
# O build roda numa pasta do filesystem Linux: chroot em /mnt/c (NTFS) nao funciona.
set -euo pipefail

SRC="$(cd "$(dirname "$0")" && pwd)"
TARGET="${1:-iso}"
WORK="${DOHSEC_WORK:-$HOME/dohsec-build}"
ISO=dohsec-os-amd64.hybrid.iso
SUDO=
[ "$(id -u)" -ne 0 ] && SUDO=sudo

case "$TARGET" in
  iso|wsl|disco) ;;
  *) echo "uso: $0 [iso|wsl|disco]  (disco precisa de uma ISO gerada antes)" >&2; exit 2 ;;
esac

if ! grep -q '^ID=debian$' /etc/os-release; then
  exec $SUDO bash "$SRC/scripts/debian-builder.sh" "$SRC" "$TARGET"
fi

if [ "$TARGET" = wsl ]; then
  exec $SUDO bash "$SRC/scripts/build-wsl.sh" "$SRC"
fi

if [ "$TARGET" = disco ]; then
  exec $SUDO bash "$SRC/scripts/build-disco.sh" "$SRC" "$WORK"
fi

if ! command -v lb >/dev/null 2>&1; then
  $SUDO apt-get update
  $SUDO apt-get install -y live-build
fi

# Copia a config limpa para a pasta de trabalho (o cache de pacotes e mantido)
mkdir -p "$WORK"
cd "$WORK"
# Nada pode estar montado dentro do chroot na hora de limpar: o rm -rf do lb clean
# atravessaria um /dev montado e apagaria o /dev do proprio sistema
if [ -d chroot ]; then
  for m in $(awk -v r="$(pwd)/chroot" 'index($2, r) == 1 {print $2}' /proc/mounts | sort -r); do
    $SUDO umount -l "$m" || true
  done
fi
$SUDO lb clean 2>/dev/null || true
$SUDO rm -rf auto config
cp -r "$SRC/auto" "$SRC/config" .

# Permissoes corretas (arquivos vindos do Windows chegam todos como 777)
find auto config -type d -exec chmod 755 {} +
find config -type f -exec chmod 644 {} +
chmod 755 auto/* config/hooks/live/*.hook.chroot config/includes.chroot/usr/local/bin/*

lb config
$SUDO lb build

cp "$WORK/$ISO" "$SRC/"
echo "ISO pronta: $SRC/$ISO"
