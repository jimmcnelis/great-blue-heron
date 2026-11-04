#!/usr/bin/env python3
"""Band-constrained geometry pass: staged coordinate descent on rig
v2.3 TORSO + WING geometry under a BAND-CONSTRAINED acceptance rule.

A candidate is accepted in the main descent only if it improves the
band profile (total L1 band error vs the approved bird down by more
than 0.0015) SUBJECT TO FLOORS defending the v2.3 geometry-round
gains: raw IoU >= 0.69, bird-only IoU >= 0.74. A final polish phase
spends leftover freedom on the secondary aims (core centroid back
toward approved, torso length back toward ~0.80 H) under a band
guard (band error may not grow by more than 0.0005).

Every evaluation is invariant-checked (neck channel pixel-identical
to v2.2, breast + head anchor unmoved, leg IK reachable, no clipping)
and logged with its full delta state + all three surfaces (raw,
bird-only, band profile) -- the log IS the trade-curve data.

Frozen: neck, head, plume, hips, legs, theta (pose). Search
vocabulary: torso group knobs, torso per-point x/y, wing knobs.
"""
import json, os, sys, time
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import band_core as B

LOGF = open(f'{B.OUT}/search_log_v24.jsonl', 'a')
log = []

def evaluate(st, tag):
    raw, bird, m, _, _ = B.evaluate(st)
    e = dict(tag=tag, delta=B.nonzero_state(st), **{k: m[k] for k in
             ('raw', 'bird', 'bands', 'band_err', 'mid_err', 'centroid', 'fwd_err',
              'vert_err', 'torso_w', 'torso_d', 'len_err', 'sec_err',
              'neck_ok', 'endp_ok', 'ik_ok', 'clip', 'ok', 'floors_ok')})
    log.append(e); LOGF.write(json.dumps(e) + '\n'); LOGF.flush()
    print(f"{tag:24s} raw={raw:.4f} bird={bird:.4f} band_err={m['band_err']:.4f} "
          f"mid={m['bands']['band1']:.4f} fwd={m['fwd_err']:+.4f} len={m['torso_w']:.3f} ok={m['ok']}",
          flush=True)
    return m

cur = dict(B.INIT_STATE)
cur_m = evaluate(cur, 'base-v23-baked')
assert cur_m['ok'] and abs(cur_m['raw'] - 0.7121) < 0.001 and abs(cur_m['bird'] - 0.7656) < 0.001, \
    'search base must reproduce baked v2.3'
print(f"BASE band_err={cur_m['band_err']:.4f} bands={cur_m['bands']} "
      f"centroid={cur_m['centroid']} torso_w={cur_m['torso_w']}", flush=True)

accepted_keys = []

def accept_band(m):
    return m['ok'] and m['floors_ok'] and m['band_err'] < cur_m['band_err'] - 0.0015

def accept_sec(m):
    return (m['ok'] and m['floors_ok'] and m['band_err'] <= cur_m['band_err'] + 0.0005
            and m['sec_err'] < cur_m['sec_err'] - 0.004
            and m['bird'] >= cur_m['bird'] - 0.002 and m['raw'] >= cur_m['raw'] - 0.002)

def cd(key, step, tag, mode='band', max_rep=4):
    global cur, cur_m
    accept = accept_band if mode == 'band' else accept_sec
    for sgn in (1, -1):
        rep = 0
        while rep < max_rep:
            p = dict(cur); p[key] = cur.get(key, 0.0) + sgn * step
            m = evaluate(p, f'{tag}-{key}')
            if accept(m):
                cur, cur_m = p, m
                if key not in accepted_keys: accepted_keys.append(key)
                rep += 1
            else:
                break
    print(f"  after {tag}-{key}: raw={cur_m['raw']:.4f} bird={cur_m['bird']:.4f} "
          f"band_err={cur_m['band_err']:.4f} {key}={cur.get(key, 0.0)}", flush=True)

def stage(name):
    print(f"== {name}: raw={cur_m['raw']:.4f} bird={cur_m['bird']:.4f} "
          f"band_err={cur_m['band_err']:.4f} mid={cur_m['bands']['band1']:.4f}", flush=True)
    with open(f'{B.OUT}/search_state_v24.json', 'w') as f:
        json.dump(dict(state=cur, metrics={k: cur_m[k] for k in
                       ('raw', 'bird', 'bands', 'band_err', 'centroid', 'torso_w', 'sec_err')},
                       accepted=accepted_keys), f, indent=1)

# ---- stage 1: torso group knobs, coarse then fine
for key, step in (('t_keel', 1.2), ('t_bl', 1.2), ('t_crown', 1.2), ('t_bk', 1.2),
                  ('t_taildx', 1.5), ('t_brdx', 1.2), ('t_taildy', 1.2)):
    cd(key, step, 's1')
for key in list(accepted_keys):
    if key.startswith('t_'):
        cd(key, 0.6, 's1r')
stage('stage1-groups')

# ---- stage 2: torso per-point y
for idx in range(13):
    cd(f'tp{idx}y', 0.6, 's2')
for key in list(accepted_keys):
    if key.startswith('tp') and key.endswith('y'):
        cd(key, 0.3, 's2r')
stage('stage2-points-y')

# ---- stage 3: torso per-point x (length + centroid levers)
for idx in (0, 1, 4, 5, 6, 9, 12):
    cd(f'tp{idx}x', 0.6, 's3')
for key in list(accepted_keys):
    if key.startswith('tp') and key.endswith('x'):
        cd(key, 0.3, 's3r')
stage('stage3-points-x')

# ---- stage 4: wing (inside the torso-core union)
for key, step in (('w_top', 1.0), ('w_bot', 1.0), ('w_fwd', 1.0)):
    cd(key, step, 's4')
for idx in (5, 6, 7):
    cd(f'wp{idx}y', 0.6, 's4')
for key in list(accepted_keys):
    if key.startswith('w'):
        cd(key, 0.3, 's4r')
stage('stage4-wing')

# ---- stage 5: joint re-polish under the band rule
for key in list(accepted_keys):
    cd(key, 0.3, 's5')
stage('stage5-band-polish')

# ---- stage 6: secondary polish (centroid + length) under the band guard
sec_keys = [k for k in accepted_keys] + [k for k in
            ('t_taildx', 't_brdx', 't_bk', 't_crown', 't_bl', 't_keel') if k not in accepted_keys]
for key in sec_keys:
    cd(key, 0.3, 's6', mode='sec')
stage('stage6-secondary-polish')

evaluate(cur, 'final-incumbent')

# ---- winner selection: incumbent vs best logged candidate on the
# lexicographic (band_err, sec_err, -bird) among ok + floors-ok evals
best = None
for e in log:
    if e['ok'] and e['floors_ok']:
        key = (e['band_err'], e['sec_err'], -e['bird'])
        if best is None or key < best[0]:
            best = (key, e)
inc_key = (cur_m['band_err'], cur_m['sec_err'], -cur_m['bird'])
win_state, win_m = cur, cur_m
if best is not None and best[0] < inc_key:
    cand = dict(B.INIT_STATE); cand.update(best[1]['delta'])
    m2 = evaluate(cand, 'log-best-recheck')
    if m2['ok'] and m2['floors_ok'] and (m2['band_err'], m2['sec_err'], -m2['bird']) < inc_key:
        win_state, win_m = cand, m2
        print('WINNER: a logged non-incumbent candidate dominates the incumbent; adopted after recheck',
              flush=True)

with open(f'{B.OUT}/winning_params_v24.json', 'w') as f:
    json.dump(dict(state=win_state, delta=B.nonzero_state(win_state),
                   metrics={k: win_m[k] for k in
                            ('raw', 'bird', 'bands', 'band_err', 'mid_err', 'centroid',
                             'fwd_err', 'vert_err', 'torso_w', 'torso_d', 'len_err', 'sec_err')},
                   accepted=accepted_keys, n_evals=len(log)), f, indent=1)
print('FINAL', json.dumps(dict(raw=win_m['raw'], bird=win_m['bird'], band_err=win_m['band_err'],
                               bands=win_m['bands'], centroid=win_m['centroid'],
                               torso_w=win_m['torso_w'])), flush=True)
print('DELTA', json.dumps(B.nonzero_state(win_state)), flush=True)
print(f'TOTAL EVALS {len(log)}', flush=True)
