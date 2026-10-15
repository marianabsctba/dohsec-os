# Qual download e legitimo?

Foram baixadas quatro versoes do controlador do reator, do site oficial e de um "espelho rapido".
Hash sozinho nao basta: quem troca o arquivo pode trocar a lista de hashes junto. Por isso o site oficial
**assina** a lista com GPG. Voce tem a chave publica oficial (`chave-oficial-usina.asc`).

| Comando | O que faz |
| --- | --- |
| `gpg --import chave-oficial-usina.asc` | importa a chave oficial |
| `gpg --verify SHA256SUMS.asc SHA256SUMS` | confere a assinatura da lista |
| `sha256sum -c SHA256SUMS --ignore-missing` | confere os arquivos contra a lista |

Atencao a mensagem do gpg: "Assinatura valida" ("Good signature") **de quem**? O aviso de chave nao
certificada e normal: confira a impressao digital da chave com a publicada em `site-oficial/impressao-digital-da-chave.txt`.
O `sha256sum -c` responde `SUCESSO` (ou `OK`) para o arquivo que bate.

## Evidencias

- `downloads/reator-ctl-1.1.tar.gz`
- `downloads/reator-ctl-1.2.tar.gz`
- `downloads/reator-ctl-1.3.tar.gz`
- `downloads/reator-ctl-1.4.tar.gz`
- `chave-oficial-usina.asc`
- `site-oficial/impressao-digital-da-chave.txt`
- `site-oficial/SHA256SUMS`
- `site-oficial/SHA256SUMS.asc`
- `espelho-rapido/SHA256SUMS`
- `espelho-rapido/SHA256SUMS.asc`

## Pergunta

Qual pacote tem a lista de hashes assinada pela chave oficial e o hash batendo? (o nome do arquivo)

Responda com `lab responder 52 "sua resposta"`. Travou? `lab dica 52`.
