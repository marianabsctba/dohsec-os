# D'OH!Sec OS

Distro Linux com tema Springfield, baseada em Debian 13 (trixie), feita a partir do esboço
[Desafio_Homer](https://github.com/marianabsctba/Desafio_Homer). Sai em dois formatos do mesmo código:

- **WSL** (`dohsec-os.wsl`): instala no Windows com dois cliques, abre no Terminal com tema próprio
- **ISO live** (`dohsec-os-amd64.hybrid.iso`): para máquina virtual (Hyper-V, VirtualBox, QEMU) ou Ventoy

## O que vem nela

- **D'OH!Sec Academy**: o simulador do esboço, no Firefox (`academy` no terminal ou pelo menu Iniciar)
- **Terminal**: prompt `D'oh$`, banner com frase aleatória (`doh`), donut 3D (`donut`) e "D'oh!" para comando inexistente
- **Sistema**: host `springfield`, pt-BR, fuso de São Paulo
- **Só na ISO**: menu de boot próprio, boot com donut girando (Plymouth), XFCE com tema Springfield
  (janelas amarelas, painel marrom com menu de donut, ícones Papirus com pastas amarelas, terminal com a
  paleta), usuário live `homer` e a Academy abrindo sozinha no login
- **Só no WSL**: cria o usuário no primeiro uso (padrão `homer`), atalho e ícone no Iniciar, esquema de
  cores no Windows Terminal

## Carreira na Usina

O D'OH!Sec OS é o front do esboço rodando como sistema operacional de verdade (Debian por baixo).
Você entra como **Estagiário** e vai sendo promovido(a) resolvendo casos reais:

| Cargo | Etapa | Casos |
| --- | --- | --- |
| 🍩 Estagiário | o terminal | 8 |
| 🔧 Operador da Usina | o sistema por dentro | 11 |
| 🛡️ Supervisor de Segurança | logs, tráfego e detecção | 12 |
| 🔬 Chefe de Segurança | forense e endurecimento | 6 |
| 👔 Assistente do Sr. Burns | Teste final do Sr. Burns | 3 |

As etapas liberam em ordem. Cada promoção chega por memorando do Smithers e gera um certificado do
cargo. No front: **Minha carreira** (ficha e plano), **Mesa do Incidente** (casos da etapa atual),
**Laboratório** (todas as etapas), **Ferramentas** (o que usar em cada etapa) e **Certificado**.
Os apps do sistema também são reais: Terminal (bash), Arquivos, Processos, Rede, Logs, Mini SIEM,
Permissões, Updates, Reiniciar e Desligar.

## Laboratório Springfield

Casos de resposta a incidente da Usina, com evidências de verdade para investigar no terminal
(logs, e-mail, processos, histórico de grupos). Tudo é sintético: IPs de documentação, domínios `.test`
e nenhum binário malicioso.

```bash
lab
```

| Comando | O que faz |
| --- | --- |
| `lab` | lista os casos, o progresso e o cargo atual |
| `lab iniciar 1` | copia as evidências do caso para `~/springfield/casos/` e mostra o contexto |
| `lab dica 1` | mostra a próxima dica |
| `lab responder 1 "resposta"` | confere a resposta (maiúsculas, aspas e espaços não importam) |
| `lab zerar` | apaga o progresso |

As respostas ficam no `casos.json` só como hash. Para criar ou mudar casos, edite
`scripts/gen-lab.py` e rode `python3 scripts/gen-lab.py`.

## Céu noturno

Das 18h às 6h o papel de parede vira a versão noturna, com lua e estrelas piscando. O boot é sempre
noturno, com as estrelas animadas.

| Comando | O que faz |
| --- | --- |
| `noturno` | mostra a configuração |
| `noturno on` / `off` / `auto` | noite sempre, dia sempre, ou pelo relógio |
| `noturno pisca off` | estrelas paradas (máquina fraca) |

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
- `config/bootloaders/` - menu de boot da ISO (isolinux e GRUB)
- `config/wsl/` - só do WSL: pacotes, primeiro uso, ícone, perfil do Terminal
- `scripts/gen-xfwm4-theme.py` - gera as bordas de janela do tema Springfield (rodar após mudar a paleta)
- `scripts/gen-ceu-noturno.py` - gera o papel de parede noturno
- `scripts/gen-lab.py` - gera os casos do Laboratório Springfield
- `build.sh` - ponto de entrada (`iso` ou `wsl`)
- `scripts/build-wsl.sh` - monta o rootfs do WSL
- `scripts/debian-builder.sh` - monta o chroot Debian quando o host não é Debian

## Próximos passos

- Instalador (Calamares) para instalar no disco
- Imagem de disco pronta para VM (`.vhdx`, `.qcow2`) e para nuvem
- Cursor e sons próprios
- Fontes do app embutidas (hoje vêm do Google Fonts e caem no fallback offline)
