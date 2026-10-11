# Extensao mente, conteudo nao

A extensao (.jpg, .pdf) e so parte do nome: qualquer um muda. O comando `file`
olha o conteudo de verdade (os primeiros bytes, a 'assinatura').

| Comando | O que faz |
| --- | --- |
| `file arq` | diz o tipo real |
| `file pasta/*` | de todos |
| `xxd arq \| head` | mostra os bytes em hexadecimal |

## Evidencias

- `anexos/relatorio.pdf`
- `anexos/foto-do-turno.jpg`
- `anexos/apresentacao.png`
- `anexos/musica-do-intervalo.mp3`
- `anexos/notas.txt`

## Pergunta

Um dos anexos esta disfarcado: na verdade e um arquivo ZIP. Qual?

Responda com `lab responder 13 "sua resposta"`. Travou? `lab dica 13`.
