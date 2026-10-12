# D'OH!Sec OS

Distro Linux de treinamento em cibersegurança com tema Springfield, baseada em Debian 13 (trixie).
Nasceu do esboço [Desafio_Homer](https://github.com/marianabsctba/Desafio_Homer): o front do esboço
virou o próprio sistema operacional, com terminal, apps e ferramentas de verdade, e uma carreira que
vai de **Estagiário** a **Assistente do Sr. Burns** resolvendo 48 casos de resposta a incidente.

> Projeto de fã com caráter acadêmico e sem fins lucrativos. *Os Simpsons* pertencem a Matt Groening e à
> 20th Television / Disney. Veja [Créditos e aviso legal](#créditos-e-aviso-legal).

![Área de trabalho do D'OH!Sec OS](docs/prints/03-desktop.png)

## Formatos

Para usar, **não precisa clonar este repositório**: baixe o arquivo pronto na página de
[Releases](https://github.com/marianabsctba/dohsec-os/releases) e siga o passo a passo do formato.

| Formato | Arquivo (em Releases) | Para quê | Guarda o progresso? |
| --- | --- | --- | --- |
| WSL | `dohsec-os.wsl` | terminal e Laboratório dentro do Windows, sem máquina virtual | ✅ sim |
| ISO | `dohsec-os-amd64.hybrid.iso` | a experiência completa (desktop, apps, sons) numa máquina virtual ou pendrive | ❌ não, recomeça a cada boot |

Passo a passo: [Instalar no WSL](#instalar-no-wsl-passo-a-passo) e
[Rodar a ISO numa máquina virtual](#rodar-a-iso-numa-máquina-virtual-passo-a-passo).

Quem gera a partir do código também pode criar um **disco instalado para o VMware** (`build.sh disco`),
que tem a experiência completa e guarda o progresso. Ele não vai para Releases por ser grande demais.

## Como é

O boot vai direto para o **D'OH!BIOS** e para a tela de login do esboço. Não tem menu de boot nem
desktop genérico: o front é a sessão gráfica (Firefox em modo quiosque, sobre o xfwm4), e cada app
conversa com o sistema real por um serviço local (`dohsec-api`).

| | |
| --- | --- |
| ![D'OH!BIOS](docs/prints/01-bios.png) | ![Login](docs/prints/02-login.png) |
| **D'OH!BIOS**: a primeira tela depois do boot | **Login**: nome para o certificado e a ficha na Usina |

### Apps do sistema (todos reais)

| App | O que mostra ou faz |
| --- | --- |
| 💻 Terminal | bash de verdade (xterm.js); também abre com **Ctrl+Alt+T** |
| 🗂️ Arquivos | navega pelas pastas, mostra arquivos e abre no Inspetor |
| ⚙️ Processos | `ps` ao vivo; encerra os processos do próprio usuário |
| 📡 Rede | `ip`, rotas, `ss` (portas e conexões) e DNS |
| 📜 Logs/Eventos | `journalctl`: sistema, logins e sudo, avisos, kernel |
| 🛡️ Mini SIEM | busca no journal, em `/var/log` e nas evidências dos casos |
| 🔐 Permissões | `id`, contas, `sudo -l`, `ls -la ~` e programas SUID |
| 🧩 Updates | pacotes pendentes e atualização pelo Terminal |
| 🔌 Reiniciar / Desligar | pelo menu Iniciar |

<img src="docs/prints/14-menu.png" alt="Menu Iniciar" width="640">

### Exclusivos do D'OH!Sec

| | |
| --- | --- |
| ![Painel do Sr. Burns](docs/prints/08-painel-burns.png) | ![Inspetor de Arquivos](docs/prints/09-inspetor.png) |
| **👔 Painel do Sr. Burns**: nota de segurança da própria máquina (firewall, updates, portas expostas, logins falhos, UID 0, contas sem senha, senha padrão, arquivos graváveis, auditd, AIDE), com botão de corrigir. Só verifica e corrige: nunca enfraquece nada. | **🔬 Inspetor de Arquivos**: laudo de um arquivo suspeito com `file`, `strings`, `exiftool`, `binwalk`, YARA e ClamAV, sem nunca executá-lo. Pega extensão falsa, extensão dupla, arquivo embutido e metadados. |
| ![Captura de Rede](docs/prints/10-captura.png) | ![Relatório de Incidente](docs/prints/11-relatorio.png) |
| **🦈 Captura de Rede**: grava 10, 30 ou 60 segundos com `dumpcap` e resume com `tshark` (quem falou com quem, DNS, sites HTTPS e HTTP). Abre no Wireshark com um clique. | **📝 Relatório de Incidente**: diário do analista em cada caso, mais resumo, linha do tempo, IOCs, impacto, remediação e lições. As evidências entram sozinhas com SHA-256. Exporta Markdown e HTML para `~/Relatorios`. |
| ![Conquistas](docs/prints/12-conquistas.png) | ![Certificado](docs/prints/13-certificado.png) |
| **🏅 Conquistas**: 25 medalhas ganhas de verdade (comandos do terminal, casos, relatórios, capturas e apps). Aparecem num aviso na tela, na ficha e no certificado. | **🏆 Certificado**: o cargo atual, os casos resolvidos e as medalhas. Salva em PNG. |

## Carreira na Usina

Você entra como **Estagiário** e vai sendo promovido(a) resolvendo casos reais. As etapas liberam em
ordem, cada promoção chega por memorando do Smithers e o progresso fica salvo
(`~/.local/share/dohsec/lab.json`).

| Cargo | Etapa | Casos |
| --- | --- | --- |
| 🍩 Estagiário | o terminal | 8 |
| 🔧 Operador da Usina | o sistema por dentro | 13 |
| 🛡️ Supervisor de Segurança | logs, tráfego e detecção | 15 |
| 🔬 Chefe de Segurança | forense e endurecimento | 9 |
| 👔 Assistente do Sr. Burns | Teste final do Sr. Burns | 3 |

| | |
| --- | --- |
| ![Minha carreira](docs/prints/04-carreira.png) | ![Mesa do Incidente](docs/prints/05-mesa.png) |
| **🎯 Minha carreira**: ficha funcional, plano de carreira, medalhas e histórico de promoções | **🚨 Mesa do Incidente**: os casos da etapa atual |

## Laboratório Springfield

Casos de resposta a incidente da Usina com evidências de verdade para investigar no terminal: logs de
SSH e de firewall, e-mails com cabeçalhos, capturas `.pcap`, CSVs de eventos do Windows e do Sysmon,
`docker inspect`, crontabs, `sudo -l`, imagens com metadados e arquivos embutidos, relatórios do AIDE
e do auditd. Tudo é sintético: IPs de documentação (RFC 5737), domínios `.test` e nenhum binário malicioso.

![Laboratório](docs/prints/06-laboratorio.png)

| Comando | O que faz |
| --- | --- |
| `lab` | lista os casos, o progresso e o cargo atual |
| `lab iniciar 1` | copia as evidências do caso para `~/springfield/casos/` e mostra o contexto |
| `lab dica 1` | mostra a próxima dica |
| `lab responder 1 "resposta"` | confere a resposta (maiúsculas, aspas e espaços não importam) |
| `lab revisar 1` | mostra o que aprendemos no caso |
| `lab zerar` | apaga o progresso |

As ferramentas instaladas para resolver os casos: `grep`, `awk`, `jq`, `sqlite3`, `file`, `xxd`,
`strings`, `sha256sum`, `tcpdump`, `tshark`, Wireshark, `nmap`, YARA, ClamAV, `exiftool`, `binwalk`,
`foremost`, Sleuth Kit, `testdisk`, `lynis`, `auditd`, AIDE, `ufw`, `nftables`, Suricata e Scapy.
O app **🧰 Ferramentas** mostra o que usar em cada etapa.

As respostas ficam no `casos.json` só como hash. Para criar ou mudar casos, edite
`scripts/gen-lab.py`, `scripts/lab_casos.py` ou `scripts/lab_esboco.py` e rode `python3 scripts/gen-lab.py`.
Cada caso novo deve ter a própria semente (veja `lab_esboco.py`) para não mudar as respostas dos outros.

## Comandos do terminal

![Terminal](docs/prints/07-terminal.png)

| Comando | O que faz |
| --- | --- |
| `doh` | banner com frase aleatória e resumo da máquina |
| `oque TERMO` | glossário sem jargão: `oque firewall`, `oque hash` (aceita sem acento e só o começo) |
| `cola TEMA` | os comandos mais úteis por tema: `cola rede`, `cola forense`, `cola tudo` |
| `lab` | o Laboratório Springfield (acima) |
| `relatorio anota "pista"` | anota no diário do caso (dentro da pasta do caso o número é opcional) |
| `relatorio ver N` / `exportar N` | mostra ou exporta o relatório do caso |
| `conquistas` | as medalhas ganhas e o que falta |
| `donut` | donut 3D girando |
| `noturno on` / `off` / `auto` | papel de parede noturno com estrelas piscando (só na ISO e no disco) |

## Instalar no WSL (passo a passo)

O D'OH!Sec instala como uma **distro separada**: não precisa clonar o repositório nem abrir o Ubuntu
que você já tenha, e ele não é alterado. Tudo é feito no Windows.

1. **Baixe** o `dohsec-os.wsl` em [Releases](https://github.com/marianabsctba/dohsec-os/releases).
   Ele vai para a pasta Downloads.
2. **Abra o PowerShell** (ou o Windows Terminal) e atualize o WSL. Precisa da versão 2.4.4 ou mais nova:

   ```powershell
   wsl --update
   ```

3. **Instale**: dê dois cliques no `dohsec-os.wsl` baixado, ou rode no PowerShell:

   ```powershell
   wsl --install --from-file "$env:USERPROFILE\Downloads\dohsec-os.wsl"
   ```

4. **Primeiro uso**: abre um terminal pedindo um usuário (Enter aceita `homer`) e uma senha, digitada
   duas vezes. A senha não aparece enquanto você digita: é normal.
5. **Pronto.** Para abrir de novo: menu Iniciar → **DOHSec-OS**, ou o perfil **DOHSec-OS** no Windows
   Terminal, ou no PowerShell:

   ```powershell
   wsl -d DOHSec-OS
   ```

6. **Comece pelo Laboratório**: digite `lab` e depois `lab iniciar 1`.

Vem com o terminal temático, o Laboratório, `oque`, `cola`, `relatorio` e `conquistas`. O desktop do
front, os apps e os sons são da ISO; no WSL, `academy` abre o esboço original numa janela.
As ferramentas de análise dos casos mais avançados não vêm na imagem do WSL. Para instalar:

```bash
sudo apt update && sudo apt install -y jq tshark yara libimage-exiftool-perl binwalk sleuthkit xxd bind9-dnsutils
```

(se o `tshark` perguntar se usuários comuns podem capturar pacotes, responda **Não**)

Para desinstalar (apaga a distro e o progresso dela):

```powershell
wsl --unregister DOHSec-OS
```

## Rodar a ISO numa máquina virtual (passo a passo)

1. **Baixe** a `dohsec-os-amd64.hybrid.iso` em [Releases](https://github.com/marianabsctba/dohsec-os/releases).
2. **Crie uma máquina virtual nova** no programa que você usa:
   - **VMware Workstation Player**: *Create a New Virtual Machine* → *Installer disc image file (iso)* →
     escolha a ISO → sistema *Linux / Debian 12.x 64-bit* → 20 GB de disco (não é usado) → em
     *Customize Hardware*, **4 GB de memória** e confirme que há *Sound Card*.
   - **VirtualBox**: *Novo* → tipo *Linux*, versão *Debian (64-bit)* → **4096 MB** de memória → sem disco
     → em *Configurações → Armazenamento*, coloque a ISO no drive óptico; em *Áudio*, deixe habilitado.
   - **QEMU**: `qemu-system-x86_64 -m 4096 -enable-kvm -cdrom dohsec-os-amd64.hybrid.iso`
3. **Ligue a VM.** Ela vai direto para o **D'OH!BIOS**. Escolha *Inicializar com efeitos sonoros* para
   ter a música (dá para ligar e desligar depois no 🔇/🔊 da bandeja).
4. **Login**: digite seu nome (vai para o certificado) e clique em *Entrar no desktop*.

A ISO roda da memória: **ao desligar, o progresso some**. Para guardar o progresso, use o WSL ou o
disco do VMware.
Se a VM mostrar "Network boot from Intel E1000", ela não achou a ISO: confira o caminho do arquivo nas
configurações do CD (e não troque a ISO com a VM suspensa).

Também roda de pendrive: instale o [Ventoy](https://www.ventoy.net) no pendrive e copie a ISO para ele.

## Disco instalado para o VMware (quem gera a partir do código)

Depois de `build.sh iso` e `build.sh disco`, abra no VMware **Player → File → Open...** e escolha
`vm/dohsec-os.vmx`. O sistema entra direto, sem pedir senha (usuário `homer`, senha `donut`; troque com
`passwd`). A VM usa UEFI, 4 GB de RAM e 2 CPUs. Para levar as mudanças do código para uma VM já criada
sem perder o progresso, ligue a VM e rode `scripts/atualiza-vm.sh` no Git Bash.

## Gerar

Roda em qualquer Linux com root ou `sudo`, inclusive no WSL do Windows (Ubuntu serve):

```bash
wsl -d Ubuntu -u root -- bash /mnt/c/Projetos/dohsec-os/build.sh iso
```

```bash
wsl -d Ubuntu -u root -- bash /mnt/c/Projetos/dohsec-os/build.sh wsl
```

```bash
wsl -d Ubuntu -u root -- bash /mnt/c/Projetos/dohsec-os/build.sh disco
```

Num Debian, builda direto. Em outra distro, monta antes um chroot Debian 13 em `/var/lib/dohsec-builder`
(só na primeira vez) e builda lá dentro. O resultado volta para esta pasta. O WSL leva uns 5 minutos.
A primeira ISO baixa uns 2 GB e leva de 30 a 60 minutos; as seguintes reaproveitam o cache.
O `disco` precisa de uma ISO gerada antes e cria `vm/dohsec-os.vmdk` e `vm/dohsec-os.vmx`.

Não rode o build com uma VM ligada na mesma máquina: os dois juntos podem esgotar a memória.

## Segurança

- O `dohsec-api` escuta só em `127.0.0.1:7700`, roda como o usuário da sessão (nunca root) e exige um
  token sorteado a cada sessão e o cabeçalho `Host` correto (contra DNS rebinding).
- O terminal do front (`dohsec-pty`) escuta só em `127.0.0.1:7681` e confere a origem e o mesmo token.
- O Inspetor nunca executa o arquivo analisado. O Painel do Sr. Burns só verifica e endurece.
- No disco do VMware, o `homer` usa `sudo` sem senha para facilitar o laboratório. Não use essa
  imagem como máquina de produção.

## Estrutura

- `config/includes.chroot/` - arquivos comuns aos formatos: front, apps, comandos, casos, arte
  - `usr/share/dohsec/academy/index.html` - o front do esboço
  - `usr/share/dohsec/front/` - a ponte (`bridge.js`, `bridge.css`) que liga o front ao sistema
  - `usr/local/bin/` - `dohsec-api`, `dohsec-pty`, `dohsec-shell`, `lab`, `oque`, `cola`, `relatorio`, `conquistas`...
  - `usr/share/dohsec/lab/` - os casos gerados (evidências e `casos.json`)
- `config/package-lists/`, `config/hooks/live/`, `auto/config` - ISO (live-build)
- `config/bootloaders/` - boot da ISO (sem menu, direto para o sistema)
- `config/wsl/` - só do WSL: pacotes, primeiro uso, ícone, perfil do Terminal
- `config/vm/dohsec-os.vmx` - modelo da VM do VMware
- `scripts/gen-lab.py`, `lab_casos.py`, `lab_esboco.py` - geram os casos do Laboratório
- `scripts/gen-xfwm4-theme.py`, `gen-ceu-noturno.py` - bordas das janelas e céu noturno
- `scripts/build-wsl.sh`, `build-disco.sh`, `debian-builder.sh` - montagem de cada formato
- `scripts/atualiza-vm.sh` - leva o código novo para a VM sem recriar o disco
- `build.sh` - ponto de entrada (`iso`, `wsl` ou `disco`)
- `docs/prints/` - os prints deste README

## Créditos e aviso legal

O D'OH!Sec OS é um projeto de fã com **caráter acadêmico**: foi feito para ensinar Linux e
cibersegurança, sem fins lucrativos, e não é vendido nem usado comercialmente.

*Os Simpsons*, Homer Simpson, Sr. Burns, Smithers, a Usina Nuclear de Springfield e demais personagens,
nomes e imagens são criação de **Matt Groening** e pertencem à **20th Television / The Walt Disney
Company**. Este projeto não tem ligação, patrocínio ou aprovação deles. As referências servem só de tema
para o treinamento.

O sistema é baseado no **Debian** e usa software livre, cada um com a sua licença. As fontes VT323 e
Share Tech Mono são distribuídas sob a SIL Open Font License, que acompanha os arquivos em
`usr/share/fonts/truetype/dohsec/`.

Se algum detentor de direitos quiser que um conteúdo seja removido, abra uma issue no repositório que
ele será retirado.

## Próximos passos

- Ferramentas de análise também na imagem do WSL
- Instalador (Calamares) para instalar em disco físico
- Imagem para Hyper-V e VirtualBox (`.vhdx`, `.vdi`)
- Cursor e sons próprios
