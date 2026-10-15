# Senha que passou pela rede

Os equipamentos da usina mandam logs pela rede para um servidor central (syslog, porta UDP 514),
**sem criptografia**. Um painel mal configurado registrou um login com a senha junto. A captura `rede.pcap`
tem esse trafego. O `tcpdump` le capturas direto no terminal.

| Comando | O que faz |
| --- | --- |
| `tcpdump -nn -r rede.pcap` | lista os pacotes (-nn: sem traduzir nomes e portas) |
| `tcpdump -nn -r rede.pcap udp port 514` | so o syslog |
| `tcpdump -nn -A -r rede.pcap udp port 514` | mostra o conteudo em texto (-A) |

## Evidencias

- `rede.pcap`

## Pergunta

Qual senha apareceu em texto claro nos logs que passaram pela rede?

Responda com `lab responder 23 "sua resposta"`. Travou? `lab dica 23`.
