# Vazamento por DNS

DNS traduz nomes em IPs e quase nunca e bloqueado. Por isso invasores escondem
dados dentro dos nomes consultados (subdominios longos e sem sentido).

| Comando | O que faz |
| --- | --- |
| `tshark -r arq.pcap` | lista os pacotes de uma captura |
| `tshark -r arq.pcap -Y dns -T fields -e dns.qry.name` | so os nomes consultados |
| `wireshark arq.pcap` | abre a captura na interface grafica |

## Evidencias

- `dns.pcap`

## Pergunta

A captura mostra consultas DNS estranhas. Para qual dominio os dados estao sendo enviados? (so o dominio principal, sem os subdominios)

Responda com `lab responder 28 "sua resposta"`. Travou? `lab dica 28`.
