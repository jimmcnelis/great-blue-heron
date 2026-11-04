#!/usr/bin/env python3
"""Band pass: controls FIRST. v2 / v2.1 / v2.2 / v2.3 must reproduce
their certified numbers (raw 0.5257 / 0.5501 / 0.6141 / 0.7121,
bird-only 0.5642 / 0.5879 / 0.6567 / 0.7656) before any band-pass
number counts; the band_core init state (zero delta on the baked
v2.3 files) must reproduce v2.3's mask stack PIXEL-IDENTICALLY and
its band surface (0.2615 / 0.4349 / 0.3180, centroid -0.2855/+0.1136,
torso_w 0.849).
"""
import copy, json, os, sys, time
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import band_core as B
import geo_common as G
import roster_render_v21 as RR21
import roster_render_v22 as RR22
import roster_render_v23 as RR23

res = {}
def hold(hxhy=(36.17, -26.34)):
    pose = copy.deepcopy(G.RC.CHARTS['idle_hunt']().frames[0])
    pose['hx'], pose['hy'] = hxhy
    return pose

t0 = time.time()
sil2, _, _ = G.MV.sil_of(G.MV.RR2, G.MV.M2, 'idle_hunt', 0)
r, p, b, _ = G.score(sil2); res['control_v2'] = dict(raw=r, prm=p, bird=b)
print(f"v2   raw={r:.4f} bird={b:.4f}  ({time.time()-t0:.1f}s)", flush=True)

t0 = time.time()
sil21, _, _ = G.sil_stack(RR21, hold())
r, p, b, _ = G.score(sil21); res['control_v21'] = dict(raw=r, prm=p, bird=b)
print(f"v2.1 raw={r:.4f} bird={b:.4f}  ({time.time()-t0:.1f}s)", flush=True)

t0 = time.time()
pose22 = json.load(open(f'{G.BP}/pose_tracks_v22.json'))['idle'][0]
sil22, stack22, kpm22 = G.sil_stack(RR22, copy.deepcopy(pose22))
r, p, b, _ = G.score(sil22); res['control_v22'] = dict(raw=r, prm=p, bird=b)
bm22 = B.band_metrics(stack22, sil22, kpm22, pose22)
res['control_v22_bands'] = bm22
print(f"v2.2 raw={r:.4f} bird={b:.4f} bands={bm22['bands']} ({time.time()-t0:.1f}s)", flush=True)

t0 = time.time()
pose23 = json.load(open(f'{B.GEO}/pose_tracks_v23.json'))['idle'][0]
sil23, stack23, kpm23 = G.sil_stack(RR23, copy.deepcopy(pose23))
r, p, b, _ = G.score(sil23); res['control_v23'] = dict(raw=r, prm=p, bird=b)
bm23 = B.band_metrics(stack23, sil23, kpm23, pose23)
res['control_v23_bands'] = bm23
print(f"v2.3 raw={r:.4f} bird={b:.4f} bands={bm23['bands']} band_err={bm23['band_err']} "
      f"centroid={bm23['centroid']} torso_w={bm23['torso_w']} ({time.time()-t0:.1f}s)", flush=True)

t0 = time.time()
raw0, bird0, m0, sil0, stack0 = B.evaluate(dict(B.INIT_STATE))
ident = all(bool(np.array_equal(stack0[i], stack23[i])) for i in range(8))
res['zero_delta'] = dict(raw=raw0, bird=bird0, metrics=m0, stack_pixel_identical_to_v23=ident,
                         channels_identical=[bool(np.array_equal(stack0[i], stack23[i])) for i in range(8)])
print(f"zero-delta raw={raw0:.4f} bird={bird0:.4f} bands={m0['bands']} stack_identical={ident} "
      f"({time.time()-t0:.1f}s)", flush=True)

res['asserts'] = {k: bool(v) for k, v in dict(
    v2_ok=abs(res['control_v2']['raw'] - 0.5257) < 0.001 and abs(res['control_v2']['bird'] - 0.5642) < 0.001,
    v21_ok=abs(res['control_v21']['raw'] - 0.5501) < 0.001 and abs(res['control_v21']['bird'] - 0.5879) < 0.001,
    v22_ok=abs(res['control_v22']['raw'] - 0.6141) < 0.001 and abs(res['control_v22']['bird'] - 0.6567) < 0.001,
    v23_ok=abs(res['control_v23']['raw'] - 0.7121) < 0.001 and abs(res['control_v23']['bird'] - 0.7656) < 0.001,
    zero_ok=ident and abs(raw0 - 0.7121) < 0.001 and abs(bird0 - 0.7656) < 0.001 and m0['ok'],
    v23_bands_ok=abs(bm23['bands']['band1'] - 0.4349) < 0.001 and abs(bm23['torso_w'] - 0.849) < 0.002).items()}
print(json.dumps(res['asserts'], indent=1))
def _np_default(o):
    if isinstance(o, (np.bool_,)): return bool(o)
    if isinstance(o, (np.floating,)): return float(o)
    if isinstance(o, (np.integer,)): return int(o)
    raise TypeError(str(type(o)))
with open(f'{B.OUT}/controls_results_v24.json', 'w') as f:
    json.dump(res, f, indent=1, default=_np_default)
assert all(res['asserts'].values()), 'CONTROL FAILURE -- do not trust any band-pass number'
print('CONTROLS PASS')
