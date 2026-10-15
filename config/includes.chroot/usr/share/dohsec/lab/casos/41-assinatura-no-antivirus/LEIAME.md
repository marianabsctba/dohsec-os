# Assinatura propria no antivirus

O CERT da usina descobriu um "dropper" (programa que baixa e roda outro) e mandou uma
**assinatura** para o ClamAV: o arquivo `usina.ndb`. Com ela, o antivirus reconhece o malware mesmo sem
internet e sem a base oficial. Varra os anexos do e-mail recebidos esta semana.

| Comando | O que faz |
| --- | --- |
| `clamscan -d usina.ndb -r anexos/` | varre a pasta usando so a assinatura do CERT |
| `--infected` | mostra so o que foi detectado |
| `cat usina.ndb` | a assinatura: nome, tipo, posicao e os bytes em hexadecimal |

O ClamAV abre arquivos .zip sozinho e procura dentro deles.

## Evidencias

- `usina.ndb`
- `anexos/escala-00.txt`
- `anexos/planilha-01.txt`
- `anexos/relatorio-02.txt`
- `anexos/contrato-03.txt`
- `anexos/contrato-04.txt`
- `anexos/foto-05.txt`
- `anexos/planilha-06.txt`
- `anexos/contrato-07.txt`
- `anexos/escala-08.txt`
- `anexos/escala-09.txt`
- `anexos/foto-10.txt`
- `anexos/foto-11.txt`
- `anexos/planilha-12.txt`
- `anexos/foto-13.txt`
- `anexos/notas-fiscais-marco.zip`
- `anexos/confraternizacao.zip`

## Pergunta

Qual anexo o ClamAV detectou com a assinatura do CERT? (o nome do arquivo)

Responda com `lab responder 41 "sua resposta"`. Travou? `lab dica 41`.
