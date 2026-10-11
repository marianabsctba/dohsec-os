# RDP publico com fornecedor admin

Um fornecedor ganhou acesso "temporario" de area de trabalho remota (RDP, porta 3389) em 2023
e ninguem tirou. O RDP so deveria ser usado pela VPN (rede 10.99.x.x). Voce tem as regras de NAT
do firewall e os logons do Windows (evento **4624**; LogonType **10** = area de trabalho remota).

## Evidencias

- `nat-firewall.txt`
- `logons.csv`

## Pergunta

Qual conta entrou por RDP vindo direto da internet (de fora da VPN)?

Responda com `lab responder 35 "sua resposta"`. Travou? `lab dica 35`.
