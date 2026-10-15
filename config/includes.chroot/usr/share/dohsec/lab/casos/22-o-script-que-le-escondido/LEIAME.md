# O script que le escondido

O `reator-status.sh` diz que so mostra o status do reator, mas o time desconfia que ele mexe em
algum arquivo escondido. Em vez de decifrar o codigo, **observe o que ele faz**: o `strace` mostra cada
chamada que um programa faz ao sistema, inclusive cada arquivo que ele abre.

| Comando | O que faz |
| --- | --- |
| `strace -f -e trace=openat bash script.sh` | lista os arquivos que o script abre |
| `... 2>&1 \| grep -v -e /usr -e /lib -e /etc` | tira os arquivos do proprio sistema |

## Evidencias

- `reator-status.sh`
- `.cache/.usina/chaves-do-cofre.dat`
- `.cache/.usina/lixo-00.tmp`
- `.cache/.usina/lixo-01.tmp`
- `.cache/.usina/lixo-02.tmp`
- `.cache/.usina/lixo-03.tmp`
- `.cache/.usina/lixo-04.tmp`
- `.cache/.usina/lixo-05.tmp`
- `.cache/.usina/lixo-06.tmp`
- `.cache/.usina/lixo-07.tmp`

## Pergunta

Qual arquivo escondido o script le? (so o nome do arquivo)

Responda com `lab responder 22 "sua resposta"`. Travou? `lab dica 22`.
