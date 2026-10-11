#!/usr/bin/env python3
"""Gera as imagens XPM do tema de janelas (xfwm4) Springfield.

Uso: python3 scripts/gen-xfwm4-theme.py
Escreve em config/includes.chroot/usr/share/themes/Springfield/xfwm4/.

As janelas de fora do front (Wireshark, terminal do Ctrl+Alt+T) imitam as janelas do front:
borda preta, barra em degrade rosa -> laranja (amarela quando inativa), titulo branco e os
botoes quadrados estilo XP (cinza para _ e [], vermelho para x).
"""
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "config/includes.chroot/usr/share/themes/Springfield/xfwm4"

TITLE_H = 30          # .titlebar do front
BORDER = 4            # 2 px de contorno preto + 2 px da cor da janela
LARGURA_DEGRADE = 1920  # o xfwm4 repete a imagem: mais larga que a tela, para nao repetir
RAMPA = 600              # o degrade chega ao laranja em 600 px e segue laranja ate os botoes
BTN_W = 24            # botao de 21 px + espaco
BTN = 21

CONTORNO = "#111111"
FUNDO_JANELA = "#ece9d8"
# Degrade da barra: igual ao .titlebar (inativa) e .active-window .titlebar (ativa) do front
DEGRADE = {"active": ("#ff5fb7", "#f4b400"), "inactive": ("#ffcf2e", "#f4b400")}

# Botoes: (cima-esquerda, baixo-direita) do degrade diagonal, por estado
CINZA = {"normal": ("#d0d0d0", "#b0b0b0"), "prelight": ("#e0e0e0", "#c0c0c0"), "pressed": ("#b0b0b0", "#d0d0d0")}
VERMELHO = {"normal": ("#e03030", "#c02020"), "prelight": ("#f04040", "#d03030"), "pressed": ("#c02020", "#e03030")}


def hex_rgb(c):
    return tuple(int(c[i:i + 2], 16) for i in (1, 3, 5))


def rgb_hex(rgb):
    return "#%02x%02x%02x" % tuple(max(0, min(255, round(v))) for v in rgb)


def mistura(a, b, t):
    a, b = hex_rgb(a), hex_rgb(b)
    return rgb_hex(tuple(a[i] * (1 - t) + b[i] * t for i in range(3)))


def escreve_xpm(nome, pixels):
    h, w = len(pixels), len(pixels[0])
    cores = sorted({c for linha in pixels for c in linha})
    simbolos = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+-*/=!?<>()[]{}"
    cpp = 1 if len(cores) <= len(simbolos) else 2
    codigo = {}
    for i, c in enumerate(cores):
        codigo[c] = simbolos[i] if cpp == 1 else simbolos[i // len(simbolos)] + simbolos[i % len(simbolos)]
    linhas = [f'"{w} {h} {len(cores)} {cpp}",']
    linhas += [f'"{codigo[c]} c {c}",' for c in cores]
    linhas += ['"' + "".join(codigo[c] for c in linha) + '",' for linha in pixels]
    linhas[-1] = linhas[-1].rstrip(",")
    var = nome.replace("-", "_")
    (OUT / f"{nome}.xpm").write_text(
        "/* XPM */\nstatic char * " + var + "_xpm[] = {\n" + "\n".join(linhas) + "\n};\n",
        newline="\n",
    )


def barra(cor, w):
    """Faixa da barra de titulo com o contorno preto em cima."""
    return [[CONTORNO if y < 2 else cor] * w for y in range(TITLE_H)]


def barra_degrade(estado, w):
    a, b = DEGRADE[estado]
    cores = [mistura(a, b, min(1.0, x / RAMPA)) for x in range(w)]
    return [[CONTORNO] * w if y < 2 else list(cores) for y in range(TITLE_H)]


def canto_superior(estado, lado):
    cor = DEGRADE[estado][0 if lado == "left" else 1]
    pixels = barra(cor, BORDER)
    for y in range(TITLE_H):
        for x in range(BORDER):
            borda_externa = x < 2 if lado == "left" else x >= BORDER - 2
            if borda_externa:
                pixels[y][x] = CONTORNO
    return pixels


def lateral(lado, altura=1):
    linha = [CONTORNO, CONTORNO, FUNDO_JANELA, FUNDO_JANELA]
    if lado == "right":
        linha = linha[::-1]
    return [list(linha) for _ in range(altura)]


def glifo(tipo, x, y):
    """x, y dentro do quadrado do botao (0..BTN-1)."""
    meio = (BTN - 1) / 2
    if tipo == "close":
        dx, dy = x - meio, y - meio
        return abs(abs(dx) - abs(dy)) < 1.0 and abs(dx) <= 4.5
    if tipo == "hide":
        return 13 <= y <= 14 and 6 <= x <= 14
    if tipo == "maximize":
        dentro = 5 <= x <= 15 and 5 <= y <= 15
        borda = x in (5, 15) or y in (5, 15) or y == 6
        return dentro and borda
    if tipo == "maximize-toggled":
        tras = (8 <= x <= 15 and 4 <= y <= 11) and (x in (8, 15) or y in (4, 5, 11))
        frente = (5 <= x <= 12 and 8 <= y <= 15) and (x in (5, 12) or y in (8, 9, 15))
        miolo_frente = 6 <= x <= 11 and 10 <= y <= 14
        return frente or (tras and not miolo_frente and not (5 <= x <= 12 and 8 <= y <= 15))
    if tipo == "menu":
        return 7 <= x <= 13 and y in (7, 10, 13)
    if tipo.startswith("shade"):
        return 6 <= x <= 14 and y in (6, 7)
    if tipo.startswith("stick"):
        return (x - meio) ** 2 + (y - meio) ** 2 <= 6
    return False


def botao(tipo, estado, modo):
    """Botao quadrado com bisel, sobre a cor do fim do degrade (canto direito da barra)."""
    fundo = DEGRADE[estado][1]
    pixels = barra(fundo, BTN_W)
    claro, escuro = (VERMELHO if tipo == "close" else CINZA)[modo]
    cor_glifo = "#ffffff" if tipo == "close" else "#000000"
    x0 = (BTN_W - BTN) // 2
    y0 = 2 + (TITLE_H - 2 - BTN) // 2
    afundado = modo == "pressed"
    for y in range(BTN):
        for x in range(BTN):
            canto = (x in (0, BTN - 1)) and (y in (0, BTN - 1))
            if canto:
                continue
            if (y == 0 or x == 0) and not afundado or (y == BTN - 1 or x == BTN - 1) and afundado:
                c = "#ffffff"
            elif (y == BTN - 1 or x == BTN - 1) and not afundado or (y == 0 or x == 0) and afundado:
                c = "#555555"
            elif glifo(tipo, x, y):
                c = cor_glifo
            else:
                c = mistura(claro, escuro, (x + y) / (2 * (BTN - 1)))
            pixels[y0 + y][x0 + x] = c
    return pixels


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for velho in OUT.glob("*.xpm"):
        velho.unlink()
    for estado in ("active", "inactive"):
        inicio, fim = DEGRADE[estado]
        escreve_xpm(f"title-1-{estado}", barra(inicio, 2))
        escreve_xpm(f"title-2-{estado}", barra(inicio, 2))
        escreve_xpm(f"title-3-{estado}", barra_degrade(estado, LARGURA_DEGRADE))
        escreve_xpm(f"title-4-{estado}", barra(fim, 2))
        escreve_xpm(f"title-5-{estado}", barra(fim, 2))
        escreve_xpm(f"top-left-{estado}", canto_superior(estado, "left"))
        escreve_xpm(f"top-right-{estado}", canto_superior(estado, "right"))
        escreve_xpm(f"left-{estado}", lateral("left"))
        escreve_xpm(f"right-{estado}", lateral("right"))
        escreve_xpm(f"bottom-{estado}", [[FUNDO_JANELA]] * 2 + [[CONTORNO]] * 2)
        canto = [[CONTORNO] * BORDER for _ in range(BORDER)]
        for y in range(2):
            for x in range(2, BORDER):
                canto[y][x] = FUNDO_JANELA
        escreve_xpm(f"bottom-left-{estado}", canto)
        escreve_xpm(f"bottom-right-{estado}", [linha[::-1] for linha in canto])

    tipos = ["close", "hide", "maximize", "maximize-toggled", "menu", "shade", "shade-toggled", "stick", "stick-toggled"]
    for tipo in tipos:
        escreve_xpm(f"{tipo}-active", botao(tipo, "active", "normal"))
        escreve_xpm(f"{tipo}-prelight", botao(tipo, "active", "prelight"))
        escreve_xpm(f"{tipo}-pressed", botao(tipo, "active", "pressed"))
        escreve_xpm(f"{tipo}-inactive", botao(tipo, "inactive", "normal"))

    (OUT / "themerc").write_text(
        "active_text_color=#ffffff\n"
        "inactive_text_color=#ffffff\n"
        "title_alignment=left\n"
        "full_width_title=true\n"
        "button_offset=2\n"
        "button_spacing=0\n"
        "title_horizontal_offset=6\n"
        "title_vertical_offset_active=1\n"
        "title_vertical_offset_inactive=1\n"
        "title_shadow_active=true\n"
        "title_shadow_inactive=true\n"
        "active_text_shadow_color=#000000\n"
        "inactive_text_shadow_color=#000000\n"
        "shadow_delta_height=2\n",
        newline="\n",
    )
    print(f"{len(list(OUT.glob('*.xpm')))} imagens em {OUT}")


if __name__ == "__main__":
    main()
