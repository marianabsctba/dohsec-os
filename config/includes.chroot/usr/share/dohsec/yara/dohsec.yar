// Regras YARA do Inspetor de Arquivos do D'OH!Sec OS.
// Sinais genericos, para ensinar o que olhar; nao substituem um antivirus.

rule Executavel_Windows
{
    meta:
        descricao = "Programa do Windows (cabecalho MZ/PE)"
        nivel = "alerta"
    condition:
        uint16(0) == 0x5A4D
}

rule Executavel_Linux
{
    meta:
        descricao = "Programa do Linux (cabecalho ELF)"
        nivel = "alerta"
    condition:
        uint32(0) == 0x464C457F
}

rule PowerShell_Codificado
{
    meta:
        descricao = "Comando de PowerShell escondido em base64 (-enc)"
        nivel = "risco"
    strings:
        $a = /powershell(\.exe)?[^\n]{0,60}-e(nc|ncodedcommand)?\s+[A-Za-z0-9+\/=]{40,}/ nocase
    condition:
        $a
}

rule Download_E_Execucao
{
    meta:
        descricao = "Baixa algo da internet e executa em seguida"
        nivel = "risco"
    strings:
        $a = "DownloadString" nocase
        $b = "IEX" nocase
        $c = /curl[^\n]{0,80}\|\s*(ba)?sh/ nocase
        $d = /wget[^\n]{0,80}\|\s*(ba)?sh/ nocase
    condition:
        ($a and $b) or $c or $d
}

rule Macro_Office
{
    meta:
        descricao = "Documento do Office com macro (VBA)"
        nivel = "alerta"
    strings:
        $a = "vbaProject.bin" nocase
        $b = "AutoOpen" nocase
        $c = "Document_Open" nocase
    condition:
        any of them
}

rule Nota_De_Resgate_Donut
{
    meta:
        descricao = "Nota de resgate do grupo Donut (casos do laboratorio)"
        nivel = "risco"
    strings:
        $nota = "DONUT_RANSOM"
        $marca = { 44 4F 48 21 }
    condition:
        $nota and $marca
}
