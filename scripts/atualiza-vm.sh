#!/bin/bash
# Atualiza o D'OH!Sec OS dentro da VM do VMware sem recriar o disco (o progresso fica intacto).
# Roda no Windows (Git Bash) com a VM ligada: copia programas, front e laboratorio pelo vmrun e
# reinicia a VM no fim.
#   scripts/atualiza-vm.sh [caminho.vmx]
set -euo pipefail
export MSYS_NO_PATHCONV=1

RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
VMX="${1:-$(cygpath -w "$RAIZ/vm/dohsec-os.vmx")}"
VMRUN="/c/Program Files (x86)/VMware/VMware Player/vmrun.exe"
G=(-T player -gu homer -gp donut)
PACOTE="$(mktemp -d)/dohsec-atualizacao.tar.gz"

"$VMRUN" list | grep -qiF "$(basename "$VMX")" || { echo "Ligue a VM antes: $VMX" >&2; exit 1; }

# So o que roda em tempo de execucao (o resto vem da imagem e nao muda)
tar -C "$RAIZ/config/includes.chroot" -czf "$PACOTE" \
  usr/local/bin usr/share/dohsec etc/dohsec etc/firefox
"$VMRUN" "${G[@]}" CopyFileFromHostToGuest "$VMX" "$(cygpath -w "$PACOTE")" /tmp/dohsec-atualizacao.tar.gz
"$VMRUN" "${G[@]}" runProgramInGuest "$VMX" /usr/bin/bash -c \
  "sudo tar -C / --no-same-owner -xzf /tmp/dohsec-atualizacao.tar.gz && \
   sudo chmod 755 /usr/local/bin/* && rm -f /tmp/dohsec-atualizacao.tar.gz && \
   { [ -f /etc/dohsec/senha-padrao ] || LC_ALL=C chage -l homer 2>/dev/null | head -1 | cut -d: -f2- | sed 's/^ *//' | sudo tee /etc/dohsec/senha-padrao >/dev/null; }"
rm -f "$PACOTE"
# Reinicia pelo VMware (reiniciar de dentro da VM deixa o vmrun esperando para sempre)
"$VMRUN" -T player reset "$VMX" soft
echo "Atualizado. A VM esta reiniciando."
