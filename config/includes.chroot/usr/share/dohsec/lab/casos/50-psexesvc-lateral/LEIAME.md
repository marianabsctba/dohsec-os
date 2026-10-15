# Movimentacao lateral com PSEXESVC

Um invasor que entra numa maquina tenta pular para as outras (**movimentacao lateral**).
Uma forma comum no Windows deixa rastro claro: o servico **PSEXESVC** e instalado em cada maquina
alcancada (evento **7045**, "servico instalado"). O arquivo junta os eventos 7045 exportados de cada
maquina, uma depois da outra: a ordem do arquivo NAO e a ordem do tempo.

## Evidencias

- `servicos.csv`

## Pergunta

Em qual maquina o PSEXESVC apareceu PRIMEIRO? (o nome do computador)

Responda com `lab responder 50 "sua resposta"`. Travou? `lab dica 50`.
