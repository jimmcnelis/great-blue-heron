#!/usr/bin/env python3
"""Band pass, phase 3: exchange-rate-ordered climb from the v2.3 base.

Phase 2's probes repriced every lever. The main descent spent the
IoU budget on the keel first and met t_bl -- the single biggest band
lever (one +1.2 step: band error -0.0600) -- only after the floors
were already pinned. This climb goes cheapest-first: t_bl, then the
near-free per-point levers in probe-ranked order, group knobs after,
keel in small steps, with a per-move IoU bleed cap so no single
lever can binge the budget again.

Same band acceptance rule and floors as the main search. At the end
the climb winner is reconciled against the main search's winner
(lexicographic: band_err, sec_err, -bird) and winning_params_v24
.json is replaced only if the climb state wins.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import band_core as B

LOGF = open(f'{B.OUT}/climb_log_v24.jsonl', 'a')
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
assert cur_m['ok'] and abs(cur_m['raw'] - 0.7121) < 0.001 and abs(cur_m['bird'] - 0.7656) < 0.001
accepted_keys = []

def accept_band(m):
    return (m['ok'] and m['floors_ok'] and m['band_err'] < cur_m['band_err'] - 0.0015
            and m['raw'] >= cur_m['raw'] - 0.012 and m['bird'] >= cur_m['bird'] - 0.014)

def accept_sec(m):
    return (m['ok'] and m['floors_ok'] and m['band_err'] <= cur_m['band_err'] + 0.0005
            and m['sec_err'] < cur_m['sec_err'] - 0.004
            and m['bird'] >= cur_m['bird'] - 0.002 and m['raw'] >= cur_m['raw'] - 0.002)

def cd(key, step, tag, mode='band', max_rep=6):
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
    with open(f'{B.OUT}/climb_state_v24.json', 'w') as f:
        json.dump(dict(state=cur, metrics={k: cur_m[k] for k in
                       ('raw', 'bird', 'bands', 'band_err', 'centroid', 'torso_w', 'sec_err')},
                       accepted=accepted_keys), f, indent=1)

# ---- stage 1: t_bl, the big lever, while the budget is fresh
cd('t_bl', 1.2, 'c1')
cd('t_bl', 0.6, 'c1r')
stage('climb1-bottom-line')

# ---- stage 2: near-free per-point levers, probe-ranked
for key in ('tp9y', 'tp11y', 'tp5x', 'tp3y', 'tp10y', 'tp6x', 'tp8y', 'tp7y', 'tp1y'):
    cd(key, 0.6, 'c2')
stage('climb2-cheap-points')

# ---- stage 3: remaining torso points y + the x set
for idx in (0, 2, 4, 6, 12):
    cd(f'tp{idx}y', 0.6, 'c3')
for idx in (0, 1, 5, 6, 9, 12):
    cd(f'tp{idx}x', 0.6, 'c3')
stage('climb3-points-rest')

# ---- stage 4: group knobs + keel in small steps
for key, step in (('t_brdx', 1.2), ('t_keel', 0.6), ('t_bk', 1.2), ('t_taildy', 1.2),
                  ('t_crown', 1.2), ('w_top', 1.0), ('w_bot', 1.0)):
    cd(key, step, 'c4')
stage('climb4-groups')

# ---- stage 5: re-polish everything accepted, fine steps
for key in list(accepted_keys):
    cd(key, 0.3, 'c5')
cd('t_bl', 0.3, 'c5')
stage('climb5-polish')

# ---- stage 6: secondary polish under the band guard
sec_keys = list(accepted_keys) + [k for k in ('t_taildx', 't_brdx', 'tp0x', 'tp12x')
                                  if k not in accepted_keys]
for key in sec_keys:
    cd(key, 0.3, 'c6', mode='sec')
stage('climb6-secondary')

evaluate(cur, 'climb-final')

# ---- reconcile against the main search winner
sw = json.load(open(f'{B.OUT}/winning_params_v24.json'))
sm = sw['metrics']
inc_key = (cur_m['band_err'], cur_m['sec_err'], -cur_m['bird'])
search_key = (sm['band_err'], sm['sec_err'], -sm['bird'])
verdict = dict(climb=dict(raw=cur_m['raw'], bird=cur_m['bird'], band_err=cur_m['band_err'],
                          bands=cur_m['bands'], centroid=cur_m['centroid'],
                          torso_w=cur_m['torso_w'], sec_err=cur_m['sec_err']),
               search=dict(raw=sm['raw'], bird=sm['bird'], band_err=sm['band_err'],
                           bands=sm['bands'], centroid=sm['centroid'],
                           torso_w=sm['torso_w'], sec_err=sm['sec_err']),
               climb_n_evals=len(log))
if inc_key < search_key:
    with open(f'{B.OUT}/winning_params_v24_search.json', 'w') as f:
        json.dump(sw, f, indent=1)
    with open(f'{B.OUT}/winning_params_v24.json', 'w') as f:
        json.dump(dict(state=cur, delta=B.nonzero_state(cur),
                       metrics={k: cur_m[k] for k in
                                ('raw', 'bird', 'bands', 'band_err', 'mid_err', 'centroid',
                                 'fwd_err', 'vert_err', 'torso_w', 'torso_d', 'len_err', 'sec_err')},
                       accepted=accepted_keys, n_evals=len(log), source='climb'), f, indent=1)
    verdict['winner'] = 'climb'
    print('RECONCILED: climb state WINS and replaces winning_params_v24.json', flush=True)
else:
    verdict['winner'] = 'search'
    print('RECONCILED: main search winner stands', flush=True)
with open(f'{B.OUT}/climb_results_v24.json', 'w') as f:
    json.dump(verdict, f, indent=1)
print('CLIMB FINAL', json.dumps(verdict['climb']), flush=True)
print('DELTA', json.dumps(B.nonzero_state(cur)), flush=True)
