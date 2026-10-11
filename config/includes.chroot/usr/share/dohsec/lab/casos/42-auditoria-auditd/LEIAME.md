# Auditoria com auditd

O `auditd` registra o que acontece no kernel: quem executou o que, com qual usuario.
`auid` e o usuario que fez login (nao muda nem com sudo).

| Comando | O que faz |
| --- | --- |
| `ausearch -if audit.log -ua 1003 -i` | eventos do usuario 1003, legiveis |
| `grep auid=1003 audit.log` | o mesmo, no braco |

## Evidencias

- `audit.log`

## Pergunta

O usuario de auid 1003 abriu uma conexao para fora. Qual programa (caminho completo do exe) ele executou?

Responda com `lab responder 42 "sua resposta"`. Travou? `lab dica 42`.
