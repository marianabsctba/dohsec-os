# SSH exposto com root login

O `usina-srv02` aceita SSH de qualquer lugar e alguem entrou **direto como root**, com senha.
Na vida real o root nunca deveria entrar pelo SSH: cada pessoa entra com a propria conta e usa `sudo`
(fica registrado quem fez o que). Compare a configuracao do servidor com o que aconteceu.

## Evidencias

- `sshd_config`
- `ss-tlnp.txt`
- `auth.log`

## Pergunta

Qual linha do sshd_config permite entrar direto como root? (escreva a linha como esta no arquivo)

Responda com `lab responder 20 "sua resposta"`. Travou? `lab dica 20`.
