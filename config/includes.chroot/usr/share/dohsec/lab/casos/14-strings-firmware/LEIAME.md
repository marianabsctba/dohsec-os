# Achando texto com strings

Arquivos binarios (programas, firmwares) tem texto escondido no meio dos bytes:
mensagens, versoes e, as vezes, senhas esquecidas pelo fabricante.

| Comando | O que faz |
| --- | --- |
| `strings arq` | mostra os trechos de texto legivel |
| `strings arq \| grep -i senha` | so os que interessam |

## Evidencias

- `firmware-painel.bin`

## Pergunta

O firmware do painel do reator tem uma senha padrao embutida. Qual e?

Responda com `lab responder 14 "sua resposta"`. Travou? `lab dica 14`.
