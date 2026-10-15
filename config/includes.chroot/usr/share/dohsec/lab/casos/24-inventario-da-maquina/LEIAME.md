# Inventario da propria maquina

Antes de defender uma maquina, saiba o que ela expoe. O `nmap` testa portas e diz quais estao
abertas, como um invasor veria. Aqui o alvo e **a sua propria maquina** (`127.0.0.1`): nunca escaneie
redes de outras pessoas sem autorizacao.

O D'OH!Sec roda servicos locais que fazem o desktop funcionar. Descubra quais portas eles usam.
Este caso e para o D'OH!Sec completo (ISO ou VM): no WSL esses servicos nao existem.

| Comando | O que faz |
| --- | --- |
| `nmap 127.0.0.1` | as 1000 portas mais comuns |
| `nmap -p 7000-8000 127.0.0.1` | so uma faixa de portas |
| `nmap -sV -p PORTA 127.0.0.1` | tenta descobrir o servico (-sV) |
| `sudo ss -tlnp` | confirma pelo proprio sistema qual programa escuta |

## Evidencias

- (nenhum arquivo: use o proprio sistema)

## Pergunta

Quantas portas TCP abertas o nmap encontra em 127.0.0.1 entre 7000 e 8000?

Responda com `lab responder 24 "sua resposta"`. Travou? `lab dica 24`.
