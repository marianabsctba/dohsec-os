# Container privilegiado suspeito

Alguem subiu um container "de metricas" no `usina-docker01` sem passar pela TI. Container
**privilegiado** e com a raiz do servidor montada (`/:/host`) nao isola nada: quem controla o container
controla o servidor inteiro. Voce tem o `docker ps` e o `docker inspect` de todos.

## Evidencias

- `docker-ps.txt`
- `inspect.json`

## Pergunta

Qual container roda privilegiado? (o nome, sem a barra /)

Responda com `lab responder 43 "sua resposta"`. Travou? `lab dica 43`.
