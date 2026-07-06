// build-web-v3.mjs — v3 demo gallery (MP4 <video> grid, grouped by channel) → web-v3/.
// Speculative: references demos/<slug>.mp4 + posters/<slug>.png relatively; publish
// the page alongside those dirs (or a GitHub Release per HOSTING.md #420). CTA is the
// generic onboarding front door — the per-demo src_<domain>_<workflow> deep link wires
// via the funnel contract #431 / card hook #409 (do NOT hand-format before then).
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const ROOT = path.dirname(fileURLToPath(import.meta.url));
const WORDMARK_SVG = fs.readFileSync(path.join(ROOT, 'assets', 'deckhand-wordmark.svg'), 'utf8');  // inlined → self-contained page
const OUT = path.join(ROOT, 'web-v3');
const FRONT_DOOR = 'https://t.me/the_deckhand_bot';   // Phase A target (DM ?start=src_<domain>_<workflow>)
// Phase B (#407, 2026-06-18): CTAs point at the "Deckhand — Start Here" onboarding GROUP invite —
// new contacts join, the deckhand-welcome plugin greets them. Per-demo src_ routing waits on the
// Phase-A gateway DM-onboarding; data-start is kept on each CTA so it lights up when A ships.
const START_HERE = 'https://t.me/+iUstcUn2dHA4YWQ5';
// Sustainable hosting (update.sh): USE_RELEASE=1 points <video> at the GitHub Release
// (stable URLs, --clobber to update in place) + a ?v=<contenthash> cache-bust so viewers
// always get the latest without the URL changing. Default = local relative paths (preview).
const USE_RELEASE = !!process.env.USE_RELEASE;
const REL = 'https://github.com/vamseeachanta/deckhand-sandbox/releases/download/demos';
const cb = rel => { try { const s = fs.statSync(path.join(ROOT, rel)); return Math.round(s.mtimeMs).toString(36) + '-' + s.size.toString(36); } catch { return '0'; } };
const murl = rel => USE_RELEASE ? `${REL}/${path.basename(rel)}?v=${cb(rel)}` : rel;
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

const cslug = c => 'topic-' + c.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');

const card = d => {
  const tag = `src_${DOMAIN[d.spec.channel.name] || 'open-deck'}_${d.slug}`;   // wired via #409/#431
  const hasV = fs.existsSync(path.join(ROOT, 'demos', `${d.slug}v.mp4`));
  const title = esc(d.spec.title?.big || d.slug);
  return `        <article class="card" id="${d.slug}">
          <button class="vwrap" data-src="${murl(`demos/${d.slug}.mp4`)}" data-title="${title}" aria-label="Play ${title}">
            <img class="thumb" loading="lazy" decoding="async" width="640" height="360" src="${murl(`thumbs/${d.slug}.jpg`)}" alt="${title}">
            <span class="play" aria-hidden="true">▶</span>
          </button>
          <div class="meta">
            <h3>${title}</h3>
            <div class="row">
              <a class="cta" href="${START_HERE}" data-start="${tag}" target="_blank" rel="noopener">Join Deckhand — Start Here →</a>
              ${hasV ? `<button class="alt" data-src="${murl(`demos/${d.slug}v.mp4`)}" data-title="${title} · vertical">▤ vertical</button>` : ''}
            </div>
          </div>
        </article>`;
};
const section = c => `    <section class="chan" id="${cslug(c)}"><h2>${esc(c)}</h2>\n      <div class="grid">\n${byChan[c].map(card).join('\n')}\n      </div>\n    </section>`;
const nav = channels.map(c => `        <div class="navgroup"><a class="navh" href="#${cslug(c)}" data-target="${cslug(c)}">${esc(c)}</a>
          <ul>${byChan[c].map(d => `<li><a href="#${d.slug}">${esc(d.spec.title?.big || d.slug)}</a></li>`).join('')}</ul></div>`).join('\n');

const page = `<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>Deckhand — see it work | AceEngineer</title>
<meta name="description" content="Watch Deckhand run real offshore & subsea engineering calculations from a plain-English chat and send back a code-checked report.">
<style>
:root{--navy:#0B3D91;--teal:#2BB2A6;--bg:#070c16;--panel:#0e1726;--ink:#e8eef9;--muted:#90a0bd;--line:#22304f;--side:288px}
*{box-sizing:border-box;margin:0;padding:0}html{scroll-behavior:smooth}
body{font-family:-apple-system,"Segoe UI",Roboto,Arial,sans-serif;background:var(--bg);color:var(--ink);line-height:1.5}
a{color:inherit}
.side{position:fixed;top:0;left:0;bottom:0;width:var(--side);background:#0a1120;border-right:1px solid var(--line);display:flex;flex-direction:column;padding:22px 16px;overflow-y:auto;z-index:20}
.side .brand{display:inline-flex;align-self:flex-start;background:#fff;border-radius:11px;padding:9px 15px;margin-bottom:4px}.side .brand svg{height:28px;width:auto;display:block}
.side .tag{font-size:12px;color:var(--muted);margin:0 0 16px 3px}
.side nav{flex:1}.navgroup{margin-bottom:13px}
.navh{display:block;font-size:14px;font-weight:700;color:#cfe0f2;text-decoration:none;padding:7px 10px;border-radius:8px;border-left:3px solid transparent}
.navh:hover,.navh.active{background:#11203a;border-left-color:var(--teal);color:#fff}
.navgroup ul{list-style:none;margin:3px 0 0;padding:0}
.navgroup li a{display:block;font-size:12.5px;color:var(--muted);text-decoration:none;padding:5px 10px 5px 16px;border-radius:7px;border-left:3px solid transparent}
.navgroup li a:hover{color:#fff;background:#0e1a30;border-left-color:#37506f}
.side .start{margin-top:14px;text-align:center;font-weight:700;color:#06243b;background:linear-gradient(135deg,var(--teal),#7af0c0);padding:11px;border-radius:11px;text-decoration:none}
main{margin-left:var(--side);max-width:1200px;padding:0 30px 80px}
.hero{padding:42px 4px 8px}.hero h1{font-size:30px;font-weight:800}.hero p{color:var(--muted);font-size:17px;margin-top:10px;max-width:780px}
.chan{margin-top:42px;scroll-margin-top:18px}.chan h2{font-size:20px;border-left:4px solid var(--teal);padding-left:12px;margin-bottom:18px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:22px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:16px;overflow:hidden;scroll-margin-top:18px;transition:transform .15s,border-color .15s}
.card:hover{transform:translateY(-3px);border-color:#3a4d74}.card:target{border-color:var(--teal);box-shadow:0 0 0 2px rgba(43,178,166,.45)}
.vwrap{display:block;width:100%;padding:0;border:0;background:#070c16;cursor:pointer;position:relative;aspect-ratio:16/9;overflow:hidden}
.thumb{width:100%;height:100%;object-fit:cover;display:block}
.vwrap .play{position:absolute;inset:0;margin:auto;width:56px;height:56px;display:flex;align-items:center;justify-content:center;background:rgba(7,12,22,.5);border:2px solid rgba(255,255,255,.85);border-radius:50%;color:#fff;font-size:20px;padding-left:4px;transition:.15s}
.vwrap:hover .play{background:var(--teal);border-color:var(--teal);color:#06243b;transform:scale(1.06)}
.meta{padding:14px 16px 16px}.meta h3{font-size:15.5px;font-weight:700;line-height:1.3}
.row{display:flex;align-items:center;gap:12px;margin-top:12px}
.cta{font-size:13.5px;font-weight:700;color:#06243b;background:linear-gradient(135deg,#4cc2ff,#7af0c0);padding:9px 14px;border-radius:10px;text-decoration:none}
.alt{font-size:13px;color:var(--teal);background:none;border:0;cursor:pointer;font-family:inherit;padding:0}
.lb{position:fixed;inset:0;background:rgba(3,6,12,.93);display:flex;align-items:center;justify-content:center;z-index:50;padding:28px}
.lb[hidden]{display:none}
.lbbox{position:relative;display:flex;flex-direction:column;align-items:center;max-width:95vw}
.lbbox video{max-width:min(1120px,95vw);max-height:84vh;width:auto;height:auto;border-radius:12px;background:#000;display:block}
.lbt{color:#cfe0f2;text-align:center;margin-top:12px;font-size:15px;font-weight:600}
.lbx{position:absolute;top:-16px;right:-12px;width:40px;height:40px;border-radius:50%;border:0;background:#fff;color:#0b1426;font-size:24px;cursor:pointer;line-height:1;box-shadow:0 4px 18px rgba(0,0,0,.5)}
footer{margin-left:var(--side);text-align:center;color:var(--muted);font-size:13px;padding:28px 30px 50px;border-top:1px solid var(--line)}footer a{color:var(--teal)}
@media(max-width:980px){:root{--side:0px}
 .side{position:sticky;top:0;bottom:auto;width:auto;flex-direction:row;align-items:center;gap:10px;overflow-x:auto;padding:9px 14px}
 .side .brand{margin:0;flex:none}.side .tag,.side .start,.navgroup ul{display:none}
 .side nav{display:flex;gap:6px}.navgroup{margin:0}
 .navh{white-space:nowrap;border-left:0;border-bottom:3px solid transparent;padding:7px 10px}.navh.active{border-left:0;border-bottom-color:var(--teal)}
 main,footer{margin-left:0}.hero{padding-top:26px}}
</style></head><body>
<aside class="side">
  <div class="brand">${WORDMARK_SVG}</div>
  <div class="tag">Open Deck · engineering demos</div>
  <nav>
${nav}
  </nav>
  <a class="start" href="${START_HERE}" target="_blank" rel="noopener">Start on Deckhand →</a>
</aside>
<main>
  <header class="hero"><h1>See Deckhand work</h1>
  <p>Ask a real engineering question in plain English. Deckhand asks for what it needs, runs the calculation to the design code, and sends back a report you can keep. Pick a topic on the left, or click any demo to play it.</p></header>
${channels.map(section).join('\n')}
  <footer>A product of <a href="https://aceengineer.com">AceEngineer</a> · powered by digitalmodel &amp; worldenergydata. Demos use synthetic inputs.</footer>
</main>
<div id="lb" class="lb" hidden><div class="lbbox"><button class="lbx" aria-label="Close">×</button><video id="lbv" controls playsinline preload="auto"></video><div class="lbt" id="lbt"></div></div></div>
<script>
(function(){var lb=document.getElementById('lb'),lbv=document.getElementById('lbv'),lbt=document.getElementById('lbt');
function op(src,t){lbv.src=src;lbt.textContent=t||'';lb.hidden=false;try{lbv.currentTime=0;}catch(e){}lbv.play().catch(function(){});document.body.style.overflow='hidden';}
function cl(){lbv.pause();lbv.removeAttribute('src');lbv.load();lb.hidden=true;document.body.style.overflow='';}
document.querySelectorAll('[data-src]').forEach(function(b){b.addEventListener('click',function(){op(b.getAttribute('data-src'),b.getAttribute('data-title'));});});
lb.addEventListener('click',function(e){if(e.target===lb||e.target.classList.contains('lbx'))cl();});
document.addEventListener('keydown',function(e){if(e.key==='Escape'&&!lb.hidden)cl();});
var nh={};document.querySelectorAll('.navh[data-target]').forEach(function(a){nh[a.getAttribute('data-target')]=a;});
if(window.IntersectionObserver){var ob=new IntersectionObserver(function(es){es.forEach(function(e){var a=nh[e.target.id];if(a)a.classList.toggle('active',e.isIntersecting);});},{rootMargin:'-12% 0px -75% 0px'});
document.querySelectorAll('section.chan').forEach(function(s){ob.observe(s);});}
})();
</script>
</body></html>`;

fs.rmSync(OUT, { recursive: true, force: true });
fs.mkdirSync(path.join(OUT, 'assets'), { recursive: true });
fs.writeFileSync(path.join(OUT, 'index.html'), page);
const wm = path.resolve(ROOT, '../../../aceengineer-strategy/strategy/deckhand/release/assets/deckhand-logo.svg');
if (fs.existsSync(wm)) fs.copyFileSync(wm, path.join(OUT, 'assets', 'deckhand-logo.svg'));
// symlink demos/ + posters/ for local preview (publisher co-locates the real files)
for (const d of ['demos', 'posters', 'thumbs']) { try { fs.symlinkSync(path.join('..', d), path.join(OUT, d)); } catch {} }
fs.writeFileSync(path.join(OUT, 'README.md'),
`# web-v3/ — generated v3 demo gallery (deckhand#430)\n\nGenerated by build-web-v3.mjs. To publish: copy this dir + demos/<slug>.mp4 + posters/<slug>.png\nto the host (aceengineer.com page or a Pages site), or point at a GitHub Release per HOSTING.md (#420).\nCTAs use the onboarding front door; the per-demo src_<domain>_<workflow> deep link wires via #409/#431.\n`);
console.log(`web-v3/ built — ${demos.length} demos across ${channels.length} channels`);
for (const c of channels) console.log(`  ${c}: ${byChan[c].map(d => d.slug).join(', ')}`);
