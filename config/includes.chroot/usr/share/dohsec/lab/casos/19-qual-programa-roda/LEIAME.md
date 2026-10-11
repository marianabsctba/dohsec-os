# Qual programa roda de verdade?

Quando voce digita um comando, o sistema procura o programa nas pastas do `PATH`,
na ordem. Invasores tentam colocar um programa falso antes do verdadeiro.

| Comando | O que faz |
| --- | --- |
| `echo $PATH` | mostra as pastas, na ordem |
| `which ls` | qual arquivo roda quando voce digita ls |
| `type ls` | idem, e avisa se e alias |

## Evidencias

- (nenhum arquivo: use o proprio sistema)

## Pergunta

Neste sistema, qual arquivo (caminho completo) roda quando voce digita `ls`?

Responda com `lab responder 19 "sua resposta"`. Travou? `lab dica 19`.
