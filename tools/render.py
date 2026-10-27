"""Renderiza carrosséis Bridge & Co. (1080x1350 JPEG) a partir de um JSON de posts.
uso: python3 render.py posts.json pasta_saida pasta_fontes
"""
import json, sys, base64, html
from pathlib import Path
from playwright.sync_api import sync_playwright

posts_file, out_dir, font_dir = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
out_dir.mkdir(parents=True, exist_ok=True)

def font(path):
    return "data:font/woff2;base64," + base64.b64encode(Path(path).read_bytes()).decode()

pf = font(next(font_dir.glob("**/playfair-display-latin-600-normal.woff2")))
dm4 = font(next(font_dir.glob("**/dm-sans-latin-400-normal.woff2")))
dm7 = font(next(font_dir.glob("**/dm-sans-latin-700-normal.woff2")))

CSS = f"""
@font-face{{font-family:PF;src:url({pf})}}
@font-face{{font-family:DM;src:url({dm4});font-weight:400}}
@font-face{{font-family:DM;src:url({dm7});font-weight:700}}
*{{margin:0;box-sizing:border-box}}
body{{width:1080px;height:1350px;background:#0B1F3A;color:#F5F1E8;font-family:DM}}
.s{{width:1080px;height:1350px;padding:110px 96px;display:flex;flex-direction:column;justify-content:space-between;position:relative}}
.top{{display:flex;justify-content:space-between;font-size:26px;letter-spacing:4px;text-transform:uppercase;color:#C9A24A;font-weight:700}}
.h{{font-family:PF;font-size:96px;line-height:1.08}}
.sub{{font-family:PF;font-size:64px;color:#C9A24A;margin-top:36px}}
.t{{font-size:60px;line-height:1.3}}
.bar{{width:120px;height:6px;background:#C9A24A;margin-bottom:56px}}
.foot{{display:flex;justify-content:space-between;align-items:center;font-size:28px;color:#B8C2D3}}
.brand{{font-family:PF;font-size:36px;color:#F5F1E8}} .brand b{{color:#C9A24A;font-weight:400}}
.cta{{background:#C9A24A;color:#0B1F3A}} .cta .top,.cta .foot{{color:#0B1F3A}} .cta .brand{{color:#0B1F3A}} .cta .brand b{{color:#0B1F3A}}
.pill{{display:inline-block;margin-top:56px;padding:30px 48px;background:#0B1F3A;color:#F5F1E8;border-radius:12px;font-size:48px;font-weight:700}}
"""

def slide_html(sl, i, n, avatar):
    e = html.escape
    kind = sl.get("t")
    cls = "s cta" if kind == "cta" else "s"
    top = f'<div class="top"><span>{e(avatar)}</span><span>{i:02d}/{n:02d}</span></div>'
    if kind == "capa":
        body = f'<div><div class="bar"></div><div class="h">{e(sl["h"])}</div>' + (f'<div class="sub">{e(sl["s"])}</div>' if sl.get("s") else "") + "</div>"
    elif kind == "cta":
        body = f'<div><div class="h" style="font-size:84px">{e(sl["h"])}</div><div class="pill">{e(sl["s"])}</div></div>'
    else:
        body = f'<div><div class="bar"></div><div class="t">{e(kind)}</div></div>'
    foot = '<div class="foot"><span class="brand">Bridge <b>&amp;</b> Co.</span><span>' + ("@danielbridgeco  →" if i < n else "@danielbridgeco") + "</span></div>"
    return f'<html><head><meta charset="utf-8"><style>{CSS}</style></head><body><div class="{cls}">{top}{body}{foot}</div></body></html>'

posts = json.loads(Path(posts_file).read_text())
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1080, "height": 1350})
    for post in posts:
        n = len(post["slides"])
        for i, sl in enumerate(post["slides"], 1):
            pg.set_content(slide_html(sl, i, n, post["avatar"]))
            pg.evaluate("document.fonts.ready")
            pg.screenshot(path=str(out_dir / f"dia{post['dia']:02d}_{i}.jpg"), type="jpeg", quality=90)
    b.close()
print("ok", len(list(out_dir.glob("*.jpg"))))
