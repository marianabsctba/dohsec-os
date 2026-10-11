# Firewall com ufw

O `ufw` e o firewall simples do Debian/Ubuntu. Cada regra numerada diz o que entra
e de onde. Banco de dados nunca deve ficar aberto para a internet.

| Comando | O que faz |
| --- | --- |
| `sudo ufw status numbered` | lista as regras numeradas |
| `sudo ufw delete N` | apaga a regra N |
| `sudo ufw allow from REDE to any port P` | libera so para uma rede |

## Evidencias

- `ufw-status.txt`

## Pergunta

Qual o numero da regra que expoe o banco de dados (PostgreSQL, porta 5432) para qualquer lugar?

Responda com `lab responder 35 "sua resposta"`. Travou? `lab dica 35`.
