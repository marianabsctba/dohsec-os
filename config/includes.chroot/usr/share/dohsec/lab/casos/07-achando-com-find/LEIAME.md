# Achando arquivos com find

Quando nao sabemos onde um arquivo esta, o `find` procura pasta por pasta.

| Comando | O que faz |
| --- | --- |
| `find PASTA -name 'nome'` | procura pelo nome |
| `find PASTA -name '*.bak'` | o * vale qualquer coisa: todos os .bak |
| `find PASTA -type f` | so arquivos (sem pastas) |
| `tree PASTA` | mostra a arvore de pastas |

## Evidencias

- `arquivo-morto/2019/janeiro/caixa-1/inventario.txt`
- `arquivo-morto/2019/janeiro/caixa-2/inventario.txt`
- `arquivo-morto/2019/janeiro/caixa-3/inventario.txt`
- `arquivo-morto/2019/marco/caixa-1/inventario.txt`
- `arquivo-morto/2019/marco/caixa-2/inventario.txt`
- `arquivo-morto/2019/marco/caixa-3/inventario.txt`
- `arquivo-morto/2019/julho/caixa-1/inventario.txt`
- `arquivo-morto/2019/julho/caixa-2/inventario.txt`
- `arquivo-morto/2019/julho/caixa-3/inventario.txt`
- `arquivo-morto/2019/outubro/caixa-1/inventario.txt`
- `arquivo-morto/2019/outubro/caixa-2/inventario.txt`
- `arquivo-morto/2019/outubro/caixa-3/inventario.txt`
- `arquivo-morto/2020/janeiro/caixa-1/inventario.txt`
- `arquivo-morto/2020/janeiro/caixa-2/inventario.txt`
- `arquivo-morto/2020/janeiro/caixa-3/inventario.txt`
- `arquivo-morto/2020/marco/caixa-1/inventario.txt`
- `arquivo-morto/2020/marco/caixa-2/inventario.txt`
- `arquivo-morto/2020/marco/caixa-3/inventario.txt`
- `arquivo-morto/2020/julho/caixa-1/inventario.txt`
- `arquivo-morto/2020/julho/caixa-2/inventario.txt`
- `arquivo-morto/2020/julho/caixa-3/inventario.txt`
- `arquivo-morto/2020/outubro/caixa-1/inventario.txt`
- `arquivo-morto/2020/outubro/caixa-2/inventario.txt`
- `arquivo-morto/2020/outubro/caixa-3/inventario.txt`
- `arquivo-morto/2021/janeiro/caixa-1/inventario.txt`
- `arquivo-morto/2021/janeiro/caixa-2/inventario.txt`
- `arquivo-morto/2021/janeiro/caixa-3/inventario.txt`
- `arquivo-morto/2021/marco/caixa-1/inventario.txt`
- `arquivo-morto/2021/marco/caixa-2/inventario.txt`
- `arquivo-morto/2021/marco/caixa-3/inventario.txt`
- `arquivo-morto/2021/julho/caixa-1/inventario.txt`
- `arquivo-morto/2021/julho/caixa-2/inventario.txt`
- `arquivo-morto/2021/julho/caixa-3/inventario.txt`
- `arquivo-morto/2021/outubro/caixa-1/inventario.txt`
- `arquivo-morto/2021/outubro/caixa-2/inventario.txt`
- `arquivo-morto/2021/outubro/caixa-3/inventario.txt`
- `arquivo-morto/2020/julho/caixa-2/.planta-do-reator.bak`

## Pergunta

Ha um arquivo de backup (`.bak`) perdido no `arquivo-morto`. Qual o nome dele?

Responda com `lab responder 7 "sua resposta"`. Travou? `lab dica 7`.
