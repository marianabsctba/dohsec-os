# D'OH!Sec OS

Distro Linux live com tema Springfield, baseada em Debian 13 (trixie), feita a partir do esboço
[Desafio_Homer](https://github.com/marianabsctba/Desafio_Homer).

## O que vem nela

- **Boot**: tema Plymouth com donut girando sobre céu amarelo
- **Desktop**: XFCE com papel de parede próprio, login no LightDM tematizado
- **D'OH!Sec Academy**: o simulador do esboço abre sozinho no login (e fica no menu, ou `academy` no terminal)
- **Terminal**: prompt `D'oh$`, banner com frase aleatória (`doh`), donut 3D (`donut`) e "D'oh!" para comando inexistente
- **Live**: usuário `homer`, host `springfield`, pt-BR, teclado ABNT2, fuso de São Paulo

## Gerar a ISO

Precisa de um Debian com `sudo`. No Windows, use o WSL com Debian:

```bash
wsl --install -d Debian
```

Depois, dentro do Debian:

```bash
/mnt/c/Projetos/dohsec-os/build.sh
```

O script instala o `live-build` se faltar, roda o build em `~/dohsec-build` (chroot não funciona em `/mnt/c`)
e copia `dohsec-os-amd64.hybrid.iso` de volta para esta pasta. O primeiro build baixa uns 2 GB e leva
de 20 a 40 minutos.

## Testar no QEMU

```bash
qemu-system-x86_64 -m 4096 -enable-kvm -cdrom dohsec-os-amd64.hybrid.iso
```

No Windows, sem KVM, troque `-enable-kvm` por `-accel whpx` (ou só remova).

## Estrutura

- `auto/config` - opções do live-build (distribuição, nome da ISO, parâmetros de boot)
- `config/package-lists/` - pacotes instalados
- `config/hooks/live/` - hook que aplica a identidade (os-release, papel de parede, Plymouth, shell)
- `config/includes.chroot/` - arquivos copiados para o sistema: app, arte, tema de boot, comandos
- `build.sh` - gera a ISO

## Próximos passos

- Instalador (Calamares) para instalar no disco
- Tema GTK e ícones próprios
- Splash do GRUB/isolinux da ISO
- Fontes do app embutidas (hoje vêm do Google Fonts e caem no fallback offline)
