#!/bin/sh
# Roda dentro do rootfs WSL, depois dos pacotes e arquivos copiados
set -e

sed -i 's/^# *pt_BR.UTF-8/pt_BR.UTF-8/' /etc/locale.gen
locale-gen
update-locale LANG=pt_BR.UTF-8

ln -sf /usr/share/zoneinfo/America/Sao_Paulo /etc/localtime
echo America/Sao_Paulo > /etc/timezone

if ! grep -q '/etc/dohsec/bashrc' /etc/bash.bashrc; then
  printf '\n[ -f /etc/dohsec/bashrc ] && . /etc/dohsec/bashrc\n' >> /etc/bash.bashrc
fi

chmod 755 /usr/local/bin/doh /usr/local/bin/donut /usr/local/bin/lab /usr/local/bin/oque /usr/local/bin/cola /usr/lib/wsl/oobe.sh
