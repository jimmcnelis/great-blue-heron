#!/usr/bin/env python3
"""Band pass: trade-curve analysis over the full search log.

For floor pairs of interest, the best band error any logged
(ok-invariant) candidate achieved -- i.e. what the bands cost in IoU,
measured, not argued. Plus a scatter chart: band error vs raw IoU,
bird-only as color, floors and the winner marked.
"""
import json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
log = []
for fn, src in (('search_log_v24.jsonl', 'search'), ('probe_log_v24.jsonl', 'probe'),
                ('climb_log_v24.jsonl', 'climb')):
    for l in open(f'{HERE}/{fn}'):
        if l.strip():
            e = json.loads(l); e['source'] = src; log.append(e)
ok = [e for e in log if e['ok']]
print(f'{len(log)} evals logged, {len(ok)} invariant-ok')

rows = []
for rf, bf in ((0.7121, 0.7656), (0.705, 0.755), (0.70, 0.75), (0.69, 0.74),
               (0.69, 0.0), (0.0, 0.74), (0.0, 0.0)):
    if (rf, bf) == (0.69, 0.74):
        cand = [e for e in ok if e['floors_ok']]  # exact (unrounded) floor test
    else:
        cand = [e for e in ok if e['raw'] >= rf and e['bird'] >= bf]
    if cand:
        best = min(cand, key=lambda e: (e['band_err'], e['sec_err']))
        rows.append(dict(raw_floor=rf, bird_floor=bf, n=len(cand),
                         best_band_err=best['band_err'], best_mid=best['bands']['band1'],
                         at_raw=best['raw'], at_bird=best['bird'], tag=best['tag']))
    else:
        rows.append(dict(raw_floor=rf, bird_floor=bf, n=0))
for r in rows:
    print(r)
with open(f'{HERE}/trade_curve_v24.json', 'w') as f:
    json.dump(rows, f, indent=1)

# Pareto frontier (band_err down, raw up) for the report table
front, best_raw = [], -1
for e in sorted(ok, key=lambda e: (e['band_err'], -e['raw'])):
    if e['raw'] > best_raw:
        front.append(e); best_raw = e['raw']
print(f'pareto points: {len(front)}')
for e in front:
    print(f"  band_err={e['band_err']:.4f} raw={e['raw']:.4f} bird={e['bird']:.4f} "
          f"mid={e['bands']['band1']:.4f} {e['tag']}")

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    win = json.load(open(f'{HERE}/winning_params_v24.json'))
    wm = win['metrics']
    fig, ax = plt.subplots(figsize=(8, 5.5))
    xs = [e['band_err'] for e in ok]; ys = [e['raw'] for e in ok]; cs = [e['bird'] for e in ok]
    sc = ax.scatter(xs, ys, c=cs, cmap='viridis', s=14, alpha=0.75)
    fig.colorbar(sc, label='bird-only IoU')
    ax.axhline(0.69, color='r', ls='--', lw=1, label='raw floor 0.69')
    ax.axvline(0.1594, color='grey', ls=':', lw=1, label='v2.3 band error')
    ax.plot([wm['band_err']], [wm['raw']], marker='*', ms=18, color='red', label='v2.4 winner')
    ax.plot([0.1594], [0.7121], marker='s', ms=8, color='black', label='v2.3')
    ax.set_xlabel('total band-profile error (L1 vs approved)')
    ax.set_ylabel('raw IoU')
    ax.set_title('Band-constrained pass: the measured trade curve')
    ax.legend(loc='lower left', fontsize=8)
    fig.tight_layout()
    fig.savefig(f'{HERE}/trade_curve_v24.png', dpi=110)
    print('chart written: trade_curve_v24.png')
except FileNotFoundError:
    print('no winner yet -- chart skipped')
except Exception as ex:
    print('chart failed:', ex)
