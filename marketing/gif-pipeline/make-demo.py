#!/usr/bin/env python3
# make-demo.py <slug> — the rinse-and-repeat factory. Given a chat spec
# (specs/<slug>.json) + a report (proto-reports/<slug>.report.html), it:
#   1. captures the report to a full-page image (proto-reports/<slug>.png)
#   2. auto-detects layout (detect_report) — stops/spotlight/plot/crops
#   3. emits demo-<slug>.html (16:9) + demo-<slug>v.html (9:16) reusing the
#      finalized engines, with all polish. Per-spec `demo` overrides honoured.
# Render: SLUG=<slug> bash render-anim.sh   ·   SLUG=<slug>v bash render-vert.sh
import sys, json, subprocess, tempfile, shutil, pathlib
from PIL import Image, ImageChops
from detect_report import detect

ROOT = pathlib.Path(__file__).parent
SEG16, SEG9 = 1900, 1500
LOGOMARK = '<svg class="mk"><use href="#dhmark"/></svg>'
SYMBOL = ('<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>'
 '<symbol id="dhmark" viewBox="-8 2 246 216">'
 '<path d="M0 10h130c58 0 100 42 100 100s-42 100-100 100H0z" fill="#0B3D91"/>'
 '<path d="M38 72c20-32 64-32 84 0v76c-20 32-64 32-84 0z" fill="#2BB2A6" opacity=".9"/>'
 '<path d="M30 140c12 16 31 26 55 26s43-10 55-26" fill="none" stroke="#6FE8D4" stroke-width="6" stroke-linecap="round"/>'
 '<path d="M30 110c12 16 31 26 55 26s43-10 55-26" fill="none" stroke="#12A6B0" stroke-width="6" stroke-linecap="round" opacity=".7"/>'
 '<path d="M30 80c12 16 31 26 55 26s43-10 55-26" fill="none" stroke="#0B3D91" stroke-width="6" stroke-linecap="round" opacity=".45"/>'
 '<rect x="18" y="48" width="20" height="120" fill="#0B3D91"/>'
 '<path d="M16 52c0-6.6 5.4-12 12-12s12 5.4 12 12-5.4 12-12 12-12-5.4-12-12z" fill="#0B3D91"/>'
 '</symbol></defs></svg>')

def extract_engine(fname):
    t = (ROOT/fname).read_text(); m = 'ENGINE = r"""'
    s = t.index(m) + len(m); return t[s:t.index('"""', s)]
ENGINE16 = extract_engine("build-v3-proto.py")
ENGINE9  = extract_engine("build-v3-vertical.py")

def capture_report(slug):
    """Render proto-reports/<slug>.report.html to a trimmed full-page PNG."""
    rhtml = ROOT/f"proto-reports/{slug}.report.html"; png = ROOT/f"proto-reports/{slug}.png"
    if png.exists(): return png
    if not rhtml.exists(): raise SystemExit(f"no report for {slug} ({rhtml})")
    raw = f"/tmp/{slug}.raw.png"; ud = tempfile.mkdtemp()
    subprocess.run(["google-chrome","--headless=new","--no-sandbox","--disable-gpu","--hide-scrollbars",
        "--force-device-scale-factor=2","--window-size=1200,3400",f"--user-data-dir={ud}",
        "--virtual-time-budget=11000",f"--screenshot={raw}",f"file://{rhtml}"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); shutil.rmtree(ud, ignore_errors=True)
    im = Image.open(raw).convert("RGB"); W, Hh = im.size; px = im.load()
    bg = im.getpixel((W-6, Hh-6))   # bottom-right = page background (may not be white)
    d = lambda p: abs(p[0]-bg[0])+abs(p[1]-bg[1])+abs(p[2]-bg[2])
    last = 0
    for y in range(0, Hh, 4):
        if any(d(px[x, y]) > 28 for x in range(20, W-20, 28)): last = y
    im.crop((0, 0, W, min(Hh, last + round(60*W/1200)))).save(png)
    return png

def auto_stops(det):
    # Robust proportional scroll (works across native + composed report styles).
    # The chart region is reliably detected by colour, so dwell on it; everything
    # else is proportional. Precise spotlights come from a per-spec `demo` override.
    doch = det["doch"]; maxS = doch - (675-40-42)
    cl = lambda y: max(0, min(maxS, round(y)))
    S = [{"y":0,"dwell":1400,"label":"Methodology & inputs"},
         {"y":cl(round(maxS*0.36)),"dwell":1600,"label":"Results"}]
    if det["plot_region"] and det["plot_region"][1] < doch-200:
        S.append({"y":cl(det["plot_region"][1]-90),"dwell":2000,"label":"Charts"})
    else:
        S.append({"y":cl(round(maxS*0.70)),"dwell":1600,"label":"Detail"})
    S.append({"y":maxS,"dwell":1500,"label":"Conclusions & caveat"})
    return S

def auto_crops(det):
    doch = det["doch"]
    cf = lambda docy, w: round(-(docy*w/1200 - 90))     # bring docy ~90px below the bar
    C = [{"w":540,"x":0,"y":0,"dwell":1500,"label":"📄 The report you receive"},
         {"w":1080,"x":-8,"y":cf(round(doch*0.30),1080),"dwell":1700,"label":"Results"}]
    if det["plot_region"] and det["plot_region"][1] < doch-200:
        C.append({"w":900,"x":-120,"y":cf(det["plot_region"][1]+120,900),"dwell":2000,"label":"Charts"})
    C.append({"w":1080,"x":-8,"y":cf(max(0,doch-560),1080),"dwell":1600,"label":"Conclusions"})
    return C

def dur16(spec, stops):
    cur = 3000
    for tn in spec["turns"]: cur += tn.get("hold", 1200 if tn.get("typing") else 3000)
    t0 = cur + 300 + 750
    for i, s in enumerate(stops): t0 += (0 if i==0 else SEG16) + s["dwell"]
    return t0 + 600 + 3500

def dur9(turns, crops):
    cur = 500
    for tn in turns: cur += tn.get("hold", 1100 if tn.get("typing") else 3000)
    c0 = cur + 400 + 650
    for i, s in enumerate(crops): c0 += (0 if i==0 else SEG9) + s["dwell"]
    return c0 + 600 + 3200

def main(slug):
    spec = json.loads((ROOT/f"specs/{slug}.json").read_text())
    demo = spec.get("demo", {})
    png = capture_report(slug)
    iw, ih = Image.open(png).size; doch = round(ih*1200/iw)
    det = detect(str(png)); img = f"file://{png}"
    rfile = f"{slug}_report.html"
    # 16:9
    stops = demo.get("stops") or auto_stops(det)
    html16 = (ENGINE16.replace("__SYMBOL__",SYMBOL).replace("__MK__",LOGOMARK)
        .replace("__IMG__",img).replace("__RFILE__",rfile).replace("__DOCH__",str(doch))
        .replace("__SEG__",str(SEG16)).replace("__STOPS__",json.dumps(stops))
        .replace("__SPEC__",json.dumps(spec, ensure_ascii=False)))
    (ROOT/f"demo-{slug}.html").write_text(html16)
    (ROOT/f"demo-{slug}.dur").write_text(str(dur16(spec, stops)))
    # 9:16 — Telegram side mapping me->out, bot->in
    turns9 = [{**t, "side": ("out" if t.get("side")=="me" else "in")} for t in spec["turns"]]
    crops = demo.get("crops") or auto_crops(det)
    ctah = spec.get("title",{}).get("big") or spec["closing"]["headline"]
    html9 = (ENGINE9.replace("__SYMBOL__",SYMBOL).replace("__IMG__",img).replace("__SEG__",str(SEG9))
        .replace("__CTAH__",json.dumps(ctah)).replace("__TURNS__",json.dumps(turns9, ensure_ascii=False))
        .replace("__CROPS__",json.dumps(crops)))
    (ROOT/f"demo-{slug}v.html").write_text(html9)
    (ROOT/f"demo-{slug}v.dur").write_text(str(dur9(turns9, crops)))
    print(f"{slug}: report {iw}x{ih}->1200x{doch} · tables {det['tables']} · results {det['results_y']} "
          f"· stops {len(stops)} · 16:9 {dur16(spec,stops)/1000:.0f}s · 9:16 {dur9(turns9,crops)/1000:.0f}s")

if __name__ == "__main__":
    main(sys.argv[1])
