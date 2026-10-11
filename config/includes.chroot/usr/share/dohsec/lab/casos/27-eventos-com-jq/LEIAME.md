# Eventos em JSON com jq

Sistemas de nuvem e de seguranca registram eventos em JSON, um por linha.
O `jq` filtra e formata JSON no terminal.

| Comando | O que faz |
| --- | --- |
| `jq . arq.json` | mostra formatado |
| `jq -c 'select(.evento=="X")' arq.json` | so os eventos X |
| `jq -r '.ip' arq.json` | so o campo ip |

## Evidencias

- `eventos.json`

## Pergunta

Alguem apagou os backups da usina na nuvem. De qual IP veio o evento ApagarBackup?

Responda com `lab responder 27 "sua resposta"`. Travou? `lab dica 27`.
