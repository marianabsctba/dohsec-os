# Aula 3: procurando com grep

Logs tem milhares de linhas. Ninguem le tudo: a gente procura.

| Comando | O que faz | Exemplo |
| --- | --- | --- |
| `less` | abre arquivo grande para rolar (q sai, / procura) | `less turno.log` |
| `head` / `tail` | mostram o comeco / o fim | `tail -5 turno.log` |
| `grep` | mostra so as linhas com uma palavra | `grep cafe turno.log` |
| `grep -n` | mostra tambem o numero da linha | `grep -n cafe turno.log` |
| `grep -i` | ignora maiusculas e minusculas | `grep -i CAFE turno.log` |

## Desafio

O `turno.log` tem 600 linhas de rotina e uma linha de ALERTA.
Em qual numero de linha esta o alerta?

Responda com `lab responder 3 "sua resposta"`. Travou? `lab dica 3`.
