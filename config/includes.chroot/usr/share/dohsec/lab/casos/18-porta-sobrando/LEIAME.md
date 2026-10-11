# Porta que nao deveria estar aberta

Programas que esperam conexoes 'escutam' numa porta. O `ss` mostra quais.

| Comando | O que faz |
| --- | --- |
| `ss -tlnp` | portas TCP escutando, com o programa |
| `ss -tunap` | todas as conexoes |

## Evidencias

- `ss-tlnp.txt`
- `inventario.txt`

## Pergunta

Compare as portas escutando com o inventario autorizado. Qual porta esta sobrando?

Responda com `lab responder 18 "sua resposta"`. Travou? `lab dica 18`.
