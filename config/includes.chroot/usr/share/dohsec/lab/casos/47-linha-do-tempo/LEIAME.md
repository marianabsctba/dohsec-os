# Montando a linha do tempo

Num incidente, as pistas estao espalhadas em varios logs. Juntar tudo em ordem de
tempo mostra a historia do ataque.

| Comando | O que faz |
| --- | --- |
| `cat *.log \| sort` | junta os logs e ordena pela data (quando a data vem primeiro) |

## Evidencias

- `vpn.log`
- `auth.log`
- `web.log`

## Pergunta

Monte a linha do tempo. Qual conta o invasor usou **primeiro** para entrar na rede?

Responda com `lab responder 47 "sua resposta"`. Travou? `lab dica 47`.
