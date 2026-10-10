#!/usr/bin/env python3
"""Gera o papel de parede noturno (modelo SVG) do D'OH!Sec OS.

Uso: python3 scripts/gen-ceu-noturno.py
Escreve config/includes.chroot/usr/share/dohsec/wallpaper-noite.svg. As estrelas ficam em
3 grupos com opacidade @A@, @B@ e @C@; o hook troca esses valores para gerar os quadros
que piscam.
"""
import random
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "config/includes.chroot/usr/share/dohsec/wallpaper-noite.svg"
W, H = 1920, 1080

# Areas sem estrela: donut, titulo e lua
LIVRE = [(960, 500, 300), (960, 920, 420), (1600, 200, 170)]


def livre(x, y):
    return all((x - cx) ** 2 + (y - cy) ** 2 > r * r for cx, cy, r in LIVRE)


def estrelas(rnd, n):
    pontos = []
    while len(pontos) < n:
        x, y = rnd.uniform(20, W - 20), rnd.uniform(20, H * 0.95)
        if livre(x, y):
            pontos.append((x, y))
    return pontos


def brilho(x, y, s):
    """Estrela de 4 pontas."""
    return (f'<path transform="translate({x:.0f} {y:.0f}) scale({s:.2f})" '
            'd="M0-10C1-3 3-1 10 0 3 1 1 3 0 10-1 3-3 1-10 0-3-1-1-3 0-10z"/>')


def main():
    rnd = random.Random(1989)
    grupos = {"A": [], "B": [], "C": []}
    for i, (x, y) in enumerate(estrelas(rnd, 150)):
        g = "ABC"[i % 3]
        if i % 7 == 0:
            grupos[g].append(brilho(x, y, rnd.uniform(0.8, 1.6)))
        else:
            grupos[g].append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{rnd.uniform(1.2, 2.6):.1f}"/>')

    camadas = "\n".join(
        f'  <g fill="#fff6d7" opacity="@{g}@">\n    ' + "\n    ".join(itens) + "\n  </g>"
        for g, itens in grupos.items()
    )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <defs>
    <linearGradient id="ceu" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#0b1a3a"/>
      <stop offset="1" stop-color="#1d3b78"/>
    </linearGradient>
    <radialGradient id="brilho-lua">
      <stop offset="0" stop-color="#fff6d7" stop-opacity="0.35"/>
      <stop offset="1" stop-color="#fff6d7" stop-opacity="0"/>
    </radialGradient>
    <mask id="crescente">
      <circle cx="1600" cy="200" r="90" fill="#fff"/>
      <circle cx="1645" cy="170" r="82" fill="#000"/>
    </mask>
    <g id="nuvem" fill="#2a4a8a" opacity="0.55">
      <ellipse cx="0" cy="0" rx="120" ry="55"/>
      <ellipse cx="-90" cy="20" rx="80" ry="45"/>
      <ellipse cx="95" cy="22" rx="85" ry="42"/>
      <ellipse cx="20" cy="-35" rx="75" ry="50"/>
    </g>
  </defs>

  <rect width="{W}" height="{H}" fill="url(#ceu)"/>
{camadas}

  <!-- Lua -->
  <circle cx="1600" cy="200" r="170" fill="url(#brilho-lua)"/>
  <circle cx="1600" cy="200" r="90" fill="#ffe680" mask="url(#crescente)"/>

  <use href="#nuvem" x="300" y="260"/>
  <use href="#nuvem" x="1350" y="880"/>
  <use href="#nuvem" x="420" y="930"/>

  <!-- Donut -->
  <g transform="translate(960 500)">
    <circle r="270" fill="#ff5fb7" opacity="0.12"/>
    <circle r="250" fill="#d9a066"/>
    <path fill="#ff5fb7" d="M0-235c80 0 150 40 190 105 25 30 10 50 30 80 20 35-5 70 5 105-35 70-125 115-225 115-90 0-170-40-210-105-15-35 15-60-5-95-20-35 10-70 5-100C-170-195-90-235 0-235z"/>
    <circle r="85" fill="url(#ceu)"/>
    <g stroke-width="14" stroke-linecap="round">
      <line x1="-150" y1="-110" x2="-120" y2="-130" stroke="#ffd84d"/>
      <line x1="-60" y1="-180" x2="-25" y2="-170" stroke="#3bb273"/>
      <line x1="60" y1="-170" x2="90" y2="-150" stroke="#2f7df6"/>
      <line x1="150" y1="-80" x2="165" y2="-45" stroke="#fff6d7"/>
      <line x1="170" y1="40" x2="150" y2="75" stroke="#ffd84d"/>
      <line x1="90" y1="150" x2="55" y2="165" stroke="#e84d5b"/>
      <line x1="-30" y1="175" x2="-65" y2="160" stroke="#3bb273"/>
      <line x1="-140" y1="110" x2="-165" y2="80" stroke="#2f7df6"/>
      <line x1="-180" y1="-10" x2="-170" y2="25" stroke="#e84d5b"/>
      <line x1="-115" y1="-30" x2="-95" y2="-60" stroke="#fff6d7"/>
      <line x1="110" y1="-60" x2="125" y2="-25" stroke="#ff9b30"/>
      <line x1="100" y1="90" x2="70" y2="105" stroke="#fff6d7"/>
    </g>
  </g>

  <text x="960" y="900" text-anchor="middle" font-family="DejaVu Sans" font-weight="bold"
        font-size="96" fill="#ffd84d" stroke="#171717" stroke-width="5" paint-order="stroke">D'OH!Sec OS</text>
  <text x="960" y="960" text-anchor="middle" font-family="DejaVu Sans" font-size="32"
        fill="#fff6d7">seguranca com cobertura de granulado</text>
</svg>
'''
    OUT.write_text(svg, newline="\n")
    print(f"ok {OUT}")


if __name__ == "__main__":
    main()
