"""Génère l'attestation PDF d'une personne de people.json.

Usage : python3 attestation.py <slug>
Le code QR pointe vers https://azizabdoulsenou-code.github.io/balani-awards/<slug>.html
Champs utilisés dans people.json : nom, attestation_roles (1 ou 2 lignes), attestation_texte,
attestation_taille_nom (facultatif, 29 par défaut ; réduire si le nom déborde).
Prérequis : pip install qrcode[pil] playwright ; Chrome/Chromium.
"""
import html, io, json, base64, sys, shutil
from pathlib import Path
import qrcode
from qrcode.constants import ERROR_CORRECT_H
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
BASE = 'https://azizabdoulsenou-code.github.io/balani-awards/'

def chrome():
    for c in ['/usr/bin/google-chrome', '/usr/bin/chromium', '/usr/bin/chromium-browser']:
        if Path(c).exists():
            return c
    return None

def make(p, out_dir):
    q = qrcode.QRCode(error_correction=ERROR_CORRECT_H, box_size=16, border=2)
    q.add_data(BASE + p['slug'] + '.html'); q.make(fit=True)
    buf = io.BytesIO(); q.make_image(fill_color='#0d0b08', back_color='#fbf6ea').save(buf, 'PNG')
    qr = 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()
    t = (ROOT / 'attestation_template.html').read_text(encoding='utf-8')
    t = (t.replace('{{NOMSIZE}}', str(p.get('attestation_taille_nom', 29)))
          .replace('{{NOM}}', html.escape(p['nom']))
          .replace('{{ROLE}}', '<br>'.join(html.escape(r) for r in p['attestation_roles']))
          .replace('{{TEXTE}}', html.escape(p['attestation_texte']))
          .replace('{{QR}}', qr))
    out_dir.mkdir(parents=True, exist_ok=True)
    src = out_dir / f"attestation_{p['slug']}.html"; src.write_text(t, encoding='utf-8')
    pdf = out_dir / f"Attestation_{p['slug']}.pdf"
    with sync_playwright() as pw:
        kw = {'executable_path': chrome()} if chrome() else {}
        b = pw.chromium.launch(**kw)
        pg = b.new_page(viewport={'width': 1123, 'height': 794})
        pg.goto(src.as_uri()); pg.wait_for_timeout(600)
        pg.screenshot(path=str(out_dir / f"attestation_{p['slug']}.png"))
        pg.pdf(path=str(pdf), width='1123px', height='794px', print_background=True)
        b.close()
    return pdf

if __name__ == '__main__':
    people = {x['slug']: x for x in json.loads((ROOT / 'people.json').read_text(encoding='utf-8'))}
    for slug in sys.argv[1:]:
        print(make(people[slug], ROOT.parent / 'attestations'))
