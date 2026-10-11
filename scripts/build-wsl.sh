#!/bin/bash
# Gera dohsec-os.wsl: rootfs Debian 13 com a identidade do D'OH!Sec, instalavel com dois cliques
# (ou wsl --install --from-file). Roda num Debian como root.
set -euo pipefail

SRC="$1"
WORK="${DOHSEC_WORK:-$HOME/dohsec-build}/wsl"
ROOT="$WORK/rootfs"
STAGE="$WORK/stage"
MIRROR=https://deb.debian.org/debian
OUT=dohsec-os.wsl

apt-get install -y debootstrap librsvg2-bin imagemagick >/dev/null

cleanup() {
  for m in dev/pts dev proc; do umount -l "$ROOT/$m" 2>/dev/null || true; done
}
trap cleanup EXIT

cleanup
rm -rf "$ROOT" "$STAGE"
mkdir -p "$WORK"
debootstrap --variant=minbase trixie "$ROOT" "$MIRROR"

mount -t proc proc "$ROOT/proc"
mount --bind /dev "$ROOT/dev"
mount --make-rslave "$ROOT/dev"
mount --bind /dev/pts "$ROOT/dev/pts"
cp /etc/resolv.conf "$ROOT/etc/resolv.conf"

chroot "$ROOT" apt-get update
chroot "$ROOT" env DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
  $(grep -v '^#' "$SRC/config/wsl/packages.list")

# Arquivos compartilhados com a ISO, menos o que so faz sentido no live (boot, login, XFCE)
mkdir -p "$STAGE"
cp -r "$SRC/config/includes.chroot/." "$STAGE/"
cp -r "$SRC/config/wsl/rootfs/." "$STAGE/"
rm -rf "$STAGE/usr/share/plymouth" "$STAGE/etc/lightdm" "$STAGE/etc/xdg/autostart" "$STAGE/etc/xdg/xfce4" \
  "$STAGE/usr/local/bin/dohsec-session" "$STAGE/usr/local/bin/dohsec-ceu" "$STAGE/usr/local/bin/noturno" \
  "$STAGE/usr/local/bin/dohsec-shell" "$STAGE/usr/local/bin/dohsec-terminal" "$STAGE/usr/share/xsessions" "$STAGE/etc/dohsec/xbindkeysrc" \
  "$STAGE/usr/share/dohsec/wallpaper.svg" "$STAGE/usr/share/dohsec/wallpaper-noite.svg"

rsvg-convert -w 256 -h 256 "$STAGE/usr/share/dohsec/donut.svg" -o "$STAGE/usr/share/dohsec/donut.png"
convert "$STAGE/usr/share/dohsec/donut.png" -define icon:auto-resize=256,64,48,32,16 "$STAGE/usr/lib/wsl/dohsec.ico"

# Permissoes corretas (arquivos vindos do Windows chegam todos como 777)
find "$STAGE" -type d -exec chmod 755 {} +
find "$STAGE" -type f -exec chmod 644 {} +
chown -R root:root "$STAGE"
cp -a "$STAGE/." "$ROOT/"

cp "$SRC/config/wsl/setup.sh" "$ROOT/tmp/setup.sh"
chroot "$ROOT" /bin/sh /tmp/setup.sh

chroot "$ROOT" apt-get clean
rm -rf "$ROOT/var/lib/apt/lists/"* "$ROOT/tmp/"* "$ROOT/etc/resolv.conf"
cleanup

tar --numeric-owner -czf "$SRC/$OUT" -C "$ROOT" .
echo "WSL pronto: $SRC/$OUT"
