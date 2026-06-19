#!/usr/bin/env python3
# build-v3-vertical.py — wall-thickness v3 VERTICAL 9:16 (#434 + #435).
# Real Telegram-client chat shell -> report opens -> cinematic Ken-Burns through
# readable crops (overview -> verdict -> plot -> caveat) -> CTA (unwired #409/#431).
# Frame 540x960 logical (render at 2x = 1080x1920). Render: SLUG=wt-v3v bash render-anim.sh
import json, pathlib
ROOT = pathlib.Path(__file__).parent
WORDMARK = (ROOT/"assets/deckhand-wordmark.svg").read_text()   # "Deckhand" wordmark (pamphlet brand)
IMG = "file:///tmp/wt-report.png"

# Telegram-styled chat turns (aligned to the real 300-bar report)
TURNS = [
 {"side":"out","time":"09:34","hold":2600,"html":"I've got a 12-inch export line going into 1500&nbsp;m in the Gulf — quick wall-thickness screen across the codes before we order line pipe?"},
 {"side":"in","typing":True,"hold":1100},
 {"side":"in","time":"09:34","hold":4200,"html":"Two things drive the wall, so first:<ul><li><b>Pressure basis</b> — operating or design?</li><li><b>Buckle arrestors</b> — running them or not?</li></ul>Then line size, grade, water depth.<span class='note'>I screen to DNV-ST-F101 + API&nbsp;RP&nbsp;1111.</span>"},
 {"side":"out","time":"09:36","hold":4200,"file":{"name":"line_datasheet.csv","size":"1.4 KB"},"html":"12.75-in OD, X65, 1500&nbsp;m. The <b>300&nbsp;bar</b> is <b>design</b> pressure, and we're planning <b>buckle arrestors</b>. 3&nbsp;mm CA in the file."},
 {"side":"in","typing":True,"hold":1100},
 {"side":"in","time":"09:36","hold":3200,"html":"Got it — running DNV-ST-F101 + API&nbsp;RP&nbsp;1111 now…"},
 {"side":"in","wide":True,"time":"09:37","hold":3400,"file":{"name":"wall_thickness_quickcheck_report.html","size":"inputs · method · results","deliver":True},"html":"Here's the screen — with &amp; without arrestors:<table><tr><th>Case</th><th>Min</th><th>Selected</th></tr><tr><td>With arrestors</td><td>17.08</td><td>SCH 80 <span class='ok'>✓</span></td></tr><tr><td>Without</td><td>25.41</td><td>SCH 140</td></tr></table><span class='note'>SCH 80 carries it, but tight — containment at 97%.</span>"},
]

# Ken-Burns crops over the report image (frame 540x960, doc bar 46px). w=display width.
CROPS = [
 {"w":540,  "x":0,    "y":0,     "dwell":1500, "label":"📄 The report you receive"},
 {"w":1180, "x":-8,   "y":-560,  "dwell":1300, "label":"Results — SCH 80 selected"},
 {"w":1180, "x":-235, "y":-560,  "dwell":1800, "label":"pressure-containment · U 0.97"},
 {"w":900,  "x":-120, "y":-1075, "dwell":2200, "label":"Utilisation plot"},
 {"w":1080, "x":-8,   "y":-2010, "dwell":1900, "label":"Design-basis caveat"},
]
SEG = 1500

SYMBOL='<svg width="0" height="0" style="position:absolute"><defs><symbol id="dhmark" viewBox="-8 2 246 216"><path d="M0 10h130c58 0 100 42 100 100s-42 100-100 100H0z" fill="#0B3D91"/><path d="M38 72c20-32 64-32 84 0v76c-20 32-64 32-84 0z" fill="#2BB2A6" opacity=".9"/><path d="M30 140c12 16 31 26 55 26s43-10 55-26" fill="none" stroke="#6FE8D4" stroke-width="6" stroke-linecap="round"/><path d="M30 110c12 16 31 26 55 26s43-10 55-26" fill="none" stroke="#12A6B0" stroke-width="6" stroke-linecap="round" opacity=".7"/><rect x="18" y="48" width="20" height="120" fill="#0B3D91"/><path d="M16 52c0-6.6 5.4-12 12-12s12 5.4 12 12-5.4 12-12 12-12-5.4-12-12z" fill="#0B3D91"/></symbol></defs></svg>'

ENGINE = r"""<!doctype html><html lang="en"><head><meta charset="utf-8"><style>
*{box-sizing:border-box;margin:0;padding:0;font-family:-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
html,body{width:540px;height:960px;overflow:hidden;background:#000}
.phone{position:relative;width:540px;height:960px;overflow:hidden;background:#cdd8e3;display:flex;flex-direction:column}
.phone::before{content:"";position:absolute;inset:0;background:radial-gradient(circle at 22% 14%,rgba(255,255,255,.05) 0 6px,transparent 7px),radial-gradient(circle at 72% 32%,rgba(0,0,0,.025) 0 8px,transparent 9px),linear-gradient(180deg,#c6d3df,#cdd8e3);background-size:150px 150px,190px 190px,100% 100%;z-index:0}
.hdr{position:relative;z-index:2;height:58px;background:#527da5;display:flex;align-items:center;gap:11px;padding:0 12px;color:#fff;box-shadow:0 1px 3px rgba(0,0,0,.2)}
.hdr .bk{font-size:23px;margin-right:1px}.hdr .av{height:38px;border-radius:11px;background:#fff;display:flex;align-items:center;justify-content:center;padding:0 11px}.hdr .av svg{height:20px;width:auto;display:block}
.hdr .nm{font-size:16px;font-weight:600;line-height:1.15}.hdr .sub{font-size:12px;color:#cfe0f2}.hdr .badge{font-size:9px;background:rgba(255,255,255,.22);border-radius:4px;padding:1px 5px;margin-left:6px;font-weight:600}.hdr .dots{margin-left:auto;font-size:21px}
.msgs{position:relative;z-index:1;flex:1;min-height:0;display:flex;flex-direction:column;justify-content:flex-end;gap:7px;padding:12px 11px 8px;overflow:hidden}
.turn{display:flex;overflow:hidden}.turn.out{justify-content:flex-end}.turn.in{justify-content:flex-start}
.b{max-width:81%;border-radius:13px;padding:7px 10px 5px;font-size:14px;line-height:1.42;color:#0e1621;box-shadow:0 1px 1px rgba(0,0,0,.13)}
.turn.wide .b{max-width:93%}
.in .b{background:#fff;border-bottom-left-radius:5px}.out .b{background:#effdde;border-bottom-right-radius:5px}
.b .t{font-size:10.5px;color:#8aa0b0;float:right;margin:3px 0 0 9px;position:relative;top:3px}.out .b .t{color:#5aa845}.tick{font-weight:700}
.b ul{margin:4px 0 2px;padding-left:17px}.b li{margin:2px 0}.b .note{display:block;margin-top:6px;font-size:12px;color:#3a8a5a;border-top:1px solid #eef3f0;padding-top:5px}
.b .file{margin-top:6px;display:flex;align-items:center;gap:8px;background:#f3f7fb;border-radius:9px;padding:6px 9px}.b .file .ic{width:30px;height:30px;border-radius:50%;background:#5aa7e6;color:#fff;display:flex;align-items:center;justify-content:center;font-size:15px}.b .file.deliver .ic{background:#2b8acb}.b .file .fn{font-size:12px;font-weight:600;color:#15324a}.b .file .fs{font-size:10.5px;color:#7e96a8}
.b table{border-collapse:collapse;width:100%;margin-top:5px;font-size:11.5px}.b th,.b td{border-bottom:1px solid #e6edf3;padding:3px 5px;text-align:left}.b th{color:#789;font-weight:600;font-size:9.5px;text-transform:uppercase}.b .ok{color:#1b9e4b;font-weight:700}
.typing{display:inline-flex;gap:4px;padding:3px 2px}.typing i{width:7px;height:7px;border-radius:50%;background:#9fb3c4}
.inp{position:relative;z-index:2;height:50px;background:#fff;display:flex;align-items:center;gap:11px;padding:0 14px;border-top:1px solid #dde6ee}.inp .ph{flex:1;color:#9bb0c2;font-size:15px}.inp .ic{color:#7e98ad;font-size:19px}
/* report takeover */
.report{position:absolute;inset:0;background:#fff;overflow:hidden;z-index:5;opacity:0}
.report .rbar{position:absolute;top:0;left:0;right:0;height:46px;background:#0d1730;display:flex;align-items:center;gap:8px;padding:0 14px;z-index:3;color:#aebbd4;font-size:12px}.report .rbar .mk{width:20px;height:20px}.report .rbar .wmchip{background:#fff;border-radius:6px;padding:3px 7px;display:inline-flex;align-items:center}.report .rbar .wmchip svg{height:13px;width:auto;display:block}.report .rbar b{color:#eaf4ff;font-weight:600;font-size:11.5px}
#doc{position:absolute;top:46px;left:0;transform-origin:top left;will-change:transform,width}
.seclabel{position:absolute;left:50%;bottom:26px;transform:translateX(-50%);background:rgba(8,14,26,.86);border:1px solid #2a3a55;color:#fff;font-size:15.5px;font-weight:600;padding:8px 18px;border-radius:999px;z-index:6;opacity:0;white-space:nowrap}
.cta{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:40px;background:radial-gradient(700px 700px at 50% 36%,#13224a,#0a0f1f);z-index:9;opacity:0}
.cta .lg{width:84px;height:84px;border-radius:21px;background:#eaf4ff;display:flex;align-items:center;justify-content:center;margin-bottom:22px}.cta .lg .mk{width:58px;height:58px}
.cta .wordplate{background:#fff;border-radius:16px;padding:18px 28px;margin-bottom:22px;box-shadow:0 10px 34px rgba(0,0,0,.34);display:flex;align-items:center;justify-content:center}.cta .wordplate svg{height:46px;width:auto;display:block}
.cta h2{color:#eef4ff;font-size:27px;font-weight:800;line-height:1.18;max-width:440px}.cta p{color:#9fb0c8;font-size:16px;margin-top:14px}
.cta .btn{margin-top:26px;font-size:18px;font-weight:700;color:#06243b;background:linear-gradient(135deg,#4cc2ff,#7af0c0);padding:15px 30px;border-radius:13px}.cta .hd{margin-top:12px;font-size:12px;color:#7e90ad}
</style></head><body>
__SYMBOL__
<div class="phone">
 <div class="hdr"><span class="bk">‹</span><div class="av">__WM__</div><div><div class="nm">Open Deck<span class="badge">BOT</span></div><div class="sub">bot · online</div></div><span class="dots">⋮</span></div>
 <div class="msgs" id="msgs"></div>
 <div class="inp"><span class="ic">😊</span><span class="ph">Message</span><span class="ic">📎</span><span class="ic">🎤</span></div>
 <div class="report" id="report"><div class="rbar"><span class="wmchip">__WM__</span><span>📄 <b>__RFILE__</b></span></div><img id="doc" src="__IMG__"></div>
 <div class="seclabel" id="seclabel"></div>
 <div class="cta" id="cta"><div class="wordplate">__WM__</div><h2 id="cta-h"></h2><p>No spreadsheets, no setup. Just ask, in plain English.</p><div class="btn">Join Deckhand — Start Here →</div><div class="hd">CTA wired via #409 (contract #431)</div></div>
</div>
<script>
var TURNS=__TURNS__,CROPS=__CROPS__,SEG=__SEG__;
function el(id){return document.getElementById(id);}
function ease(x){return x<.5?2*x*x:1-Math.pow(-2*x+2,2)/2;}
function clamp(v,a,b){return Math.max(a,Math.min(b,v));}
el('cta-h').textContent=__CTAH__;
var msgs=el('msgs');
TURNS.forEach(function(tn,i){var d=document.createElement('div');d.className='turn '+tn.side+(tn.wide?' wide':'');d.id='t-'+i;
 if(tn.typing){d.innerHTML='<div class="b"><span class="typing"><i></i><i></i><i></i></span></div>';}
 else{var fh='';if(tn.file){var cls=tn.file.deliver?'file deliver':'file';var ic=tn.file.deliver?'📄':'📎';fh='<span class="'+cls+'"><span class="ic">'+ic+'</span><span><span class="fn">'+tn.file.name+'</span><br><span class="fs">'+tn.file.size+'</span></span></span>'+(tn.html?'<br>':'');}
  var tick=tn.side==='out'?' <span class="tick">✓✓</span>':'';
  d.innerHTML='<div class="b">'+fh+(tn.html||'')+'<span class="t">'+(tn.time||'')+tick+'</span></div>';}
 msgs.appendChild(d);});
var ENTER=460,RFADE=600,CHAT_START=500,CLOSE_HOLD=3200,REP_FADE=650;
var turns=TURNS,cursor=CHAT_START;
turns.forEach(function(tn){tn._in=cursor;var h=tn.hold||(tn.typing?1100:3000);if(tn.typing)tn._out=cursor+h;cursor+=h;});
var repIn=cursor+400,c0=repIn+REP_FADE,cur=c0;
CROPS.forEach(function(s,i){if(i===0){s._from=cur;s._to=cur;}else{s._from=cur;s._to=cur+SEG;}s._dEnd=s._to+s.dwell;cur=s._dEnd;});
var repOut=cur,closeIn=repOut+RFADE,DURATION=closeIn+CLOSE_HOLD;window.DURATION=DURATION;
var Hh={};
function measure(){turns.forEach(function(tn,i){var e=el('t-'+i);e.style.display='flex';e.style.maxHeight='none';e.style.opacity='0';Hh[i]=e.offsetHeight;});}
function seek(t){
 turns.forEach(function(tn,i){var e=el('t-'+i);var present=t>=tn._in&&(tn._out==null||t<tn._out);if(!present){e.style.display='none';return;}
  e.style.display='flex';var p=ease(clamp((t-tn._in)/ENTER,0,1));e.style.opacity=p;e.style.maxHeight=(Hh[i]*p+(p>=1?40:0))+'px';e.style.transform='translateY('+((1-p)*10)+'px)';});
 var rep=el('report'),doc=el('doc'),sl=el('seclabel');
 if(t>=repIn&&t<closeIn){
   var o=t<repIn+REP_FADE?(t-repIn)/REP_FADE:(t>repOut?Math.max(0,1-(t-repOut)/RFADE):1);rep.style.opacity=clamp(o,0,1);
   var w=CROPS[0].w,x=CROPS[0].x,y=CROPS[0].y,lbl=CROPS[0].label;
   for(var i=0;i<CROPS.length;i++){var s=CROPS[i];if(t>=s._from){
     if(i>0&&t<s._to){var p=ease((t-s._from)/SEG),a=CROPS[i-1];w=a.w+(s.w-a.w)*p;x=a.x+(s.x-a.x)*p;y=a.y+(s.y-a.y)*p;lbl=(p>.55)?s.label:a.label;}
     else{w=s.w;x=s.x;y=s.y;lbl=s.label;}}}
   doc.style.width=w+'px';doc.style.transform='translate('+x+'px,'+y+'px)';
   sl.textContent=lbl;sl.style.opacity=clamp((t-(repIn+REP_FADE))/300,0,1)*(t>repOut?0:1);
 } else {rep.style.opacity=0;sl.style.opacity=0;}
 var cta=el('cta');if(t>=closeIn){cta.style.opacity=clamp((t-closeIn)/RFADE,0,1);}else cta.style.opacity=0;
}
window.seek=seek;measure();
var _tp=new URLSearchParams(location.search).get('t');seek(_tp!==null?parseInt(_tp,10):0);
</script></body></html>"""

html=(ENGINE.replace("__SYMBOL__",SYMBOL).replace("__IMG__",IMG).replace("__SEG__",str(SEG))
      .replace("__RFILE__","wall_thickness_quickcheck_report.html").replace("__WM__",WORDMARK)
      .replace("__CTAH__",json.dumps("Pipeline wall thickness, via engineering conversation."))
      .replace("__TURNS__",json.dumps(TURNS,ensure_ascii=False)).replace("__CROPS__",json.dumps(CROPS,ensure_ascii=False)))
(ROOT/"demo-wt-v3v.html").write_text(html)
cur=500
for tn in TURNS: cur+=tn.get("hold",1100 if tn.get("typing") else 3000)
repIn=cur+400;c0=repIn+650
for i,s in enumerate(CROPS): c0=c0+(0 if i==0 else SEG)+s["dwell"]
closeIn=c0+600;DUR=closeIn+3200
(ROOT/"demo-wt-v3v.dur").write_text(str(DUR))
print(f"demo-wt-v3v.html  DURATION={DUR}ms (~{DUR/1000:.1f}s)  [540x960 -> 2x 1080x1920]")
