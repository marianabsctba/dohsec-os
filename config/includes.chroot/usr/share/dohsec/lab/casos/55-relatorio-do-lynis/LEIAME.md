# O relatorio do Lynis

O Lynis faz uma auditoria de endurecimento: roda centenas de testes e da uma nota (hardening index).
O relatorio da maquina `usina-srv02` foi salvo em `lynis-report.dat`. Cada achado tem o **codigo do teste**,
e e por ele que se procura a explicacao e a correcao.

| Onde | O que tem |
| --- | --- |
| `warning[]=` | avisos: problemas para corrigir logo |
| `suggestion[]=` | sugestoes de melhoria |
| `hardening_index=` | a nota de 0 a 100 |

Depois, rode na sua maquina: `sudo lynis audit system` (leva alguns minutos) e compare.

## Evidencias

- `lynis-report.dat`

## Pergunta

Qual o codigo do teste do Lynis que avisou que o SSH deixa o root entrar?

Responda com `lab responder 55 "sua resposta"`. Travou? `lab dica 55`.
