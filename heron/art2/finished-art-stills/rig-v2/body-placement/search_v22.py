#!/usr/bin/env python3
"""Body-placement search: staged coordinate descent on the hold
pose's placement parameters, scored by the certified mask-surface
protocol (measure_v2.aligned_iou vs the approved rest mask).

Parameters (all placement; part sizes and head/neck frozen):
  theta  body_rot_b, rigid rotation of body-local outputs about the
         transformed breast point (neck endpoints invariant)
  pdx/pdy  plume offset-set translation (design units)
  hnx/hfx  HIP_NEAR / HIP_FAR local-x shifts (leg IK bases)
  fxn/fxf  hold pose leg fx (foot stance)
Start point for legs/plume comes from body_measurements2.json
deltas, not from a blind grid. Every eval asserts the neck
invariants (breast + head anchor unmoved) and leg IK reachability.
"""
import copy, json, os, sys
import numpy as np
from PIL import Image

HOME = os.path.expanduser('~')
ART2 = f'{HOME}/workspace/heron/art2'
FS = f'{ART2}/finished-art-stills'
RIGV2 = f'{FS}/rig-v2'
OUT = f'{RIGV2}/body-placement'
sys.path.insert(0, ART2)
sys.path.insert(0, f'{HOME}/workspace/heron/src13')
sys.path.insert(0, f'{FS}/refinish-corpus/work')
sys.path.insert(0, f'{RIGV2}/work')
import measure_v2 as MV
import roster_charts as RC
import roster_render_v22 as RR22
import rig13_r4_v22 as R22
import maskrender_v2 as M2

W, H = 1024, 600
rest = np.asarray(Image.open(f'{RIGV2}/masks/approved_rest_mask.png')) > 0
BASE_HIP_N = R22.HIP_NEAR
BASE_HIP_F = R22.HIP_FAR
base_pose = copy.deepcopy(RC.CHARTS['idle_hunt']().frames[0])
base_pose['hx'], base_pose['hy'] = 36.17, -26.34

Breast0 = Anchor0 = None
log = []

def build(params):
    R22.HIP_NEAR = (BASE_HIP_N[0] + params['hnx'], BASE_HIP_N[1])
    R22.HIP_FAR = (BASE_HIP_F[0] + params['hfx'], BASE_HIP_F[1])
    RR22.PLUME_DX, RR22.PLUME_DY = params['pdx'], params['pdy']
    pose = copy.deepcopy(base_pose)
    pose['body_rot_b'] = params['theta']
    pose['leg_near'] = dict(pose['leg_near'], fx=params['fxn'])
    pose['leg_far'] = dict(pose['leg_far'], fx=params['fxf'])
    kpm = RR22.kp_master(pose)
    scalars = dict(neck_w=float(pose['neck_w']), bulge_pos=float(pose['bulge_pos']),
                   bulge_amp=float(pose['bulge_amp']), px_per_unit=RR22.U)
    stack = M2.build_mask_stack(kpm, scalars, (W, H))
    return np.any(stack > 0, axis=0), pose, kpm

def score(params, tag=''):
    global Breast0, Anchor0
    sil, pose, kpm = build(params)
    breast = np.array(kpm['spine'][0], float)
    anchor = np.array(kpm['head_c'], float)
    if Breast0 is None:
        Breast0, Anchor0 = breast, anchor
    neck_ok = np.allclose(breast, Breast0, atol=0.6) and np.allclose(anchor, Anchor0, atol=0.6)
    ik_ok = True
    for nm in ('n', 'f'):
        hip = np.array(kpm[f'hip_{nm}'], float); foot = np.array(kpm[f'foot_{nm}'], float)
        knee = np.array(kpm[f'knee_{nm}'], float)
        d = np.hypot(*(hip - foot)) / RR22.U
        if not (np.all(np.isfinite(knee)) and d < 39.6 * 0.995 and d > 2.0):
            ik_ok = False
    ys, xs = np.nonzero(sil)
    clip = xs.min() <= 0 or xs.max() >= W - 1 or ys.min() <= 0 or ys.max() >= H - 1
    iou, prm = MV.aligned_iou(rest, sil)
    entry = dict(tag=tag, params=dict(params), iou=round(float(iou), 4), prm=prm,
                 neck_ok=bool(neck_ok), ik_ok=bool(ik_ok), clip=bool(clip))
    log.append(entry)
    print(f"{tag:22s} iou={iou:.4f} theta={params['theta']:+.2f} plume=({params['pdx']:+.1f},{params['pdy']:+.1f}) "
          f"hips=({params['hnx']:+.2f},{params['hfx']:+.2f}) fx=({params['fxn']:+.1f},{params['fxf']:+.1f}) "
          f"neck_ok={neck_ok} ik_ok={ik_ok} clip={clip}", flush=True)
    return iou if (neck_ok and ik_ok and not clip) else -1.0

P0 = dict(theta=0.0, pdx=0.0, pdy=0.0, hnx=0.0, hfx=0.0, fxn=6.0, fxf=-5.0)
best = score(P0, 'control-v22-zero-delta')
assert abs(log[-1]['iou'] - 0.5501) < 0.001, 'v2.2 zero-delta must reproduce v2.1 0.5501'
cur = dict(P0); cur_iou = best

# stage 1: theta
for th in (-9.0, -7.5, -6.0, -4.5, -3.0, -1.5, 1.5, 3.0):
    p = dict(cur, theta=th)
    v = score(p, 'stage1-theta')
    if v > cur_iou:
        cur, cur_iou = p, v
print('after stage1:', cur, cur_iou, flush=True)

# stage 2: plume translate grid, then refine
best_pd = (cur['pdx'], cur['pdy'])
for pdx in (-20.0, -16.0, -12.0, -8.0, -4.0):
    for pdy in (0.0, 4.0, 8.0, 11.5, 15.0, 19.0):
        if pdx == cur['pdx'] and pdy == cur['pdy']:
            continue
        p = dict(cur, pdx=pdx, pdy=pdy)
        v = score(p, 'stage2-plume')
        if v > cur_iou:
            cur, cur_iou = p, v
for step in (2.0, 1.0):
    improved = True
    while improved:
        improved = False
        for dx in (-step, 0.0, step):
            for dy in (-step, 0.0, step):
                if dx == dy == 0.0:
                    continue
                p = dict(cur, pdx=cur['pdx'] + dx, pdy=cur['pdy'] + dy)
                v = score(p, 'stage2-refine')
                if v > cur_iou:
                    cur, cur_iou = p, v; improved = True
print('after stage2:', cur, cur_iou, flush=True)

# stage 3: legs -- feet first (measured start), then hip bases
p = dict(cur, fxn=-3.6, fxf=-11.1)
v = score(p, 'stage3-feet-measured')
if v > cur_iou:
    cur, cur_iou = p, v
for key, steps in (('fxn', (2.0, 1.0, 0.5)), ('fxf', (2.0, 1.0, 0.5)),
                   ('hnx', (1.5, 0.75)), ('hfx', (1.5, 0.75))):
    for step in steps:
        improved = True
        while improved:
            improved = False
            for d in (-step, step):
                p = dict(cur); p[key] = cur[key] + d
                v = score(p, f'stage3-{key}')
                if v > cur_iou:
                    cur, cur_iou = p, v; improved = True
print('after stage3:', cur, cur_iou, flush=True)

# stage 4: joint polish
for key, step in (('theta', 0.75), ('pdx', 1.0), ('pdy', 1.0),
                  ('fxn', 0.5), ('fxf', 0.5), ('hnx', 0.5), ('hfx', 0.5),
                  ('theta', 0.375)):
    improved = True
    while improved:
        improved = False
        for d in (-step, step):
            p = dict(cur); p[key] = cur[key] + d
            v = score(p, f'stage4-{key}')
            if v > cur_iou + 0.0004:
                cur, cur_iou = p, v; improved = True
print('FINAL:', cur, cur_iou, flush=True)

with open(f'{OUT}/search_log.json', 'w') as f:
    json.dump(dict(log=log, final=dict(params=cur, iou=cur_iou)), f, indent=1)
# persist the winning build for the verify step
sil, pose, kpm = build(cur)
Image.fromarray((sil * 255).astype(np.uint8)).save(f'{OUT}/rig_v2_2_idle_silhouette.png')
with open(f'{OUT}/winning_params.json', 'w') as f:
    json.dump(dict(params=cur, iou=cur_iou), f, indent=1)
print('saved silhouette + winning params')
