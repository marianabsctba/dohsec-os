# D'OH!Sec OS

Distro Linux com tema Springfield, baseada em Debian 13 (trixie), feita a partir do esboço
[Desafio_Homer](https://github.com/marianabsctba/Desafio_Homer). Sai em dois formatos do mesmo código:

- **WSL** (`dohsec-os.wsl`): instala no Windows com dois cliques, abre no Terminal com tema próprio
- **ISO live** (`dohsec-os-amd64.hybrid.iso`): para máquina virtual (Hyper-V, VirtualBox, QEMU) ou Ventoy

## O que vem nela

- **D'OH!Sec Academy**: o simulador do esboço, no Firefox (`academy` no terminal ou pelo menu Iniciar)
- **Terminal**: prompt `D'oh$`, banner com frase aleatória (`doh`), donut 3D (`donut`) e "D'oh!" para comando inexistente
- **Sistema**: host `springfield`, pt-BR, fuso de São Paulo
- **Só na ISO**: boot com donut girando (Plymouth), XFCE com papel de parede próprio, usuário live `homer`
  e a Academy abrindo sozinha no login
- **Só no WSL**: cria o usuário no primeiro uso (padrão `homer`), atalho e ícone no Iniciar, esquema de
  cores no Windows Terminal

## Instalar no WSL

Dois cliques no `dohsec-os.wsl`, ou:

```bash
wsl --install --from-file dohsec-os.wsl
```

Precisa do WSL 2.4.4 ou mais novo. A Academy abre no Windows como janela normal (WSLg).

## Rodar a ISO numa VM

No Hyper-V ou VirtualBox, crie uma VM com 4 GB de RAM e aponte o drive de DVD para a ISO. No QEMU:

```bash
qemu-system-x86_64 -m 4096 -enable-kvm -cdrom dohsec-os-amd64.hybrid.iso
```

## Gerar

Roda em qualquer Linux com root ou `sudo`, inclusive no WSL do Windows (Ubuntu serve):

```bash
wsl -d Ubuntu -u root -- bash /mnt/c/Projetos/dohsec-os/build.sh wsl
```

```bash
wsl -d Ubuntu -u root -- bash /mnt/c/Projetos/dohsec-os/build.sh iso
```

Num Debian, builda direto. Em outra distro, monta antes um chroot Debian 13 em `/var/lib/dohsec-builder`
(só na primeira vez) e builda lá dentro. O resultado volta para esta pasta. O WSL leva uns 5 minutos.
A primeira ISO baixa uns 2 GB e leva de 30 a 60 minutos; as seguintes reaproveitam o cache.

## Estrutura

- `config/includes.chroot/` - arquivos comuns aos dois formatos: app, arte, identidade, comandos
- `config/package-lists/`, `config/hooks/live/`, `auto/config` - só da ISO (live-build)
- `config/wsl/` - só do WSL: pacotes, primeiro uso, ícone, perfil do Terminal
- `build.sh` - ponto de entrada (`iso` ou `wsl`)
- `scripts/build-wsl.sh` - monta o rootfs do WSL
- `scripts/debian-builder.sh` - monta o chroot Debian quando o host não é Debian

## Próximos passos

- Menu de boot da ISO com tema próprio e tempo limite
- Instalador (Calamares) para instalar no disco
- Imagem de disco pronta para VM (`.vhdx`, `.qcow2`) e para nuvem
- Tema GTK e ícones próprios
- Fontes do app embutidas (hoje vêm do Google Fonts e caem no fallback offline)
