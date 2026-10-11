"""Casos extras do Laboratorio Springfield, do nivel 0 (Estagiario) ao 3 (Especialista).

Usado por scripts/gen-lab.py. Cada caso e uma funcao (rnd, caso_id) -> dict e grava suas
evidencias em config/includes.chroot/usr/share/dohsec/lab/casos/<caso_id>/.
Tudo e ficticio: IPs de documentacao (RFC 5737), dominios .test, nenhum binario executavel.
Os casos de metadados e arquivo embutido usam o Pillow (so na hora de gerar).
"""
import base64
import hashlib
import io
import json
import struct
import tarfile
import zipfile
from datetime import datetime, timedelta
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "config/includes.chroot/usr/share/dohsec/lab"
INICIO = datetime(2026, 3, 14, 7, 0, 0)
FUNCIONARIOS = ["homer", "lenny", "carl", "marge", "smithers", "frank.grimes"]


def normaliza(resposta):
    return resposta.strip().strip("'\"").strip().lower()


def hash_resposta(resposta):
    return hashlib.sha256(normaliza(resposta).encode()).hexdigest()


def grava(caso_id, nome, conteudo):
    p = OUT / "casos" / caso_id / nome
    p.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(conteudo, bytes):
        p.write_bytes(conteudo)
    else:
        p.write_text(conteudo, newline="\n")


def caso(caso_id, titulo, trilha, nivel, texto, pergunta, resposta, dicas, aprendizado, arquivos):
    """Grava evidencias + LEIAME e devolve a entrada do casos.json."""
    for nome, conteudo in arquivos.items():
        grava(caso_id, nome, conteudo)
    n = caso_id[:2].lstrip("0")
    lista = "\n".join(f"- `{a}`" for a in arquivos) or "- (nenhum arquivo: use o proprio sistema)"
    grava(caso_id, "LEIAME.md", f"""# {titulo}

{texto}

## Evidencias

{lista}

## Pergunta

{pergunta}

Responda com `lab responder {n} "sua resposta"`. Travou? `lab dica {n}`.
""")
    return {"id": caso_id, "titulo": titulo, "trilha": trilha, "nivel": nivel,
            "pergunta": pergunta, "resposta": hash_resposta(resposta),
            "dicas": dicas, "aprendizado": aprendizado}


# ---------------------------------------------------------------------------
# pcap (Ethernet + IPv4 + UDP), para os casos de trafego
# ---------------------------------------------------------------------------
def _checksum(dados):
    if len(dados) % 2:
        dados += b"\0"
    s = sum(struct.unpack(f"!{len(dados) // 2}H", dados))
    s = (s >> 16) + (s & 0xFFFF)
    s += s >> 16
    return ~s & 0xFFFF


def _ip(endereco):
    return bytes(int(x) for x in endereco.split("."))


def pacote_udp(origem, destino, porta_o, porta_d, carga):
    udp = struct.pack("!HHHH", porta_o, porta_d, 8 + len(carga), 0) + carga
    ip = struct.pack("!BBHHHBBH4s4s", 0x45, 0, 20 + len(udp), 0, 0x4000, 64, 17, 0, _ip(origem), _ip(destino))
    ip = ip[:10] + struct.pack("!H", _checksum(ip)) + ip[12:]
    eth = b"\x02\x00\x00\x00\x00\x01" + b"\x02\x00\x00\x00\x00\x02" + b"\x08\x00"
    return eth + ip + udp


def pcap(pacotes):
    """pacotes: lista de (datetime, bytes)."""
    saida = struct.pack("<IHHiIII", 0xA1B2C3D4, 2, 4, 0, 0, 65535, 1)
    for t, dados in pacotes:
        ts = t.timestamp()
        saida += struct.pack("<IIII", int(ts), int((ts % 1) * 1e6), len(dados), len(dados)) + dados
    return saida


def consulta_dns(ident, nome):
    q = b"".join(bytes([len(p)]) + p.encode() for p in nome.split(".")) + b"\0"
    return struct.pack("!HHHHHH", ident, 0x0100, 1, 0, 0, 0) + q + struct.pack("!HH", 1, 1)


# ===========================================================================
# Nivel 0: Estagiario
# ===========================================================================
def e_manual(rnd, cid):
    return caso(cid, "Lendo o manual", "estagiario", "basico",
                """Todo comando do Linux tem manual. Ninguem decora tudo: a gente consulta.

| Comando | O que faz |
| --- | --- |
| `man ls` | abre o manual do ls (setas rolam, q sai) |
| `/palavra` | dentro do man, procura a palavra (n vai para a proxima) |
| `ls --help` | ajuda curta, direto no terminal |""",
                "Qual opcao do `ls` ordena os arquivos pelo tamanho, do maior para o menor?",
                "-S",
                ["Abra o manual: man ls", "Dentro do man, digite /size e aperte Enter.",
                 "E uma letra maiuscula depois do traco."],
                ["man COMANDO abre o manual completo; COMANDO --help mostra um resumo.",
                 "Dentro do man, / procura e q sai.",
                 "Na duvida, o manual responde: e o primeiro lugar para olhar."], {})


def e_find(rnd, cid):
    arquivos = {}
    for ano in (2019, 2020, 2021):
        for mes in ("janeiro", "marco", "julho", "outubro"):
            for cx in range(1, 4):
                base = f"arquivo-morto/{ano}/{mes}/caixa-{cx}"
                arquivos[f"{base}/inventario.txt"] = f"Caixa {cx} de {mes}/{ano}: papeis do RH.\n"
    arquivos["arquivo-morto/2020/julho/caixa-2/.planta-do-reator.bak"] = "Copia antiga da planta do reator.\n"
    return caso(cid, "Achando arquivos com find", "estagiario", "basico",
                """Quando nao sabemos onde um arquivo esta, o `find` procura pasta por pasta.

| Comando | O que faz |
| --- | --- |
| `find PASTA -name 'nome'` | procura pelo nome |
| `find PASTA -name '*.bak'` | o * vale qualquer coisa: todos os .bak |
| `find PASTA -type f` | so arquivos (sem pastas) |
| `tree PASTA` | mostra a arvore de pastas |""",
                "Ha um arquivo de backup (`.bak`) perdido no `arquivo-morto`. Qual o nome dele?",
                ".planta-do-reator.bak",
                ["Tente: find arquivo-morto -name '*.bak'",
                 "O nome comeca com ponto: e um arquivo escondido.",
                 "A resposta e so o nome do arquivo, com o ponto do inicio."],
                ["find procura em todas as subpastas de uma vez.",
                 "-name com * acha padroes como *.bak, *.log, *.conf.",
                 "Backups esquecidos (.bak, .old) sao alvo comum de invasores: vale procurar."], arquivos)


def e_tar(rnd, cid):
    interno = io.BytesIO()
    with tarfile.open(fileobj=interno, mode="w") as t:
        dados = b"Lacre aberto! Palavra-chave: casquinha-de-chocolate\n"
        info = tarfile.TarInfo("lacre/bilhete.txt")
        info.size = len(dados)
        t.addfile(info, io.BytesIO(dados))
    externo = io.BytesIO()
    with tarfile.open(fileobj=externo, mode="w:gz") as t:
        info = tarfile.TarInfo("caixa/lacre.tar")
        info.size = len(interno.getvalue())
        t.addfile(info, io.BytesIO(interno.getvalue()))
    return caso(cid, "Abrindo pacotes com tar", "estagiario", "basico",
                """Arquivos chegam empacotados e comprimidos. O `tar` empacota e desempacota.

| Comando | O que faz |
| --- | --- |
| `tar -tzf arq.tar.gz` | lista o conteudo de um .tar.gz sem extrair |
| `tar -xzf arq.tar.gz` | extrai um .tar.gz |
| `tar -xf arq.tar` | extrai um .tar (sem compressao) |""",
                "Dentro da `caixa.tar.gz` tem outro pacote lacrado. Qual a palavra-chave do bilhete la dentro?",
                "casquinha-de-chocolate",
                ["Veja o que tem dentro: tar -tzf caixa.tar.gz",
                 "Extraia: tar -xzf caixa.tar.gz e depois entre em caixa/",
                 "O lacre.tar e outro pacote: tar -xf caixa/lacre.tar"],
                ["tar -t lista, tar -x extrai; o z cuida da compressao gzip.",
                 "Pacotes podem ter pacotes dentro: va abrindo camada por camada.",
                 "Liste antes de extrair: evita espalhar arquivos onde voce nao queria."],
                {"caixa.tar.gz": externo.getvalue()})


ESTAGIARIO = [("lendo-o-manual", e_manual), ("achando-com-find", e_find), ("abrindo-pacotes", e_tar)]


# ===========================================================================
# Nivel 1: Operador
# ===========================================================================
def o_quem_sou(rnd, cid):
    return caso(cid, "Quem sou eu?", "operador", "facil",
                """Todo usuario tem um numero (UID). O sistema decide o que voce pode fazer por ele.

| Comando | O que faz |
| --- | --- |
| `whoami` | seu nome de usuario |
| `id` | seu UID, seu grupo principal e todos os grupos |
| `groups` | so os grupos |""",
                "Qual e o UID (numero) do seu usuario neste sistema?",
                "1000",
                ["Rode: id", "O UID aparece logo no comeco: uid=NUMERO(nome)"],
                ["id mostra quem voce e para o sistema: UID e grupos.",
                 "UID 0 e o root (administrador); usuarios comuns comecam em 1000.",
                 "Os grupos (como sudo e adm) definem poderes extras."], {})


def o_ls_l(rnd, cid):
    listagem = """total 28
-rw-r----- 1 smithers rh       2210 mar 14 07:12 folha-de-pagamento.csv
-rw-r--r-- 1 lenny    usina     812 mar 14 07:30 cardapio.txt
-rwxr-x--- 1 root     operacao 4096 mar 13 22:01 desliga-reator.sh
-rw-rw-rw- 1 carl     usina    1540 mar 14 06:55 senhas-wifi.txt
-rw------- 1 burns    burns     990 mar 12 18:40 diario-secreto.txt
-rw-r--r-- 1 homer    usina     120 mar 14 08:02 lista-de-donuts.txt
"""
    return caso(cid, "Lendo permissoes com ls -l", "operador", "facil",
                """O `ls -l` mostra quem pode ler (r), escrever (w) e executar (x) cada arquivo,
em tres grupos de letras: **dono**, **grupo** e **todo mundo**.

Exemplo: `-rw-r-----` = dono le e escreve, grupo so le, os outros nada.""",
                "Qual arquivo da listagem **qualquer pessoa** do sistema pode alterar?",
                "senhas-wifi.txt",
                ["Olhe o ultimo trio de letras de cada linha (os 'outros').",
                 "Procure um w no ultimo trio: rw-rw-rw-"],
                ["As permissoes vem em 3 trios: dono, grupo, outros.",
                 "w no trio dos outros = qualquer um altera: quase sempre um erro.",
                 "Arquivo de senha legivel ou alteravel por todos e incidente na certa."],
                {"listagem.txt": listagem})


def o_chmod(rnd, cid):
    script = f"""#!/bin/bash
# Abre o cofre de donuts da usina
echo "Cofre aberto! Codigo: $(echo {base64.b64encode(b'doh-742').decode()} | base64 -d)"
"""
    return caso(cid, "Dando permissao com chmod", "operador", "facil",
                """Para rodar um script como programa, ele precisa da permissao de execucao (x).

| Comando | O que faz |
| --- | --- |
| `ls -l arq` | mostra as permissoes |
| `chmod +x arq` | da permissao de execucao |
| `./arq` | roda o programa que esta nesta pasta |""",
                "Rode o `abre-cofre.sh`. Qual codigo o cofre mostra?",
                "doh-742",
                ["Tente rodar: ./abre-cofre.sh (vai dar permissao negada)",
                 "De permissao de execucao: chmod +x abre-cofre.sh",
                 "Agora sim: ./abre-cofre.sh"],
                ["chmod +x torna um arquivo executavel; chmod -x tira.",
                 "./ diz: rode o programa desta pasta.",
                 "Antes de rodar um script desconhecido, leia o conteudo (cat ou less)."],
                {"abre-cofre.sh": script})


def o_hash(rnd, cid):
    arquivos = {}
    verdadeiro = None
    for v in range(1, 13):
        dados = bytes(rnd.getrandbits(8) for _ in range(4096))
        nome = f"downloads/atualizacao-reator-v{v}.bin"
        arquivos[nome] = dados
        if v == 9:
            verdadeiro = hashlib.sha256(dados).hexdigest()
    arquivos["site-oficial.txt"] = (f"Atualizacao oficial do controle do reator\n"
                                    f"SHA256: {verdadeiro}\n")
    return caso(cid, "Conferindo hash", "operador", "facil",
                """Um hash e a impressao digital de um arquivo: mudou um bit, muda o hash inteiro.
Sites oficiais publicam o hash para voce conferir o que baixou.

| Comando | O que faz |
| --- | --- |
| `sha256sum arq` | calcula o hash SHA-256 |
| `sha256sum pasta/*` | calcula de todos |""",
                "Varias versoes da atualizacao foram baixadas de sites diferentes. Qual arquivo bate com o hash oficial?",
                "atualizacao-reator-v9.bin",
                ["Veja o hash oficial: cat site-oficial.txt",
                 "Calcule todos: sha256sum downloads/*",
                 "Filtre pelo comeco do hash oficial: sha256sum downloads/* | grep PRIMEIROS-CARACTERES"],
                ["sha256sum confere se o arquivo e exatamente o publicado.",
                 "Arquivo de fonte estranha com hash diferente: nao instale.",
                 "Hash tambem identifica malware conhecido em listas de inteligencia."], arquivos)


def o_file(rnd, cid):
    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, "w") as z:
        z.writestr("dentro.txt", "Nao era uma imagem.\n")
    arquivos = {
        "anexos/relatorio.pdf": b"%PDF-1.4\n% relatorio de turno\n%%EOF\n",
        "anexos/foto-do-turno.jpg": b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00" + bytes(64),
        "anexos/apresentacao.png": zip_buf.getvalue(),
        "anexos/musica-do-intervalo.mp3": b"ID3\x04\x00\x00\x00\x00\x00\x00" + bytes(64),
        "anexos/notas.txt": "Reuniao as 15h.\n",
    }
    return caso(cid, "Extensao mente, conteudo nao", "operador", "facil",
                """A extensao (.jpg, .pdf) e so parte do nome: qualquer um muda. O comando `file`
olha o conteudo de verdade (os primeiros bytes, a 'assinatura').

| Comando | O que faz |
| --- | --- |
| `file arq` | diz o tipo real |
| `file pasta/*` | de todos |
| `xxd arq \\| head` | mostra os bytes em hexadecimal |""",
                "Um dos anexos esta disfarcado: na verdade e um arquivo ZIP. Qual?",
                "apresentacao.png",
                ["Rode: file anexos/*", "Procure 'Zip archive' na saida."],
                ["file identifica o tipo pelo conteudo, nao pelo nome.",
                 "Golpes disfarcam arquivos (o caso do invoice_real.pdf.exe e parecido).",
                 "xxd mostra a assinatura: ZIP comeca com PK, PDF com %PDF."], arquivos)


def o_strings(rnd, cid):
    blob = bytearray(rnd.getrandbits(8) for _ in range(20000))
    segredo = b"SENHA_PADRAO=rosquinha123\0"
    blob[12345:12345 + len(segredo)] = segredo
    blob[3000:3000 + 18] = b"VERSAO=4.25.1998\0\0"
    return caso(cid, "Achando texto com strings", "operador", "medio",
                """Arquivos binarios (programas, firmwares) tem texto escondido no meio dos bytes:
mensagens, versoes e, as vezes, senhas esquecidas pelo fabricante.

| Comando | O que faz |
| --- | --- |
| `strings arq` | mostra os trechos de texto legivel |
| `strings arq \\| grep -i senha` | so os que interessam |""",
                "O firmware do painel do reator tem uma senha padrao embutida. Qual e?",
                "rosquinha123",
                ["Rode: strings firmware-painel.bin", "Filtre: strings firmware-painel.bin | grep -i senha"],
                ["strings acha texto dentro de qualquer arquivo binario.",
                 "Senha padrao embutida em firmware e falha classica de fabricante.",
                 "Troque sempre a senha padrao de equipamentos novos."],
                {"firmware-painel.bin": bytes(blob)})


def o_sudo(rnd, cid):
    linhas = []
    t = INICIO - timedelta(hours=5)
    comandos = ["/usr/bin/apt update", "/usr/bin/systemctl restart nginx", "/usr/bin/journalctl -u reator",
                "/usr/bin/tail /var/log/syslog", "/usr/sbin/ufw status"]
    for _ in range(140):
        t += timedelta(minutes=rnd.randint(1, 6))
        u = rnd.choice(["homer", "carl", "smithers"])
        linhas.append(f"{t:%b %d %H:%M:%S} usina-srv01 sudo: {u:>9} : TTY=pts/{rnd.randint(0, 4)} ; "
                      f"PWD=/home/{u} ; USER=root ; COMMAND={rnd.choice(comandos)}")
    t_suspeito = INICIO - timedelta(hours=3, minutes=48)
    linhas.insert(40, f"{t_suspeito:%b %d %H:%M:%S} usina-srv01 sudo:     lenny : TTY=pts/7 ; "
                      f"PWD=/tmp ; USER=root ; COMMAND=/usr/bin/cat /etc/shadow")
    linhas.sort(key=lambda l: datetime.strptime("2026 " + l[:15], "%Y %b %d %H:%M:%S"))
    return caso(cid, "O que fizeram com sudo?", "operador", "medio",
                """Tudo que alguem roda com `sudo` fica registrado: quem, quando, onde e o comando.
Isso esta no log de autenticacao (`/var/log/auth.log` ou `journalctl`).""",
                "De madrugada alguem leu um arquivo sensivel com sudo. Qual arquivo?",
                "/etc/shadow",
                ["Filtre os comandos: grep COMMAND auth.log",
                 "Procure algo fora da rotina (o lenny nem costuma usar sudo).",
                 "A resposta e o caminho do arquivo lido."],
                ["Todo uso de sudo fica no log: grep COMMAND ou journalctl _COMM=sudo.",
                 "/etc/shadow guarda os hashes de senha: le-lo e sinal de ataque.",
                 "Revise quem esta no grupo sudo e alerte uso fora do horario."],
                {"auth.log": "\n".join(linhas) + "\n"})


def o_cron(rnd, cid):
    cron = """# crontab -l -u root  (usina-srv01)
# m  h  dom mon dow  comando
*/5  *  *   *   *    /usr/local/sbin/coleta-sensores.sh
0    6  *   *   1-5  /usr/local/sbin/relatorio-turno.sh
30   2  *   *   *    /usr/local/sbin/backup-reator.sh
15   23 1   *   *    /usr/local/sbin/limpa-logs.sh
"""
    return caso(cid, "Lendo o agendador (cron)", "operador", "facil",
                """O cron roda tarefas no horario marcado. Cada linha tem 5 campos de tempo e o comando:
**minuto hora dia-do-mes mes dia-da-semana**. `*` = todos; `*/5` = a cada 5.""",
                "A que horas roda o backup do reator? Responda no formato HH:MM.",
                "02:30",
                ["Ache a linha do backup-reator.sh.", "O primeiro numero e o minuto, o segundo e a hora."],
                ["Os 5 campos do cron: minuto, hora, dia do mes, mes, dia da semana.",
                 "crontab -l lista as tarefas do usuario; /etc/cron.* tem as do sistema.",
                 "Invasores adoram cron para persistencia (lembra do donutcoin?)."],
                {"crontab.txt": cron})


def o_servico(rnd, cid):
    linhas = []
    t = INICIO
    servicos = ["ssh.service", "cron.service", "nginx.service", "sensores.service", "resfriamento.service"]
    for _ in range(200):
        t += timedelta(seconds=rnd.randint(5, 90))
        s = rnd.choice(servicos)
        linhas.append(f"{t:%b %d %H:%M:%S} usina-srv01 systemd[1]: {rnd.choice(['Started', 'Reloaded'])} {s}.")
    t_falha = INICIO + timedelta(hours=1, minutes=17)
    falha = [f"{t_falha:%b %d %H:%M:%S} usina-srv01 systemd[1]: resfriamento.service: Main process exited, code=exited, status=1/FAILURE",
             f"{t_falha:%b %d %H:%M:%S} usina-srv01 systemd[1]: resfriamento.service: Failed with result 'exit-code'."]
    linhas[90:90] = falha
    return caso(cid, "Qual servico caiu?", "operador", "facil",
                """Servicos sao programas que rodam em segundo plano, gerenciados pelo `systemctl`.
Quando um cai, o `journalctl` registra.

| Comando | O que faz |
| --- | --- |
| `systemctl status SERVICO` | estado de um servico |
| `systemctl --failed` | servicos que falharam |
| `journalctl -u SERVICO` | log de um servico |""",
                "O alarme de temperatura disparou. Qual servico falhou? (nome completo, com .service)",
                "resfriamento.service",
                ["Procure a palavra Failed: grep -i failed journal.txt"],
                ["systemctl --failed lista os servicos que cairam.",
                 "journalctl -u NOME mostra o historico de um servico.",
                 "Na vida real: grep -i failed e o primeiro passo em incidente de disponibilidade."],
                {"journal.txt": "\n".join(linhas) + "\n"})


def o_porta(rnd, cid):
    ss = """State  Recv-Q Send-Q Local Address:Port  Peer Address:Port Process
LISTEN 0      128          0.0.0.0:22         0.0.0.0:*     users:(("sshd",pid=911,fd=3))
LISTEN 0      511          0.0.0.0:80         0.0.0.0:*     users:(("nginx",pid=1204,fd=6))
LISTEN 0      511          0.0.0.0:443        0.0.0.0:*     users:(("nginx",pid=1204,fd=7))
LISTEN 0      244        127.0.0.1:5432       0.0.0.0:*     users:(("postgres",pid=1301,fd=5))
LISTEN 0      5            0.0.0.0:31337      0.0.0.0:*     users:(("kworker-donut",pid=6672,fd=3))
LISTEN 0      4096       127.0.0.1:9100       0.0.0.0:*     users:(("node_exporter",pid=1410,fd=3))
"""
    inventario = """Portas autorizadas no usina-web01
22   ssh (administracao)
80   http (site)
443  https (site)
5432 postgres (so local)
9100 monitoramento (so local)
"""
    return caso(cid, "Porta que nao deveria estar aberta", "operador", "medio",
                """Programas que esperam conexoes 'escutam' numa porta. O `ss` mostra quais.

| Comando | O que faz |
| --- | --- |
| `ss -tlnp` | portas TCP escutando, com o programa |
| `ss -tunap` | todas as conexoes |""",
                "Compare as portas escutando com o inventario autorizado. Qual porta esta sobrando?",
                "31337",
                ["Liste as portas da coluna Local Address:Port.",
                 "Compare com inventario.txt: qual nao esta la?"],
                ["ss -tlnp mostra o que escuta e qual programa.",
                 "Porta aberta sem dono no inventario: investigue o processo.",
                 "Inventario de portas autorizadas e a base de qualquer auditoria."],
                {"ss-tlnp.txt": ss, "inventario.txt": inventario})


def o_which(rnd, cid):
    return caso(cid, "Qual programa roda de verdade?", "operador", "facil",
                """Quando voce digita um comando, o sistema procura o programa nas pastas do `PATH`,
na ordem. Invasores tentam colocar um programa falso antes do verdadeiro.

| Comando | O que faz |
| --- | --- |
| `echo $PATH` | mostra as pastas, na ordem |
| `which ls` | qual arquivo roda quando voce digita ls |
| `type ls` | idem, e avisa se e alias |""",
                "Neste sistema, qual arquivo (caminho completo) roda quando voce digita `ls`?",
                "/usr/bin/ls",
                ["Rode: which ls", "Se aparecer um alias, use: type -a ls"],
                ["O PATH define onde o sistema procura os comandos, na ordem.",
                 "which e type mostram qual programa vai rodar de fato.",
                 "Pasta gravavel no comeco do PATH e porta para programa falso."], {})


OPERADOR = [("quem-sou-eu", o_quem_sou), ("lendo-permissoes", o_ls_l), ("chmod-cofre", o_chmod),
            ("conferindo-hash", o_hash), ("extensao-mente", o_file), ("strings-firmware", o_strings),
            ("sudo-de-madrugada", o_sudo), ("lendo-o-cron", o_cron), ("servico-caiu", o_servico),
            ("porta-sobrando", o_porta), ("qual-programa-roda", o_which)]


# ===========================================================================
# Nivel 2: Analista SOC
# ===========================================================================
def a_jq(rnd, cid):
    eventos = []
    t = INICIO
    acoes = ["ListarArquivos", "LerConfiguracao", "Login", "BaixarRelatorio", "CriarUsuario"]
    for _ in range(400):
        t += timedelta(seconds=rnd.randint(5, 60))
        eventos.append({"hora": t.isoformat(), "usuario": rnd.choice(FUNCIONARIOS),
                        "ip": f"10.20.{rnd.randint(1, 9)}.{rnd.randint(2, 250)}",
                        "evento": rnd.choice(acoes), "resultado": "sucesso"})
    eventos.insert(311, {"hora": eventos[311]["hora"], "usuario": "svc_backup", "ip": "198.51.100.200",
                         "evento": "ApagarBackup", "resultado": "sucesso"})
    return caso(cid, "Eventos em JSON com jq", "analista", "medio",
                """Sistemas de nuvem e de seguranca registram eventos em JSON, um por linha.
O `jq` filtra e formata JSON no terminal.

| Comando | O que faz |
| --- | --- |
| `jq . arq.json` | mostra formatado |
| `jq -c 'select(.evento=="X")' arq.json` | so os eventos X |
| `jq -r '.ip' arq.json` | so o campo ip |""",
                "Alguem apagou os backups da usina na nuvem. De qual IP veio o evento ApagarBackup?",
                "198.51.100.200",
                ["Filtre: jq -c 'select(.evento==\"ApagarBackup\")' eventos.json",
                 "O IP esta no campo ip."],
                ["jq e o grep do JSON: select filtra, .campo extrai.",
                 "Apagar backup e passo tipico antes de ransomware.",
                 "Conta de servico usada de IP externo merece alerta imediato."],
                {"eventos.json": "\n".join(json.dumps(e) for e in eventos) + "\n"})


def a_pcap_dns(rnd, cid):
    pacotes = []
    t = INICIO
    normais = ["usina-springfield.test", "intranet.usina-springfield.test", "atualizacoes.debian.test",
               "mail.usina-springfield.test", "cdn.donuts.test"]
    for i in range(300):
        t += timedelta(seconds=rnd.uniform(0.2, 3))
        nome = rnd.choice(normais)
        if i % 9 == 4:
            pedaco = base64.b32encode(bytes(rnd.getrandbits(8) for _ in range(20))).decode().strip("=").lower()
            nome = f"{pedaco}.dados.donut-cloud.test"
        pacotes.append((t, pacote_udp(f"10.20.3.{rnd.choice([14, 15, 77])}", "10.20.0.2",
                                      rnd.randint(30000, 60000), 53, consulta_dns(i, nome))))
    return caso(cid, "Vazamento por DNS", "analista", "avancado",
                """DNS traduz nomes em IPs e quase nunca e bloqueado. Por isso invasores escondem
dados dentro dos nomes consultados (subdominios longos e sem sentido).

| Comando | O que faz |
| --- | --- |
| `tshark -r arq.pcap` | lista os pacotes de uma captura |
| `tshark -r arq.pcap -Y dns -T fields -e dns.qry.name` | so os nomes consultados |
| `wireshark arq.pcap` | abre a captura na interface grafica |""",
                "A captura mostra consultas DNS estranhas. Para qual dominio os dados estao sendo enviados? (so o dominio principal, sem os subdominios)",
                "donut-cloud.test",
                ["Liste os nomes: tshark -r dns.pcap -Y dns -T fields -e dns.qry.name",
                 "Junte com sort | uniq -c para ver os repetidos e os estranhos.",
                 "Os nomes estranhos terminam todos no mesmo dominio. Responda so ele (ex.: exemplo.test)."],
                ["tshark e o Wireshark no terminal: -Y filtra, -T fields extrai campos.",
                 "Subdominios longos e aleatorios = sinal de exfiltracao ou tunel por DNS.",
                 "Monitore volume e tamanho das consultas DNS por maquina."],
                {"dns.pcap": pcap(pacotes)})


def a_pcap_conversa(rnd, cid):
    pacotes = []
    t = INICIO
    maquinas = [f"10.20.4.{n}" for n in (11, 12, 13, 21, 22, 30)]
    for _ in range(400):
        t += timedelta(seconds=rnd.uniform(0.1, 2))
        pacotes.append((t, pacote_udp(rnd.choice(maquinas), rnd.choice(["10.20.0.2", "10.20.0.5"]),
                                      rnd.randint(30000, 60000), rnd.choice([53, 123, 514]), b"rotina")))
    for _ in range(90):
        t += timedelta(seconds=rnd.uniform(0.1, 2))
        pacotes.append((t, pacote_udp("10.20.4.22", "203.0.113.66", 40000, 8443, bytes(400))))
    for _ in range(6):
        t += timedelta(seconds=rnd.uniform(0.1, 2))
        pacotes.append((t, pacote_udp("10.20.4.13", "203.0.113.66", 40001, 8443, bytes(40))))
    pacotes.sort(key=lambda p: p[0])
    return caso(cid, "Quem mais fala com o servidor suspeito?", "analista", "medio",
                """O tshark tem estatisticas prontas: quem conversou com quem e quanto.

| Comando | O que faz |
| --- | --- |
| `tshark -r arq.pcap -q -z conv,ip` | conversas por par de IPs |
| `tshark -r arq.pcap -Y 'ip.dst==X'` | so pacotes para o IP X |""",
                "O IP externo 203.0.113.66 esta na lista de ameacas. Qual maquina interna enviou mais dados para ele?",
                "10.20.4.22",
                ["Veja as conversas: tshark -r rede.pcap -q -z conv,ip",
                 "Procure as linhas com 203.0.113.66 e compare os bytes."],
                ["-z conv,ip resume quem falou com quem e quanto.",
                 "Muito dado saindo para IP de ameaca = possivel vazamento.",
                 "Isole a maquina e investigue o processo que gerou o trafego."],
                {"rede.pcap": pcap(pacotes)})


def a_yara(rnd, cid):
    arquivos = {}
    for i in range(1, 11):
        txt = f"Relatorio {i} da usina. " + " ".join(rnd.choice(["reator", "turno", "donut", "sensor"]) for _ in range(200))
        arquivos[f"amostras/arquivo-{i:02d}.dat"] = txt.encode()
    arquivos["amostras/arquivo-07.dat"] = b"Relatorio 7. " + b"DOH!" + b" ... DONUT_RANSOM: seus arquivos foram trancados ..." + bytes(300)
    regra = """rule DonutRansom
{
    meta:
        descricao = "Nota de resgate do grupo Donut"
    strings:
        $nota = "DONUT_RANSOM"
        $marca = { 44 4F 48 21 }   // "DOH!" em hexadecimal
    condition:
        $nota and $marca
}
"""
    arquivos["donut.yar"] = regra
    return caso(cid, "Cacando com regras YARA", "analista", "medio",
                """YARA descreve 'cara de malware' em regras: textos e bytes que precisam aparecer.
Equipes de seguranca do mundo todo compartilham regras assim.

| Comando | O que faz |
| --- | --- |
| `cat regra.yar` | le a regra |
| `yara regra.yar pasta/` | testa todos os arquivos da pasta |
| `yara -s regra.yar arq` | mostra onde bateu |""",
                "Use a regra `donut.yar` nas amostras. Qual arquivo bate com a regra?",
                "arquivo-07.dat",
                ["Leia a regra: cat donut.yar", "Rode: yara donut.yar amostras/"],
                ["Uma regra YARA junta strings e uma condicao.",
                 "yara -s mostra exatamente quais strings bateram.",
                 "Regras publicas (de CERTs e fabricantes) ajudam a achar ameacas conhecidas."], arquivos)


def _access_log(rnd, n, extra):
    linhas = []
    t = INICIO
    paginas = ["/", "/sobre", "/contato", "/noticias", "/img/logo.png", "/css/site.css", "/vagas"]
    for _ in range(n):
        t += timedelta(seconds=rnd.randint(1, 30))
        ip = f"203.0.113.{rnd.randint(2, 250)}"
        pag = rnd.choice(paginas)
        linhas.append(f'{ip} - - [{t:%d/%b/%Y:%H:%M:%S} -0300] "GET {pag} HTTP/1.1" 200 '
                      f'{rnd.randint(300, 9000)} "-" "Mozilla/5.0"')
    for pos, linha in extra:
        linhas.insert(pos, linha)
    return "\n".join(linhas) + "\n"


def a_sqli(rnd, cid):
    atacante = "198.51.100.45"
    extra = [(700 + k, f'{atacante} - - [14/Mar/2026:11:{10 + k:02d}:00 -0300] '
                       f'"GET /noticias?id=7%27%20UNION%20SELECT%20usuario,senha%20FROM%20contas--{k} HTTP/1.1" '
                       f'500 312 "-" "sqlmap/1.8"') for k in range(6)]
    return caso(cid, "Tentativa de SQL injection", "analista", "medio",
                """O log do servidor web registra cada pedido: IP, hora, pagina e resultado.
Ataques a banco de dados deixam rastros como `UNION SELECT` na URL (as vezes codificados, %20 = espaco).""",
                "Alguem tentou roubar dados do banco pelo site. Qual IP?",
                atacante,
                ["Procure: grep -i 'union' access.log", "O IP e o primeiro campo da linha."],
                ["Logs web mostram tentativas de injecao direto na URL.",
                 "%20 e %27 sao espaco e aspas codificados: decodifique mentalmente.",
                 "Defesa: consultas parametrizadas no codigo e um WAF na frente."],
                {"access.log": _access_log(rnd, 1500, extra)})


def a_exfil_web(rnd, cid):
    extra = [(900, '203.0.113.99 - - [14/Mar/2026:13:44:10 -0300] "GET /backup/clientes.sql HTTP/1.1" '
                   '200 48273911 "-" "curl/8.5"')]
    return caso(cid, "O maior download do dia", "analista", "medio",
                """O decimo campo do log web e o tamanho da resposta em bytes. Downloads enormes e
fora do padrao merecem atencao.

| Comando | O que faz |
| --- | --- |
| `awk '{print $10, $7}' access.log` | tamanho e pagina de cada pedido |
| `sort -n` | ordena por numero |
| `tail -1` | fica com o ultimo (o maior) |""",
                "Qual arquivo (caminho na URL) foi o maior download do dia?",
                "/backup/clientes.sql",
                ["Extraia tamanho e pagina: awk '{print $10, $7}' access.log",
                 "Ordene: ... | sort -n | tail -3"],
                ["awk separa colunas por espaco: $1, $7, $10...",
                 "Pasta de backup acessivel pela web e falha grave de configuracao.",
                 "Alertar por volume de saida pega vazamentos que passam por outros filtros."],
                {"access.log": _access_log(rnd, 1500, extra)})


def a_suricata(rnd, cid):
    assinaturas = [(2001219, "ET SCAN Potential SSH Scan"), (2013028, "ET POLICY curl User-Agent Outbound"),
                   (2027865, "ET INFO Observed DNS Query to .cloud TLD"), (2210054, "SURICATA STREAM excessive retransmissions")]
    pesos = [5, 2, 3, 1]
    eventos = []
    t = INICIO
    for _ in range(250):
        t += timedelta(seconds=rnd.randint(5, 120))
        sid, msg = rnd.choices(assinaturas, weights=pesos)[0]
        eventos.append({"timestamp": t.isoformat(), "event_type": "alert",
                        "src_ip": f"198.51.100.{rnd.randint(2, 250)}", "dest_ip": "10.20.5.14",
                        "alert": {"signature_id": sid, "signature": msg, "severity": 2}})
        if rnd.random() < 0.3:
            eventos.append({"timestamp": t.isoformat(), "event_type": "flow", "src_ip": "10.20.5.14"})
    contagem = {}
    for e in eventos:
        if e["event_type"] == "alert":
            contagem[e["alert"]["signature_id"]] = contagem.get(e["alert"]["signature_id"], 0) + 1
    mais = max(contagem, key=contagem.get)
    return caso(cid, "Alertas do Suricata", "analista", "avancado",
                """O Suricata e um IDS: olha o trafego e gera alertas quando bate com uma regra.
Ele grava tudo em `eve.json` (um JSON por linha).""",
                "Qual alerta (signature_id) mais disparou contra o servidor?",
                str(mais),
                ["So os alertas: jq -c 'select(.event_type==\"alert\")' eve.json",
                 "Extraia o id: jq -r 'select(.event_type==\"alert\") | .alert.signature_id' eve.json",
                 "Conte: ... | sort | uniq -c | sort -rn | head -1"],
                ["O eve.json do Suricata e lido com jq como qualquer JSON.",
                 "A receita sort | uniq -c | sort -rn funciona em qualquer campo.",
                 "Varredura de SSH em massa: bloqueie, use chave e fail2ban."],
                {"eve.json": "\n".join(json.dumps(e) for e in eventos) + "\n"})


ANALISTA = [("eventos-com-jq", a_jq), ("vazamento-por-dns", a_pcap_dns), ("conversa-suspeita", a_pcap_conversa),
            ("regras-yara", a_yara), ("sql-injection", a_sqli), ("maior-download", a_exfil_web),
            ("alertas-suricata", a_suricata)]


# ===========================================================================
# Nivel 3: Especialista
# ===========================================================================
def s_exif(rnd, cid):
    from PIL import Image
    img = Image.new("RGB", (320, 200), (255, 216, 77))
    exif = Image.Exif()
    exif[0x010E] = "Cracha provisorio - sala de controle"
    exif[0x013B] = "waylon.smithers"
    exif[0x0131] = "Camera da Usina v2"
    exif[0x0132] = "2026:03:13 23:58:12"
    buf = io.BytesIO()
    img.save(buf, "JPEG", exif=exif.tobytes())
    return caso(cid, "Metadados com exiftool", "especialista", "medio",
                """Fotos e documentos carregam metadados: autor, programa, data, as vezes GPS.
Isso ajuda (e muito) a descobrir de onde algo veio.

| Comando | O que faz |
| --- | --- |
| `exiftool arq` | mostra todos os metadados |
| `exiftool -Artist arq` | so o autor |""",
                "Uma foto de cracha falso apareceu na sala de controle. Quem consta como autor (Artist) da foto?",
                "waylon.smithers",
                ["Rode: exiftool foto-cracha.jpg", "Procure o campo Artist."],
                ["exiftool le metadados de fotos, PDFs, documentos do Office...",
                 "Data e autor nos metadados ajudam a montar a linha do tempo.",
                 "Antes de publicar arquivos, limpe os metadados (exiftool -all= arq)."],
                {"foto-cracha.jpg": buf.getvalue()})


def s_binwalk(rnd, cid):
    from PIL import Image
    img = Image.new("RGB", (240, 120), (47, 125, 246))
    buf = io.BytesIO()
    img.save(buf, "PNG")
    z = io.BytesIO()
    with zipfile.ZipFile(z, "w") as zf:
        zf.writestr("codigo.txt", "Codigo de acesso ao setor: reator-7G\n")
    return caso(cid, "Arquivo escondido dentro da imagem", "especialista", "avancado",
                """Da para 'colar' um arquivo no fim de outro: a imagem abre normal, mas carrega um
segredo. O `binwalk` procura assinaturas de arquivos dentro de arquivos.

| Comando | O que faz |
| --- | --- |
| `binwalk arq` | lista o que tem dentro e em que posicao |
| `binwalk -e arq` | extrai o que achar |
| `unzip -l arq` | lista um zip (mesmo com dados antes) |""",
                "O logo do site da usina esta maior do que deveria. Qual codigo de acesso esta escondido nele?",
                "reator-7G",
                ["Veja o que tem dentro: binwalk logo-usina.png",
                 "Tem um Zip depois do PNG. Extraia: binwalk -e logo-usina.png (ou unzip logo-usina.png)",
                 "Leia o codigo.txt extraido."],
                ["binwalk acha arquivos embutidos pelas assinaturas.",
                 "Tamanho fora do normal e a primeira pista de dado escondido.",
                 "Tecnica usada para vazar dados e esconder ferramentas: fique de olho."],
                {"logo-usina.png": buf.getvalue() + z.getvalue()})


def s_aide(rnd, cid):
    relatorio = """Start timestamp: 2026-03-14 04:00:01 -0300 (AIDE 0.18)
AIDE found differences between database and filesystem!!

Summary:
  Total number of entries:      48211
  Added entries:                1
  Removed entries:              0
  Changed entries:              2

---------------------------------------------------
Added entries:
---------------------------------------------------

f++++++++++++++++: /var/tmp/.cache/kdonut-watch.sh

---------------------------------------------------
Changed entries:
---------------------------------------------------

f   ...    .C... : /usr/bin/passwd
f   ...    .C... : /etc/motd

---------------------------------------------------
Detailed information about changes:
---------------------------------------------------

File: /usr/bin/passwd
  SHA256    : 4GBzO0n1u1VWD3kcx4ySv0cmc/fd3Lc6tW8m | Y7zR8q2tKQx8iGfJdP0tQ0b5qv1T9mN3cX2a

File: /etc/motd
  SHA256    : n3cX2aQ0b5qv1T9mY7zR8q2tKQx8iGfJdP0t | tW8m4GBzO0n1u1VWD3kcx4ySv0cmc/fd3Lc6
"""
    return caso(cid, "Integridade com AIDE", "especialista", "medio",
                """O AIDE tira uma 'foto' (hashes) dos arquivos do sistema e depois avisa o que mudou.
Programas do sistema nao mudam sozinhos: so com atualizacao oficial.""",
                "O AIDE avisou mudancas. Qual **programa do sistema** foi alterado (e e o mais grave)?",
                "/usr/bin/passwd",
                ["Olhe a secao Changed entries.", "/etc/motd e so a mensagem de boas-vindas; e o outro?"],
                ["AIDE compara hashes com uma base de referencia confiavel.",
                 "Binario do sistema alterado fora de atualizacao = possivel rootkit.",
                 "Guarde a base do AIDE fora da maquina, senao o invasor tambem a altera."],
                {"aide-relatorio.txt": relatorio})


def s_ufw(rnd, cid):
    status = """Status: active
Logging: on (low)
Default: deny (incoming), allow (outgoing), disabled (routed)

     To                         Action      From
     --                         ------      ----
[ 1] 22/tcp                     ALLOW IN    10.20.0.0/16
[ 2] 80/tcp                     ALLOW IN    Anywhere
[ 3] 443/tcp                    ALLOW IN    Anywhere
[ 4] 5432/tcp                   ALLOW IN    Anywhere
[ 5] 9100/tcp                   ALLOW IN    10.20.0.10
"""
    return caso(cid, "Firewall com ufw", "especialista", "medio",
                """O `ufw` e o firewall simples do Debian/Ubuntu. Cada regra numerada diz o que entra
e de onde. Banco de dados nunca deve ficar aberto para a internet.

| Comando | O que faz |
| --- | --- |
| `sudo ufw status numbered` | lista as regras numeradas |
| `sudo ufw delete N` | apaga a regra N |
| `sudo ufw allow from REDE to any port P` | libera so para uma rede |""",
                "Qual o numero da regra que expoe o banco de dados (PostgreSQL, porta 5432) para qualquer lugar?",
                "4",
                ["Procure a porta 5432 na lista.", "Responda so o numero entre colchetes."],
                ["ufw status numbered mostra as regras com numero.",
                 "'Anywhere' = a internet inteira pode tentar conectar.",
                 "Banco so deve aceitar conexao do servidor da aplicacao."],
                {"ufw-status.txt": status})


def s_timeline(rnd, cid):
    vpn = ["2026-03-14T00:41:10 vpn: login ok usuario=marge ip=10.99.0.12",
           "2026-03-14T01:02:33 vpn: login ok usuario=carl ip=198.51.100.23",
           "2026-03-14T06:58:02 vpn: login ok usuario=lenny ip=10.99.0.40"]
    auth = ["2026-03-14T01:09:51 usina-srv01 sshd: Accepted password for carl from 10.99.0.77",
            "2026-03-14T01:15:04 usina-srv01 sudo: carl : COMMAND=/usr/bin/useradd -o -u 0 manutencao",
            "2026-03-14T07:05:12 usina-srv01 sshd: Accepted publickey for lenny from 10.99.0.40"]
    web = ["2026-03-14T01:31:47 usina-web01 POST /admin/upload arquivo=donut-shell.php usuario=manutencao",
           "2026-03-14T08:00:00 usina-web01 GET / 200"]
    return caso(cid, "Montando a linha do tempo", "especialista", "avancado",
                """Num incidente, as pistas estao espalhadas em varios logs. Juntar tudo em ordem de
tempo mostra a historia do ataque.

| Comando | O que faz |
| --- | --- |
| `cat *.log \\| sort` | junta os logs e ordena pela data (quando a data vem primeiro) |""",
                "Monte a linha do tempo. Qual conta o invasor usou **primeiro** para entrar na rede?",
                "carl",
                ["Junte e ordene: cat *.log | sort", "Procure o primeiro acesso de IP externo (198.51.100.x)."],
                ["Datas no formato ISO (2026-03-14T01:02) ordenam certinho com sort.",
                 "A historia aqui: VPN com conta roubada, SSH, conta root falsa, webshell.",
                 "Linha do tempo e o coracao do relatorio de incidente."],
                {"vpn.log": "\n".join(vpn) + "\n", "auth.log": "\n".join(auth) + "\n", "web.log": "\n".join(web) + "\n"})


def s_auditd(rnd, cid):
    linhas = []
    base = 1773470000
    progs = ["/usr/bin/ls", "/usr/bin/cat", "/usr/bin/grep", "/usr/bin/vim", "/usr/bin/ps"]
    for i in range(150):
        uid = rnd.choice([1000, 1001, 1002])
        prog = rnd.choice(progs)
        ts = base + i * 7
        linhas.append(f"type=SYSCALL msg=audit({ts}.{i:03d}:{900 + i}): arch=c000003e syscall=59 success=yes "
                      f"exit=0 auid={uid} uid={uid} comm=\"{prog.split('/')[-1]}\" exe=\"{prog}\" key=\"execucao\"")
    ts = base + 75 * 7 + 3
    linhas.insert(76, f"type=SYSCALL msg=audit({ts}.999:1999): arch=c000003e syscall=59 success=yes exit=0 "
                      f"auid=1003 uid=1003 comm=\"nc\" exe=\"/usr/bin/nc.openbsd\" key=\"execucao\"")
    linhas.insert(77, f"type=EXECVE msg=audit({ts}.999:1999): argc=3 a0=\"nc\" a1=\"198.51.100.88\" a2=\"4444\"")
    return caso(cid, "Auditoria com auditd", "especialista", "avancado",
                """O `auditd` registra o que acontece no kernel: quem executou o que, com qual usuario.
`auid` e o usuario que fez login (nao muda nem com sudo).

| Comando | O que faz |
| --- | --- |
| `ausearch -if audit.log -ua 1003 -i` | eventos do usuario 1003, legiveis |
| `grep auid=1003 audit.log` | o mesmo, no braco |""",
                "O usuario de auid 1003 abriu uma conexao para fora. Qual programa (caminho completo do exe) ele executou?",
                "/usr/bin/nc.openbsd",
                ["Filtre: grep auid=1003 audit.log", "O caminho esta no campo exe=."],
                ["auditd registra execucoes com o usuario original (auid).",
                 "nc (netcat) conectando a IP externo e sinal classico de shell reversa.",
                 "ausearch e aureport resumem os logs do auditd."],
                {"audit.log": "\n".join(linhas) + "\n"})


ESPECIALISTA = [("metadados-exif", s_exif), ("escondido-na-imagem", s_binwalk), ("integridade-aide", s_aide),
                ("firewall-ufw", s_ufw), ("linha-do-tempo", s_timeline), ("auditoria-auditd", s_auditd)]
