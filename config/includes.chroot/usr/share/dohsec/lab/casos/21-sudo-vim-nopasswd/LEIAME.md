# sudo -l com vim NOPASSWD

A auditoria exportou o `sudo -l` de todo mundo. Algumas regras parecem inocentes:
"so pode editar UM arquivo". Mas um editor como o vim, rodando como root, consegue abrir outros arquivos
e ate um terminal: na pratica a pessoa vira root, e sem senha.
O smithers e administrador de proposito (ALL), entao ele nao conta.

## Evidencias

- `sudo-l.txt`

## Pergunta

Qual usuario, alem do smithers, na pratica pode virar root sem senha?

Responda com `lab responder 21 "sua resposta"`. Travou? `lab dica 21`.
