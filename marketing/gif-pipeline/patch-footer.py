#!/usr/bin/env python3
# patch-footer.py — fix the GTMReportBuilder generic footer disclaimer in composed
# reports ("parametric analysis" -> "engineering analysis"; not every run is a sweep).
import glob, pathlib
n = 0
for f in glob.glob("/mnt/local-analysis/deckhand-sandbox/marketing/gif-pipeline/proto-reports/*.report.html"):
    p = pathlib.Path(f); t = p.read_text()
    if "parametric analysis" in t:
        p.write_text(t.replace("parametric analysis", "engineering analysis")); n += 1
print(f"patched {n} report footers")
