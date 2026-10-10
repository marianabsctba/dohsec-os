#!/bin/bash
# Primeira abertura no WSL: cria o usuario (padrao homer) com sudo
set -u

DEFAULT_UID=1000

if getent passwd "$DEFAULT_UID" >/dev/null; then
  exit 0
fi

doh
echo "Bem-vinda(o) a Springfield! Vamos criar seu usuario."
echo

while true; do
  read -rp "Usuario [homer]: " name
  name=${name:-homer}
  if adduser --quiet --uid "$DEFAULT_UID" --comment "" "$name" && usermod -aG sudo "$name"; then
    break
  fi
  deluser --remove-home "$name" >/dev/null 2>&1 || true
  echo "D'oh! Nao deu certo, tenta de novo."
done

echo
echo "Pronto, $name. Digite 'academy' para abrir a D'OH!Sec Academy ou 'donut' para um lanche."
