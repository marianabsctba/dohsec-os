# Credencial em memoria suspeita

O **lsass.exe** guarda as credenciais de quem esta logado no Windows. Por isso, programa estranho
lendo a memoria dele e alarme vermelho. O Sysmon registra cada acesso a outro processo (**evento 10**):
quem acessou (SourceImage), quem foi acessado (TargetImage) e com quais permissoes (GrantedAccess).
Antivirus e processos do sistema acessam o lsass o tempo todo: isso e normal.

## Evidencias

- `sysmon-10.csv`

## Pergunta

Qual programa fora do normal acessou o lsass.exe? (caminho completo)

Responda com `lab responder 51 "sua resposta"`. Travou? `lab dica 51`.
