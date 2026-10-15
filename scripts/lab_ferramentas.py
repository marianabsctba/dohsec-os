"""Casos que cobram as ferramentas instaladas que ainda nao tinham desafio.

Usado por scripts/gen-lab.py. Como em lab_esboco.py, cada caso usa a propria semente, entao incluir
estes casos nao muda as respostas dos outros. Tudo e ficticio e defensivo; as evidencias ficam no
proprio caso e funcionam sem internet.

Para gerar: Pillow (fotos), cryptography (certificados) e o gpg no PATH (assinatura).
"""
import base64
import hashlib
import io
import os
import random
import sqlite3
import struct
import subprocess
import tempfile
import zipfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

from lab_casos import FUNCIONARIOS, INICIO, caso, consulta_dns, pacote_udp, pcap
from lab_esboco import semente


# ===========================================================================
# Operador da Usina
# ===========================================================================
@semente
def strace_escondido(rnd, cid):
    caminho = ".cache/.usina/chaves-do-cofre.dat"
    codificado = base64.b64encode(caminho.encode()).decode()
    script = f"""#!/bin/bash
# Mostra o status do reator. (So isso. Juro.)
cd "$(dirname "$0")"
alvo=$(echo {codificado} | base64 -d)
cat "$alvo" > /dev/null 2>&1
echo "Reator: estavel. Nada para ver aqui."
"""
    arquivos = {"reator-status.sh": script,
                caminho: "chave-mestra: " + "".join(rnd.choice("0123456789abcdef") for _ in range(32)) + "\n"}
    for i in range(8):
        arquivos[f".cache/.usina/lixo-{i:02d}.tmp"] = "".join(rnd.choice("abcdef") for _ in range(40)) + "\n"
    return caso(cid, "O script que le escondido", "operador", "medio",
                """O `reator-status.sh` diz que so mostra o status do reator, mas o time desconfia que ele mexe em
algum arquivo escondido. Em vez de decifrar o codigo, **observe o que ele faz**: o `strace` mostra cada
chamada que um programa faz ao sistema, inclusive cada arquivo que ele abre.

| Comando | O que faz |
| --- | --- |
| `strace -f -e trace=openat bash script.sh` | lista os arquivos que o script abre |
| `... 2>&1 \\| grep -v -e /usr -e /lib -e /etc` | tira os arquivos do proprio sistema |""",
                "Qual arquivo escondido o script le? (so o nome do arquivo)",
                "chaves-do-cofre.dat",
                ["O strace escreve na saida de erro: use 2>&1 para poder filtrar.",
                 "strace -f -e trace=openat bash reator-status.sh 2>&1 | grep -v -e /usr -e /lib -e /etc",
                 "Procure um openat de um arquivo dentro de .cache."],
                ["strace mostra o que um programa faz de verdade, mesmo com o codigo disfarcado (base64).",
                 "-e trace=openat filtra so as aberturas de arquivo; -f segue os processos filhos.",
                 "Na vida real, rode programas suspeitos so em maquina isolada: aqui o script e inofensivo.",
                 "Comando que ficou: strace -f -e trace=openat COMANDO"],
                arquivos)


@semente
def tcpdump_senha(rnd, cid):
    senha = "Donut#Rosa2026"
    pacotes = []
    t = INICIO
    for i in range(160):
        t += timedelta(milliseconds=rnd.randint(200, 2500))
        if rnd.random() < 0.35:
            nome = rnd.choice(["deb.debian.org", "usina.test", "intranet.usina.test", "ntp.usina.test"])
            pacotes.append((t, pacote_udp(f"10.20.4.{rnd.randint(10, 60)}", "10.20.0.53", rnd.randint(30000, 60000), 53,
                                          consulta_dns(rnd.getrandbits(16), nome))))
        else:
            host = rnd.choice(["reator-01", "reator-02", "bomba-03", "portaria"])
            msg = rnd.choice(["temperatura normal", "pressao estavel", "cracha lido", "ronda concluida"])
            carga = f"<14>{t:%b %d %H:%M:%S} {host} usina: {msg}".encode()
            pacotes.append((t, pacote_udp(f"10.20.5.{rnd.randint(10, 60)}", "10.20.0.9", 514, 514, carga)))
    t_vaz = pacotes[97][0] + timedelta(milliseconds=300)
    carga = f"<11>{t_vaz:%b %d %H:%M:%S} painel-02 login: falha para smithers password={senha}".encode()
    pacotes.insert(98, (t_vaz, pacote_udp("10.20.5.77", "10.20.0.9", 514, 514, carga)))
    return caso(cid, "Senha que passou pela rede", "operador", "medio",
                """Os equipamentos da usina mandam logs pela rede para um servidor central (syslog, porta UDP 514),
**sem criptografia**. Um painel mal configurado registrou um login com a senha junto. A captura `rede.pcap`
tem esse trafego. O `tcpdump` le capturas direto no terminal.

| Comando | O que faz |
| --- | --- |
| `tcpdump -nn -r rede.pcap` | lista os pacotes (-nn: sem traduzir nomes e portas) |
| `tcpdump -nn -r rede.pcap udp port 514` | so o syslog |
| `tcpdump -nn -A -r rede.pcap udp port 514` | mostra o conteudo em texto (-A) |""",
                "Qual senha apareceu em texto claro nos logs que passaram pela rede?",
                senha,
                ["Filtre so o syslog: tcpdump -nn -r rede.pcap udp port 514",
                 "Veja o conteudo com -A e procure: ... -A | grep -i pass",
                 "A senha vem depois de password="],
                ["Tudo que vai pela rede sem criptografia pode ser lido por quem captura o trafego.",
                 "tcpdump -A mostra o conteudo dos pacotes; filtros como 'udp port 514' cortam o barulho.",
                 "Prevencao: syslog com TLS, nunca registrar senhas em log, trocar a senha vazada (smithers).",
                 "Comando que ficou: tcpdump -nn -A -r ARQ.pcap 'udp port 514'"],
                {"rede.pcap": pcap(pacotes)})


def nmap_inventario(rnd, cid):
    return caso(cid, "Inventario da propria maquina", "operador", "medio",
                """Antes de defender uma maquina, saiba o que ela expoe. O `nmap` testa portas e diz quais estao
abertas, como um invasor veria. Aqui o alvo e **a sua propria maquina** (`127.0.0.1`): nunca escaneie
redes de outras pessoas sem autorizacao.

O D'OH!Sec roda servicos locais que fazem o desktop funcionar. Descubra quais portas eles usam.
Este caso e para o D'OH!Sec completo (ISO ou VM): no WSL esses servicos nao existem.

| Comando | O que faz |
| --- | --- |
| `nmap 127.0.0.1` | as 1000 portas mais comuns |
| `nmap -p 7000-8000 127.0.0.1` | so uma faixa de portas |
| `nmap -sV -p PORTA 127.0.0.1` | tenta descobrir o servico (-sV) |
| `sudo ss -tlnp` | confirma pelo proprio sistema qual programa escuta |""",
                "Quantas portas TCP abertas o nmap encontra em 127.0.0.1 entre 7000 e 8000?",
                "2",
                ["nmap -p 7000-8000 127.0.0.1",
                 "Conte as linhas com 'open'.",
                 "Confira quem sao com: sudo ss -tlnp | grep -e 7681 -e 7700"],
                ["nmap mostra a maquina como um atacante veria: o que esta aberto e para quem.",
                 "Comparar o nmap com o ss -tlnp liga cada porta ao programa responsavel.",
                 "Servicos so em 127.0.0.1 nao sao alcancaveis pela rede: e o que o D'OH!Sec faz.",
                 "Escaneie so o que e seu ou com autorizacao por escrito."],
                {})


# ===========================================================================
# Supervisor de Seguranca
# ===========================================================================
@semente
def sqlite_historico(rnd, cid):
    golpe = "fatura-burns.test"
    pasta = Path(tempfile.mkdtemp())
    db = pasta / "places.sqlite"
    con = sqlite3.connect(db)
    con.executescript("""
CREATE TABLE moz_places (id INTEGER PRIMARY KEY, url TEXT, title TEXT, visit_count INTEGER, last_visit_date INTEGER);
CREATE TABLE moz_historyvisits (id INTEGER PRIMARY KEY, place_id INTEGER, visit_date INTEGER, visit_type INTEGER);
""")
    sites = [("https://intranet.usina.test/", "Intranet da Usina"), ("https://mail.usina.test/", "E-mail"),
             ("https://deb.debian.org/", "Debian"), ("https://cardapio.usina.test/hoje", "Cardapio do refeitorio"),
             ("https://wiki.usina.test/reator", "Wiki do reator"), ("https://www.wikipedia.org/", "Wikipedia"),
             ("https://ponto.usina.test/", "Ponto eletronico")]
    sites.append((f"http://{golpe}/pagar?id=88231", "Pagamento urgente - Financeiro"))
    for i, (url, titulo) in enumerate(sites, 1):
        con.execute("INSERT INTO moz_places VALUES (?,?,?,?,?)", (i, url, titulo, 0, 0))
    t = INICIO + timedelta(hours=1)
    visitas = []
    for _ in range(140):
        t += timedelta(seconds=rnd.randint(20, 240))
        visitas.append((rnd.randint(1, 7), t))
    momento = INICIO + timedelta(hours=2, minutes=13, seconds=27)   # logo depois do e-mail das 09:12
    visitas = [v for v in visitas if abs((v[1] - momento).total_seconds()) > 60]
    visitas.append((len(sites), momento))
    visitas.sort(key=lambda v: v[1])
    for n, (pid, quando) in enumerate(visitas, 1):
        us = int(quando.replace(tzinfo=timezone(timedelta(hours=-3))).timestamp() * 1_000_000)
        con.execute("INSERT INTO moz_historyvisits VALUES (?,?,?,?)", (n, pid, us, 1))
        con.execute("UPDATE moz_places SET visit_count = visit_count + 1, last_visit_date = ? WHERE id = ?", (us, pid))
    con.commit()
    con.close()
    dados = db.read_bytes()
    db.unlink()
    pasta.rmdir()
    return caso(cid, "Historico do navegador", "analista", "medio",
                """O Lenny jura que nao clicou no link do e-mail falso que chegou as **09:12**. O historico do Firefox
dele (`places.sqlite`) e um banco de dados SQLite: da para consultar com SQL pelo `sqlite3`.
As datas estao em **microssegundos desde 1970** (formato do Firefox).

| Comando | O que faz |
| --- | --- |
| `sqlite3 places.sqlite '.tables'` | lista as tabelas |
| `sqlite3 places.sqlite '.schema moz_places'` | mostra as colunas |
| `sqlite3 places.sqlite 'SELECT ... ;'` | roda uma consulta |

Para mostrar a data legivel: `datetime(visit_date/1000000, 'unixepoch', 'localtime')`.""",
                "Qual dominio o Lenny visitou logo depois do e-mail das 09:12?",
                golpe,
                ["As visitas ficam em moz_historyvisits e os enderecos em moz_places (ligados por place_id = id).",
                 "sqlite3 places.sqlite \"SELECT datetime(v.visit_date/1000000,'unixepoch','localtime'), p.url FROM moz_historyvisits v JOIN moz_places p ON p.id = v.place_id ORDER BY v.visit_date\"",
                 "Procure a visita entre 09:12 e 09:20: grep ' 09:1'"],
                ["Navegadores guardam o historico em SQLite: um otimo lugar para confirmar cliques.",
                 "JOIN junta tabelas; datetime(..., 'unixepoch') converte o horario.",
                 "Resposta: bloquear o dominio, trocar as senhas do Lenny e ver se ele digitou algo no site falso.",
                 "Comando que ficou: sqlite3 ARQ.sqlite 'SELECT ...'"],
                {"places.sqlite": dados})


@semente
def clamav_assinatura(rnd, cid):
    marca = b"DONUT-DROPPER-v2::baixa_e_executa"
    sig = "Usina.Dropper.Donut:0:*:" + marca.hex()
    arquivos = {"usina.ndb": f"{sig}\n"}
    alvo_zip = "anexos/notas-fiscais-marco.zip"
    for i in range(14):
        nome = f"anexos/{rnd.choice(['relatorio', 'planilha', 'foto', 'contrato', 'escala'])}-{i:02d}.txt"
        arquivos[nome] = "".join(rnd.choice("abcdefghij \n") for _ in range(400))
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("nf-001.txt", "Nota fiscal 001 - donuts sortidos\n")
        z.writestr("nf-002.dat", b"\x00\x01dados" + marca + b"\x00" * 64)
        z.writestr("nf-003.txt", "Nota fiscal 003 - cafe\n")
    arquivos[alvo_zip] = buf.getvalue()
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("fotos.txt", "fotos da confraternizacao\n")
    arquivos["anexos/confraternizacao.zip"] = buf.getvalue()
    return caso(cid, "Assinatura propria no antivirus", "analista", "medio",
                """O CERT da usina descobriu um "dropper" (programa que baixa e roda outro) e mandou uma
**assinatura** para o ClamAV: o arquivo `usina.ndb`. Com ela, o antivirus reconhece o malware mesmo sem
internet e sem a base oficial. Varra os anexos do e-mail recebidos esta semana.

| Comando | O que faz |
| --- | --- |
| `clamscan -d usina.ndb -r anexos/` | varre a pasta usando so a assinatura do CERT |
| `--infected` | mostra so o que foi detectado |
| `cat usina.ndb` | a assinatura: nome, tipo, posicao e os bytes em hexadecimal |

O ClamAV abre arquivos .zip sozinho e procura dentro deles.""",
                "Qual anexo o ClamAV detectou com a assinatura do CERT? (o nome do arquivo)",
                "notas-fiscais-marco.zip",
                ["clamscan -d usina.ndb -r anexos/",
                 "Use --infected para ver so os detectados.",
                 "A resposta e o arquivo que esta na pasta anexos (o ClamAV tambem achou dentro dele)."],
                ["Assinatura = padrao de bytes que identifica um malware; o -d usa uma base sua.",
                 "Times de defesa criam assinaturas para ameacas novas antes da base oficial ter.",
                 "O ClamAV abre zip, e por isso malware escondido em arquivo compactado tambem e pego.",
                 "Comando que ficou: clamscan -d ASSINATURAS.ndb -r PASTA --infected"],
                arquivos)


@semente
def openssl_certificado(rnd, cid):
    from cryptography import x509
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import ed25519
    from cryptography.x509.oid import NameOID

    def chave(n):
        return ed25519.Ed25519PrivateKey.from_private_bytes(hashlib.sha256(f"usina-{n}".encode()).digest())

    def nome(cn):
        return x509.Name([x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Usina Nuclear de Springfield"),
                          x509.NameAttribute(NameOID.COMMON_NAME, cn)])

    ac_chave = chave("ac")
    ac = nome("AC Interna da Usina")
    servidores = [("intranet.usina.test", datetime(2025, 1, 10), datetime(2030, 1, 10)),
                  ("mail.usina.test", datetime(2025, 6, 1), datetime(2030, 6, 1)),
                  ("ponto.usina.test", datetime(2022, 3, 1), datetime(2024, 3, 1)),
                  ("wiki.usina.test", datetime(2025, 9, 15), datetime(2031, 9, 15)),
                  ("cardapio.usina.test", datetime(2025, 2, 20), datetime(2030, 2, 20))]
    arquivos = {}
    for i, (cn, ini, fim) in enumerate(servidores):
        cert = (x509.CertificateBuilder().subject_name(nome(cn)).issuer_name(ac)
                .public_key(chave(cn).public_key()).serial_number(1000 + i)
                .not_valid_before(ini.replace(tzinfo=timezone.utc)).not_valid_after(fim.replace(tzinfo=timezone.utc))
                .add_extension(x509.SubjectAlternativeName([x509.DNSName(cn)]), critical=False)
                .sign(ac_chave, None))
        arquivos[f"certs/{cn.split('.')[0]}.pem"] = cert.public_bytes(serialization.Encoding.PEM)
    return caso(cid, "Certificado vencido", "analista", "medio",
                """Desde ontem o navegador mostra **"Sua conexao nao e particular"** num dos sistemas internos, e o
pessoal esta clicando em "aceitar o risco". O time exportou os certificados TLS dos servidores.
Certificado tem validade: depois da data **notAfter**, deixa de valer.

| Comando | O que faz |
| --- | --- |
| `openssl x509 -in ARQ.pem -noout -subject -dates` | para quem e o certificado e as datas |
| `openssl x509 -in ARQ.pem -noout -checkend 0` | diz se ja venceu |
| `openssl x509 -in ARQ.pem -noout -text` | tudo |""",
                "Qual certificado esta vencido? (o nome do arquivo)",
                "ponto.pem",
                ["Veja as datas de um: openssl x509 -in certs/intranet.pem -noout -dates",
                 "Todos de uma vez: for c in certs/*.pem; do echo $c; openssl x509 -in $c -noout -enddate; done",
                 "Ou deixe o openssl dizer: for c in certs/*.pem; do openssl x509 -in $c -noout -checkend 0 > /dev/null || echo \"$c vencido\"; done"],
                ["Certificado vencido quebra a confianca do HTTPS: nao clique em 'aceitar o risco'.",
                 "Treinar o usuario a ignorar o aviso e perigoso: no dia do ataque de verdade ele tambem ignora.",
                 "Prevencao: monitorar validade (checkend) e renovar automaticamente.",
                 "Comando que ficou: openssl x509 -in ARQ.pem -noout -subject -dates"],
                arquivos)


# ===========================================================================
# Chefe de Seguranca
# ===========================================================================
def _caminho_gpg(caminho):
    """O gpg do Git para Windows (MSYS) so entende caminhos como /d/Temp/..."""
    if os.name == "nt" and len(caminho) > 2 and caminho[1] == ":":
        return "/" + caminho[0].lower() + caminho[2:].replace("\\", "/")
    return caminho


def _gpg(*args, gnupghome, entrada=None):
    return subprocess.run(["gpg", "--batch", "--homedir", _caminho_gpg(gnupghome), "--pinentry-mode", "loopback",
                           "--passphrase", "", *args], input=entrada, capture_output=True, check=True).stdout


@semente
def gpg_download(rnd, cid):
    arquivos = {}
    pacotes = {}
    for v in range(1, 5):
        dados = bytes(rnd.getrandbits(8) for _ in range(8192))
        pacotes[f"reator-ctl-1.{v}.tar.gz"] = dados
        arquivos[f"downloads/reator-ctl-1.{v}.tar.gz"] = dados
    oficial = "reator-ctl-1.3.tar.gz"
    falso = "reator-ctl-1.4.tar.gz"
    sums = f"{hashlib.sha256(pacotes[oficial]).hexdigest()}  {oficial}\n"
    sums_espelho = f"{hashlib.sha256(pacotes[falso]).hexdigest()}  {falso}\n"
    home = tempfile.mkdtemp()
    try:
        _gpg("--quick-gen-key", "Usina Release <release@usina.test>", "ed25519", "sign", "never", gnupghome=home)
        chave = _gpg("--armor", "--export", "release@usina.test", gnupghome=home)
        colunas = _gpg("--with-colons", "--fingerprint", "release@usina.test", gnupghome=home).decode()
        digital = next(l.split(":")[9] for l in colunas.splitlines() if l.startswith("fpr:"))
        assinatura = _gpg("--armor", "--detach-sign", "--output", "-", gnupghome=home, entrada=sums.encode())
        # O espelho assinou com outra chave, que nao e a oficial
        _gpg("--quick-gen-key", "Espelho Rapido <admin@espelho-rapido.test>", "ed25519", "sign", "never", gnupghome=home)
        assinatura_espelho = _gpg("--armor", "--detach-sign", "--local-user", "admin@espelho-rapido.test",
                                  "--output", "-", gnupghome=home, entrada=sums_espelho.encode())
    finally:
        subprocess.run(["gpgconf", "--homedir", _caminho_gpg(home), "--kill", "all"], capture_output=True)
        for raiz, _, nomes in os.walk(home, topdown=False):
            for n in nomes:
                try:
                    os.remove(os.path.join(raiz, n))
                except OSError:
                    pass
            try:
                os.rmdir(raiz)
            except OSError:
                pass
    digital_legivel = " ".join(digital[i:i + 4] for i in range(0, len(digital), 4))
    arquivos.update({"chave-oficial-usina.asc": chave,
                     "site-oficial/impressao-digital-da-chave.txt":
                         "Impressao digital oficial da chave de release da Usina\n"
                         "(confirmada tambem no cracha do Smithers e na intranet)\n\n" + digital_legivel + "\n",
                     "site-oficial/SHA256SUMS": sums, "site-oficial/SHA256SUMS.asc": assinatura,
                     "espelho-rapido/SHA256SUMS": sums_espelho, "espelho-rapido/SHA256SUMS.asc": assinatura_espelho})
    return caso(cid, "Qual download e legitimo?", "especialista", "avancado",
                """Foram baixadas quatro versoes do controlador do reator, do site oficial e de um "espelho rapido".
Hash sozinho nao basta: quem troca o arquivo pode trocar a lista de hashes junto. Por isso o site oficial
**assina** a lista com GPG. Voce tem a chave publica oficial (`chave-oficial-usina.asc`).

| Comando | O que faz |
| --- | --- |
| `gpg --import chave-oficial-usina.asc` | importa a chave oficial |
| `gpg --verify SHA256SUMS.asc SHA256SUMS` | confere a assinatura da lista |
| `sha256sum -c SHA256SUMS --ignore-missing` | confere os arquivos contra a lista |

Atencao a mensagem do gpg: "Assinatura valida" ("Good signature") **de quem**? O aviso de chave nao
certificada e normal: confira a impressao digital da chave com a publicada em `site-oficial/impressao-digital-da-chave.txt`.
O `sha256sum -c` responde `SUCESSO` (ou `OK`) para o arquivo que bate.""",
                "Qual pacote tem a lista de hashes assinada pela chave oficial e o hash batendo? (o nome do arquivo)",
                oficial,
                ["Importe a chave oficial e verifique as duas listas: cd site-oficial; gpg --verify SHA256SUMS.asc SHA256SUMS",
                 "A lista do espelho foi assinada por uma chave que voce nao tem (ou nao e a oficial): nao confie.",
                 "Com a lista oficial confirmada: cd ../downloads; sha256sum -c ../site-oficial/SHA256SUMS --ignore-missing"],
                ["A assinatura GPG garante quem publicou a lista; o hash garante que o arquivo e o da lista.",
                 "O aviso 'chave nao certificada' se resolve conferindo a impressao digital por outro canal.",
                 "Assinatura valida de uma chave qualquer nao vale: tem que ser da chave oficial, obtida por canal confiavel.",
                 "E assim que o Debian e muitos projetos protegem os downloads.",
                 "Comandos que ficaram: gpg --verify ARQ.asc ARQ e sha256sum -c ARQ"],
                arquivos)


def _fat12(arquivos, apagados):
    """Imagem FAT12 de 1,44 MB. arquivos: [(NOME.EXT, bytes)]; apagados: nomes que ficam como excluidos."""
    setor, total = 512, 2880
    img = bytearray(setor * total)
    bpb = struct.pack("<3s8sHBHBHHBHHHII", b"\xeb\x3c\x90", b"USINA1.0", setor, 1, 1, 2, 224, total, 0xF0, 9, 18, 2, 0, 0)
    ebpb = struct.pack("<BBBI11s8s", 0, 0, 0x29, 0x0D0E5EC0, b"PENDRIVE   ", b"FAT12   ")
    img[:len(bpb) + len(ebpb)] = bpb + ebpb
    img[510:512] = b"\x55\xaa"
    fat = {0: 0xFF0, 1: 0xFFF}
    raiz = 19 * setor
    dados0 = 33 * setor
    cluster = 2
    for i, (nome, conteudo) in enumerate(arquivos):
        base, ext = nome.split(".")
        n = max(1, -(-len(conteudo) // setor))
        inicio = cluster
        for k in range(n):
            pos = dados0 + (cluster - 2 + k) * setor
            pedaco = conteudo[k * setor:(k + 1) * setor]
            img[pos:pos + len(pedaco)] = pedaco
        if nome not in apagados:
            for k in range(n):
                fat[inicio + k] = inicio + k + 1 if k < n - 1 else 0xFFF
        entrada = bytearray(f"{base:<8}{ext:<3}".encode()) + struct.pack("<BBBHHHHHHHI", 0x20, 0, 0, 0x6000, 0x5A6E,
                                                                          0x5A6E, 0, 0x6000, 0x5A6E, inicio, len(conteudo))
        if nome in apagados:
            entrada[0] = 0xE5
        img[raiz + i * 32: raiz + (i + 1) * 32] = entrada
        cluster += n
    tabela = bytearray(9 * setor)
    for c, v in fat.items():
        off = c * 3 // 2
        atual = tabela[off] | (tabela[off + 1] << 8)
        atual = (atual & 0x000F) | (v << 4) if c % 2 else (atual & 0xF000) | v
        tabela[off], tabela[off + 1] = atual & 0xFF, (atual >> 8) & 0xFF
    for f in range(2):
        img[(1 + f * 9) * setor:(1 + f * 9) * setor + len(tabela)] = tabela
    return bytes(img)


@semente
def sleuthkit_apagado(rnd, cid):
    senha = "cofre-donut-742"
    arquivos = [("LEIAME.TXT", b"Pendrive da sala de controle. Nao levar para casa.\n"),
                ("ESCALA.CSV", "dia,turno\n" .encode() + b"".join(f"{d},{rnd.choice(['A', 'B', 'C'])}\n".encode() for d in range(1, 31))),
                ("PLANO.TXT", f"Plano de fuga do Homer\n1. sair cedo\n2. passar no Moe\nsenha do cofre: {senha}\n".encode()),
                ("CARDAPIO.TXT", b"Segunda: donut\nTerca: donut\n"),
                ("RONDA.LOG", b"".join(f"{h:02d}:00 ronda ok\n".encode() for h in range(24)))]
    imagem = _fat12(arquivos, {"PLANO.TXT"})
    return caso(cid, "O arquivo apagado do pendrive", "especialista", "avancado",
                """Um pendrive da sala de controle foi achado na lixeira. Alguem **apagou** um arquivo antes de jogar
fora. Apagar no FAT so marca a entrada como livre: o conteudo continua la ate ser sobrescrito.
O Sleuth Kit le a imagem do disco (`pendrive.img`) sem precisar montar nada.

| Comando | O que faz |
| --- | --- |
| `fsstat pendrive.img` | o tipo de sistema de arquivos |
| `fls -r pendrive.img` | lista os arquivos; os apagados aparecem com `*` |
| `fls -rd pendrive.img` | so os apagados |
| `icat pendrive.img NUMERO` | mostra o conteudo pelo numero (inode) que o fls mostrou |

No FAT, o nome apagado perde a primeira letra (vira `_`).""",
                "Qual e a senha do cofre escrita no arquivo apagado?",
                senha,
                ["fls -rd pendrive.img mostra so os apagados, com o numero de cada um.",
                 "O numero vem antes do dois-pontos, por exemplo: r/r * 6: _LANO.TXT",
                 "icat pendrive.img NUMERO"],
                ["Apagar nao destroi o conteudo: so libera o espaco. Forense recupera enquanto nao for sobrescrito.",
                 "Trabalhe sempre numa copia da imagem (sha256sum antes e depois), nunca no disco original.",
                 "Para apagar de verdade: criptografia de disco desde o inicio, ou sobrescrever e destruir.",
                 "Comandos que ficaram: fls -rd IMG e icat IMG INODE"],
                {"pendrive.img": imagem})


@semente
def foremost_fotos(rnd, cid):
    from PIL import Image, ImageDraw

    cores = [(255, 216, 77), (255, 95, 183), (47, 125, 246), (59, 178, 115), (255, 155, 48)]
    fotos = []
    for i, cor in enumerate(cores):
        img = Image.new("RGB", (160, 120), cor)
        d = ImageDraw.Draw(img)
        d.ellipse((50, 30, 110, 90), outline=(91, 53, 24), width=6)
        d.text((8, 100), f"FOTO {i + 1}", fill=(0, 0, 0))
        buf = io.BytesIO()
        img.save(buf, "JPEG", quality=70)
        fotos.append(buf.getvalue())
    # Cartao "formatado": sem sistema de arquivos, so os dados no meio de lixo (sem bytes 0xFF, que
    # poderiam formar um cabecalho JPEG falso)
    def lixo(n):
        return bytes(rnd.randrange(0, 255) for _ in range(n))
    img = bytearray(lixo(4096))
    for foto in fotos:
        img += foto + lixo(rnd.randint(2000, 9000))
    img += bytes(64 * 1024)
    return caso(cid, "Fotos de um cartao formatado", "especialista", "medio",
                """O cartao de memoria da camera da portaria foi **formatado** depois do incidente. Sem sistema de
arquivos, o `fls` nao ajuda. Mas as fotos continuam la, no meio dos bytes. O `foremost` faz **carving**:
procura os bytes de inicio e fim de cada tipo de arquivo (um JPEG comeca com `FF D8 FF`) e recorta.

| Comando | O que faz |
| --- | --- |
| `foremost -t jpg -i cartao.img -o recuperado` | recorta os JPEG para a pasta recuperado/ (ela nao pode existir antes) |
| `cat recuperado/audit.txt` | o resumo do que foi achado |
| `ls recuperado/jpg` | as fotos |""",
                "Quantas fotos JPEG o foremost recupera do cartao?",
                str(len(fotos)),
                ["foremost -t jpg -i cartao.img -o recuperado",
                 "Se reclamar que a pasta existe, use outro nome ou apague a anterior.",
                 "O total aparece no fim do recuperado/audit.txt (ou conte: ls recuperado/jpg | wc -l)"],
                ["Formatar so apaga o indice; os dados ficam ate serem sobrescritos.",
                 "Carving recupera arquivos pelo formato, mesmo sem sistema de arquivos.",
                 "Para ver os bytes do comeco de um JPEG: xxd recuperado/jpg/ARQ.jpg | head -1",
                 "Comando que ficou: foremost -t jpg -i IMG -o PASTA"],
                {"cartao.img": bytes(img)})


@semente
def lynis_relatorio(rnd, cid):
    linhas = ["# Lynis Report", "report_version_major=1", "report_version_minor=0",
              "report_datetime_start=2026-03-14 06:10:02", "auditor=Equipe de Seguranca da Usina",
              "hostname=usina-srv02", "os=Linux", "os_name=Debian", "os_version=13", "lynis_version=3.1.4",
              "hardening_index=58", "tests_executed=268"]
    sugestoes = [("AUTH-9230", "Configure password hashing rounds in /etc/login.defs"),
                 ("BOOT-5122", "Set a password on GRUB boot loader to prevent altering boot configuration"),
                 ("KRNL-5788", "Determine why /vmlinuz or /boot/vmlinuz is missing on this Debian/Ubuntu system"),
                 ("PKGS-7370", "Install debsums utility for the verification of packages"),
                 ("LOGG-2154", "Enable logging to an external logging host for archiving purposes"),
                 ("NETW-3200", "Determine if protocol 'dccp' is really needed on this system"),
                 ("HRDN-7230", "Harden the system by installing at least one malware scanner")]
    for teste, texto in sugestoes:
        linhas.append(f"suggestion[]={teste}|{texto}|-|-|")
    linhas += ["warning[]=FIRE-4512|iptables module(s) loaded, but no rules active|-|-|",
               "warning[]=SSH-7408|SSH option PermitRootLogin is set to yes|PermitRootLogin|-|",
               "warning[]=PKGS-7392|Found one or more vulnerable packages.|-|-|"]
    for _ in range(40):
        linhas.append(f"installed_package[]={rnd.choice(['openssh-server', 'nginx', 'postgresql', 'cron', 'sudo'])},"
                      f"{rnd.randint(1, 9)}.{rnd.randint(0, 20)}")
    linhas.append("report_datetime_end=2026-03-14 06:13:47")
    return caso(cid, "O relatorio do Lynis", "especialista", "medio",
                """O Lynis faz uma auditoria de endurecimento: roda centenas de testes e da uma nota (hardening index).
O relatorio da maquina `usina-srv02` foi salvo em `lynis-report.dat`. Cada achado tem o **codigo do teste**,
e e por ele que se procura a explicacao e a correcao.

| Onde | O que tem |
| --- | --- |
| `warning[]=` | avisos: problemas para corrigir logo |
| `suggestion[]=` | sugestoes de melhoria |
| `hardening_index=` | a nota de 0 a 100 |

Depois, rode na sua maquina: `sudo lynis audit system` (leva alguns minutos) e compare.""",
                "Qual o codigo do teste do Lynis que avisou que o SSH deixa o root entrar?",
                "SSH-7408",
                ["Os avisos estao nas linhas warning[]: grep '^warning' lynis-report.dat",
                 "Procure o aviso que fala de PermitRootLogin.",
                 "O codigo vem logo depois do =, antes da primeira barra (|)."],
                ["Lynis aponta o que endurecer; comece pelos warning[], depois as suggestion[].",
                 "O codigo do teste (ex.: SSH-7408) leva a documentacao do Lynis e a correcao.",
                 "Rode de novo depois de corrigir e veja o hardening index subir.",
                 "Comando que ficou: sudo lynis audit system"],
                {"lynis-report.dat": "\n".join(linhas) + "\n"})


OPERADOR = [("o-script-que-le-escondido", strace_escondido), ("senha-pela-rede", tcpdump_senha),
            ("inventario-da-maquina", nmap_inventario)]
ANALISTA = [("historico-do-navegador", sqlite_historico), ("assinatura-no-antivirus", clamav_assinatura),
            ("certificado-vencido", openssl_certificado)]
ESPECIALISTA = [("download-legitimo", gpg_download), ("arquivo-apagado-do-pendrive", sleuthkit_apagado),
                ("fotos-do-cartao", foremost_fotos), ("relatorio-do-lynis", lynis_relatorio)]
