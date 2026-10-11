# Quem mais fala com o servidor suspeito?

O tshark tem estatisticas prontas: quem conversou com quem e quanto.

| Comando | O que faz |
| --- | --- |
| `tshark -r arq.pcap -q -z conv,ip` | conversas por par de IPs |
| `tshark -r arq.pcap -Y 'ip.dst==X'` | so pacotes para o IP X |

## Evidencias

- `rede.pcap`

## Pergunta

O IP externo 203.0.113.66 esta na lista de ameacas. Qual maquina interna enviou mais dados para ele?

Responda com `lab responder 29 "sua resposta"`. Travou? `lab dica 29`.
