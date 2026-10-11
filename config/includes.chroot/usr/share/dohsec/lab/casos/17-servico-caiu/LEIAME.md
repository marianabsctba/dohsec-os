# Qual servico caiu?

Servicos sao programas que rodam em segundo plano, gerenciados pelo `systemctl`.
Quando um cai, o `journalctl` registra.

| Comando | O que faz |
| --- | --- |
| `systemctl status SERVICO` | estado de um servico |
| `systemctl --failed` | servicos que falharam |
| `journalctl -u SERVICO` | log de um servico |

## Evidencias

- `journal.txt`

## Pergunta

O alarme de temperatura disparou. Qual servico falhou? (nome completo, com .service)

Responda com `lab responder 17 "sua resposta"`. Travou? `lab dica 17`.
