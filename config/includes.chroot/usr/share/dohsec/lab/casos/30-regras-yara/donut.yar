rule DonutRansom
{
    meta:
        descricao = "Nota de resgate do grupo Donut"
    strings:
        $nota = "DONUT_RANSOM"
        $marca = { 44 4F 48 21 }   // "DOH!" em hexadecimal
    condition:
        $nota and $marca
}
