#!/usr/bin/env python3
# build-youtube-manifest.py — per-video YouTube upload manifest for the v3 demos.
# Output: youtube-upload-manifest.csv (one row per cut). Feed to Claude-for-Chrome
# (drives YouTube Studio) or upload manually; then capture the video IDs and wire
# them into the gallery + send-packs. CTA = onboarding front door (src_ deep link
# wires via #409/#431). Gallery link filled once published (#430).
import csv, json, glob, os, pathlib
ROOT = pathlib.Path(__file__).parent
DOMAIN = {"Floating & Marine Systems": "floating-marine",
          "Subsea, Pipelines & Integrity": "subsea-pipelines-integrity",
          "Wells & Subsurface": "wells-subsurface",
          "Cathodic Protection": "subsea-pipelines-integrity"}
TAGS = {"floating-marine": "offshore,mooring,FPSO,naval architecture,hydrodynamics",
        "subsea-pipelines-integrity": "subsea,pipeline,pipeline integrity,DNV,API 579,cathodic protection",
        "wells-subsurface": "petroleum engineering,production,reservoir,artificial lift,well economics"}
FRONT = "https://t.me/the_deckhand_bot"          # src_<domain>_<slug> deep link wires via #409/#431
GALLERY = "https://www.aceengineer.com/demos/deckhand/"   # live after #430 publish

rows = []
for f in sorted(glob.glob(str(ROOT / "specs/*.json"))):
    slug = os.path.basename(f)[:-5]
    if not (ROOT / "demos" / f"{slug}.mp4").exists():
        continue
    spec = json.load(open(f))
    title = spec.get("title", {}).get("big", slug)
    chan = spec["channel"]["name"]
    dom = DOMAIN.get(chan, "open-deck")
    tags = TAGS.get(dom, "engineering") + ",Deckhand,AceEngineer,digitalmodel"
    desc = (f"{title}\n\n"
            f"Watch Deckhand run a real {chan} calculation from a plain-English chat and send back a "
            f"code-checked report you can keep — no spreadsheets, no setup.\n\n"
            f"Try it on Deckhand: {FRONT}\n"
            f"More demos: {GALLERY}\n\n"
            f"A product of AceEngineer · powered by digitalmodel & worldenergydata. Demo uses synthetic inputs.")
    # 16:9 regular
    rows.append({"slug": slug, "cut": "16:9", "file": f"demos/{slug}.mp4",
                 "title": f"{title} | Deckhand", "visibility": "unlisted",
                 "tags": tags, "description": desc})
    # 9:16 Short
    if (ROOT / "demos" / f"{slug}v.mp4").exists():
        rows.append({"slug": slug, "cut": "9:16 Short", "file": f"demos/{slug}v.mp4",
                     "title": f"{title} #Shorts | Deckhand", "visibility": "unlisted",
                     "tags": tags + ",Shorts", "description": desc + "\n#Shorts"})

out = ROOT / "youtube-upload-manifest.csv"
with open(out, "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=["slug", "cut", "file", "title", "visibility", "tags", "description"])
    w.writeheader(); w.writerows(rows)
print(f"{out.name}: {len(rows)} videos ({sum(1 for r in rows if r['cut']=='16:9')} × 16:9 + "
      f"{sum(1 for r in rows if 'Short' in r['cut'])} × Shorts)")
