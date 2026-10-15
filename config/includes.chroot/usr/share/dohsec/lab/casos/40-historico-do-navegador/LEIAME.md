# Historico do navegador

O Lenny jura que nao clicou no link do e-mail falso que chegou as **09:12**. O historico do Firefox
dele (`places.sqlite`) e um banco de dados SQLite: da para consultar com SQL pelo `sqlite3`.
As datas estao em **microssegundos desde 1970** (formato do Firefox).

| Comando | O que faz |
| --- | --- |
| `sqlite3 places.sqlite '.tables'` | lista as tabelas |
| `sqlite3 places.sqlite '.schema moz_places'` | mostra as colunas |
| `sqlite3 places.sqlite 'SELECT ... ;'` | roda uma consulta |

Para mostrar a data legivel: `datetime(visit_date/1000000, 'unixepoch', 'localtime')`.

## Evidencias

- `places.sqlite`

## Pergunta

Qual dominio o Lenny visitou logo depois do e-mail das 09:12?

Responda com `lab responder 40 "sua resposta"`. Travou? `lab dica 40`.
