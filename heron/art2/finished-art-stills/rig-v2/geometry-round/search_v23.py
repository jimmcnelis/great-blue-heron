#!/usr/bin/env python3
"""Bird-completion geometry round: staged coordinate descent on rig
v2.3 GEOMETRY (torso hull outline + internal distribution, wing
outline, plume fan shape/placement, head outline bulk, leg fine-tune),
scored by the certified protocol. BOTH scores logged per eval: raw
mask IoU and bird-only IoU (scenery band excluded). Jimmy steers by
bird-only; acceptance = bird improves > 0.0004 and raw stays within
0.0015 of the incumbent (absolute floor raw >= 0.6100).

Frozen, asserted per eval: neck channel pixel-identical to v2.2,
breast + head anchor unmoved, leg IK reachable, no frame clipping.
Part sizes untouched (no HEAD_S / BILL_LEN / xform-scale changes);
the neck is never a parameter.
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

# reference invariants from the baked v2.2 build
pose22 = json.load(open(f'{G.BP}/pose_tracks_v22.json'))['idle'][0]
_, stack22_ref, kpm22_ref = G.sil_stack(RR22, copy.deepcopy(pose22))
REF_NECK = stack22_ref[1]
REF_BREAST = np.array(kpm22_ref['spine'][0], float)
REF_ANCHOR = np.array(kpm22_ref['head_c'], float)

LOGF = open(f'{G.OUT}/search_log_v23.jsonl', 'a')
log = []

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
    log.append(e); LOGF.write(json.dumps(e) + '\n'); LOGF.flush()
    print(f"{tag:26s} raw={raw:.4f} bird={bird:.4f} ok={ok}", flush=True)
    return (raw, bird) if ok else (-1.0, -1.0)

BASE_STATE = dict(theta=-6.75, pdx=6.0, pdy=-17.0, pl_len=1.0, pl_wid=1.0, pl_bot=0.0,
                  fxn=5.5, fxf=-7.5, hnx=0.0, hfx=0.0,
                  t_bk=0.0, t_crown=0.0, t_bl=0.0, t_keel=0.0, t_brdx=0.0,
                  t_taildx=0.0, t_taildy=0.0, w_bot=0.0, w_top=0.0, w_fwd=0.0,
                  h_nape=0.0, h_crown=0.0, h_cheek=0.0, h_napedy=0.0)
RESUMING = '--resume' in sys.argv
cur = dict(BASE_STATE)
accepted_keys = []
if RESUMING:
    saved = json.load(open(f'{G.OUT}/search_state_v23.json'))
    cur.update(saved['state']); cur_raw, cur_bird = saved['raw'], saved['bird']
    accepted_keys = list(saved['accepted'])
    print(f'RESUMED at raw={cur_raw:.4f} bird={cur_bird:.4f}', flush=True)
else:
    cur_raw, cur_bird = evaluate(cur, 'base-v22-geometry')
    assert abs(cur_raw - 0.6141) < 0.001 and abs(cur_bird - 0.6567) < 0.001, 'search base must reproduce v2.2'

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

# ---- stage 1: torso group knobs (skipped on resume; state restored)
if not RESUMING:
    for key, step in (('t_bk', 1.2), ('t_crown', 1.2), ('t_bl', 1.2), ('t_keel', 1.2),
                      ('t_brdx', 1.2), ('t_taildx', 1.5), ('t_taildy', 1.2)):
        cd(key, step, 's1')
    for key in list(accepted_keys):
        if key.startswith('t_'):
            cd(key, 0.6, 's1r')
    stage('stage1-torso-groups')

# ---- stage 2: torso per-point
for idx in (1, 2, 3, 4, 5, 6, 8, 9, 10, 11):
    cd(f'tp{idx}y', 0.6, 's2')
for idx in (0, 1, 4, 5, 6, 9, 12):
    cd(f'tp{idx}x', 0.6, 's2')
for key in list(accepted_keys):
    if key.startswith('tp'):
        cd(key, 0.3, 's2r')
stage('stage2-torso-points')

# ---- stage 3: wing
for key, step in (('w_bot', 1.0), ('w_top', 1.0), ('w_fwd', 1.0)):
    cd(key, step, 's3')
for idx in (5, 6, 7):
    cd(f'wp{idx}y', 0.6, 's3')
stage('stage3-wing')

# ---- stage 4: plume -- coarse translate grid, then shape
best_grid = None
for gx in (6.0, 0.0, -6.0, -12.0):
    for gy in (-17.0, -6.0, 4.0, 14.0):
        if gx == cur['pdx'] and gy == cur['pdy']:
            continue
        p = dict(cur, pdx=gx, pdy=gy)
        v_raw, v_bird = evaluate(p, 's4-grid')
        if accept(v_raw, v_bird):
            cur, cur_raw, cur_bird = p, v_raw, v_bird
            best_grid = (gx, gy)
print(f'  plume grid -> pdx={cur["pdx"]} pdy={cur["pdy"]} raw={cur_raw:.4f} bird={cur_bird:.4f}', flush=True)
for key, step in (('pl_len', 0.2), ('pl_wid', 0.15), ('pl_bot', 4.0)):
    cd(key, step, 's4')
cd('pdx', 3.0, 's4r'); cd('pdy', 3.0, 's4r')
cd('pdx', 1.5, 's4r2'); cd('pdy', 1.5, 's4r2')
for idx in (3, 4, 5, 6):
    cd(f'pp{idx}y', 2.0, 's4p')
stage('stage4-plume')

# ---- stage 5: head bulk
for key, step in (('h_nape', 0.6), ('h_crown', 0.45), ('h_cheek', 0.45), ('h_napedy', 0.6)):
    cd(key, step, 's5')
for idx in (0, 1, 2, 6, 7, 8):
    cd(f'hp{idx}x' if idx in (0, 8) else f'hp{idx}y', 0.3, 's5p')
stage('stage5-head')

# ---- stage 6: legs
for key, step in (('fxn', 1.0), ('fxf', 1.0), ('hnx', 0.75), ('hfx', 0.75)):
    cd(key, step, 's6')
for key in ('fxn', 'fxf', 'hnx', 'hfx'):
    cd(key, 0.5, 's6r')
stage('stage6-legs')

# ---- stage 7: joint polish (theta + every accepted key at small step)
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
