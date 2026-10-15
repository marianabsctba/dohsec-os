# O arquivo apagado do pendrive

Um pendrive da sala de controle foi achado na lixeira. Alguem **apagou** um arquivo antes de jogar
fora. Apagar no FAT so marca a entrada como livre: o conteudo continua la ate ser sobrescrito.
O Sleuth Kit le a imagem do disco (`pendrive.img`) sem precisar montar nada.

| Comando | O que faz |
| --- | --- |
| `fsstat pendrive.img` | o tipo de sistema de arquivos |
| `fls -r pendrive.img` | lista os arquivos; os apagados aparecem com `*` |
| `fls -rd pendrive.img` | so os apagados |
| `icat pendrive.img NUMERO` | mostra o conteudo pelo numero (inode) que o fls mostrou |

No FAT, o nome apagado perde a primeira letra (vira `_`).

## Evidencias

- `pendrive.img`

## Pergunta

Qual e a senha do cofre escrita no arquivo apagado?

Responda com `lab responder 53 "sua resposta"`. Travou? `lab dica 53`.
