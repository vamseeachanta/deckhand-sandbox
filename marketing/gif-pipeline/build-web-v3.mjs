// build-web-v3.mjs — v3 demo gallery (MP4 <video> grid, grouped by channel) → web-v3/.
// Speculative: references demos/<slug>.mp4 + posters/<slug>.png relatively; publish
// the page alongside those dirs (or a GitHub Release per HOSTING.md #420). CTA is the
// generic onboarding front door — the per-demo src_<domain>_<workflow> deep link wires
// via the funnel contract #431 / card hook #409 (do NOT hand-format before then).
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const ROOT = path.dirname(fileURLToPath(import.meta.url));
const OUT = path.join(ROOT, 'web-v3');
const FRONT_DOOR = 'https://t.me/the_deckhand_bot';   // #431/#409 will append ?start=src_<domain>_<workflow>
const DOMAIN = {
  'Floating & Marine Systems': 'floating-marine',
  'Subsea, Pipelines & Integrity': 'subsea-pipelines-integrity',
  'Wells & Subsurface': 'wells-subsurface',
  'Cathodic Protection': 'subsea-pipelines-integrity',
};
const ORDER = ['Floating & Marine Systems', 'Subsea, Pipelines & Integrity', 'Wells & Subsurface', 'Cathodic Protection'];
const esc = s => String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');

const demos = fs.readdirSync(path.join(ROOT, 'specs')).filter(f => f.endsWith('.json'))
  .map(f => f.replace(/\.json$/, ''))
  .filter(slug => fs.existsSync(path.join(ROOT, 'demos', `${slug}.mp4`)))   // only rendered ones
  .map(slug => ({ slug, spec: JSON.parse(fs.readFileSync(path.join(ROOT, 'specs', `${slug}.json`), 'utf8')) }))
  .sort();

const byChan = {};
for (const d of demos) (byChan[d.spec.channel.name] ||= []).push(d);
const channels = ORDER.filter(c => byChan[c]).concat(Object.keys(byChan).filter(c => !ORDER.includes(c)));

const card = d => {
  const tag = `src_${DOMAIN[d.spec.channel.name] || 'open-deck'}_${d.slug}`;   // wired via #409/#431
  const hasV = fs.existsSync(path.join(ROOT, 'demos', `${d.slug}v.mp4`));
  return `      <article class="card">
        <video class="v" muted loop autoplay playsinline preload="metadata"
               poster="posters/${d.slug}.png"><source src="demos/${d.slug}.mp4" type="video/mp4"></video>
        <div class="meta">
          <h3>${esc(d.spec.title?.big || d.slug)}</h3>
          <div class="row">
            <a class="cta" href="${FRONT_DOOR}" data-start="${tag}" target="_blank" rel="noopener">Try it on Deckhand →</a>
            ${hasV ? `<a class="alt" href="demos/${d.slug}v.mp4" target="_blank" rel="noopener">▤ vertical</a>` : ''}
          </div>
        </div>
      </article>`;
};
const section = c => `    <section class="chan"><h2>${esc(c)}</h2>\n      <div class="grid">\n${byChan[c].map(card).join('\n')}\n      </div>\n    </section>`;

const page = `<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Deckhand — see it work | AceEngineer</title>
<meta name="description" content="Watch Deckhand run real offshore & subsea engineering calculations from a plain-English chat and send back a code-checked report.">
<style>
:root{--navy:#0B3D91;--teal:#2BB2A6;--bg:#070c16;--panel:#0e1726;--ink:#e8eef9;--muted:#90a0bd;--line:#22304f}
*{box-sizing:border-box;margin:0;padding:0}body{font-family:-apple-system,"Segoe UI",Roboto,Arial,sans-serif;background:var(--bg);color:var(--ink);line-height:1.5}
header{padding:46px 24px 30px;text-align:center;background:radial-gradient(1100px 460px at 50% -10%,#13224a,#070c16)}
header img{height:44px;margin-bottom:16px}header h1{font-size:33px;font-weight:800}header p{color:var(--muted);font-size:18px;margin:12px auto 0;max-width:760px}
header .start{display:inline-block;margin-top:22px;font-weight:700;color:#06243b;background:linear-gradient(135deg,var(--teal),#7af0c0);padding:13px 26px;border-radius:12px;text-decoration:none}
main{max-width:1180px;margin:0 auto;padding:16px 20px 70px}.chan{margin-top:40px}.chan h2{font-size:21px;border-left:4px solid var(--teal);padding-left:12px;margin-bottom:18px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(330px,1fr));gap:22px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:16px;overflow:hidden}
.v{width:100%;aspect-ratio:16/9;display:block;background:#070c16;object-fit:cover}
.meta{padding:14px 16px 16px}.meta h3{font-size:16px;font-weight:700;line-height:1.3}
.row{display:flex;align-items:center;gap:12px;margin-top:12px}
.cta{font-size:14px;font-weight:700;color:#06243b;background:linear-gradient(135deg,#4cc2ff,#7af0c0);padding:9px 15px;border-radius:10px;text-decoration:none}
.alt{font-size:13px;color:var(--teal);text-decoration:none}
footer{text-align:center;color:var(--muted);font-size:13px;padding:30px 20px 50px;border-top:1px solid var(--line)}footer a{color:var(--teal)}
</style></head><body>
<header><img src="assets/deckhand-logo.svg" alt="Deckhand"><h1>See Deckhand work</h1>
<p>Ask a real engineering question in plain English. Deckhand asks for what it needs, runs the calculation to the design code, and sends back a report you can keep.</p>
<a class="start" href="${FRONT_DOOR}" target="_blank" rel="noopener">Start on Deckhand →</a></header>
<main>
${channels.map(section).join('\n')}
</main>
<footer>A product of <a href="https://aceengineer.com">AceEngineer</a> · powered by digitalmodel &amp; worldenergydata. Demos use synthetic inputs.</footer>
</body></html>`;

fs.rmSync(OUT, { recursive: true, force: true });
fs.mkdirSync(path.join(OUT, 'assets'), { recursive: true });
fs.writeFileSync(path.join(OUT, 'index.html'), page);
const wm = path.resolve(ROOT, '../../../aceengineer-strategy/strategy/deckhand/release/assets/deckhand-logo.svg');
if (fs.existsSync(wm)) fs.copyFileSync(wm, path.join(OUT, 'assets', 'deckhand-logo.svg'));
// symlink demos/ + posters/ for local preview (publisher co-locates the real files)
for (const d of ['demos', 'posters']) { try { fs.symlinkSync(path.join('..', d), path.join(OUT, d)); } catch {} }
fs.writeFileSync(path.join(OUT, 'README.md'),
`# web-v3/ — generated v3 demo gallery (deckhand#430)\n\nGenerated by build-web-v3.mjs. To publish: copy this dir + demos/<slug>.mp4 + posters/<slug>.png\nto the host (aceengineer.com page or a Pages site), or point at a GitHub Release per HOSTING.md (#420).\nCTAs use the onboarding front door; the per-demo src_<domain>_<workflow> deep link wires via #409/#431.\n`);
console.log(`web-v3/ built — ${demos.length} demos across ${channels.length} channels`);
for (const c of channels) console.log(`  ${c}: ${byChan[c].map(d => d.slug).join(', ')}`);
