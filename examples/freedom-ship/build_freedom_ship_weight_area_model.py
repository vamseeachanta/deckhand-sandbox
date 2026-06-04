from pathlib import Path
import csv, json, datetime

# Output goes next to this script, in ./model/ (override with FREEDOM_SHIP_OUTDIR).
import os
outdir = Path(os.environ.get('FREEDOM_SHIP_OUTDIR', Path(__file__).resolve().parent / 'model'))
outdir.mkdir(parents=True, exist_ok=True)

LOA=1609.34
B=228.60
rho=1.025
footprint=LOA*B
acres=footprint/4046.8564224
sqkm=footprint/1e6
DECKS=25
rect_gross=footprint*DECKS

eff_factors=[0.55,0.60,0.65,0.70,0.78,0.85,0.92,0.96,0.98,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,0.98,0.95,0.92,0.88,0.82,0.75,0.65,0.50]
ng_mid=[0.38,0.43,0.45,0.49,0.54,0.58,0.60,0.62,0.63,0.60,0.63,0.65,0.65,0.65,0.65,0.62,0.58,0.56,0.54,0.51,0.49,0.46,0.42,0.39,0.35]
programs=[
'Double bottom / ballast / tanks / damage-control voids',
'Fuel, water, wastewater tanks; low machinery; utility trunks',
'Power auxiliaries, desalination, fire pumps, substations, workshops',
'Freight/logistics spine, stores, waste sorting, crew service',
'Parking/service vehicles, cold/dry stores, loading docks',
'Arrival harbor interface, security, customs-style processing, terminals',
'Main transit concourse, public-safety staging, logistics ring',
'Retail, food halls, civic services, clinics, lower boulevard',
'Major civic deck: hospital expansion, education, municipal services',
'Mixed public/residential transition, schools, neighborhood services',
'Residential neighborhood A, local retail, clinics, refuge zones',
'Residential/hotel neighborhood B, medium-density housing',
'Residential/hotel neighborhood C, distributed MEP rooms',
'Residential neighborhood D, schools/community, parks/atria breaks',
'Residential/hotel neighborhood E, reserve for trunks/egress',
'Residential plus major refuge/transfer deck and leisure/civic uses',
'Parks, sports, entertainment, residential edges, atria/voids',
'Upper residential/hotels, conference/leisure, HVAC/life-safety plant',
'Upper residential/hotel, restaurants, observation amenities',
'Lower-density residential, resort/amenity, outdoor protected decks',
'Recreation, parks, upper civic/entertainment, solar/utility zones',
'Resort/amenity, observation, event space, upper mechanical rooms',
'Open-air recreation, sports, gardens, aviation/drone/emergency clearances',
'Weather deck, pools/recreation, solar, exhaust/intake, lifesaving systems',
'Observation/comms/navigation, emergency assembly, lightweight amenities'
]

struct_density=[]
outfit_density=[]
payload_density=[]
kg_band=[]
for i in range(25):
    d=i+1
    if d<=3:
        sd=1.20; od=0.20; pd=0.25; kg=4+d*2
    elif d<=5:
        sd=0.95; od=0.28; pd=0.45; kg=12+d*2.5
    elif d<=9:
        sd=0.80; od=0.32; pd=0.25; kg=18+d*3.2
    elif d<=16:
        sd=0.68; od=0.30; pd=0.18; kg=25+d*3.7
    elif d<=20:
        sd=0.62; od=0.34; pd=0.20; kg=30+d*4.0
    elif d<=23:
        sd=0.55; od=0.45; pd=0.28; kg=35+d*4.2
    else:
        sd=0.45; od=0.35; pd=0.18; kg=40+d*4.3
    struct_density.append(sd); outfit_density.append(od); payload_density.append(pd); kg_band.append(kg)

deck_rows=[]
for idx in range(25):
    d=idx+1
    eff_gross=footprint*eff_factors[idx]
    net=eff_gross*ng_mid[idx]
    structure=eff_gross*struct_density[idx]
    outfit=net*outfit_density[idx]
    payload=net*payload_density[idx]
    deck_rows.append(dict(deck=d, factor=eff_factors[idx], gross_m2=eff_gross, net_m2=net, ng=ng_mid[idx], program=programs[idx], struct_t=structure, outfit_t=outfit, payload_t=payload, kg_m=kg_band[idx]))

sum_eff=sum(r['gross_m2'] for r in deck_rows)
sum_net=sum(r['net_m2'] for r in deck_rows)
shipwide_ng=sum_net/sum_eff
W_struct=sum(r['struct_t'] for r in deck_rows)
W_outfit=sum(r['outfit_t'] for r in deck_rows)
W_payload_area=sum(r['payload_t'] for r in deck_rows)

def util_model(N, p_kw_person=5.0, peak_factor=1.8, reserve=1.25, water_lpd=220, waste_lpd=180, food_kgpd=2.2, food_days=30, water_days=3, fuel_days=14, diesel_mwh_per_t=5.0):
    avg_mw=N*p_kw_person/1000
    installed_mw=avg_mw*peak_factor*reserve
    water_m3d=N*water_lpd/1000
    water_store_t=water_m3d*water_days
    waste_m3d=N*waste_lpd/1000
    food_t= N*food_kgpd/1000*food_days
    fuel_t= avg_mw*24*fuel_days/diesel_mwh_per_t
    people_t=N*0.09
    personal_t=N*1.0
    hospital_beds=N/1000*3
    hospital_m2=hospital_beds*150
    students=N*0.18
    school_m2=students*12
    refuge_m2=N*2.0
    solid_waste_tpd=N*1.5/1000
    solid_waste_buffer_t=solid_waste_tpd*14
    battery_mwh=avg_mw*2
    battery_t=battery_mwh*8
    return locals()

scenarios=[util_model(N) for N in [60000,80000,100000]]
W_mach_fixed=sum_eff*0.22
W_secondary=sum_eff*0.16
m80=util_model(80000)
W_variable80=m80['people_t']+m80['personal_t']+m80['water_store_t']+m80['food_t']+m80['fuel_t']+m80['solid_waste_buffer_t']+m80['battery_t']
W_nominal80=W_struct+W_secondary+W_outfit+W_payload_area+W_mach_fixed+W_variable80
W_margin80=W_nominal80*0.22
W_design80=W_nominal80+W_margin80

hydro=[]
for T in [25,30,35,40,45,50]:
    for Cb in [0.85,0.90,0.95]:
        disp=rho*footprint*T*Cb
        hydro.append(dict(T=T,Cb=Cb,disp_t=disp,reserve_t=disp-W_design80,reserve_pct=(disp-W_design80)/disp*100))

cat_rows=[
('Primary/deck cellular structure', W_struct, 'Deck-by-deck effective gross x structural density; central density varies 0.45-1.20 t/m2'),
('Secondary structure, shafts, trunks, foundations', W_secondary, '0.16 t/m2 over effective programmable gross'),
('Architectural outfit and accommodation fit-out', W_outfit, 'Deck net area x outfit density by deck type; central 0.20-0.45 t/m2'),
('Area payload/inventory/parks/vehicles allowance', W_payload_area, 'Deck net area x carried-payload density by deck type; excludes people and consumable liquids'),
('Fixed machinery, utilities, MEP, plant and distribution', W_mach_fixed, '0.22 t/m2 over effective gross; central distributed independent-city plant allowance'),
('People', m80['people_t'], '80,000 x 0.09 t/person'),
('Personal effects / residential contents', m80['personal_t'], '80,000 x 1.0 t/person central long-stay allowance'),
('Potable/technical water reserve', m80['water_store_t'], '220 L/person/day x 3 days'),
('Food reserve', m80['food_t'], '2.2 kg/person/day x 30 days'),
('Diesel-equivalent fuel reserve', m80['fuel_t'], '5 kW/person average x 14 days / 5 MWh/t'),
('Solid waste buffer', m80['solid_waste_buffer_t'], '1.5 kg/person/day x 14 days'),
('Battery critical ride-through', m80['battery_t'], '2 h average-load equivalent x 8 t/MWh'),
('Design growth / estimating margin', W_margin80, '22% on nominal estimated weight'),
]

with open(outdir/'deck_area_weight_model.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(deck_rows[0].keys()))
    w.writeheader(); w.writerows(deck_rows)
with open(outdir/'population_utility_scenarios.csv','w',newline='') as f:
    fields=['N','avg_mw','installed_mw','water_m3d','water_store_t','waste_m3d','food_t','fuel_t','people_t','personal_t','hospital_beds','hospital_m2','students','school_m2','refuge_m2','solid_waste_tpd','solid_waste_buffer_t','battery_mwh','battery_t']
    w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
    for s in scenarios: w.writerow({k:s[k] for k in fields})
with open(outdir/'hydrostatic_capacity_sweep.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=['T','Cb','disp_t','reserve_t','reserve_pct'])
    w.writeheader(); w.writerows(hydro)

snapshot=dict(LOA_m=LOA,beam_m=B,footprint_m2=footprint,footprint_acres=acres,rectangular_25_deck_gross_m2=rect_gross,effective_gross_m2=sum_eff,net_area_m2=sum_net,shipwide_net_gross=shipwide_ng,weights_t={k:v for k,v,_ in cat_rows},design80_total_t=W_design80)
(outdir/'model_snapshot.json').write_text(json.dumps(snapshot,indent=2))

fmt=lambda x: f"{x:,.0f}"
fmt1=lambda x: f"{x:,.1f}"
def row(cells): return '<tr>'+''.join(f'<td>{c}</td>' for c in cells)+'</tr>'
deck_html=''.join(row([r['deck'], r['program'], f"{r['factor']:.2f}", fmt(r['gross_m2']), fmt(r['net_m2']), f"{r['ng']:.2f}", fmt(r['struct_t']), fmt(r['outfit_t']), fmt(r['payload_t']), f"{r['kg_m']:.1f}"]) for r in deck_rows)
cat_html=''.join(row([name, fmt(w), f"{w/W_design80*100:.1f}%", basis]) for name,w,basis in cat_rows)
scen_html=''.join(row([s['N'], fmt1(s['avg_mw']), fmt1(s['installed_mw']), fmt(s['water_m3d']), fmt(s['water_store_t']), fmt(s['food_t']), fmt(s['fuel_t']), fmt(s['hospital_m2']), fmt(s['school_m2']), fmt(s['refuge_m2'])]) for s in scenarios)
hydro_html=''.join(row([h['T'], f"{h['Cb']:.2f}", fmt(h['disp_t']), fmt(h['reserve_t']), f"{h['reserve_pct']:.1f}%"]) for h in hydro)
html=f"""<!doctype html>
<html lang='en'>
<head><meta charset='utf-8'/><meta name='viewport' content='width=device-width, initial-scale=1'/><title>Freedom Ship - Weight and Area Model</title>
<style>
:root{{--bg:#09111f;--panel:#101827;--panel2:#162033;--ink:#e5e7eb;--muted:#a7b0c0;--line:#334155;--accent:#38bdf8;--warn:#f59e0b;--bad:#fb7185;--good:#34d399}}
body{{margin:0;background:linear-gradient(180deg,#07101f,#0b1220 35%,#111827);color:var(--ink);font:15px/1.55 system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif}}
header{{padding:42px 28px 28px;border-bottom:1px solid var(--line);background:radial-gradient(circle at 18% 0%,rgba(56,189,248,.24),transparent 34%),linear-gradient(135deg,#08111f,#111827)}}
main{{max-width:1280px;margin:0 auto;padding:26px}} h1{{font-size:40px;line-height:1.05;margin:0 0 10px}} h2{{font-size:25px;margin:32px 0 10px;border-bottom:1px solid var(--line);padding-bottom:8px}} h3{{font-size:19px;margin:22px 0 8px;color:#dbeafe}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px}} .card{{background:linear-gradient(180deg,var(--panel),var(--panel2));border:1px solid var(--line);border-radius:14px;padding:15px}} .label{{font-size:12px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted)}} .big{{font-size:24px;font-weight:800}} .muted{{color:var(--muted)}}
table{{width:100%;border-collapse:collapse;margin:12px 0 20px;background:rgba(17,24,39,.82);border:1px solid var(--line);border-radius:12px;overflow:hidden}} th,td{{border-bottom:1px solid var(--line);padding:9px 10px;text-align:left;vertical-align:top}} th{{background:#1e293b;color:#dbeafe;position:sticky;top:0}} tr:last-child td{{border-bottom:0}} .small{{font-size:13px;color:var(--muted)}} .callout{{border-left:4px solid var(--accent);background:rgba(56,189,248,.08);padding:14px 16px;border-radius:10px;margin:16px 0}} .risk{{border-left-color:var(--bad);background:rgba(251,113,133,.08)}} .warn{{border-left-color:var(--warn);background:rgba(245,158,11,.08)}} code{{background:#0f172a;border:1px solid var(--line);border-radius:5px;padding:1px 4px}} .scroll{{overflow:auto;max-height:640px;border-radius:12px}}
</style></head><body><header><h1>Freedom Ship - Weight and Area Model</h1>
<p class='muted'>Concept-level deck-by-deck area, mass, CG, utilities, reserve, and hydrostatic capacity model. Generated {datetime.datetime.now().isoformat(timespec='seconds')}. This is a preliminary engineering model, not a class-approved design.</p></header><main>
<section><h2>1. Executive model snapshot</h2><div class='grid'>
<div class='card'><div class='label'>Planform footprint</div><div class='big'>{fmt(footprint)} m2</div><div class='small'>{sqkm:.3f} km2 / {acres:.1f} acres</div></div>
<div class='card'><div class='label'>Rectangular 25-deck gross</div><div class='big'>{fmt(rect_gross)} m2</div><div class='small'>Full box, before setbacks and voids</div></div>
<div class='card'><div class='label'>Effective programmable gross</div><div class='big'>{fmt(sum_eff)} m2</div><div class='small'>{sum_eff/rect_gross*100:.1f}% of rectangular envelope</div></div>
<div class='card'><div class='label'>Planning net area</div><div class='big'>{fmt(sum_net)} m2</div><div class='small'>Shipwide net/gross {shipwide_ng:.2f}</div></div>
<div class='card'><div class='label'>80k design estimated mass</div><div class='big'>{fmt(W_design80)} t</div><div class='small'>Includes 22% growth/estimating margin</div></div>
<div class='card'><div class='label'>Net area per person</div><div class='big'>{sum_net/80000:.1f} m2/person</div><div class='small'>At 80,000 steady population; {sum_net/100000:.1f} m2/person at 100,000 surge</div></div>
</div><div class='callout risk'><strong>Key conclusion:</strong> this concept is not area-limited; it is weight, CG, safety, utilities, and regulatory-basis limited. Structural density sensitivity is enormous: +/-0.20 t/m2 over the effective gross envelope moves mass by about {fmt(sum_eff*0.20)} tonnes before knock-on ballast and margin.</div></section>
<section><h2>2. Modeling rules and equations</h2><ul><li><code>A_footprint = L x B</code></li><li><code>A_effective,deck = A_footprint x deck_factor</code></li><li><code>A_net,deck = A_effective,deck x net_gross_factor</code></li><li><code>W_deck = A_effective x w_structure + A_net x (w_outfit + w_payload)</code></li><li><code>Delta = rho x L x B x T x Cb</code>, with seawater density 1.025 t/m3.</li><li><code>KG_total = sum(W_i x KG_i) / sum(W_i)</code>. This report includes deck-level KG bands for the next-stage moment model.</li></ul><p>All densities are central planning values. Use the CSVs to run low/base/high sweeps before committing to any hydrostatic or structural basis.</p></section>
<section><h2>3. Deck-by-deck area and mass model</h2><div class='scroll'><table><thead><tr><th>Deck</th><th>Primary program</th><th>Eff. factor</th><th>Eff. gross m2</th><th>Net m2</th><th>N/G</th><th>Structure t</th><th>Outfit t</th><th>Payload t</th><th>KG m</th></tr></thead><tbody>{deck_html}</tbody></table></div></section>
<section><h2>4. Weight summary - 80,000-person steady design case</h2><table><thead><tr><th>Category</th><th>Weight t</th><th>Share</th><th>Basis</th></tr></thead><tbody>{cat_html}</tbody></table><div class='callout warn'><strong>Interpretation:</strong> the 80k central design estimate is {fmt(W_design80)} t. This is a screening weight, not an endorsed displacement. At this maturity, a +/-25-40% swing is credible until primary structure, draft, hull depth, utility concept, vehicle policy, parks/soil, and autonomy are fixed.</div></section>
<section><h2>5. Population-driven utility and civic scenarios</h2><p>Central assumptions: 5 kW/person average all-in electrical load, peak factor 1.8, installed reserve 1.25; 220 L/person/day water, 3-day water reserve; 2.2 kg/person/day food, 30-day food reserve; diesel-equivalent 14-day fuel reserve at 5 MWh/t; hospital 3 beds/1,000 persons at 150 m2/bed; students 18% of population at 12 m2/student; refuge 2.0 m2/person.</p><table><thead><tr><th>Population</th><th>Avg MW</th><th>Installed MW</th><th>Water m3/d</th><th>Water store t</th><th>Food reserve t</th><th>Fuel reserve t</th><th>Hospital m2</th><th>School m2</th><th>Refuge m2</th></tr></thead><tbody>{scen_html}</tbody></table></section>
<section><h2>6. Hydrostatic capacity sweep against central 80k model</h2><p>This sweep uses a simple rectangular/block displacement approximation. It is only a capacity screen; true hydrostatics need hull form, compartmentation, freeboard, damage stability, and reserve buoyancy.</p><table><thead><tr><th>Draft T m</th><th>Cb</th><th>Displacement t</th><th>Reserve vs model t</th><th>Reserve %</th></tr></thead><tbody>{hydro_html}</tbody></table></section>
<section><h2>7. Red flags that can break the model</h2><ol><li><strong>Upper-deck mass:</strong> parks, pools, soil, stadiums, and heavy civic spaces high above baseline can consume stability margin even if displacement is available.</li><li><strong>Free surface:</strong> ballast, pools, water features, wastewater tanks, and large liquid stores must be compartmented and included in GM correction.</li><li><strong>Evacuation/refuge:</strong> 100,000-person surge requires district refuge, smoke control, protected stairs, and external evacuation capacity; area alone does not prove safety.</li><li><strong>Utility independence:</strong> power, desalination, wastewater, district cooling, fuel, exhaust, and fire segregation may require more technical volume than area heuristics assume.</li><li><strong>Structural unknown:</strong> global bending/torsion across 1.6 km and modular joint fatigue may drive structure far above simple t/m2 assumptions.</li><li><strong>Vehicle policy:</strong> private cars are a design fork. They add mass, fire risk, ventilation, parking area, ramps, and structural loads.</li><li><strong>Regulatory basis:</strong> class/flag/IMO equivalency can force compartment, refuge, egress, lifesaving, and machinery redundancy penalties not captured here.</li></ol></section>
<section><h2>8. Next calculation passes</h2><ol><li>Turn deck rows into a real longitudinal/transverse compartment matrix: 16 x 6 modules x 25 decks.</li><li>Add low/base/high density bands and Monte Carlo/sensitivity output.</li><li>Add KG/LCG/TCG moments per module, not just deck center bands.</li><li>Close hydrostatic loop: select draft/hull depth/freeboard, displacement, GM, ballast, damage cases.</li><li>Split technical systems: power, HVAC, desalination, wastewater, firewater, fuel, emergency systems, transport.</li><li>Build evacuation/refuge occupancy model by district and vertical core.</li></ol></section>
<section><h2>9. Produced files</h2><ul><li><code>deck_area_weight_model.csv</code> - deck factors, areas, net/gross, mass by deck, KG band.</li><li><code>population_utility_scenarios.csv</code> - 60k/80k/100k utility and civic sizing.</li><li><code>hydrostatic_capacity_sweep.csv</code> - draft/Cb displacement and reserve screen.</li><li><code>model_snapshot.json</code> - core dimensions and central design weights.</li></ul></section>
</main></body></html>"""
(outdir/'freedom-ship-weight-area-model-2026-06-03.html').write_text(html)
for p in sorted(outdir.iterdir()): print(f"{p.name}\t{p.stat().st_size} bytes")
print('SUMMARY')
print(json.dumps({'footprint_m2':round(footprint,1),'effective_gross_m2':round(sum_eff,1),'net_area_m2':round(sum_net,1),'shipwide_ng':round(shipwide_ng,3),'design80_total_t':round(W_design80,1),'html':str(outdir/'freedom-ship-weight-area-model-2026-06-03.html')}, indent=2))
