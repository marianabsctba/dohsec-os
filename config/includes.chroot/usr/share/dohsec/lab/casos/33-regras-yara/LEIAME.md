# Cacando com regras YARA

YARA descreve 'cara de malware' em regras: textos e bytes que precisam aparecer.
Equipes de seguranca do mundo todo compartilham regras assim.

| Comando | O que faz |
| --- | --- |
| `cat regra.yar` | le a regra |
| `yara regra.yar pasta/` | testa todos os arquivos da pasta |
| `yara -s regra.yar arq` | mostra onde bateu |

## Evidencias

- `amostras/arquivo-01.dat`
- `amostras/arquivo-02.dat`
- `amostras/arquivo-03.dat`
- `amostras/arquivo-04.dat`
- `amostras/arquivo-05.dat`
- `amostras/arquivo-06.dat`
- `amostras/arquivo-07.dat`
- `amostras/arquivo-08.dat`
- `amostras/arquivo-09.dat`
- `amostras/arquivo-10.dat`
- `donut.yar`

## Pergunta

Use a regra `donut.yar` nas amostras. Qual arquivo bate com a regra?

Responda com `lab responder 33 "sua resposta"`. Travou? `lab dica 33`.
