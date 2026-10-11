# O maior download do dia

O decimo campo do log web e o tamanho da resposta em bytes. Downloads enormes e
fora do padrao merecem atencao.

| Comando | O que faz |
| --- | --- |
| `awk '{print $10, $7}' access.log` | tamanho e pagina de cada pedido |
| `sort -n` | ordena por numero |
| `tail -1` | fica com o ultimo (o maior) |

## Evidencias

- `access.log`

## Pergunta

Qual arquivo (caminho na URL) foi o maior download do dia?

Responda com `lab responder 30 "sua resposta"`. Travou? `lab dica 30`.
