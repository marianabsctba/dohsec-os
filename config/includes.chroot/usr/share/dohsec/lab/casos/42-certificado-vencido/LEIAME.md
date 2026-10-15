# Certificado vencido

Desde ontem o navegador mostra **"Sua conexao nao e particular"** num dos sistemas internos, e o
pessoal esta clicando em "aceitar o risco". O time exportou os certificados TLS dos servidores.
Certificado tem validade: depois da data **notAfter**, deixa de valer.

| Comando | O que faz |
| --- | --- |
| `openssl x509 -in ARQ.pem -noout -subject -dates` | para quem e o certificado e as datas |
| `openssl x509 -in ARQ.pem -noout -checkend 0` | diz se ja venceu |
| `openssl x509 -in ARQ.pem -noout -text` | tudo |

## Evidencias

- `certs/intranet.pem`
- `certs/mail.pem`
- `certs/ponto.pem`
- `certs/wiki.pem`
- `certs/cardapio.pem`

## Pergunta

Qual certificado esta vencido? (o nome do arquivo)

Responda com `lab responder 42 "sua resposta"`. Travou? `lab dica 42`.
