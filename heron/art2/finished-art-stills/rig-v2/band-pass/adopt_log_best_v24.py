#!/usr/bin/env python3
"""Adopt the pooled-log best candidate as the pass winner.

Scans search + probe + climb logs for the lexicographic best
(band_err, sec_err, -bird) among invariant-ok AND floors_ok evals
(floors_ok is computed on unrounded values in band_core). If that
candidate beats the current winning_params_v24.json, it is rebuilt,
re-evaluated, and -- only if the recheck reproduces the dominance --
written in as the winner (the previous winner is preserved).
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import band_core as B

best = None
for fn in ('search_log_v24.jsonl', 'probe_log_v24.jsonl', 'climb_log_v24.jsonl'):
    for l in open(f'{B.OUT}/{fn}'):
        if not l.strip():
            continue
        e = json.loads(l)
        if e['ok'] and e['floors_ok']:
            k = (e['band_err'], e['sec_err'], -e['bird'])
            if best is None or k < best[0]:
                best = (k, fn, e)
k, fn, e = best
print(f'log-best: {fn} tag={e["tag"]} key={k}')
print(f"  raw={e['raw']:.4f} bird={e['bird']:.4f} bands={e['bands']} delta={json.dumps(e['delta'])}")

win = json.load(open(f'{B.OUT}/winning_params_v24.json'))
wm = win['metrics']
cur_key = (wm['band_err'], wm['sec_err'], -wm['bird'])
print(f'current winner key: {cur_key}')
if k >= cur_key:
    print('current winner stands -- nothing to adopt')
    sys.exit(0)

cand = dict(B.INIT_STATE); cand.update(e['delta'])
raw, bird, m, _, _ = B.evaluate(cand)
rk = (m['band_err'], m['sec_err'], -m['bird'])
print(f'recheck: raw={raw:.4f} bird={bird:.4f} band_err={m["band_err"]:.4f} key={rk}')
assert m['ok'] and m['floors_ok'], 'recheck candidate fails invariants/floors'
assert rk < cur_key, 'recheck does not reproduce the dominance -- winner stands'
with open(f'{B.OUT}/winning_params_v24_prev.json', 'w') as f:
    json.dump(win, f, indent=1)
with open(f'{B.OUT}/winning_params_v24.json', 'w') as f:
    json.dump(dict(state=cand, delta=B.nonzero_state(cand),
                   metrics={kk: m[kk] for kk in
                            ('raw', 'bird', 'bands', 'band_err', 'mid_err', 'centroid',
                             'fwd_err', 'vert_err', 'torso_w', 'torso_d', 'len_err', 'sec_err')},
                   accepted=win.get('accepted', []), source=f'log-best:{fn}:{e["tag"]}'), f, indent=1)
print('ADOPTED: log-best candidate is now winning_params_v24.json (prev preserved)')
