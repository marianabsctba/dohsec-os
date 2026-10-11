"""Casos que vieram dos incidentes simulados do esboco (D'OH!Sec OS 2.0), agora com evidencias reais.

Usado por scripts/gen-lab.py. Cada caso usa a propria semente (random.Random(slug)): assim,
incluir estes casos nao muda as evidencias nem as respostas dos casos que ja existiam.
Tudo e ficticio: IPs de documentacao (RFC 5737), dominios .test, nenhum binario executavel.
So deteccao e investigacao: nada aqui ensina a atacar.
"""
import json
import random
from datetime import timedelta

from lab_casos import FUNCIONARIOS, INICIO, caso


def semente(f):
    """Ignora o rnd compartilhado e usa um gerador proprio do caso."""
    def caso_isolado(_rnd, cid):
        return f(random.Random(f.__name__), cid)
    return caso_isolado


# ===========================================================================
# Operador da Usina
# ===========================================================================
@semente
def ssh_root(rnd, cid):
    config = """# /etc/ssh/sshd_config  (usina-srv02)
Include /etc/ssh/sshd_config.d/*.conf
Port 22
ListenAddress 0.0.0.0
#LoginGraceTime 2m
PermitRootLogin yes
#StrictModes yes
MaxAuthTries 6
PubkeyAuthentication yes
PasswordAuthentication yes
KbdInteractiveAuthentication no
UsePAM yes
X11Forwarding yes
PrintMotd no
AcceptEnv LANG LC_*
Subsystem sftp /usr/lib/openssh/sftp-server
"""
    ss = """State   Recv-Q  Send-Q  Local Address:Port  Peer Address:Port  Process
LISTEN  0       128     0.0.0.0:22          0.0.0.0:*          users:(("sshd",pid=702,fd=3))
LISTEN  0       511     127.0.0.1:8080      0.0.0.0:*          users:(("java",pid=1190,fd=41))
LISTEN  0       244     127.0.0.1:5432      0.0.0.0:*          users:(("postgres",pid=988,fd=6))
"""
    linhas = []
    t = INICIO - timedelta(hours=8)
    for _ in range(220):
        t += timedelta(minutes=rnd.randint(1, 5))
        u = rnd.choice(FUNCIONARIOS[:4])
        linhas.append(f"{t:%b %d %H:%M:%S} usina-srv02 sshd[{rnd.randint(2000, 9000)}]: Accepted publickey for {u} "
                      f"from 10.20.{rnd.randint(1, 9)}.{rnd.randint(2, 250)} port {rnd.randint(30000, 65000)} ssh2")
    linhas.insert(150, f"{(INICIO - timedelta(hours=2)):%b %d %H:%M:%S} usina-srv02 sshd[6131]: Accepted password for root "
                       f"from 203.0.113.91 port 40112 ssh2")
    return caso(cid, "SSH exposto com root login", "operador", "medio",
                """O `usina-srv02` aceita SSH de qualquer lugar e alguem entrou **direto como root**, com senha.
Na vida real o root nunca deveria entrar pelo SSH: cada pessoa entra com a propria conta e usa `sudo`
(fica registrado quem fez o que). Compare a configuracao do servidor com o que aconteceu.""",
                "Qual linha do sshd_config permite entrar direto como root? (escreva a linha como esta no arquivo)",
                "PermitRootLogin yes",
                ["As opcoes do SSH ficam no sshd_config. Linhas com # sao comentarios.",
                 "Procure por Root: grep -i root sshd_config",
                 "Responda a linha inteira, por exemplo: Opcao valor"],
                ["PermitRootLogin yes deixa o root entrar pelo SSH: o certo e 'no'.",
                 "PasswordAuthentication yes aceita senha; com chave (publickey) e bem mais seguro.",
                 "ListenAddress 0.0.0.0 escuta em todas as redes: confira com ss -tlnp o que esta exposto.",
                 "Depois de mudar: sudo sshd -t (testa) e sudo systemctl reload ssh."],
                {"sshd_config": config, "ss-tlnp.txt": ss, "auth.log": "\n".join(linhas) + "\n"})


@semente
def sudo_vim(rnd, cid):
    regras = """# sudo -l de cada usuario (usina-srv01), exportado pela auditoria

Usuario carl pode executar os seguintes comandos em usina-srv01:
    (root) NOPASSWD: /usr/bin/systemctl restart reator-monitor

Usuario lenny pode executar os seguintes comandos em usina-srv01:
    (root) /usr/bin/tail -n 100 /var/log/reator.log

Usuario marge pode executar os seguintes comandos em usina-srv01:
    (root) NOPASSWD: sudoedit /etc/usina/cardapio.conf

Usuario homer pode executar os seguintes comandos em usina-srv01:
    (root) NOPASSWD: /usr/bin/vim /etc/usina/reator.conf

Usuario smithers pode executar os seguintes comandos em usina-srv01:
    (ALL : ALL) ALL

Usuario frank.grimes pode executar os seguintes comandos em usina-srv01:
    (root) /usr/bin/journalctl -u reator-monitor
"""
    return caso(cid, "sudo -l com vim NOPASSWD", "operador", "medio",
                """A auditoria exportou o `sudo -l` de todo mundo. Algumas regras parecem inocentes:
"so pode editar UM arquivo". Mas um editor como o vim, rodando como root, consegue abrir outros arquivos
e ate um terminal: na pratica a pessoa vira root, e sem senha.
O smithers e administrador de proposito (ALL), entao ele nao conta.""",
                "Qual usuario, alem do smithers, na pratica pode virar root sem senha?",
                "homer",
                ["Procure regras com NOPASSWD.",
                 "systemctl restart de UM servico e sudoedit sao restritos. Um editor rodando como root nao e.",
                 "O vim roda inteiro como root e consegue abrir um terminal."],
                ["Editores, paginadores e interpretadores (vim, less, python) rodando como root viram root completo.",
                 "Para deixar editar um arquivo, use sudoedit: a pessoa edita como ela mesma e so o arquivo muda.",
                 "Revise o sudo -l de cada conta: NOPASSWD em programa 'poderoso' e furo grave.",
                 "Existe um catalogo publico desses programas (GTFOBins) que times de defesa usam para revisar regras."],
                {"sudo-l.txt": regras})


# ===========================================================================
# Supervisor de Seguranca (analista)
# ===========================================================================
@semente
def varredura(rnd, cid):
    varredor = "198.51.100.23"
    outros = [f"203.0.113.{n}" for n in rnd.sample(range(5, 250), 15)]
    linhas = []
    t = INICIO
    for _ in range(900):
        t += timedelta(seconds=rnd.randint(1, 25))
        ip = rnd.choice(outros)
        porta = rnd.choice([22, 23, 80, 443, 3389, 445])
        linhas.append((t, ip, porta))
    inicio = INICIO + timedelta(hours=1, minutes=10)
    portas = rnd.sample(range(1, 10000), 420)
    for i, porta in enumerate(portas):
        linhas.append((inicio + timedelta(milliseconds=150 * i), varredor, porta))
    linhas.sort()
    texto = "\n".join(
        f"{t:%b %d %H:%M:%S} usina-fw01 kernel: [UFW BLOCK] IN=eth0 OUT= MAC=00:16:3e:aa:bb:cc SRC={ip} "
        f"DST=10.20.0.1 LEN=44 TOS=0x00 PREC=0x00 TTL=52 ID={rnd.randint(1000, 65000)} PROTO=TCP "
        f"SPT={rnd.randint(30000, 65000)} DPT={porta} WINDOW=1024 RES=0x00 SYN URGP=0"
        for t, ip, porta in linhas)
    return caso(cid, "Quem esta varrendo a usina?", "analista", "medio",
                """O SIEM percebeu uma enumeracao: alguem esta batendo em porta atras de porta do firewall para
descobrir o que existe la dentro (varredura de portas). Todo dia ha bloqueios "normais" de robos da
internet nas portas de sempre (22, 80, 443...). A varredura e diferente: **muitas portas diferentes**
vindas de um mesmo IP em pouco tempo.""",
                "Qual IP fez a varredura de portas?",
                varredor,
                ["Cada linha tem SRC= (quem mandou) e DPT= (porta de destino).",
                 "Conte por IP quantas portas DIFERENTES ele tentou: grep -o 'SRC=[^ ]*' e grep -o 'DPT=[0-9]*'.",
                 "Uma receita: awk '{for(i=1;i<=NF;i++) if($i~/^(SRC|DPT)=/) printf $i\" \"; print \"\"}' ufw.log | sort -u | cut -d' ' -f1 | uniq -c | sort -rn | head"],
                ["Varredura = muitas portas diferentes do mesmo IP em pouco tempo. Robos comuns repetem poucas portas.",
                 "sort -u antes do uniq -c conta valores diferentes (portas distintas), nao tentativas.",
                 "Resposta: bloquear o IP, conferir se alguma porta respondeu e se houve acesso depois.",
                 "Varredura costuma vir antes de um ataque: e um aviso, nao so barulho."],
                {"ufw.log": texto + "\n"})


@semente
def rdp_fornecedor(rnd, cid):
    regras = """# Regras de NAT do firewall de borda (usina-fw01)
regra  externo                 interno            descricao
10     0.0.0.0/0:443           10.20.0.10:443     portal-web
11     0.0.0.0/0:25            10.20.0.12:25      mx-email
12     0.0.0.0/0:3389          10.20.3.40:3389    acesso-fornecedor (temporario 2023)
13     10.99.0.0/16:3389       10.20.3.41:3389    rdp-vpn-ti
"""
    linhas = ["TimeCreated,EventID,Computador,Conta,LogonType,IpOrigem"]
    t = INICIO - timedelta(days=1)
    contas = ["ti.patty", "ti.selma", "forn.kwikemart", "forn.duffbeer"]
    for _ in range(260):
        t += timedelta(minutes=rnd.randint(2, 15))
        c = rnd.choice(contas)
        ip = f"10.99.{rnd.randint(1, 20)}.{rnd.randint(2, 250)}"
        linhas.append(f"{t.isoformat()},4624,USINA-JUMP01,{c},10,{ip}")
        if rnd.random() < 0.3:
            linhas.append(f"{t.isoformat()},4624,USINA-FS01,{rnd.choice(FUNCIONARIOS)},3,10.20.{rnd.randint(1, 9)}.{rnd.randint(2, 250)}")
    fora = INICIO - timedelta(hours=4, minutes=13)
    linhas.append(f"{fora.isoformat()},4624,USINA-JUMP02,forn.donutsys,10,198.51.100.140")
    linhas.append(f"{(fora + timedelta(minutes=22)).isoformat()},4624,USINA-JUMP02,forn.donutsys,10,198.51.100.140")
    cab, corpo = linhas[0], sorted(linhas[1:])
    return caso(cid, "RDP publico com fornecedor admin", "analista", "medio",
                """Um fornecedor ganhou acesso "temporario" de area de trabalho remota (RDP, porta 3389) em 2023
e ninguem tirou. O RDP so deveria ser usado pela VPN (rede 10.99.x.x). Voce tem as regras de NAT
do firewall e os logons do Windows (evento **4624**; LogonType **10** = area de trabalho remota).""",
                "Qual conta entrou por RDP vindo direto da internet (de fora da VPN)?",
                "forn.donutsys",
                ["Filtre logons remotos: grep ',10,' logons.csv",
                 "Logons pela VPN vem de 10.99.x.x. Procure um IP que nao comece com 10.",
                 "grep ',10,' logons.csv | grep -v ',10\\.'"],
                ["LogonType 10 = RDP; LogonType 3 = acesso pela rede (compartilhamento, por exemplo).",
                 "RDP aberto para a internet e uma das portas de entrada mais usadas em incidentes.",
                 "Acesso 'temporario' precisa de data para acabar: revise regras de firewall periodicamente.",
                 "Resposta: fechar a regra 12, desabilitar a conta e investigar o que ela fez no USINA-JUMP02."],
                {"nat-firewall.txt": regras, "logons.csv": cab + "\n" + "\n".join(corpo) + "\n"})


@semente
def share_credencial(rnd, cid):
    arquivos = {
        "share/ti/manuais/como-trocar-senha.txt":
            "Para trocar sua senha, aperte Ctrl+Alt+Del e escolha 'Alterar senha'.\n"
            "A senha deve ter 12 caracteres ou mais. Nunca anote sua senha em papel!\n",
        "share/ti/manuais/impressoras.txt": "Impressora do 2o andar: IMP-2A. Toner na sala 204.\n",
        "share/ti/scripts/limpa-temp.bat": "@echo off\r\ndel /q C:\\Windows\\Temp\\*.*\r\n",
        "share/ti/scripts/antigos/mapeia_drives_2019.bat":
            "@echo off\r\nREM script antigo do logon - nao usar mais\r\n"
            "net use S: \\\\usina-fs01\\setores /user:USINA\\svc_impressao D0nut$2019! /persistent:no\r\n"
            "net use P: \\\\usina-fs01\\publico /persistent:no\r\n",
        "share/ti/scripts/inventario.ps1": "Get-ComputerInfo | Select-Object CsName, OsName | Export-Csv inventario.csv\n",
        "share/rh/politica-de-senhas.txt":
            "Politica de senhas da Usina: senha forte, unica e trocada se houver suspeita.\n"
            "Senha nunca vai em script, e-mail ou planilha.\n",
        "share/rh/aniversariantes.csv": "nome,mes\nhomer,maio\nmarge,marco\nlenny,julho\n",
        "share/financeiro/orcamento-2026.csv": "item,valor\ndonuts,999999\nseguranca,12\n",
    }
    for i in range(20):
        arquivos[f"share/publico/fotos-confraternizacao/foto-{i:02d}.txt"] = f"(descricao da foto {i}: alguem comendo donut)\n"
    return caso(cid, "Share com credencial antiga", "analista", "facil",
                """O compartilhamento de rede da usina foi copiado para analise. Um teste de seguranca disse que
"ha uma senha em texto claro no share". Nao da para abrir arquivo por arquivo: procure.
Cuidado: a palavra "senha" aparece em varios manuais que so falam SOBRE senha.""",
                "Em qual arquivo ha uma senha de verdade escrita? (so o nome do arquivo)",
                "mapeia_drives_2019.bat",
                ["Procure em todas as pastas de uma vez: grep -ri senha share/",
                 "Senhas em scripts do Windows costumam aparecer depois de /user: ou password=.",
                 "grep -ri '/user:' share/"],
                ["grep -ri procura em todas as subpastas, ignorando maiusculas.",
                 "Script antigo com senha e muito comum: alguem 'resolve rapido' e esquece la.",
                 "Resposta: trocar a senha da conta svc_impressao na hora e apagar o script.",
                 "Prevencao: cofre de senhas, contas de servico gerenciadas e varredura periodica dos shares."],
                arquivos)


# ===========================================================================
# Chefe de Seguranca (especialista)
# ===========================================================================
@semente
def container_privilegiado(rnd, cid):
    def container(nome, imagem, privilegiado=False, volumes=(), rede="bridge", portas=None):
        return {"Id": "%064x" % rnd.getrandbits(256), "Name": "/" + nome,
                "Config": {"Image": imagem, "User": "" if privilegiado else "app"},
                "HostConfig": {"Privileged": privilegiado, "Binds": list(volumes), "NetworkMode": rede,
                               "CapAdd": None, "PortBindings": portas or {}},
                "State": {"Status": "running"}}
    lista = [
        container("usina-site", "nginx:1.27", volumes=["/srv/site:/usr/share/nginx/html:ro"],
                  portas={"80/tcp": [{"HostPort": "8080"}]}),
        container("cardapio-api", "python:3.12-slim", volumes=["/srv/cardapio:/app:ro"]),
        container("reator-db", "postgres:16", volumes=["reator-dados:/var/lib/postgresql/data"]),
        container("donut-metrics", "docker.io/donutstats/agent:latest", privilegiado=True,
                  volumes=["/:/host", "/var/run/docker.sock:/var/run/docker.sock"], rede="host"),
        container("fila-turnos", "redis:7"),
    ]
    rnd.shuffle(lista)
    ps = "CONTAINER ID   IMAGE                               STATUS       NAMES\n" + "\n".join(
        f"{c['Id'][:12]}   {c['Config']['Image']:<35} Up 3 days    {c['Name'][1:]}" for c in lista) + "\n"
    return caso(cid, "Container privilegiado suspeito", "especialista", "medio",
                """Alguem subiu um container "de metricas" no `usina-docker01` sem passar pela TI. Container
**privilegiado** e com a raiz do servidor montada (`/:/host`) nao isola nada: quem controla o container
controla o servidor inteiro. Voce tem o `docker ps` e o `docker inspect` de todos.""",
                "Qual container roda privilegiado? (o nome, sem a barra /)",
                "donut-metrics",
                ["O docker inspect e um JSON: use o jq.",
                 "Veja o campo HostConfig.Privileged de cada um: jq '.[] | {Name, p: .HostConfig.Privileged}' inspect.json",
                 "jq -r '.[] | select(.HostConfig.Privileged) | .Name' inspect.json"],
                ["Privileged: true desliga o isolamento do container.",
                 "Montar / ou o docker.sock dentro do container tambem entrega o servidor inteiro.",
                 "Imagem :latest de origem desconhecida e outro sinal de alerta: fixe versoes e use imagens confiaveis.",
                 "Resposta: parar o container, descobrir quem subiu e procurar o que ele mudou no servidor."],
                {"docker-ps.txt": ps, "inspect.json": json.dumps(lista, indent=2) + "\n"})


@semente
def psexesvc(rnd, cid):
    hosts = ["FIN-WS01", "FIN-WS02", "FIN-WS05", "USINA-FS01", "USINA-DC01", "USINA-PRINT01"]
    servicos = [("Windows Update Medic Service", "C:\\Windows\\system32\\svchost.exe -k wusvcs"),
                ("Google Update Service", "\"C:\\Program Files (x86)\\Google\\Update\\GoogleUpdate.exe\" /svc"),
                ("Impressora HP Spooler Helper", "C:\\Program Files\\HP\\hpspool.exe"),
                ("Agente de Backup Usina", "C:\\Program Files\\UsinaBackup\\agente.exe")]
    linhas = []
    t = INICIO - timedelta(days=2)
    for _ in range(180):
        t += timedelta(minutes=rnd.randint(5, 40))
        nome, caminho = rnd.choice(servicos)
        linhas.append((t, rnd.choice(hosts), nome, caminho, "LocalSystem"))
    base = INICIO + timedelta(hours=3, minutes=2)
    for atraso, host in ((0, "FIN-WS05"), (13, "USINA-FS01"), (38, "USINA-DC01")):
        linhas.append((base + timedelta(minutes=atraso), host, "PSEXESVC", "%SystemRoot%\\PSEXESVC.exe", "LocalSystem"))
    # Exportado por host (como vem de cada maquina): a ordem do arquivo nao e a ordem do tempo
    linhas.sort(key=lambda l: (l[1], l[0]))
    texto = "TimeCreated,EventID,Computador,NomeDoServico,Arquivo,Conta\n" + "\n".join(
        f"{t.isoformat()},7045,{h},{n},\"{c}\",{conta}" for t, h, n, c, conta in linhas) + "\n"
    return caso(cid, "Movimentacao lateral com PSEXESVC", "especialista", "avancado",
                """Um invasor que entra numa maquina tenta pular para as outras (**movimentacao lateral**).
Uma forma comum no Windows deixa rastro claro: o servico **PSEXESVC** e instalado em cada maquina
alcancada (evento **7045**, "servico instalado"). O arquivo junta os eventos 7045 exportados de cada
maquina, uma depois da outra: a ordem do arquivo NAO e a ordem do tempo.""",
                "Em qual maquina o PSEXESVC apareceu PRIMEIRO? (o nome do computador)",
                "FIN-WS05",
                ["Filtre o servico: grep PSEXESVC servicos.csv",
                 "A primeira coluna e a data no formato ISO: da para ordenar com sort.",
                 "grep PSEXESVC servicos.csv | sort | head -1"],
                ["Evento 7045 (servico novo) e otimo para cacar movimentacao lateral e persistencia.",
                 "Datas ISO (2026-03-14T10:02) ordenam certo com sort: junte fontes e ordene.",
                 "A primeira maquina costuma ser onde o invasor entrou: e ali que a investigacao comeca.",
                 "Resposta: isolar as 3 maquinas, trocar as senhas da conta usada e bloquear SMB entre estacoes."],
                {"servicos.csv": texto})


@semente
def acesso_lsass(rnd, cid):
    suspeito = "C:\\Users\\Public\\Music\\rosquinha.exe"
    normais = [("C:\\ProgramData\\Microsoft\\Windows Defender\\Platform\\4.18.24090-11\\MsMpEng.exe", "0x1000"),
               ("C:\\Windows\\system32\\wininit.exe", "0x1000"),
               ("C:\\Windows\\system32\\svchost.exe", "0x1000"),
               ("C:\\Windows\\system32\\csrss.exe", "0x1000"),
               ("C:\\Windows\\system32\\taskmgr.exe", "0x1400")]
    alvos = ["C:\\Windows\\system32\\svchost.exe", "C:\\Windows\\explorer.exe",
             "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"]
    linhas = []
    t = INICIO - timedelta(hours=6)
    for _ in range(500):
        t += timedelta(seconds=rnd.randint(10, 120))
        if rnd.random() < 0.5:
            origem, acesso = rnd.choice(normais)
            alvo = "C:\\Windows\\system32\\lsass.exe"
        else:
            origem, acesso = rnd.choice(normais)[0], "0x1000"
            alvo = rnd.choice(alvos)
        linhas.append((t, origem, alvo, acesso))
    linhas.append((INICIO - timedelta(hours=1, minutes=46), suspeito, "C:\\Windows\\system32\\lsass.exe", "0x1010"))
    linhas.sort()
    texto = "UtcTime,EventID,Computador,SourceImage,TargetImage,GrantedAccess\n" + "\n".join(
        f"{t.isoformat()},10,FIN-WS05,\"{o}\",\"{a}\",{g}" for t, o, a, g in linhas) + "\n"
    return caso(cid, "Credencial em memoria suspeita", "especialista", "avancado",
                """O **lsass.exe** guarda as credenciais de quem esta logado no Windows. Por isso, programa estranho
lendo a memoria dele e alarme vermelho. O Sysmon registra cada acesso a outro processo (**evento 10**):
quem acessou (SourceImage), quem foi acessado (TargetImage) e com quais permissoes (GrantedAccess).
Antivirus e processos do sistema acessam o lsass o tempo todo: isso e normal.""",
                "Qual programa fora do normal acessou o lsass.exe? (caminho completo)",
                suspeito,
                ["Filtre os acessos ao lsass: grep -i lsass sysmon-10.csv",
                 "Veja so quem acessou (4a coluna), contando: grep -i lsass sysmon-10.csv | cut -d, -f4 | sort | uniq -c",
                 "Programa do sistema mora em C:\\Windows\\system32. Qual aparece so uma vez, numa pasta publica de usuario?"],
                ["Acesso ao lsass por programa desconhecido e sinal classico de roubo de credenciais.",
                 "Pastas como C:\\Users\\Public sao gravaveis por todos: lugar comum para ferramentas de ataque.",
                 "Resposta: isolar a maquina, trocar as senhas de quem logou nela e procurar onde mais o programa aparece.",
                 "Prevencao: protecao do LSA (RunAsPPL), Credential Guard e alertas de evento 10 do Sysmon."],
                {"sysmon-10.csv": texto})


OPERADOR = [("ssh-root-exposto", ssh_root), ("sudo-vim-nopasswd", sudo_vim)]
ANALISTA = [("quem-esta-varrendo", varredura), ("rdp-fornecedor", rdp_fornecedor),
            ("share-credencial-antiga", share_credencial)]
ESPECIALISTA = [("container-privilegiado", container_privilegiado), ("psexesvc-lateral", psexesvc),
                ("credencial-em-memoria", acesso_lsass)]
