#!/usr/bin/env python3
"""Geometry round: controls FIRST. v2, v2.1, v2.2 must reproduce their
certified numbers (0.5257 / 0.5501 / 0.6141 raw) under the protocol in
this harness before any v2.3 number counts; the v2.3 files at zero
geometry delta must reproduce v2.2's mask stack PIXEL-IDENTICALLY
(all 8 channels) and score 0.6141 raw / 0.6567 bird-only.
"""
import copy, json, os, sys, time
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import geo_common as G
import roster_render_v21 as RR21
import roster_render_v22 as RR22
import roster_render_v23 as RR23

res = {}
t0 = time.time()
sil2, _, _ = G.MV.sil_of(G.MV.RR2, G.MV.M2, 'idle_hunt', 0)
raw2, prm2, bird2, _ = G.score(sil2)
res['control_v2'] = dict(raw=raw2, prm=prm2, bird=bird2)
print(f"v2   raw={raw2:.4f} bird={bird2:.4f}  ({time.time()-t0:.1f}s)", flush=True)

def hold(hxhy=(36.17, -26.34)):
    pose = copy.deepcopy(G.RC.CHARTS['idle_hunt']().frames[0])
    pose['hx'], pose['hy'] = hxhy
    return pose

t0 = time.time()
sil21, _, _ = G.sil_stack(RR21, hold())
raw21, prm21, bird21, _ = G.score(sil21)
res['control_v21'] = dict(raw=raw21, prm=prm21, bird=bird21)
print(f"v2.1 raw={raw21:.4f} bird={bird21:.4f}  ({time.time()-t0:.1f}s)", flush=True)

pose22 = json.load(open(f'{G.BP}/pose_tracks_v22.json'))['idle'][0]
t0 = time.time()
sil22, stack22, kpm22 = G.sil_stack(RR22, copy.deepcopy(pose22))
raw22, prm22, bird22, _ = G.score(sil22)
res['control_v22'] = dict(raw=raw22, prm=prm22, bird=bird22)
print(f"v2.2 raw={raw22:.4f} bird={bird22:.4f}  ({time.time()-t0:.1f}s)", flush=True)

pose23 = json.load(open(f'{G.OUT}/pose_tracks_v23.json'))['idle'][0]
t0 = time.time()
sil23, stack23, kpm23 = G.sil_stack(RR23, copy.deepcopy(pose23))
ident = all(bool(np.array_equal(stack23[i], stack22[i])) for i in range(8))
raw23, prm23, bird23, _ = G.score(sil23)
res['v23_zero_delta'] = dict(raw=raw23, prm=prm23, bird=bird23,
                             stack_pixel_identical_to_v22=ident,
                             channels_identical=[bool(np.array_equal(stack23[i], stack22[i])) for i in range(8)])
print(f"v2.3 zero-delta raw={raw23:.4f} bird={bird23:.4f} stack_identical={ident}  ({time.time()-t0:.1f}s)", flush=True)

res['asserts'] = dict(
    v2_ok=abs(raw2 - 0.5257) < 0.001,
    v21_ok=abs(raw21 - 0.5501) < 0.001,
    v22_ok=abs(raw22 - 0.6141) < 0.001,
    v23_zero_ok=ident and abs(raw23 - 0.6141) < 0.001)
print(json.dumps(res['asserts'], indent=1))
with open(f'{G.OUT}/controls_results.json', 'w') as f:
    json.dump(res, f, indent=1)
assert all(res['asserts'].values()), 'CONTROL FAILURE -- do not trust any v2.3 number'
print('CONTROLS PASS')
