# Fotos de um cartao formatado

O cartao de memoria da camera da portaria foi **formatado** depois do incidente. Sem sistema de
arquivos, o `fls` nao ajuda. Mas as fotos continuam la, no meio dos bytes. O `foremost` faz **carving**:
procura os bytes de inicio e fim de cada tipo de arquivo (um JPEG comeca com `FF D8 FF`) e recorta.

| Comando | O que faz |
| --- | --- |
| `foremost -t jpg -i cartao.img -o recuperado` | recorta os JPEG para a pasta recuperado/ (ela nao pode existir antes) |
| `cat recuperado/audit.txt` | o resumo do que foi achado |
| `ls recuperado/jpg` | as fotos |

## Evidencias

- `cartao.img`

## Pergunta

Quantas fotos JPEG o foremost recupera do cartao?

Responda com `lab responder 54 "sua resposta"`. Travou? `lab dica 54`.
