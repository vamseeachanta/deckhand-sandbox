#!/usr/bin/env python3
# detect_report.py — analyse a captured report PNG (2x, content width 1200 logical)
# and return layout anchors the factory needs: displayed height, table-header bar
# positions, plot bands, the "results" table + a spotlight row. Pure image-analysis
# (no DOM/script injection), so it generalises across reports. Returns/print JSON.
import sys, json
from PIL import Image

def detect(png, content_w=1200):
    im = Image.open(png).convert("RGB"); W, H = im.size; px = im.load()
    sx = W / content_w                      # device-scale (img px per logical px)
    doch = round(H / sx)                     # displayed height at content_w
    def isnavy(r, g, b): return abs(r-36) < 42 and abs(g-59) < 42 and abs(b-83) < 48
    def chroma(r, g, b): return max(r, g, b) - min(r, g, b)
    def isgreen(r, g, b): return g > 110 and g - r > 25 and g - b > 25     # PASS
    def isred(r, g, b): return r > 130 and r - g > 55 and r - b > 35       # FAIL
    x0, x1, step = int(140*sx), min(W-2, int(1180*sx)), max(1, int(8*sx))
    xs = list(range(x0, x1, step))
    # navy full-width table-header bars
    navy_thresh = 0.72 * len(xs)
    bars, iny, start = [], False, 0
    for y in range(0, H, 2):
        c = sum(1 for x in xs if isnavy(*px[x, y]))
        if c >= navy_thresh and not iny: start, iny = y, True
        elif c < navy_thresh and iny: bars.append((start, y)); iny = False
    tables = [round((a+b)/2/sx) for a, b in bars if (b-a) > int(20*sx)]
    # colored chart bands
    col_thresh = max(8, int(0.11*len(xs)))
    crows = [y for y in range(0, H, 2)
             if sum(1 for x in xs if chroma(*px[x, y]) > 55 and not all(v > 235 for v in px[x, y])) > col_thresh]
    plots, s, p = [], None, None
    for y in crows:
        if s is None: s = y
        elif y - p > int(120*sx):
            if p - s > int(60*sx): plots.append((round(s/sx), round(p/sx)))
            s = y
        p = y
    if s is not None and p - s > int(60*sx): plots.append((round(s/sx), round(p/sx)))
    # results table = 2nd table bar (inputs/assumptions is usually first); override in spec
    results = tables[1] if len(tables) >= 2 else (tables[0] if tables else None)
    spotlight = [34, results + 14, 1128, 44] if results else None   # 1st data row
    # plot region: from just under the last table to the end of the coloured chart bands
    plot_region = None
    if plots:
        top = (tables[-1] + 290) if (tables and plots[0][0] > tables[-1]) else max(0, plots[0][0] - 150)
        plot_region = [0, top, 1200, min(doch, plots[-1][1] + 40) - top]
    return {"doch": doch, "tables": tables, "plots": plots, "plot_region": plot_region,
            "results_y": results, "spotlight": spotlight}

if __name__ == "__main__":
    print(json.dumps(detect(sys.argv[1]), indent=2))
