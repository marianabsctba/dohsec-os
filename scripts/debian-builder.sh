#!/bin/bash
# Para hosts que nao sao Debian (ex.: WSL Ubuntu): monta um chroot Debian 13 com
# live-build e roda o build.sh la dentro. Precisa ser root.
set -euo pipefail

SRC="$1"
TARGET="${2:-iso}"
BUILDER="${DOHSEC_BUILDER:-/var/lib/dohsec-builder}"
MIRROR=https://deb.debian.org/debian
DEBOOTSTRAP=debootstrap_1.0.145_all.deb
KEYRING=debian-archive-keyring_2025.1_all.deb

if [ ! -x "$BUILDER/usr/bin/lb" ]; then
  tools=$(mktemp -d)
  wget -q -P "$tools" "$MIRROR/pool/main/d/debootstrap/$DEBOOTSTRAP" \
    "$MIRROR/pool/main/d/debian-archive-keyring/$KEYRING"
  dpkg -x "$tools/$DEBOOTSTRAP" "$tools/x"
  dpkg -x "$tools/$KEYRING" "$tools/x"

  DEBOOTSTRAP_DIR="$tools/x/usr/share/debootstrap" "$tools/x/usr/sbin/debootstrap" \
    --keyring="$tools/x/usr/share/keyrings/debian-archive-keyring.gpg" \
    trixie "$BUILDER" "$MIRROR"
  rm -rf "$tools"
fi

cleanup() {
  for m in dev/pts dev sys proc; do umount -l "$BUILDER/$m" 2>/dev/null || true; done
}
trap cleanup EXIT
mount -t proc proc "$BUILDER/proc"
mount --rbind /sys "$BUILDER/sys"
mount --make-rslave "$BUILDER/sys"
mount --bind /dev "$BUILDER/dev"
mount --make-rslave "$BUILDER/dev"
mount --bind /dev/pts "$BUILDER/dev/pts"
cp /etc/resolv.conf "$BUILDER/etc/resolv.conf"

if [ ! -x "$BUILDER/usr/bin/lb" ]; then
  chroot "$BUILDER" apt-get update
  chroot "$BUILDER" apt-get install -y live-build
fi

# So o codigo: sem .git e sem os artefatos grandes (ISO, .wsl, disco da VM)
rm -rf "$BUILDER/src"
mkdir -p "$BUILDER/src"
tar -C "$SRC" --exclude=./.git --exclude='*.iso' --exclude='*.wsl' --exclude=./vm -cf - . | tar -C "$BUILDER/src" -xf -
chroot "$BUILDER" env HOME=/root /bin/bash /src/build.sh "$TARGET"

if [ "$TARGET" = wsl ]; then
  cp "$BUILDER/src/dohsec-os.wsl" "$SRC/"
elif [ "$TARGET" = disco ]; then
  mkdir -p "$SRC/vm"
  cp "$BUILDER/src/vm/"* "$SRC/vm/"
else
  cp "$BUILDER/src/"*.iso "$SRC/"
fi
