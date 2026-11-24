"""Génère le site Balani Awards à partir de people.json.

Usage : python3 build.py
Chaque personne obtient UN fichier : <slug>.html (photo intégrée dans la page).
La page d'accueil index.html liste toutes les personnes. Aucun sous-dossier.
"""
import base64
import html
import io
import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent
people = json.loads((ROOT / "people.json").read_text(encoding="utf-8"))
PHOTOS = ROOT              # photos sources <slug>.jpg, à la racine
OUT = ROOT                 # pages générées à la racine (tout est à plat, sans dossier)

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600;700'
         '&family=Montserrat:wght@400;500;600;700;800&display=swap" rel="stylesheet">')

BASE_CSS = """
:root{--bg:#0d0b08;--card:#16130e;--gold:#d8b45a;--gold-soft:#f0d98f;--text:#f3eee4;--muted:#b8ad98;--line:rgba(216,180,90,.28)}
*{box-sizing:border-box;margin:0;padding:0}
body{background:radial-gradient(120% 70% at 50% 0%,#2a2112 0%,var(--bg) 60%) fixed,var(--bg);color:var(--text);
 font-family:Montserrat,system-ui,sans-serif;min-height:100vh}
a{color:inherit;text-decoration:none}
.brand{text-align:center;font-weight:800;letter-spacing:.3em;font-size:15px;color:var(--gold);text-transform:uppercase}
.brand span{display:block;font-weight:500;letter-spacing:.4em;font-size:11px;color:var(--muted);margin-top:4px}
footer{text-align:center;color:var(--muted);font-size:12px;margin:34px 0 10px;letter-spacing:.08em}
"""


def esc(s):
    return html.escape(s, quote=True)


def data_uri(path, max_side):
    im = Image.open(path).convert("RGB")
    im.thumbnail((max_side, max_side))
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=82)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def person_page(p):
    paras = "\n".join(f'    <p class="bio">{esc(t)}</p>' for t in p["presentation"])
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(p['nom'])} — Balani Awards</title>
<meta name="description" content="{esc(p['nom'])}, {esc(p['titre'])}">
{FONTS}
<style>{BASE_CSS}
main{{max-width:560px;margin:0 auto;padding:28px 16px 40px}}
.brand{{margin-bottom:22px}}
.photo{{position:relative;border-radius:18px;overflow:hidden;border:1px solid var(--line);box-shadow:0 20px 50px rgba(0,0,0,.55)}}
.photo img{{display:block;width:100%;aspect-ratio:4/3;object-fit:cover;object-position:50% 20%}}
.photo::after{{content:"";position:absolute;inset:auto 0 0 0;height:40%;background:linear-gradient(transparent,rgba(13,11,8,.85))}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:18px;margin-top:-48px;position:relative;z-index:1;padding:28px 24px 30px;text-align:center}}
.role{{display:inline-block;font-size:11px;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:#1a1408;background:linear-gradient(90deg,var(--gold),var(--gold-soft));padding:7px 14px;border-radius:999px}}
h1{{font-weight:700;font-size:clamp(24px,6.4vw,32px);line-height:1.2;margin:18px 0 6px;color:var(--gold-soft)}}
.sub{{color:var(--muted);font-size:14px}}
.rule{{width:56px;height:2px;background:var(--gold);margin:24px auto;border-radius:2px}}
h2{{font-family:"Cormorant Garamond",serif;font-size:24px;color:var(--gold);margin-bottom:12px;font-weight:600}}
p.bio{{font-size:15px;line-height:1.75;color:#e6dfd1;text-align:left}}
p.bio+p.bio{{margin-top:12px}}
.back{{display:block;text-align:center;margin-top:22px;color:var(--gold);font-size:13px;letter-spacing:.08em}}
</style>
</head>
<body>
<main>
  <div class="brand">Balani Awards<span>Édition 2026</span></div>
  <div class="photo"><img src="{data_uri(PHOTOS / p['photo'], 1100)}" alt="{esc(p['nom'])}"></div>
  <section class="card">
    <span class="role">{esc(p['distinction'])}</span>
    <h1>{esc(p['nom'])}</h1>
    <p class="sub">{esc(p['titre'])}</p>
    <div class="rule"></div>
    <h2>Présentation</h2>
{paras}
  </section>
  <a class="back" href="./">← Toutes les personnalités honorées</a>
  <footer>© Balani Awards 2026</footer>
</main>
</body>
</html>
"""


def home_page(people):
    cards = "\n".join(
        f"""    <a class="item" href="{esc(p['slug'])}.html">
      <img src="{data_uri(PHOTOS / p['photo'], 480)}" alt="{esc(p['nom'])}" loading="lazy">
      <div class="meta"><strong>{esc(p['nom'])}</strong><span>{esc(p['titre'])}</span></div>
    </a>""" for p in people)
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Balani Awards 2026 — Personnalités honorées</title>
{FONTS}
<style>{BASE_CSS}
main{{max-width:1100px;margin:0 auto;padding:48px 20px 40px}}
.hero{{text-align:center;margin-bottom:40px}}
.hero h1{{font-weight:800;font-size:clamp(34px,8vw,64px);letter-spacing:.06em;color:#e2c068;margin-top:18px;line-height:1.05}}
.hero p{{color:var(--muted);margin-top:12px;font-size:15px;letter-spacing:.04em}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:20px}}
.item{{background:var(--card);border:1px solid var(--line);border-radius:16px;overflow:hidden;transition:transform .2s,border-color .2s}}
.item:hover{{transform:translateY(-3px);border-color:var(--gold)}}
.item img{{display:block;width:100%;aspect-ratio:4/3;object-fit:cover;object-position:50% 20%}}
.meta{{padding:14px 16px 18px}}
.meta strong{{display:block;font-size:15px;color:var(--gold-soft);line-height:1.3}}
.meta span{{display:block;font-size:12.5px;color:var(--muted);margin-top:6px;line-height:1.4}}
</style>
</head>
<body>
<main>
  <div class="hero">
    <div class="brand">Balani Awards<span>Édition 2026</span></div>
    <h1>Personnalités honorées</h1>
    <p>Découvrez les personnes distinguées lors des Balani Awards 2026.</p>
  </div>
  <div class="grid">
{cards}
  </div>
  <footer>© Balani Awards 2026</footer>
</main>
</body>
</html>
"""


OUT.mkdir(exist_ok=True)
for p in people:
    (OUT / f"{p['slug']}.html").write_text(person_page(p), encoding="utf-8")
(OUT / "index.html").write_text(home_page(people), encoding="utf-8")
(OUT / ".nojekyll").write_text("")
print(f"{len(people)} page(s) générée(s)")
