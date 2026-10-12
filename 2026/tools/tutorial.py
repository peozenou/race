#!/usr/bin/env python3
"""Record the THE RACE 2026 navigation tutorial (1920x1080 MP4, captions in French).

It opens the dashboard, adds a cursor, captions and title cards on top of the
page, plays a scripted tour, records the screen and encodes 2026/tutoriel.mp4.

Usage:
  python3 2026/tools/tutorial.py [URL] [--proxy http://host:port]
  (URL defaults to the live site; ffmpeg must be installed)
"""
import argparse
import asyncio
import base64
import json
import os
import pathlib
import shutil
import subprocess
import tempfile

from playwright.async_api import async_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
W, H, DSF = 1280, 720, 1.5
TOP = 58  # address bar + breathing room
SITE = "peozenou.github.io/race/2026"

OVERLAY_CSS = """
#v-bar{position:fixed;top:0;left:0;right:0;z-index:9990;display:flex;align-items:center;gap:10px;height:44px;padding:0 18px;
  background:#ecebe6;border-bottom:1px solid rgba(0,0,0,.08);font:500 14px/1 ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;color:#3d3c39}
#v-bar .dots{display:flex;gap:7px}#v-bar .dots i{width:11px;height:11px;border-radius:50%;display:block;background:#d2d1c7}
#v-bar .url{flex:1;max-width:560px;margin:0 auto;background:#fff;border-radius:8px;padding:7px 14px;color:#52514e;display:flex;gap:8px;align-items:center}
#v-bar .url svg{flex:none}
body{padding-top:44px}
#v-cursor{position:fixed;left:0;top:0;width:22px;height:22px;z-index:9999;pointer-events:none;transform:translate(-3px,-2px)}
#v-ripple{position:fixed;width:34px;height:34px;margin:-17px 0 0 -17px;border-radius:50%;border:3px solid #d97757;z-index:9998;pointer-events:none;opacity:0}
#v-ripple.go{animation:rip .55s ease-out}
@keyframes rip{0%{opacity:.9;transform:scale(.3)}100%{opacity:0;transform:scale(1.5)}}
#v-cap{position:fixed;left:50%;bottom:26px;transform:translateX(-50%);max-width:82%;z-index:9997;background:rgba(24,23,22,.88);color:#fff;
  font:500 21px/1.35 ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;padding:12px 22px;border-radius:12px;box-shadow:0 8px 24px rgba(0,0,0,.25);opacity:0;transition:opacity .35s;text-align:center}
#v-cap.on{opacity:1}
#v-cap small{display:block;font-weight:400;font-size:15px;opacity:.8;margin-top:2px}
#v-card{position:fixed;inset:0;z-index:10000;background:#1f1e1d;color:#faf9f5;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:14px;transition:opacity .6s}
#v-card.off{opacity:0;pointer-events:none}
#v-card h1{font:400 46px/1.15 "Source Serif 4",ui-serif,Georgia,serif;margin:0;text-align:center}
#v-card p{font:400 22px/1.4 ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;margin:0;opacity:.85;text-align:center}
#v-card .bar{display:flex;gap:8px;margin-top:10px}
#v-card .bar i{width:46px;height:8px;border-radius:4px;display:block}
"""

OVERLAY_JS = """
([css, site]) => {
  const st = document.createElement('style'); st.textContent = css; document.head.append(st);
  const bar = document.createElement('div'); bar.id = 'v-bar';
  bar.innerHTML = '<span class="dots"><i></i><i></i><i></i></span><span class="url"><svg width="12" height="14" viewBox="0 0 12 14"><rect x="1" y="6" width="10" height="7" rx="1.5" fill="#6d6b67"/><path d="M3.5 6V4.2a2.5 2.5 0 0 1 5 0V6" stroke="#6d6b67" stroke-width="1.6" fill="none"/></svg></span>';
  bar.querySelector('.url').append(document.createTextNode(site));
  document.body.append(bar);
  document.body.insertAdjacentHTML('beforeend',
    '<svg id="v-cursor" viewBox="0 0 22 22"><path d="M3 2 L3 18 L7.5 13.8 L10.6 20.4 L13.3 19.2 L10.3 12.8 L16.5 12.6 Z" fill="#1f1e1d" stroke="#fff" stroke-width="1.6" stroke-linejoin="round"/></svg>' +
    '<div id="v-ripple"></div><div id="v-cap"></div>' +
    '<div id="v-card"><h1>THE RACE 2026</h1><p>Bilan de la saison · comment naviguer dans le tableau de bord</p><div class="bar">' +
    '<i style="background:#8e7cc3"></i><i style="background:#f6b26b"></i><i style="background:#6fa8dc"></i><i style="background:#93c47d"></i><i style="background:#999999"></i></div></div>');
  const c = document.getElementById('v-cursor'), r = document.getElementById('v-ripple');
  document.addEventListener('mousemove', (e) => { c.style.left = e.clientX + 'px'; c.style.top = e.clientY + 'px'; }, true);
  document.addEventListener('mousedown', (e) => { r.style.left = e.clientX + 'px'; r.style.top = e.clientY + 'px'; r.classList.remove('go'); void r.offsetWidth; r.classList.add('go'); }, true);
  window.vcap = (t, s) => { const el = document.getElementById('v-cap'); if (!t) { el.classList.remove('on'); return; } el.replaceChildren(document.createTextNode(t)); if (s) { const sm = document.createElement('small'); sm.textContent = s; el.append(sm); } el.classList.add('on'); };
  window.vcard = (on, h, p) => { const k = document.getElementById('v-card'); if (h) k.querySelector('h1').textContent = h; if (p) k.querySelector('p').textContent = p; k.classList.toggle('off', !on); };
}
"""


async def record(url: str, proxy: str | None, frames_dir: str) -> list:
    async with async_playwright() as p:
        browser = await p.chromium.launch(**({"proxy": {"server": proxy}} if proxy else {}))
        ctx = await browser.new_context(viewport={"width": W, "height": H}, device_scale_factor=DSF,
                                        color_scheme="light", locale="fr-FR", ignore_https_errors=True)
        pg = await ctx.new_page()
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto(url, wait_until="networkidle", timeout=60000)
        await pg.evaluate(OVERLAY_JS, [OVERLAY_CSS, SITE])
        await pg.wait_for_timeout(1500)

        cdp = await ctx.new_cdp_session(pg)
        frames = []

        def on_frame(params):
            fn = os.path.join(frames_dir, f"f{len(frames):05d}.jpg")
            with open(fn, "wb") as f:
                f.write(base64.b64decode(params["data"]))
            frames.append((fn, params["metadata"]["timestamp"]))
            asyncio.ensure_future(cdp.send("Page.screencastFrameAck", {"sessionId": params["sessionId"]}))

        cdp.on("Page.screencastFrame", on_frame)
        await cdp.send("Page.startScreencast", {"format": "jpeg", "quality": 92, "maxWidth": int(W * DSF),
                                                  "maxHeight": int(H * DSF), "everyNthFrame": 1})

        pos = {"x": W * 0.55, "y": H * 0.45}
        await pg.mouse.move(pos["x"], pos["y"])

        async def wait(ms):
            await pg.wait_for_timeout(ms)

        async def glide(x, y, ms=700):
            n = max(8, int(ms / 16))
            x0, y0 = pos["x"], pos["y"]
            for i in range(1, n + 1):
                t = i / n
                e = t * t * (3 - 2 * t)
                await pg.mouse.move(x0 + (x - x0) * e, y0 + (y - y0) * e)
                await pg.wait_for_timeout(16)
            pos["x"], pos["y"] = x, y

        async def cap(text=None, sub=None):
            await pg.evaluate("([t, s]) => vcap(t, s)", [text, sub])

        async def box(sel):
            return await pg.locator(sel).first.bounding_box()

        async def scroll_to(sel, offset=TOP, ms=1000):
            await pg.evaluate("([s, o]) => { const el = document.querySelector(s); window.scrollTo({ top: el.getBoundingClientRect().top + window.scrollY - o, behavior: 'smooth' }); }", [sel, offset])
            await wait(ms)

        async def scroll_top(ms=900):
            await pg.evaluate("() => window.scrollTo({ top: 0, behavior: 'smooth' })")
            await wait(ms)

        async def click_sel(sel, ms=600):
            bx = await box(sel)
            await glide(bx["x"] + bx["width"] / 2, bx["y"] + bx["height"] / 2, ms)
            await wait(150)
            await pg.mouse.click(pos["x"], pos["y"])

        async def bubble(name):
            return await pg.evaluate("""(n) => { const c = [...document.querySelectorAll('#scatter-chart circle')].find((e) => e.__data__ && e.__data__.short === n); if (!c) return null; const r = c.getBoundingClientRect(); return { x: r.x + r.width / 2, y: r.y + r.height / 2 }; }""", name)

        async def band(label):
            return await pg.evaluate("""(l) => { const t = [...document.querySelectorAll('#totals-chart text.tr-band-label')].find((e) => e.textContent === l); const r = t.getBoundingClientRect(); return { x: r.x + r.width / 2, y: r.y }; }""", label)

        # 0. title card
        await wait(2600)
        await pg.evaluate("vcard(false)")
        await wait(900)

        # 1. standings
        await cap("En haut : le classement des cinq équipes", "Total, points Race, duels et progression depuis la dernière mise à jour")
        b1 = await box("#standing-chef"); b5 = await box("#standing-jules")
        await glide(b1["x"] + b1["width"] / 2, b1["y"] + 60, 900)
        await wait(600)
        await glide(b5["x"] + b5["width"] / 2, b5["y"] + 60, 1700)
        await wait(700)

        # 2. main chart hover
        await cap(None); await wait(250)
        await scroll_to("#totals-card", TOP - 4)
        await cap("Survolez la courbe : le total de chaque équipe, mise à jour par mise à jour")
        bc = await box("#totals-chart")
        await glide(bc["x"] + bc["width"] * 0.16, bc["y"] + bc["height"] * 0.62, 700)
        await glide(bc["x"] + bc["width"] * 0.86, bc["y"] + bc["height"] * 0.50, 3600)
        await wait(500)

        # 3. bands
        await cap("Bandes grises : Grand Chelem (foncées) et Masters 1000 (claires)", "Après la ligne pointillée : les tournois à venir, Shanghai puis Paris")
        rg = await band("RG")
        await glide(rg["x"], bc["y"] + bc["height"] * 0.55, 900)
        await wait(1300)
        par = await band("PAR")
        await glide(par["x"], bc["y"] + bc["height"] * 0.5, 1100)
        await wait(1500)

        # 4. ranks + duels
        await cap(None); await wait(250)
        await scroll_to("#rank-card")
        await cap("Position après chaque mise à jour, et duels gagnés entre équipes", "Chaque victoire sur un joueur d’une autre équipe vaut 5 points")
        br = await box("#rank-chart")
        await glide(br["x"] + br["width"] * 0.15, br["y"] + br["height"] * 0.4, 700)
        await glide(br["x"] + br["width"] * 0.8, br["y"] + br["height"] * 0.4, 1800)
        await wait(400)
        bd = await box("#duel-table")
        await glide(bd["x"] + bd["width"] * 0.62, bd["y"] + bd["height"] * 0.45, 1000)
        await wait(1400)

        # 5. gains
        await cap(None); await wait(250)
        await scroll_to("#gains-card")
        await cap("Points gagnés à chaque mise à jour, sur la même échelle pour toutes les équipes")
        best = await pg.evaluate("""() => { let best = null; document.querySelectorAll('#gains-chart rect').forEach((r) => { const b = r.getBoundingClientRect(); if (!best || b.height > best.h) best = { x: b.x + b.width / 2, y: b.y + b.height / 2, h: b.height }; }); return best; }""")
        await glide(best["x"], best["y"], 1100)
        await wait(1700)

        # 6. players tab
        await cap(None); await wait(250)
        await scroll_top()
        await cap("Onglet Joueurs")
        await click_sel("#tab-players", 700)
        await wait(1100)

        # 7. team filter: charts and table follow the selected team
        await cap("Filtrez par équipe d’un clic", "Les graphiques et le tableau ne montrent plus que cette équipe")
        await click_sel('button[data-team="CHAN"]', 700)
        await wait(1200)
        await scroll_to("#scatter-card", TOP + 10, 1100)
        await wait(1600)
        await scroll_to("#team-filter", TOP + 90, 900)
        await click_sel('button[data-team="All"]', 600)
        await wait(800)

        # 8. composition
        await cap(None); await wait(200)
        await scroll_to("#composition-card", TOP + 10, 900)
        await cap("D’où viennent les points Race de chaque équipe", "Survolez un segment pour voir le joueur")
        bcomp = await box("#composition-chart")
        await glide(bcomp["x"] + bcomp["width"] * 0.25, bcomp["y"] + 20, 900)
        await wait(900)
        await glide(bcomp["x"] + bcomp["width"] * 0.55, bcomp["y"] + 64, 1000)
        await wait(1100)

        # 9. scatter
        await cap(None); await wait(250)
        await scroll_to("#scatter-card")
        await cap("Tournois disputés et points Race par tournoi", "La taille de la bulle suit le total de points Race")
        for name, ms, hold in (("Sinner", 1100, 1500), ("Shelton", 900, 1100), ("Blanch", 900, 1100)):
            s = await bubble(name)
            if s:
                await glide(s["x"], s["y"], ms)
                await wait(hold)

        # 10. table: sort + search
        await cap(None); await wait(250)
        await scroll_to("#table-card")
        await cap("Cliquez sur un en-tête pour trier, ou cherchez un joueur")
        await click_sel('button[data-sort="duel_pts"]', 900)
        await wait(1500)
        await click_sel("#player-search", 900)
        await pg.keyboard.type("fils", delay=140)
        await wait(1000)

        # 11. player detail
        await cap("Cliquez sur un joueur pour voir sa saison")
        await click_sel("#player-table tbody tr", 800)
        await wait(900)
        await scroll_to("#player-detail", TOP, 1100)
        await cap("Sa saison : points Race, bilan par surface et par catégorie, derniers matchs")
        bdr = await box("#detail-race")
        await glide(bdr["x"] + bdr["width"] * 0.2, bdr["y"] + bdr["height"] * 0.5, 800)
        await glide(bdr["x"] + bdr["width"] * 0.9, bdr["y"] + bdr["height"] * 0.4, 1800)
        await wait(500)
        await scroll_to("#detail-matches", TOP + 60, 1200)
        await wait(1500)

        # 12. scoring tab
        await cap(None); await wait(250)
        await scroll_top(1000)
        await cap("Barème et sources : comment les points sont comptés")
        await click_sel("#tab-notes", 800)
        await wait(2600)

        # 13. end card
        await cap(None)
        await pg.evaluate(f"vcard(true, 'THE RACE 2026', '{SITE} · mis à jour chaque lundi · bonne saison !')")
        await wait(3200)

        await cdp.send("Page.stopScreencast")
        await wait(300)
        await browser.close()
        if errs:
            print("page errors:", errs)
        return frames


def encode(frames: list, out: pathlib.Path, work: str) -> None:
    lst = os.path.join(work, "list.txt")
    with open(lst, "w") as f:
        for i, (fn, ts) in enumerate(frames):
            nxt = frames[i + 1][1] if i + 1 < len(frames) else ts + 3.0
            f.write(f"file '{fn}'\nduration {max(nxt - ts, 0.001):.4f}\n")
        f.write(f"file '{frames[-1][0]}'\n")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst,
                    "-vf", "fps=30,scale=1920:1080:flags=lanczos,format=yuv420p",
                    "-c:v", "libx264", "-preset", "slow", "-crf", "21", "-movflags", "+faststart", str(out)], check=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("url", nargs="?", default=f"https://{SITE}/")
    ap.add_argument("--proxy", default=os.environ.get("HTTPS_PROXY") or None)
    ap.add_argument("--out", default=str(ROOT / "tutoriel.mp4"))
    a = ap.parse_args()
    work = tempfile.mkdtemp(prefix="race-tutorial-")
    frames_dir = os.path.join(work, "frames"); os.makedirs(frames_dir)
    proxy = a.proxy if a.url.startswith("https") else None
    frames = asyncio.run(record(a.url, proxy, frames_dir))
    json.dump(frames, open(os.path.join(work, "frames.json"), "w"))
    encode(frames, pathlib.Path(a.out), work)
    print(f"{len(frames)} frames, {frames[-1][1] - frames[0][1]:.1f} s -> {a.out}")
    shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    main()
