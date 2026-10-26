#!/usr/bin/env python3
"""Generate the animated SVG assets for the GitHub profile README.

Direction: "assembler listing" (precision-instrument family) — cool neutrals,
one cobalt accent, a visible grid, IBM Plex Sans + Mono embedded as subsets.

Every animation starts from the element's final, visible state being the
default, so `prefers-reduced-motion: reduce` simply turns animations off.

Usage:  python3 scripts/build_assets.py
Writes: assets/*-light.svg and assets/*-dark.svg
"""
from __future__ import annotations

import base64
import io
from html import escape
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "scripts" / "fonts"
OUT = ROOT / "assets"

THEMES = {
    "light": dict(bg="#F7F9FC", panel="#FFFFFF", ink="#0E1726", muted="#5A6577",
                  faint="#8A94A6", grid="#E6EBF2", rule="#D5DCE6", accent="#2546D8",
                  accent_soft="#E8EDFD", ok="#1F7A4D"),
    "dark": dict(bg="#0D1117", panel="#111722", ink="#E6EDF3", muted="#9AA6B8",
                 faint="#6B7787", grid="#1A2230", rule="#263042", accent="#7C95FF",
                 accent_soft="#18213D", ok="#4CC38A"),
}

MONO = "'Plex Mono', ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
SANS = "'Plex Sans', -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"


# ---------------------------------------------------------------- fonts
def font_face(file: str, family: str, weight: int, text: str) -> str:
    """Subset a woff2 to the glyphs in `text` and return an @font-face rule."""
    font = TTFont(FONTS / file)
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.layout_features = ["kern", "liga"]
    sub = subset.Subsetter(opts)
    sub.populate(text=text + " ")
    sub.subset(font)
    buf = io.BytesIO()
    font.flavor = "woff2"
    font.save(buf)
    b64 = base64.b64encode(buf.getvalue()).decode()
    return (f"@font-face{{font-family:'{family}';font-weight:{weight};"
            f"src:url(data:font/woff2;base64,{b64}) format('woff2');}}")


def fonts_css(mono_text: str, sans_text: str, sans_bold_text: str = "", mono_bold_text: str = "") -> str:
    rules = [font_face("ibm-plex-mono-latin-400-normal.woff2", "Plex Mono", 400, mono_text),
             font_face("ibm-plex-sans-latin-400-normal.woff2", "Plex Sans", 400, sans_text)]
    if sans_bold_text:
        rules.append(font_face("ibm-plex-sans-latin-600-normal.woff2", "Plex Sans", 600, sans_bold_text))
    if mono_bold_text:
        rules.append(font_face("ibm-plex-mono-latin-500-normal.woff2", "Plex Mono", 500, mono_bold_text))
    return "".join(rules)


BASE_CSS = """
.m{font-family:__MONO__}.s{font-family:__SANS__}
.rise{animation:rise .8s cubic-bezier(.2,.8,.2,1) both}
.fade{animation:fade .6s ease-out both}
.slide{animation:slide .5s cubic-bezier(.2,.8,.2,1) both}
.draw{stroke-dasharray:var(--len);animation:draw 1s cubic-bezier(.65,0,.35,1) both}
.cur{animation:fade .2s 2.9s both,blink 1s steps(1) 3.1s 8}
@keyframes rise{from{transform:translateY(var(--rise,90px))}to{transform:none}}
@keyframes fade{from{opacity:0}to{opacity:1}}
@keyframes slide{from{opacity:0;transform:translateX(-10px)}to{opacity:1;transform:none}}
@keyframes draw{from{stroke-dashoffset:var(--len)}to{stroke-dashoffset:0}}
@keyframes blink{50%{opacity:0}}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}
""".replace("__MONO__", MONO).replace("__SANS__", SANS)


def grid(w: int, h: int, c: dict, step: int = 24) -> str:
    return (f'<pattern id="g" width="{step}" height="{step}" patternUnits="userSpaceOnUse">'
            f'<path d="M{step} 0H0V{step}" fill="none" stroke="{c["grid"]}" stroke-width="1"/></pattern>'
            f'<rect width="{w}" height="{h}" fill="url(#g)"/>')


def svg(w: int, h: int, title: str, css: str, body: str) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{escape(title)}"><title>{escape(title)}</title>'
            f'<style>{css}</style>{body}</svg>\n')


def d(s: float) -> str:
    return f"animation-delay:{s:.2f}s"


# ---------------------------------------------------------------- hero
LISTING = [
    ("0000", "C0DE", ".entry", "ISRAEL", ""),
    ("0004", "4A43", "lea", "r1, JCT_CS", "; B.Sc. 2025-2028"),
    ("0008", "0C0C", "mov", "r2, #C_LINUX", "; systems"),
    ("000C", "F5F5", "mov", "r3, #FULL_STACK", "; vue, react"),
    ("0010", "A1A1", "call", "AI_INTEGRATION", ""),
    ("0014", "0001", "cmp", "hackathon, #1", "; 1st place"),
    ("0018", "0002", "cmp", "hackathon, #2", "; 2nd place"),
    ("001C", "4D53", ".data", "MOSHAL", "; program"),
    ("0020", "C0FE", "jmp", "NEXT_ROLE", "; open to work"),
]

HERO_NAME = ["Israel", "Shteinberg"]
HERO_SUB = "CS student @ JCT  ·  C & Linux  ·  full-stack  ·  AI"
HERO_PROMPT = "$ ./assemble israel.asm"
HERO_OK = "assembled  ·  0 errors  ·  0 warnings"
HERO_CHIPS = ["Jerusalem, Israel", "Moshal Program", "Open to student roles"]


def hero(c: dict) -> str:
    W, H = 1200, 380
    mono_text = "".join("".join(r) for r in LISTING) + HERO_PROMPT + HERO_OK + "israel.asm".upper() + "israel.asm ADDR WORD SRC" + "".join(HERO_CHIPS) + "▌✓"
    css = fonts_css(mono_text, HERO_SUB, "".join(HERO_NAME)) + BASE_CSS
    b = [f'<rect width="{W}" height="{H}" rx="8" fill="{c["bg"]}"/>', grid(W, H, c)]
    b.append(f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="8" fill="none" stroke="{c["rule"]}"/>')

    # left: listing panel
    px, py, pw, ph = 32, 32, 500, H - 64
    b.append(f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="4" fill="{c["panel"]}" stroke="{c["rule"]}"/>')
    b.append(f'<text class="m" x="{px+20}" y="{py+30}" font-size="12" fill="{c["faint"]}" letter-spacing="1">ISRAEL.ASM</text>')
    b.append(f'<text class="m" x="{px+pw-20}" y="{py+30}" font-size="12" fill="{c["faint"]}" text-anchor="end">ADDR  WORD  SRC</text>')
    b.append(f'<line x1="{px}" y1="{py+44}" x2="{px+pw}" y2="{py+44}" stroke="{c["rule"]}"/>')
    for i, (addr, word, op, arg, com) in enumerate(LISTING):
        y = py + 74 + i * 29
        b.append(f'<g class="slide" style="{d(0.15 + i*0.11)}">'
                 f'<text class="m" x="{px+20}" y="{y}" font-size="14" xml:space="preserve">'
                 f'<tspan fill="{c["faint"]}">{addr}</tspan>'
                 f'<tspan dx="14" fill="{c["muted"]}">{word}</tspan>'
                 f'<tspan dx="16" fill="{c["accent"]}">{escape(op)}</tspan>'
                 f'<tspan x="{px+200}" fill="{c["ink"]}">{escape(arg)}</tspan></text>'
                 + (f'<text class="m" x="{px+pw-20}" y="{y}" font-size="13" fill="{c["faint"]}" text-anchor="end">{escape(com)}</text>' if com else "")
                 + '</g>')

    # right: the assembled result
    rx = 580
    b.append(f'<text class="m fade" style="{d(1.05)}" x="{rx}" y="78" font-size="15" fill="{c["muted"]}">'
             f'<tspan fill="{c["accent"]}">$</tspan> ./assemble israel.asm</text>')
    b.append(f'<text class="m fade" style="{d(1.35)}" x="{rx}" y="104" font-size="13" fill="{c["ok"]}">✓ {HERO_OK}</text>')
    for i, word in enumerate(HERO_NAME):
        top = 116 + i * 70
        b.append(f'<clipPath id="w{i}"><rect x="{rx-4}" y="{top}" width="600" height="84"/></clipPath>')
        b.append(f'<g clip-path="url(#w{i})"><text class="s rise" style="{d(1.5 + i*0.14)}" x="{rx-3}" y="{top+60}" '
                 f'font-size="62" font-weight="600" fill="{c["ink"]}" letter-spacing="-1.5">{word}</text></g>')
    line_y = 300
    b.append(f'<line class="draw" style="--len:560;{d(2.05)}" x1="{rx}" y1="{line_y}" x2="{rx+560}" y2="{line_y}" '
             f'stroke="{c["accent"]}" stroke-width="2"/>')
    b.append(f'<text class="s fade" style="{d(2.2)}" x="{rx}" y="{line_y-14}" font-size="18" fill="{c["muted"]}" xml:space="preserve">{escape(HERO_SUB)}</text>')
    cx = rx
    for i, chip in enumerate(HERO_CHIPS):
        w = 16 + len(chip) * 7.9
        b.append(f'<g class="fade" style="{d(2.6 + i*0.12)}"><rect x="{cx}" y="{line_y+20}" width="{w:.0f}" height="28" rx="4" '
                 f'fill="{c["accent_soft"]}" stroke="{c["rule"]}"/><text class="m" x="{cx+8}" y="{line_y+39}" font-size="13" fill="{c["ink"]}">{escape(chip)}</text></g>')
        cx += w + 10
    b.append(f'<text class="m cur" x="{cx+2}" y="{line_y+40}" font-size="16" fill="{c["accent"]}">▌</text>')
    return svg(W, H, "Israel Shteinberg — CS student at JCT. C and Linux, full-stack, AI.", css, "".join(b))


# ---------------------------------------------------------------- project cards
CARDS = [
    dict(slug="remind", idx="01", title="ReMind", tag="HACKATHON · 1ST PLACE",
         lines=["Automation and task management for therapists", "and their patients. I led the team and still lead it."],
         stack="team lead · full-stack · private repo"),
    dict(slug="teamsprintup", idx="02", title="TeamSprintUp", tag="MOSHAL HACKATHON · 2ND",
         lines=["A personal-learning layer on top of TechSchool", "that tracks each student's growth. I led the AI part."],
         stack="Nuxt 3 · Vue 3 · NestJS · Supabase"),
    dict(slug="assembler", idx="03", title="Modular Assembler", tag="SYSTEMS · C",
         lines=["An assembler in C across 24 modules: parsing,", "symbol table, instruction encoding, error handling."],
         stack="C · GCC · Makefiles · Linux"),
    dict(slug="casa", idx="04", title="Casa", tag="FULL-STACK APP",
         lines=["Home management: envelope budgeting, a pantry", "that tracks expiry, a shopping list that writes itself."],
         stack="React · TypeScript · Postgres · Vercel"),
    dict(slug="rentradar", idx="05", title="RentRadar", tag="FULL-STACK APP",
         lines=["Apartment hunting with automatic Yad2 import,", "side-by-side comparison, a map and price history."],
         stack="React · FastAPI · PostgreSQL · Leaflet"),
    dict(slug="socialquest", idx="06", title="SocialQuest", tag="ACCESSIBILITY · EDTECH",
         lines=["A social GPS that helps neurodivergent children", "read social situations. Private by design."],
         stack="Next.js 14 · TypeScript · Tailwind"),
]


def card(c: dict, k: dict) -> str:
    W, H = 580, 232
    mono_text = k["idx"] + k["tag"] + k["stack"] + "→"
    css = fonts_css(mono_text, "".join(k["lines"]), k["title"]) + BASE_CSS
    b = [f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="6" fill="{c["panel"]}" stroke="{c["rule"]}"/>']
    b.append(f'<text class="m" x="24" y="38" font-size="15" fill="{c["accent"]}">{k["idx"]}</text>')
    b.append(f'<text class="m" x="{W-24}" y="38" font-size="13" fill="{c["faint"]}" text-anchor="end" letter-spacing=".8">{escape(k["tag"])}</text>')
    b.append(f'<clipPath id="t"><rect x="20" y="50" width="540" height="50"/></clipPath>')
    b.append(f'<g clip-path="url(#t)"><text class="s rise" style="--rise:46px;{d(0.1)}" x="23" y="88" font-size="32" font-weight="600" '
             f'fill="{c["ink"]}" letter-spacing="-.5">{escape(k["title"])}</text></g>')
    for i, ln in enumerate(k["lines"]):
        b.append(f'<text class="s fade" style="{d(0.35 + i*0.08)}" x="24" y="{128 + i*26}" font-size="18" fill="{c["muted"]}">{escape(ln)}</text>')
    b.append(f'<line class="draw" style="--len:532;{d(0.45)}" x1="24" y1="184" x2="{W-24}" y2="184" stroke="{c["rule"]}"/>')
    b.append(f'<line class="draw" style="--len:48;{d(0.45)}" x1="24" y1="184" x2="72" y2="184" stroke="{c["accent"]}" stroke-width="2"/>')
    b.append(f'<text class="m fade" style="{d(0.7)}" x="24" y="212" font-size="15" fill="{c["ink"]}">{escape(k["stack"])}</text>')
    return svg(W, H, f'{k["title"]}: {" ".join(k["lines"])} Stack: {k["stack"]}.', css, "".join(b))


# ---------------------------------------------------------------- stack register map
STACK = [
    ("LANG", ["C", "C++", "TypeScript", "JavaScript", "Python"]),
    ("FRONT", ["Vue 3", "Nuxt 3", "React", "Next.js", "Tailwind"]),
    ("BACK", ["NestJS", "FastAPI", "Supabase", "PostgreSQL"]),
    ("TOOLS", ["Linux", "GCC", "Make", "Git", "Docker", "Vercel"]),
]


def stack(c: dict) -> str:
    W, H = 1200, 276
    words = "".join(lbl + "".join(xs) for lbl, xs in STACK) + "REGISTERSr0r1r2r3"
    css = fonts_css(words, "", "", words) + BASE_CSS
    b = [f'<rect width="{W}" height="{H}" rx="8" fill="{c["bg"]}"/>', grid(W, H, c),
         f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="8" fill="none" stroke="{c["rule"]}"/>',
         f'<text class="m" x="32" y="40" font-size="13" fill="{c["faint"]}" letter-spacing="1">REGISTERS</text>']
    n = 0
    for r, (lbl, items) in enumerate(STACK):
        y = 62 + r * 50
        b.append(f'<text class="m" x="32" y="{y+23}" font-size="14" fill="{c["faint"]}">r{r}</text>')
        b.append(f'<text class="m" x="70" y="{y+23}" font-size="15" font-weight="500" fill="{c["accent"]}">{lbl}</text>')
        x = 170
        for it in items:
            w = 28 + len(it) * 10.2
            b.append(f'<g class="slide" style="{d(0.1 + n*0.045)}"><rect x="{x}" y="{y}" width="{w:.0f}" height="36" rx="4" '
                     f'fill="{c["panel"]}" stroke="{c["rule"]}"/><text class="m" x="{x+14}" y="{y+24}" font-size="17" '
                     f'font-weight="500" fill="{c["ink"]}">{escape(it)}</text></g>')
            x += w + 10
            n += 1
    alt = "Tech stack. " + " ".join(f"{lbl.title()}: {', '.join(xs)}." for lbl, xs in STACK)
    return svg(W, H, alt, css, "".join(b))


def main() -> None:
    OUT.mkdir(exist_ok=True)
    for name, c in THEMES.items():
        (OUT / f"hero-{name}.svg").write_text(hero(c), encoding="utf-8")
        (OUT / f"stack-{name}.svg").write_text(stack(c), encoding="utf-8")
        for k in CARDS:
            (OUT / f"card-{k['slug']}-{name}.svg").write_text(card(c, k), encoding="utf-8")
    total = sum(p.stat().st_size for p in OUT.glob("*.svg"))
    print(f"wrote {len(list(OUT.glob('*.svg')))} svgs, {total/1024:.0f} KB total")


if __name__ == "__main__":
    main()
