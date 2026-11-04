#!/usr/bin/env python3
"""Geometry round RESUMPTION (parent crew): finish stages 5p/6/7 from
the prior crew's saved incumbent (search_state_v23.json, raw 0.70952 /
bird 0.76261 at stage4-plume of the resumed pass).

Machinery (apply / evaluate / accept / cd) is copied verbatim from
search_v23.py: same certified protocol, same invariant asserts per
eval (neck channel pixel-identical to v2.2, breast+anchor unmoved,
leg IK reachable, no clipping), same acceptance rule (bird improves
> 0.0004, raw within 0.0015 of incumbent, raw floor 0.6100).

Already closed at this state by the prior crew's resumed pass and NOT
re-tried: stage5 group knobs h_nape/h_crown/h_cheek (both directions
rejected) and h_napedy +0.6 (rejected). Remaining: h_napedy -0.6,
stage5 per-point, stage6 legs, stage7 joint polish.
"""
import copy, json, os, sys, time
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import geo_common as G
import roster_render_v22 as RR22
import roster_render_v23 as RR23
import rig13_r4_v23 as R23

W, H = G.W, G.H
BASE_TORSO = [tuple(p) for p in R23.TORSO]
BASE_WING = [tuple(p) for p in R23.WING]
BASE_SKULL = [tuple(p) for p in RR23.SKULL_PROFILE]
BASE_OFFS = [tuple(p) for p in RR23.PLUME_OFFS_BASE]
BASE_HIP_N = tuple(R23.HIP_NEAR); BASE_HIP_F = tuple(R23.HIP_FAR)
BASE_POSE = json.load(open(f'{G.OUT}/pose_tracks_v23.json'))['idle'][0]

pose22 = json.load(open(f'{G.BP}/pose_tracks_v22.json'))['idle'][0]
_, stack22_ref, kpm22_ref = G.sil_stack(RR22, copy.deepcopy(pose22))
REF_NECK = stack22_ref[1]
REF_BREAST = np.array(kpm22_ref['spine'][0], float)
REF_ANCHOR = np.array(kpm22_ref['head_c'], float)

LOGF = open(f'{G.OUT}/finish_log_v23.jsonl', 'a')

def apply(st):
    td = {}
    def add(d, idx, dx, dy):
        e = d.setdefault(idx, [0.0, 0.0]); e[0] += dx; e[1] += dy
    for i in (1, 2, 3, 4): add(td, i, 0.0, st['t_bk'])
    for i in (2, 3): add(td, i, 0.0, st['t_crown'])
    for i in (8, 9, 10, 11): add(td, i, 0.0, st['t_bl'])
    for i in (7, 8): add(td, i, 0.0, st['t_keel'])
    for i in (5, 6): add(td, i, st['t_brdx'], 0.0)
    for i in (0, 12): add(td, i, st['t_taildx'], st['t_taildy'])
    wd = {}
    for i in (5, 6, 7, 8): add(wd, i, 0.0, st['w_bot'])
    for i in (1, 2, 3): add(wd, i, 0.0, st['w_top'])
    for i in (4, 5): add(wd, i, 0.0, st['w_fwd'])
    hd = {}
    for i in (0, 8): add(hd, i, st['h_nape'], st['h_napedy'])
    for i in (1, 2): add(hd, i, 0.0, st['h_crown'])
    for i in (6, 7): add(hd, i, 0.0, st['h_cheek'])
    for k, v in st.items():
        if k.startswith('tp'):
            idx = int(k[2:-1]); d = td.setdefault(idx, [0.0, 0.0])
            d[0 if k[-1] == 'x' else 1] += v
        elif k.startswith('wp'):
            idx = int(k[2:-1]); d = wd.setdefault(idx, [0.0, 0.0])
            d[0 if k[-1] == 'x' else 1] += v
        elif k.startswith('hp'):
            idx = int(k[2:-1]); d = hd.setdefault(idx, [0.0, 0.0])
            d[0 if k[-1] == 'x' else 1] += v
    R23.TORSO[:] = [(x + td.get(i, [0, 0])[0], y + td.get(i, [0, 0])[1])
                    for i, (x, y) in enumerate(BASE_TORSO)]
    R23.WING[:] = [(x + wd.get(i, [0, 0])[0], y + wd.get(i, [0, 0])[1])
                   for i, (x, y) in enumerate(BASE_WING)]
    RR23.SKULL_PROFILE[:] = [(x + hd.get(i, [0, 0])[0], y + hd.get(i, [0, 0])[1])
                             for i, (x, y) in enumerate(BASE_SKULL)]
    offs = []
    for (x, y) in BASE_OFFS:
        ny = y * st['pl_len'] + (st['pl_bot'] if y > 5 else 0.0)
        offs.append((x * st['pl_wid'], ny))
    for k, v in st.items():
        if k.startswith('pp'):
            idx = int(k[2:-1]); ox, oy = offs[idx]; offs[idx] = (ox, oy + v)
    RR23.PLUME_OFFS_BASE[:] = offs
    RR23.PLUME_DX, RR23.PLUME_DY = st['pdx'], st['pdy']
    R23.HIP_NEAR = (BASE_HIP_N[0] + st['hnx'], BASE_HIP_N[1])
    R23.HIP_FAR = (BASE_HIP_F[0] + st['hfx'], BASE_HIP_F[1])
    pose = copy.deepcopy(BASE_POSE)
    pose['body_rot_b'] = st['theta']
    pose['leg_near'] = dict(pose['leg_near'], fx=st['fxn'])
    pose['leg_far'] = dict(pose['leg_far'], fx=st['fxf'])
    return pose

def evaluate(st, tag):
    pose = apply(st)
    sil, stack, kpm = G.sil_stack(RR23, pose)
    neck_ok = bool(np.array_equal(stack[1], REF_NECK))
    breast = np.array(kpm['spine'][0], float); anchor = np.array(kpm['head_c'], float)
    endp_ok = bool(np.allclose(breast, REF_BREAST, atol=0.6) and np.allclose(anchor, REF_ANCHOR, atol=0.6))
    ik_ok = True
    for nm in ('n', 'f'):
        hip = np.array(kpm[f'hip_{nm}'], float); foot = np.array(kpm[f'foot_{nm}'], float)
        knee = np.array(kpm[f'knee_{nm}'], float)
        d = np.hypot(*(hip - foot)) / RR23.U
        if not (np.all(np.isfinite(knee)) and d < 39.6 * 0.995 and d > 2.0):
            ik_ok = False
    ys, xs = np.nonzero(sil)
    clip = bool(xs.min() <= 0 or xs.max() >= W - 1 or ys.min() <= 0 or ys.max() >= H - 1)
    ok = neck_ok and endp_ok and ik_ok and not clip
    raw, prm, bird, _ = G.score(sil)
    e = dict(tag=tag, state={k: round(v, 4) if isinstance(v, float) else v for k, v in st.items()},
             raw=round(raw, 4), bird=round(bird, 4), prm=prm,
             neck_ok=neck_ok, endp_ok=endp_ok, ik_ok=ik_ok, clip=clip, ok=ok)
    LOGF.write(json.dumps(e) + '\n'); LOGF.flush()
    print(f"{tag:26s} raw={raw:.4f} bird={bird:.4f} ok={ok}", flush=True)
    return (raw, bird) if ok else (-1.0, -1.0)

saved = json.load(open(f'{G.OUT}/search_state_v23.json'))
cur = dict(saved['state']); cur_raw, cur_bird = saved['raw'], saved['bird']
accepted_keys = list(saved['accepted'])
print(f'PICKUP incumbent: raw={cur_raw:.4f} bird={cur_bird:.4f}', flush=True)
v_raw, v_bird = evaluate(cur, 'pickup-check')
assert abs(v_raw - cur_raw) < 0.0011 and abs(v_bird - cur_bird) < 0.0011, \
    f'PICKUP MISMATCH: evaluated {v_raw:.4f}/{v_bird:.4f} vs saved {cur_raw:.4f}/{cur_bird:.4f}'
print('PICKUP VERIFIED: saved state reproduces', flush=True)

def accept(v_raw, v_bird):
    return v_bird > cur_bird + 0.0004 and v_raw >= cur_raw - 0.0015 and v_raw >= 0.6100

def cd(key, step, tag, max_rep=4):
    global cur, cur_raw, cur_bird
    for sgn in (1, -1):
        rep = 0
        while rep < max_rep:
            p = dict(cur); p[key] = cur.get(key, 0.0) + sgn * step
            v_raw, v_bird = evaluate(p, f'{tag}-{key}')
            if accept(v_raw, v_bird):
                cur, cur_raw, cur_bird = p, v_raw, v_bird
                if key not in accepted_keys: accepted_keys.append(key)
                rep += 1
            else:
                break
    print(f'  after {tag}-{key}: raw={cur_raw:.4f} bird={cur_bird:.4f} {key}={cur.get(key, 0.0)}', flush=True)

def stage(name):
    print(f'== {name}: raw={cur_raw:.4f} bird={cur_bird:.4f}', flush=True)
    with open(f'{G.OUT}/search_state_v23.json', 'w') as f:
        json.dump(dict(state=cur, raw=cur_raw, bird=cur_bird, accepted=accepted_keys), f, indent=1)

# ---- stage 5 closure: h_napedy negative (the + direction was rejected
# by the prior crew at this state), then per-point skull moves
p = dict(cur); p['h_napedy'] = cur.get('h_napedy', 0.0) - 0.6
v_raw, v_bird = evaluate(p, 's5-h_napedy-neg')
if accept(v_raw, v_bird):
    cur, cur_raw, cur_bird = p, v_raw, v_bird
    if 'h_napedy' not in accepted_keys: accepted_keys.append('h_napedy')
print(f'  after s5-h_napedy-neg: raw={cur_raw:.4f} bird={cur_bird:.4f} h_napedy={cur.get("h_napedy", 0.0)}', flush=True)
for key in ('hp0x', 'hp1y', 'hp2y', 'hp6y', 'hp7y', 'hp8x'):
    cd(key, 0.3, 's5p')
stage('stage5-head-complete')

# ---- stage 6: legs
for key, step in (('fxn', 1.0), ('fxf', 1.0), ('hnx', 0.75), ('hfx', 0.75)):
    cd(key, step, 's6')
for key in ('fxn', 'fxf', 'hnx', 'hfx'):
    cd(key, 0.5, 's6r')
stage('stage6-legs')

# ---- stage 7: joint polish
cd('theta', 0.75, 's7')
for key in list(accepted_keys):
    cd(key, 0.3, 's7')
cd('theta', 0.375, 's7')
stage('stage7-polish')

evaluate(cur, 'final')
with open(f'{G.OUT}/winning_params_v23.json', 'w') as f:
    json.dump(dict(state=cur, raw=cur_raw, bird=cur_bird, accepted=accepted_keys), f, indent=1)
print('FINAL', json.dumps(dict(raw=cur_raw, bird=cur_bird)), flush=True)
print('STATE', json.dumps(cur), flush=True)
