# Arquivo escondido dentro da imagem

Da para 'colar' um arquivo no fim de outro: a imagem abre normal, mas carrega um
segredo. O `binwalk` procura assinaturas de arquivos dentro de arquivos.

| Comando | O que faz |
| --- | --- |
| `binwalk arq` | lista o que tem dentro e em que posicao |
| `binwalk -e arq` | extrai o que achar |
| `unzip -l arq` | lista um zip (mesmo com dados antes) |

## Evidencias

- `logo-usina.png`

## Pergunta

O logo do site da usina esta maior do que deveria. Qual codigo de acesso esta escondido nele?

Responda com `lab responder 33 "sua resposta"`. Travou? `lab dica 33`.
