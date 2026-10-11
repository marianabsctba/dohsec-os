#!/bin/bash
# Gera o D'OH!Sec OS instalado num disco virtual para o VMware (vm/dohsec-os.vmdk + .vmx).
# Usa o sistema da ISO ja construida (binary/live/filesystem.squashfs), instala num disco com
# boot BIOS e UEFI, tira as partes de sistema live e cria o usuario homer com login automatico.
# Roda num Debian como root: scripts/build-disco.sh SRC WORK
set -euo pipefail

SRC="$1"
WORK="$2"
SQUASH="$WORK/binary/live/filesystem.squashfs"
D="$WORK/disco"
IMG="$D/disco.raw"
ALVO="$D/raiz"
TAMANHO=24G
SAIDA="$SRC/vm"

[ -f "$SQUASH" ] || { echo "Gere a ISO antes (build.sh iso): falta $SQUASH" >&2; exit 1; }
apt-get install -y parted dosfstools e2fsprogs squashfs-tools qemu-utils >/dev/null

LOOP=""
desmonta() {
  for m in boot/efi dev/pts dev sys proc run; do umount -l "$ALVO/$m" 2>/dev/null || true; done
  umount -l "$ALVO" 2>/dev/null || true
  [ -n "$LOOP" ] && losetup -d "$LOOP" 2>/dev/null || true
}
trap desmonta EXIT

rm -rf "$D"
mkdir -p "$D" "$ALVO"
truncate -s "$TAMANHO" "$IMG"

# GPT: particao de boot BIOS (grub), particao EFI e a raiz
parted -s "$IMG" mklabel gpt \
  mkpart bios 1MiB 3MiB set 1 bios_grub on \
  mkpart esp fat32 3MiB 515MiB set 2 esp on \
  mkpart raiz ext4 515MiB 100%
LOOP=$(losetup -fP --show "$IMG")
mkfs.vfat -F 32 -n EFI "${LOOP}p2" >/dev/null
mkfs.ext4 -q -L dohsec "${LOOP}p3"

mount "${LOOP}p3" "$ALVO"
echo "Copiando o sistema da ISO para o disco..."
unsquashfs -f -q -d "$ALVO" "$SQUASH"
mkdir -p "$ALVO/boot/efi"
mount "${LOOP}p2" "$ALVO/boot/efi"

for m in proc sys dev dev/pts run; do mkdir -p "$ALVO/$m"; done
mount -t proc proc "$ALVO/proc"
mount --rbind /sys "$ALVO/sys"; mount --make-rslave "$ALVO/sys"
mount --bind /dev "$ALVO/dev"; mount --make-rslave "$ALVO/dev"
mount --bind /dev/pts "$ALVO/dev/pts"
mount -t tmpfs tmpfs "$ALVO/run"
rm -f "$ALVO/etc/resolv.conf"
cp /etc/resolv.conf "$ALVO/etc/resolv.conf"

UUID_RAIZ=$(blkid -s UUID -o value "${LOOP}p3")
UUID_EFI=$(blkid -s UUID -o value "${LOOP}p2")
cat > "$ALVO/etc/fstab" <<EOF
UUID=$UUID_RAIZ  /          ext4  errors=remount-ro  0 1
UUID=$UUID_EFI   /boot/efi  vfat  umask=0077         0 2
EOF

cat > "$ALVO/tmp/instala.sh" <<'EOS'
#!/bin/bash
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive

# Sem as partes de sistema live
apt-get purge -y live-boot live-boot-initramfs-tools live-config live-config-systemd live-tools 2>/dev/null || true
apt-get autoremove -y >/dev/null || true

# Carregador de boot (BIOS e UEFI) e kernel
apt-get update -qq
apt-get install -y -qq grub-pc-bin grub-efi-amd64-bin grub2-common >/dev/null

# Identidade, idioma, teclado e fuso (o que o live configurava no boot)
echo springfield > /etc/hostname
printf '127.0.0.1\tlocalhost\n127.0.1.1\tspringfield\n' > /etc/hosts
sed -i 's/^# *pt_BR.UTF-8/pt_BR.UTF-8/' /etc/locale.gen
locale-gen >/dev/null
update-locale LANG=pt_BR.UTF-8
ln -sf /usr/share/zoneinfo/America/Sao_Paulo /etc/localtime
echo America/Sao_Paulo > /etc/timezone
printf 'XKBMODEL="pc105"\nXKBLAYOUT="br"\nXKBVARIANT=""\nXKBOPTIONS=""\nBACKSPACE="guess"\n' > /etc/default/keyboard

# Usuario homer: login automatico na sessao do front, sudo sem senha (laboratorio local)
if ! id homer >/dev/null 2>&1; then
  useradd -m -s /bin/bash -c Homer homer
fi
getent group autologin >/dev/null || groupadd -r autologin
for g in sudo adm systemd-journal wireshark audio video plugdev netdev autologin; do
  getent group "$g" >/dev/null && usermod -aG "$g" homer
done
echo 'homer:donut' | chpasswd
echo 'homer ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers.d/homer
chmod 440 /etc/sudoers.d/homer
mkdir -p /etc/lightdm/lightdm.conf.d
cat > /etc/lightdm/lightdm.conf.d/60-autologin.conf <<'EOF'
[Seat:*]
autologin-user=homer
autologin-session=dohsec
user-session=dohsec
EOF

# Boot direto (o unico boot visivel e o D'OH!BIOS do front)
cat > /etc/default/grub <<'EOF'
GRUB_DEFAULT=0
GRUB_TIMEOUT_STYLE=hidden
GRUB_TIMEOUT=1
GRUB_DISTRIBUTOR="D'OH!Sec OS"
GRUB_CMDLINE_LINUX_DEFAULT="quiet splash loglevel=3"
GRUB_CMDLINE_LINUX=""
EOF
update-initramfs -u -k all >/dev/null
EOS
chroot "$ALVO" bash /tmp/instala.sh

# grub nos dois modos: BIOS (no disco) e UEFI (caminho removivel, funciona em qualquer VM)
chroot "$ALVO" grub-install --target=i386-pc "$LOOP"
chroot "$ALVO" grub-install --target=x86_64-efi --efi-directory=/boot/efi --removable --no-nvram
chroot "$ALVO" grub-mkconfig -o /boot/grub/grub.cfg

# O NetworkManager preenche o resolv.conf quando a rede sobe
rm -f "$ALVO/tmp/instala.sh" "$ALVO/etc/resolv.conf"
: > "$ALVO/etc/resolv.conf"
desmonta
LOOP=""

echo "Convertendo para o formato do VMware..."
mkdir -p "$SAIDA"
rm -f "$SAIDA/dohsec-os.vmdk"
qemu-img convert -f raw -O vmdk -o subformat=monolithicSparse "$IMG" "$SAIDA/dohsec-os.vmdk"
cp "$SRC/config/vm/dohsec-os.vmx" "$SAIDA/dohsec-os.vmx"
rm -f "$IMG"
echo "Disco pronto: $SAIDA/dohsec-os.vmdk"
