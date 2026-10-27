"""Renderiza carrosséis Bridge & Co. (1080x1350 JPEG) a partir de um JSON de posts.
uso: python3 tools/render.py posts/<semana>/slides.json <pasta_saida> tools/fonts

Cada post: {"dia", "avatar", "theme": navy|cream|gold, "slides": [...]}
Cada slide: {"t": "capa"|"cta"|<texto>, "h", "s", "v": {visual opcional}}
Visuais ("v.kind"): search, split, calendar, checklist, notif, chat, icons, bignum, stars
"""
import json, sys, base64, html
from pathlib import Path
from playwright.sync_api import sync_playwright

posts_file, out_dir, font_dir = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
out_dir.mkdir(parents=True, exist_ok=True)
e = html.escape

def font(name):
    return "data:font/woff2;base64," + base64.b64encode(next(font_dir.glob(f"**/{name}")).read_bytes()).decode()

THEMES = {
    "navy":  {"bg": "#0B1F3A", "fg": "#F5F1E8", "acc": "#C9A24A", "mut": "#B8C2D3", "card": "#13294A", "line": "rgba(245,241,232,.14)"},
    "cream": {"bg": "#F4EFE4", "fg": "#0B1F3A", "acc": "#8A6A1F", "mut": "#4A5568", "card": "#FFFFFF", "line": "rgba(11,31,58,.12)"},
    "gold":  {"bg": "#C9A24A", "fg": "#0B1F3A", "acc": "#0B1F3A", "mut": "#2E3A4D", "card": "#F5F1E8", "line": "rgba(11,31,58,.18)"},
}
FLIP = {"navy": "cream", "cream": "navy", "gold": "navy"}

CSS_BASE = f"""
@font-face{{font-family:PF;src:url({font('playfair-display-latin-600-normal.woff2')})}}
@font-face{{font-family:DM;src:url({font('dm-sans-latin-400-normal.woff2')});font-weight:400}}
@font-face{{font-family:DM;src:url({font('dm-sans-latin-700-normal.woff2')});font-weight:700}}
*{{margin:0;box-sizing:border-box}}
body{{width:1080px;height:1350px;font-family:DM}}
.s{{width:1080px;height:1350px;padding:100px 90px;display:flex;flex-direction:column;justify-content:space-between;background:var(--bg);color:var(--fg)}}
.top{{display:flex;justify-content:space-between;font-size:24px;letter-spacing:4px;text-transform:uppercase;color:var(--acc);font-weight:700}}
.mid{{display:flex;flex-direction:column;gap:56px}}
.h{{font-family:PF;font-size:88px;line-height:1.08}}
.sub{{font-family:PF;font-size:60px;color:var(--acc);margin-top:28px}}
.t{{font-size:58px;line-height:1.3}}
.bar{{width:110px;height:6px;background:var(--acc);margin-bottom:44px}}
.foot{{display:flex;justify-content:space-between;align-items:center;font-size:26px;color:var(--mut)}}
.foot b{{font-family:PF;font-weight:400;font-size:30px;color:var(--fg)}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:22px;padding:30px 34px}}
.pill{{display:inline-block;margin-top:48px;padding:28px 46px;background:var(--fg);color:var(--bg);border-radius:14px;font-size:46px;font-weight:700}}
.row{{display:flex;gap:24px;align-items:center}}
.muted{{color:var(--mut)}}
"""

STAR = '<svg width="{s}" height="{s}" viewBox="0 0 24 24"><path fill="{c}" d="M12 2l2.9 6.6 7.1.6-5.4 4.7 1.6 7L12 17.3 5.8 20.9l1.6-7L2 9.2l7.1-.6z"/></svg>'
ICONS = {
    "pin": '<path d="M12 22s7-6.2 7-12a7 7 0 10-14 0c0 5.8 7 12 7 12z"/><circle cx="12" cy="10" r="2.5"/>',
    "search": '<circle cx="11" cy="11" r="7"/><path d="M20 20l-4-4"/>',
    "camera": '<path d="M4 7h3l2-3h6l2 3h3v12H4z"/><circle cx="12" cy="13" r="3.5"/>',
    "shield": '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/><path d="M8.5 12l2.5 2.5 4.5-5"/>',
    "heart": '<path d="M12 20s-7-4.4-7-10a4 4 0 017-2.6A4 4 0 0119 10c0 5.6-7 10-7 10z"/>',
    "phone": '<path d="M5 4h4l2 5-2.5 1.5a11 11 0 005 5L15 13l5 2v4a2 2 0 01-2 2A16 16 0 013 6a2 2 0 012-2z"/>',
    "check": '<path d="M5 12.5l4.5 4.5L19 7.5"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "star": '<path d="M12 3l2.7 6 6.3.6-4.8 4.2 1.4 6.2L12 16.8 6.4 20l1.4-6.2L3 9.6 9.3 9z"/>',
    "tool": '<path d="M14.5 6.5a4 4 0 005 5L13 18l-3 1 1-3 6.5-6.5"/><path d="M4 20l6-6"/>',
    "home": '<path d="M3 11l9-7 9 7"/><path d="M5 10v10h14V10"/>',
}

def icon(name, size, color, sw=1.8):
    return f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round">{ICONS[name]}</svg>'

def stars(n, size, color):
    return "".join(STAR.format(s=size, c=color) for _ in range(n))

def visual(v, th):
    k = v["kind"]
    if k == "search":
        res = "".join(
            f'<div class="card row" style="justify-content:space-between;{"border:3px solid "+th["acc"] if r.get("hl") else ""}">'
            f'<div><div style="font-size:34px;font-weight:700">{e(r["name"])}</div>'
            f'<div class="row" style="gap:6px;margin-top:10px">{stars(r.get("stars",5),30,"#E0A526")}<span class="muted" style="font-size:26px;margin-left:10px">{e(r.get("meta",""))}</span></div></div>'
            f'{icon("pin",48,th["acc"])}</div>' for r in v.get("results", []))
        return (f'<div style="display:flex;flex-direction:column;gap:18px"><div class="card row" style="border-radius:999px;padding:24px 36px">'
                f'{icon("search",40,th["mut"])}<span style="font-size:36px">{e(v["query"])}</span></div>{res}</div>')
    if k == "split":
        cols = "".join(
            f'<div class="card" style="flex:1;display:flex;flex-direction:column;gap:20px;{"background:"+th["acc"]+";color:"+th["bg"] if c.get("hl") else ""}">'
            f'{icon(c["icon"],64,th["bg"] if c.get("hl") else th["acc"])}<div style="font-family:PF;font-size:46px">{e(c["title"])}</div>'
            f'<div style="font-size:30px;line-height:1.35;opacity:.9">{e(c["text"])}</div></div>' for c in v["cols"])
        return f'<div class="row" style="align-items:stretch">{cols}</div>'
    if k == "calendar":
        marked = set(v.get("marked", []))
        cells = "".join(f'<div style="height:78px;border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:28px;'
                        f'{"background:"+th["acc"]+";color:"+th["bg"]+";font-weight:700" if d in marked else "border:1px dashed "+th["line"]+";color:"+th["mut"]}">{d}</div>'
                        for d in range(1, 32))
        return (f'<div class="card"><div style="font-family:PF;font-size:44px;margin-bottom:22px">{e(v["month"])}</div>'
                f'<div style="display:grid;grid-template-columns:repeat(7,1fr);gap:10px">{cells}</div></div>')
    if k == "checklist":
        items = "".join(f'<div class="row" style="gap:28px"><div style="width:72px;height:72px;border-radius:50%;background:{th["acc"]};display:flex;align-items:center;justify-content:center;flex:none">{icon("check",44,th["bg"],2.6)}</div>'
                        f'<div style="font-size:40px;line-height:1.25">{e(i)}</div></div>' for i in v["items"])
        return f'<div style="display:flex;flex-direction:column;gap:34px">{items}</div>'
    if k == "notif":
        cards = "".join(f'<div class="card" style="{"opacity:.45" if n.get("dim") else ""}"><div class="row" style="justify-content:space-between">'
                        f'<span style="font-size:26px;font-weight:700;letter-spacing:2px;color:{th["acc"]}">{e(n["app"])}</span><span class="muted" style="font-size:26px">{e(n["time"])}</span></div>'
                        f'<div style="font-size:36px;margin-top:12px;line-height:1.3">{e(n["text"])}</div></div>' for n in v["items"])
        return f'<div style="display:flex;flex-direction:column;gap:20px">{cards}</div>'
    if k == "chat":
        msgs = "".join(f'<div style="align-self:{"flex-end" if m.get("me") else "flex-start"};max-width:80%;padding:24px 30px;border-radius:28px;font-size:32px;line-height:1.35;'
                       f'{"background:"+th["acc"]+";color:"+th["bg"] if m.get("me") else "background:"+th["card"]+";border:1px solid "+th["line"]}">{e(m["text"])}'
                       f'<div style="font-size:22px;opacity:.7;margin-top:8px">{e(m.get("time",""))}</div></div>' for m in v["msgs"])
        return f'<div style="display:flex;flex-direction:column;gap:18px">{msgs}</div>'
    if k == "icons":
        items = "".join(f'<div class="card" style="flex:1;display:flex;flex-direction:column;align-items:center;gap:18px;padding:40px 20px">'
                        f'{icon(i["icon"],90,th["acc"])}<div style="font-size:30px;font-weight:700;text-align:center">{e(i["label"])}</div></div>' for i in v["items"])
        return f'<div class="row" style="align-items:stretch">{items}</div>'
    if k == "bignum":
        return (f'<div><div style="font-family:PF;font-size:220px;line-height:1;color:{th["acc"]}">{e(v["n"])}</div>'
                f'<div class="muted" style="font-size:34px;margin-top:16px">{e(v.get("label",""))}</div></div>')
    if k == "stars":
        return (f'<div class="card" style="text-align:center;padding:50px"><div class="row" style="justify-content:center;gap:10px">{stars(5,90,"#E0A526")}</div>'
                f'<div style="font-family:PF;font-size:64px;margin-top:20px">{e(v.get("score","4.9"))}</div>'
                f'<div class="muted" style="font-size:30px">{e(v.get("label",""))}</div></div>')
    return ""

def slide_html(sl, i, n, post):
    base = post.get("theme", "navy")
    kind = sl.get("t")
    tname = sl.get("theme") or ("gold" if kind == "cta" and base != "gold" else base if kind in ("capa", "cta") or i % 2 == 1 else FLIP[base])
    th = THEMES[tname]
    vars_ = ";".join(f"--{k}:{val}" for k, val in th.items())
    top = f'<div class="top"><span>{e(post["avatar"])}</span><span>{i:02d}/{n:02d}</span></div>'
    vis = visual(sl["v"], th) if sl.get("v") else ""
    if kind == "capa":
        size = 80 if vis else 96
        text = f'<div><div class="bar"></div><div class="h" style="font-size:{size}px">{e(sl["h"])}</div>' + (f'<div class="sub">{e(sl["s"])}</div>' if sl.get("s") else "") + "</div>"
    elif kind == "cta":
        text = f'<div><div class="h" style="font-size:80px">{e(sl["h"])}</div><div class="pill">{e(sl["s"])}</div></div>'
    else:
        text = f'<div><div class="bar"></div><div class="t" style="font-size:{50 if vis else 58}px">{e(kind)}</div></div>'
    mid = f'<div class="mid">{text}{vis}</div>'
    foot = f'<div class="foot"><b>Daniel Oliveira | Bridge &amp; Co.</b><span>{"deslize →" if i < n else ""}</span></div>'
    return f'<html><head><meta charset="utf-8"><style>{CSS_BASE}</style></head><body><div class="s" style="{vars_}">{top}{mid}{foot}</div></body></html>'

posts = json.loads(Path(posts_file).read_text())
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1080, "height": 1350})
    for post in posts:
        d = out_dir / f"dia{post['dia']:02d}"
        d.mkdir(exist_ok=True)
        n = len(post["slides"])
        for i, sl in enumerate(post["slides"], 1):
            pg.set_content(slide_html(sl, i, n, post))
            pg.evaluate("document.fonts.ready")
            pg.screenshot(path=str(d / f"{i}.jpg"), type="jpeg", quality=90)
    b.close()
print("ok", len(list(out_dir.glob("*/*.jpg"))))
