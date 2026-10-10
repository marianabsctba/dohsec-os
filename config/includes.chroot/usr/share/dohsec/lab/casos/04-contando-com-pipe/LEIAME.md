# Aula 4: contando com pipe

O pipe (`|`) liga comandos: a saida de um vira a entrada do outro.
E como uma esteira da fabrica de donuts.

| Comando | O que faz | Exemplo |
| --- | --- | --- |
| `wc -l` | conta linhas | `wc -l bombas.log` |
| `A \| B` | passa a saida de A para B | `grep OK bombas.log \| wc -l` |

Leia o exemplo assim: "pegue as linhas com OK e conte quantas sao".

## Desafio

Quantas vezes as bombas de resfriamento registraram FALHA no `bombas.log`?

Responda com `lab responder 4 "sua resposta"`. Travou? `lab dica 4`.
