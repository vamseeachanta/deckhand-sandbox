// build-web.mjs — generate the in-browser live demo gallery (deckhand#420) into web/.
// Reuses the SAME engine (template-anim.html) + specs/, swapping the ?t seek for an
// autoplay rAF loop (the ?t poster path is preserved for poster/thumbnail capture).
// No browser/ffmpeg needed — pure node. Output `web/` is committable to aceengineer-website.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.dirname(fileURLToPath(import.meta.url));
const OUT = path.join(ROOT, 'web');
const ONBOARD = 't.me/the_deckhand_bot?start=';

// channel display name -> onboarding domain slug (matches send-packs.md source tags)
const DOMAIN = {
  'Floating & Marine Systems': 'floating-marine',
  'Subsea, Pipelines & Integrity': 'subsea-pipelines-integrity',
  'Wells & Subsurface': 'wells-subsurface',
  'Cathodic Protection': 'subsea-pipelines-integrity', // CP lands in the subsea channel
};
// stable display order
const ORDER = ['Floating & Marine Systems', 'Subsea, Pipelines & Integrity',
  'Wells & Subsurface', 'Cathodic Protection'];

// ---- derive the live (autoplay) engine from the render engine ----
const engine = fs.readFileSync(path.join(ROOT, 'template-anim.html'), 'utf8');
const SEEK_TAIL = `var _tp=new URLSearchParams(location.search).get('t');
seek(_tp!==null?parseInt(_tp,10):0);`;
const LIVE_TAIL = `var _tp=new URLSearchParams(location.search).get('t');
if(_tp!==null){seek(parseInt(_tp,10));}
else{var _s=null;function _l(ts){if(_s===null)_s=ts;seek((ts-_s)%DURATION);requestAnimationFrame(_l);}requestAnimationFrame(_l);}`;
if (!engine.includes(SEEK_TAIL)) { console.error('FATAL: engine tail not found — template-anim.html changed; update build-web.mjs'); process.exit(1); }
const liveEngine = engine.replace(SEEK_TAIL, LIVE_TAIL);

// ---- read specs ----
const specDir = path.join(ROOT, 'specs');
const slugs = fs.readdirSync(specDir).filter(f => f.endsWith('.json')).map(f => f.replace(/\.json$/, '')).sort();
const demos = slugs.map(slug => {
  const txt = fs.readFileSync(path.join(specDir, `${slug}.json`), 'utf8');
  const spec = JSON.parse(txt); // validate
  return { slug, txt, spec };
});

// ---- emit one live player per demo ----
fs.rmSync(OUT, { recursive: true, force: true });
fs.mkdirSync(path.join(OUT, 'live'), { recursive: true });
fs.mkdirSync(path.join(OUT, 'assets'), { recursive: true });
for (const d of demos) {
  fs.writeFileSync(path.join(OUT, 'live', `${d.slug}.html`), liveEngine.replace('SPEC_PLACEHOLDER', d.txt));
}
// brand wordmark (copied from aceengineer-strategy release assets; synthetic, no PII)
const WORDMARK = path.resolve(ROOT, '../../../aceengineer-strategy/strategy/deckhand/release/assets/deckhand-logo.svg');
if (fs.existsSync(WORDMARK)) fs.copyFileSync(WORDMARK, path.join(OUT, 'assets', 'deckhand-logo.svg'));

// ---- group by channel ----
const byChannel = {};
for (const d of demos) { const c = d.spec.channel.name; (byChannel[c] ||= []).push(d); }
const channels = ORDER.filter(c => byChannel[c]).concat(Object.keys(byChannel).filter(c => !ORDER.includes(c)));

const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

const card = d => {
  const domain = DOMAIN[d.spec.channel.name] || 'open-deck';
  const tag = `demo_${domain}_${d.slug}`;
  const tryAsk = esc(d.spec.closing.tryThis || '');
  return `      <article class="card">
        <div class="player"><iframe loading="lazy" title="${esc(d.spec.title.big)}" data-src="live/${d.slug}.html" allow="autoplay"></iframe></div>
        <div class="meta">
          <h3>${esc(d.spec.title.big)}</h3>
          <p class="ask">Try asking: <span>"${tryAsk}"</span></p>
          <a class="cta" href="https://${ONBOARD}${tag}" target="_blank" rel="noopener">Try it on Deckhand →</a>
        </div>
      </article>`;
};

const section = c => `    <section class="chan">
      <h2>${esc(c)}</h2>
      <div class="grid">
${byChannel[c].map(card).join('\n')}
      </div>
    </section>`;

const page = `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Deckhand — live demos | AceEngineer</title>
<meta name="description" content="Watch Deckhand run real offshore & subsea engineering calculations from a plain-English chat — mooring fatigue, pipeline integrity, well economics, and more. Each demo animates live in your browser.">
<meta property="og:title" content="Deckhand — see it work">
<meta property="og:description" content="Ask in plain English; Deckhand runs the calc and sends back a code-checked report. Live demos.">
<meta property="og:type" content="website">
<meta property="og:url" content="https://aceengineer.com/demos/deckhand/">
<style>
  :root{--navy:#0B3D91;--teal:#2BB2A6;--bg:#070c16;--panel:#0e1726;--ink:#e8eef9;--muted:#90a0bd;--line:#22304f;}
  *{box-sizing:border-box;margin:0;padding:0}
  body{font-family:-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;background:var(--bg);color:var(--ink);line-height:1.5}
  header{padding:46px 24px 30px;text-align:center;background:radial-gradient(1100px 460px at 50% -10%,#13224a,#070c16)}
  header img{height:46px;margin-bottom:18px}
  header h1{font-size:34px;font-weight:800;letter-spacing:.2px}
  header p{color:var(--muted);font-size:18px;margin-top:12px;max-width:760px;margin-left:auto;margin-right:auto}
  header .start{display:inline-block;margin-top:22px;font-weight:700;color:#06243b;background:linear-gradient(135deg,var(--teal),#7af0c0);padding:13px 26px;border-radius:12px;text-decoration:none}
  main{max-width:1180px;margin:0 auto;padding:18px 20px 70px}
  .chan{margin-top:40px}
  .chan h2{font-size:21px;border-left:4px solid var(--teal);padding-left:12px;margin-bottom:18px}
  .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(330px,1fr));gap:22px}
  .card{background:var(--panel);border:1px solid var(--line);border-radius:16px;overflow:hidden;display:flex;flex-direction:column}
  .player{position:relative;width:100%;aspect-ratio:1200/675;background:#070c16;overflow:hidden}
  .player iframe{position:absolute;top:0;left:0;width:1200px;height:675px;border:0;transform-origin:top left}
  .meta{padding:15px 17px 17px}
  .meta h3{font-size:16px;font-weight:700;line-height:1.3}
  .ask{font-size:13px;color:var(--muted);margin-top:9px}.ask span{color:var(--teal)}
  .cta{display:inline-block;margin-top:14px;font-size:14px;font-weight:700;color:#06243b;background:linear-gradient(135deg,#4cc2ff,#7af0c0);padding:10px 16px;border-radius:10px;text-decoration:none}
  footer{text-align:center;color:var(--muted);font-size:13px;padding:30px 20px 50px;border-top:1px solid var(--line)}
  footer a{color:var(--teal)}
</style>
</head>
<body>
<header>
  <img src="assets/deckhand-logo.svg" alt="Deckhand">
  <h1>See Deckhand work</h1>
  <p>Ask a real engineering question in plain English. Deckhand asks for what it needs, runs the calculation to the design code, and sends back a report you can keep. Every demo below animates live — no sound needed.</p>
  <a class="start" href="https://${ONBOARD}demo_open-deck_gallery" target="_blank" rel="noopener">Start on Deckhand →</a>
</header>
<main>
${channels.map(section).join('\n')}
</main>
<footer>
  A product of <a href="https://aceengineer.com">AceEngineer</a> · powered by digitalmodel &amp; worldenergydata.
  Demos use synthetic inputs. Message <b>@the_deckhand_bot</b> to start.
</footer>
<script>
  // scale each 1200x675 live player to its card width
  function fit(f){ var w=f.parentElement.clientWidth; f.style.transform='scale('+(w/1200)+')'; }
  var frames=[].slice.call(document.querySelectorAll('.player iframe'));
  // lazy-load: only start a player when it nears the viewport (keeps many animations cheap)
  var io=new IntersectionObserver(function(es){es.forEach(function(e){
    var f=e.target;
    if(e.isIntersecting && !f.src){ f.src=f.dataset.src; f.addEventListener('load',function(){fit(f);}); }
  });},{rootMargin:'300px'});
  frames.forEach(function(f){ fit(f); io.observe(f); });
  window.addEventListener('resize',function(){frames.forEach(fit);});
</script>
</body>
</html>`;

fs.writeFileSync(path.join(OUT, 'index.html'), page);
fs.writeFileSync(path.join(OUT, 'README.md'),
`# web/ — generated live demo gallery (deckhand#420)\n\nGenerated by \`build-web.mjs\` from \`template-anim.html\` + \`specs/*.json\`. Do not hand-edit.\nPublish to aceengineer.com: copy this dir to the website as \`content/demos/deckhand/\`.\nCanonical link: https://aceengineer.com/demos/deckhand/\n\nRe-generate after any spec change: \`node build-web.mjs\`\n`);

console.log(`web/ built — ${demos.length} demos across ${channels.length} channels:`);
for (const c of channels) console.log(`  ${c}: ${byChannel[c].map(d => d.slug).join(', ')}`);
