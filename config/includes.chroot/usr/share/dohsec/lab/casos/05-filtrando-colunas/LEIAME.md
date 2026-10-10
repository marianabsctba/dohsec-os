# Aula 5: filtrando colunas

Arquivos CSV sao tabelas: cada linha e um registro e as colunas sao separadas por virgula.

| Comando | O que faz | Exemplo |
| --- | --- | --- |
| `cut -d, -f2` | pega a 2a coluna (separador virgula) | `cut -d, -f2 cracha.csv` |
| `sort` | ordena | `... \| sort` |
| `uniq -c` | junta repetidos e conta | `... \| sort \| uniq -c` |
| `sort -rn` | ordena por numero, do maior para o menor | `... \| sort -rn` |
| `head -1` | fica so com a primeira linha | `... \| head -1` |

Essa receita (`cut | sort | uniq -c | sort -rn`) e a mais usada em analise de log. Guarde ela.

## Desafio

O `cracha.csv` registra cada passagem de cracha.
Quem passou o cracha mais vezes?

Responda com `lab responder 5 "sua resposta"`. Travou? `lab dica 5`.
