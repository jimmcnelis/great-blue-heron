"""Band-constrained geometry pass (rig v2.3 -> candidate v2.4): shared core.

Deltas are applied on top of the BAKED v2.3 modules exactly as they sit
on disk (rig13_r4_v23 / roster_render_v23; the pose from
geometry-round/pose_tracks_v23.json). At the init state the build must
reproduce v2.3 pixel-identically (controls assert this).

Scoring: the certified protocol of geo_common (raw IoU + bird-only IoU),
PLUS the band surface: torso-core row bands / core centroid measured
with geo_common.body_measures at the verify_v23 Href, and the torso
length landmark (measure_v2.landmarks torso_w_over_H).

Approved targets (PROPORTION_SPEC + Phase A instruments):
  bands     top/mid/bottom = 0.281 / 0.348 / 0.371
  centroid  (-0.356, +0.111) H breast-relative
  torso len ~0.80 H
Floors defending v2.3 (0.7121 / 0.7656): raw >= 0.69, bird >= 0.74.

Frozen: neck channel pixel-identical to v2.2; breast + head anchor
unmoved; leg IK; no clipping. Search vocabulary is torso + wing ONLY
(theta, legs, hips, head, plume are not parameters of this pass).
"""
import copy, json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
GEO = os.path.expanduser('~/workspace/heron/art2/finished-art-stills/rig-v2/geometry-round')
sys.path.insert(0, GEO)
sys.path.insert(0, HERE)
import geo_common as G
import roster_render_v22 as RR22
import roster_render_v23 as RR23
import rig13_r4_v23 as R23

W, H = G.W, G.H
OUT = HERE

APPROVED = dict(band0=0.281, band1=0.348, band2=0.371,
                centroid=[-0.356, 0.111], torso_w=0.80)
RAW_FLOOR, BIRD_FLOOR = 0.69, 0.74

# ---- base = baked v2.3, captured at import
BASE_TORSO = [tuple(p) for p in R23.TORSO]
BASE_WING = [tuple(p) for p in R23.WING]
BASE_POSE = json.load(open(f'{GEO}/pose_tracks_v23.json'))['idle'][0]

# ---- invariant references from the baked v2.2 build
pose22 = json.load(open(f'{G.BP}/pose_tracks_v22.json'))['idle'][0]
_, stack22_ref, kpm22_ref = G.sil_stack(RR22, copy.deepcopy(pose22))
REF_NECK = stack22_ref[1]
REF_BREAST = np.array(kpm22_ref['spine'][0], float)
REF_ANCHOR = np.array(kpm22_ref['head_c'], float)

# ---- Href exactly as verify_v23 computed it
_a22 = np.array(kpm22_ref['head_c'], float)
HREF = 88.0 * RR23.U - (_a22[1] - 3.15 * 1.45 * RR23.U)

INIT_STATE = dict(theta=float(BASE_POSE['body_rot_b']),
                  fxn=float(BASE_POSE['leg_near']['fx']),
                  fxf=float(BASE_POSE['leg_far']['fx']),
                  pdx=float(RR23.PLUME_DX), pdy=float(RR23.PLUME_DY),
                  pl_len=1.0, pl_wid=1.0, pl_bot=0.0,
                  hnx=0.0, hfx=0.0,
                  t_bk=0.0, t_crown=0.0, t_bl=0.0, t_keel=0.0, t_brdx=0.0,
                  t_taildx=0.0, t_taildy=0.0, w_bot=0.0, w_top=0.0, w_fwd=0.0,
                  h_nape=0.0, h_crown=0.0, h_cheek=0.0, h_napedy=0.0)

def apply(st):
    """Verbatim the search_v23 apply(): deltas from BASE (here: baked v2.3)."""
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
    # SKULL / PLUME / HIPS deliberately not written: frozen in this pass,
    # their state values stay at identity in INIT_STATE and are never varied.
    pose = copy.deepcopy(BASE_POSE)
    pose['body_rot_b'] = st['theta']
    pose['leg_near'] = dict(pose['leg_near'], fx=st['fxn'])
    pose['leg_far'] = dict(pose['leg_far'], fx=st['fxf'])
    return pose

def band_metrics(stack, sil, kpm, pose):
    bm = G.body_measures(stack, sil, kpm, HREF)
    bands = bm['torso_core_row_bands']
    cen = bm['torso_core_centroid_minus_breast_over_H']
    lm = G.MV.landmarks(RR23, pose)
    band_err = float(abs(bands['band0'] - APPROVED['band0']) +
                     abs(bands['band1'] - APPROVED['band1']) +
                     abs(bands['band2'] - APPROVED['band2']))
    fwd_err = float(cen[0] - APPROVED['centroid'][0])   # + = too far forward
    vert_err = float(cen[1] - APPROVED['centroid'][1])
    len_err = float(lm['torso_w_over_H'] - APPROVED['torso_w'])
    sec_err = float(abs(fwd_err) + abs(len_err))
    return dict(bands=bands, band_err=round(band_err, 4),
                mid=bands['band1'], mid_err=round(abs(bands['band1'] - APPROVED['band1']), 4),
                centroid=cen, fwd_err=round(fwd_err, 4), vert_err=round(vert_err, 4),
                torso_w=lm['torso_w_over_H'], torso_d=lm['torso_d_over_H'],
                len_err=round(len_err, 4), sec_err=round(sec_err, 4))

def invariants(stack, kpm, sil):
    neck_ok = bool(np.array_equal(stack[1], REF_NECK))
    breast = np.array(kpm['spine'][0], float); anchor = np.array(kpm['head_c'], float)
    endp_ok = bool(np.allclose(breast, REF_BREAST, atol=0.6) and
                   np.allclose(anchor, REF_ANCHOR, atol=0.6))
    ik_ok = True
    for nm in ('n', 'f'):
        hip = np.array(kpm[f'hip_{nm}'], float); foot = np.array(kpm[f'foot_{nm}'], float)
        knee = np.array(kpm[f'knee_{nm}'], float)
        d = np.hypot(*(hip - foot)) / RR23.U
        if not (np.all(np.isfinite(knee)) and d < 39.6 * 0.995 and d > 2.0):
            ik_ok = False
    ys, xs = np.nonzero(sil)
    clip = bool(xs.min() <= 0 or xs.max() >= W - 1 or ys.min() <= 0 or ys.max() >= H - 1)
    return neck_ok, endp_ok, ik_ok, clip

def evaluate(st):
    """Returns (raw, bird, metrics dict incl. invariants)."""
    pose = apply(st)
    sil, stack, kpm = G.sil_stack(RR23, pose)
    neck_ok, endp_ok, ik_ok, clip = invariants(stack, kpm, sil)
    raw, prm, bird, _ = G.score(sil)
    m = band_metrics(stack, sil, kpm, pose)
    m.update(dict(raw=round(float(raw), 4), bird=round(float(bird), 4), prm=prm,
                  neck_ok=neck_ok, endp_ok=endp_ok, ik_ok=ik_ok, clip=clip,
                  ok=bool(neck_ok and endp_ok and ik_ok and not clip),
                  floors_ok=bool(float(raw) >= RAW_FLOOR and float(bird) >= BIRD_FLOOR)))
    return float(raw), float(bird), m, sil, stack

def nonzero_state(st):
    return {k: round(v, 4) for k, v in st.items()
            if abs(v - INIT_STATE.get(k, 0.0)) > 1e-9}
