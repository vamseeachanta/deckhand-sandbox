import yaml, json
doc = yaml.safe_load(open('/tmp/pt-results/input.yml').read())
def find(d, key):
    if isinstance(d, dict):
        if key in d: return d[key]
        for v in d.values():
            r = find(v, key)
            if r is not None: return r
    elif isinstance(d, list):
        for v in d:
            r = find(v, key)
            if r is not None: return r
    return None
sc = find(doc, 'surface_card')
# surface_card may itself nest a 'surface_card' (position/load live under it)
pos = sc.get('position') if isinstance(sc, dict) else None
load = sc.get('load') if isinstance(sc, dict) else None
if pos is None:
    inner = find(sc, 'position'); pos = inner
    load = find(sc, 'load')
out = {
  'mode': 'PUMP_TAGGING', 'seed': 711, 'api14': find(doc, 'api14'),
  'position': pos, 'load': load, 'n_points': len(pos) if pos else 0,
  'fillage': find(doc, 'pump_fillage'),
  'buckling_detected': find(doc, 'buckling_detected'),
  'diagnostic_message': find(doc, 'diagnostic_message'),
}
json.dump(out, open('/tmp/pt-card.json', 'w'), indent=2)
print('PT card:', out['n_points'], 'pts · fillage', out['fillage'])
print('diagnosis:', (out['diagnostic_message'] or '')[:100])
