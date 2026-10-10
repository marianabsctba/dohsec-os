#!/usr/bin/env python3
"""Gera as imagens XPM do tema de janelas (xfwm4) Springfield.

Uso: python3 scripts/gen-xfwm4-theme.py
Escreve em config/includes.chroot/usr/share/themes/Springfield/xfwm4/.
"""
import math
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "config/includes.chroot/usr/share/themes/Springfield/xfwm4"

TITLE_H = 28
BORDER = 4
BTN_W = 24
BTN_R = 8

PALETA = {
    "active": {"frame": "#5b3518", "title": "#ffd84d"},
    "inactive": {"frame": "#a07850", "title": "#fff6d7"},
}

# cor do botao por estado: (normal, prelight, pressed)
BOTOES = {
    "close": ("#ff5fb7", "#ff8fcb", "#d43f93"),
    "maximize": ("#2f7df6", "#6fa6ff", "#1f5fc4"),
    "maximize-toggled": ("#2f7df6", "#6fa6ff", "#1f5fc4"),
    "hide": ("#3bb273", "#5fd394", "#2a8a57"),
    "shade": ("#ff9b30", "#ffb866", "#d47a1a"),
    "shade-toggled": ("#ff9b30", "#ffb866", "#d47a1a"),
    "stick": ("#ff9b30", "#ffb866", "#d47a1a"),
    "stick-toggled": ("#ff9b30", "#ffb866", "#d47a1a"),
    "menu": ("#d9a066", "#e8b884", "#b8834c"),
}
INATIVO = "#c8b89a"
GLIFO = "#ffffff"


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


def faixa_titulo(estado, w):
    p = PALETA[estado]
    return [[p["frame"] if y < 2 else p["title"]] * w for y in range(TITLE_H)]


def no_glifo(tipo, x, y):
    """x, y relativos ao centro do botao, em pixels."""
    if tipo == "close":
        return abs(abs(x) - abs(y)) < 1.1 and abs(x) < 4.2
    if tipo.startswith("maximize"):
        borda = 4.0 if tipo == "maximize" else 3.0
        return max(abs(x), abs(y)) < borda and max(abs(x), abs(y)) > borda - 1.6
    if tipo == "hide":
        return abs(y - 1.5) < 1.0 and abs(x) < 4.2
    if tipo == "menu":
        return math.hypot(x, y) < 2.6
    return math.hypot(x, y) < 2.2


def botao(tipo, estado, cor):
    fundo = PALETA[estado]["title"]
    cx, cy = BTN_W / 2, 2 + (TITLE_H - 2) / 2
    pixels = faixa_titulo(estado, BTN_W)
    amostras = 4
    for py in range(2, TITLE_H):
        for px in range(BTN_W):
            acumulado = [0.0, 0.0, 0.0]
            for sy in range(amostras):
                for sx in range(amostras):
                    x = px + (sx + 0.5) / amostras - cx
                    y = py + (sy + 0.5) / amostras - cy
                    if math.hypot(x, y) <= BTN_R:
                        c = GLIFO if (estado == "active" and no_glifo(tipo, x, y)) else cor
                    else:
                        c = fundo
                    r, g, b = hex_rgb(c)
                    acumulado[0] += r
                    acumulado[1] += g
                    acumulado[2] += b
            n = amostras * amostras
            pixels[py][px] = rgb_hex(tuple(v / n for v in acumulado))
    return pixels


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for estado in ("active", "inactive"):
        frame = PALETA[estado]["frame"]
        for i in range(1, 6):
            escreve_xpm(f"title-{i}-{estado}", faixa_titulo(estado, BORDER))
        escreve_xpm(f"top-left-{estado}", [[frame] * BORDER for _ in range(TITLE_H)])
        escreve_xpm(f"top-right-{estado}", [[frame] * BORDER for _ in range(TITLE_H)])
        escreve_xpm(f"left-{estado}", [[frame] * BORDER])
        escreve_xpm(f"right-{estado}", [[frame] * BORDER])
        escreve_xpm(f"bottom-{estado}", [[frame] for _ in range(BORDER)])
        escreve_xpm(f"bottom-left-{estado}", [[frame] * BORDER for _ in range(BORDER)])
        escreve_xpm(f"bottom-right-{estado}", [[frame] * BORDER for _ in range(BORDER)])

    for tipo, (normal, prelight, pressed) in BOTOES.items():
        escreve_xpm(f"{tipo}-active", botao(tipo, "active", normal))
        escreve_xpm(f"{tipo}-prelight", botao(tipo, "active", prelight))
        escreve_xpm(f"{tipo}-pressed", botao(tipo, "active", pressed))
        escreve_xpm(f"{tipo}-inactive", botao(tipo, "inactive", INATIVO))

    (OUT / "themerc").write_text(
        "active_text_color=#171717\n"
        "inactive_text_color=#7a5a3a\n"
        "title_alignment=center\n"
        "full_width_title=true\n"
        "button_offset=4\n"
        "button_spacing=0\n"
        "title_vertical_offset_active=1\n"
        "title_vertical_offset_inactive=1\n"
        "title_shadow_active=false\n"
        "title_shadow_inactive=false\n"
        "shadow_delta_height=2\n",
        newline="\n",
    )
    print(f"{len(list(OUT.glob('*.xpm')))} imagens em {OUT}")


if __name__ == "__main__":
    main()
