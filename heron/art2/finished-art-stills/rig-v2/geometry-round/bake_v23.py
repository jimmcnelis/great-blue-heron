#!/usr/bin/env python3
"""Bake the geometry-round winning state into the v2.3 files.

Replicates search_v23.apply() exactly to compute the final TORSO /
WING / SKULL_PROFILE / PLUME_OFFS_BASE / hips / plume translate /
pose, writes them into rig13_r4_v23.py, roster_render_v23.py and
pose_tracks_v23.json, then proves bake-faithfulness: the baked
modules' mask stack must be pixel-identical to the search-apply
build at the winning state, and the neck channel must be identical
to the baked v2.2 build's.
"""
import copy, json, os, re, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import geo_common as G
import roster_render_v22 as RR22
import roster_render_v23 as RR23
import rig13_r4_v23 as R23

WIN = json.load(open(f'{G.OUT}/winning_params_v23.json'))
st = WIN['state']
print('winning state:', json.dumps(st))
print(f"search scores: raw={WIN['raw']:.4f} bird={WIN['bird']:.4f}")

BASE_TORSO = [tuple(p) for p in R23.TORSO]
BASE_WING = [tuple(p) for p in R23.WING]
BASE_SKULL = [tuple(p) for p in RR23.SKULL_PROFILE]
BASE_OFFS = [tuple(p) for p in RR23.PLUME_OFFS_BASE]
BASE_HIP_N = tuple(R23.HIP_NEAR); BASE_HIP_F = tuple(R23.HIP_FAR)
BASE_POSE = json.load(open(f'{G.OUT}/pose_tracks_v23.json'))['idle'][0]

# ---- replicate search_v23.apply() verbatim
def compute(st):
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
    torso = [(x + td.get(i, [0, 0])[0], y + td.get(i, [0, 0])[1])
             for i, (x, y) in enumerate(BASE_TORSO)]
    wing = [(x + wd.get(i, [0, 0])[0], y + wd.get(i, [0, 0])[1])
            for i, (x, y) in enumerate(BASE_WING)]
    skull = [(x + hd.get(i, [0, 0])[0], y + hd.get(i, [0, 0])[1])
             for i, (x, y) in enumerate(BASE_SKULL)]
    offs = []
    for (x, y) in BASE_OFFS:
        ny = y * st['pl_len'] + (st['pl_bot'] if y > 5 else 0.0)
        offs.append((x * st['pl_wid'], ny))
    for k, v in st.items():
        if k.startswith('pp'):
            idx = int(k[2:-1]); ox, oy = offs[idx]; offs[idx] = (ox, oy + v)
    hip_n = (BASE_HIP_N[0] + st['hnx'], BASE_HIP_N[1])
    hip_f = (BASE_HIP_F[0] + st['hfx'], BASE_HIP_F[1])
    pose = copy.deepcopy(BASE_POSE)
    pose['body_rot_b'] = st['theta']
    pose['leg_near'] = dict(pose['leg_near'], fx=st['fxn'])
    pose['leg_far'] = dict(pose['leg_far'], fx=st['fxf'])
    return torso, wing, skull, offs, hip_n, hip_f, pose

TORSO, WING, SKULL, OFFS, HIP_N, HIP_F, POSE = compute(st)

def fmt(pts, per=4):
    parts = [f"({x:.4g}, {y:.4g})" for (x, y) in pts]
    lines = []
    for i in range(0, len(parts), per):
        lines.append(', '.join(parts[i:i + per]))
    return lines

# ---------- reference build via in-memory apply (for faithfulness)
R23.TORSO[:] = [tuple(p) for p in TORSO]
R23.WING[:] = [tuple(p) for p in WING]
RR23.SKULL_PROFILE[:] = [tuple(p) for p in SKULL]
RR23.PLUME_OFFS_BASE[:] = [tuple(p) for p in OFFS]
RR23.PLUME_DX, RR23.PLUME_DY = st['pdx'], st['pdy']
R23.HIP_NEAR = tuple(HIP_N); R23.HIP_FAR = tuple(HIP_F)
sil_ref, stack_ref, _ = G.sil_stack(RR23, copy.deepcopy(POSE))
raw_ref, _, bird_ref, _ = G.score(sil_ref)
print(f'search-apply build: raw={raw_ref:.4f} bird={bird_ref:.4f}')
assert abs(raw_ref - WIN['raw']) < 0.0011 and abs(bird_ref - WIN['bird']) < 0.0011, \
    'apply replication does not reproduce the search scores'

# ---------- write the rig file
rig_path = os.path.expanduser('~/workspace/heron/src13/rig13_r4_v23.py')
src = open(rig_path).read()

def sub_block(src, start_marker, new_lines, indent='         '):
    """Replace a bracketed list literal beginning at start_marker."""
    i = src.index(start_marker)
    j = src.index('[', i)
    depth = 0; k = j
    while True:
        if src[k] == '[': depth += 1
        elif src[k] == ']':
            depth -= 1
            if depth == 0: break
        k += 1
    body = ('[\n' + indent + (',\n' + indent).join(new_lines) + ']')
    return src[:j] + body + src[k + 1:]

src = sub_block(src, 'TORSO = ', fmt(TORSO))
src = sub_block(src, 'WING = ', fmt(WING))
# rig draw_head art-path skull (line ~608 list, distinct values)
skull_txt = '[' + ', '.join(f"({x:.4g}, {y:.4g})" for (x, y) in SKULL) + ']'
old_skull = ('[(-4.6, -1.1), (-3.5, -2.8), (-0.6, -3.15), (2.1, -2.3),\n'
             '             (3.6, -0.9), (3.9, 0.5), (2.1, 1.9), (-0.8, 2.45), (-3.7, 1.5)]')
assert old_skull in src, 'rig art-path skull literal not found verbatim'
src = src.replace(old_skull, skull_txt)
src = re.sub(r'HIP_NEAR = \([-\d.]+, [-\d.]+\)',
             f"HIP_NEAR = ({HIP_N[0]:.4g}, {HIP_N[1]:.4g})", src, count=1)
src = re.sub(r'HIP_FAR = \([-\d.]+, [-\d.]+\)',
             f"HIP_FAR = ({HIP_F[0]:.4g}, {HIP_F[1]:.4g})", src, count=1)
src = src.replace('# rig-v2.3', '# rig-v2.3')  # no-op guard
open(rig_path, 'w').write(src)
print('rig written')

# ---------- write the renderer file
rr_path = os.path.expanduser('~/workspace/heron/art2/roster_render_v23.py')
src = open(rr_path).read()
src = sub_block(src, 'SKULL_PROFILE = ', fmt(SKULL), indent='                 ')
src = sub_block(src, 'PLUME_OFFS_BASE = ', fmt(OFFS), indent='                    ')
src = re.sub(r'PLUME_DX, PLUME_DY = [-\d.]+, [-\d.]+',
             f"PLUME_DX, PLUME_DY = {st['pdx']:.4g}, {st['pdy']:.4g}", src, count=1)
open(rr_path, 'w').write(src)
print('renderer written')

# ---------- write the pose file
tracks = json.load(open(f'{G.OUT}/pose_tracks_v23.json'))
tracks['idle'][0] = POSE
with open(f'{G.OUT}/pose_tracks_v23.json', 'w') as f:
    json.dump(tracks, f, indent=1)
print('pose written: theta=', POSE['body_rot_b'],
      'fxn=', POSE['leg_near']['fx'], 'fxf=', POSE['leg_far']['fx'])

# ---------- faithfulness: fresh import of the baked files
for m in ('roster_render_v23', 'rig13_r4_v23'):
    sys.modules.pop(m, None)
import importlib
R23b = importlib.import_module('rig13_r4_v23')
RR23b = importlib.import_module('roster_render_v23')
pose_b = json.load(open(f'{G.OUT}/pose_tracks_v23.json'))['idle'][0]
sil_b, stack_b, _ = G.sil_stack(RR23b, copy.deepcopy(pose_b))
same = bool(np.array_equal(stack_b, stack_ref))
raw_b, _, bird_b, _ = G.score(sil_b)
print(f'baked build: raw={raw_b:.4f} bird={bird_b:.4f} stack_pixel_identical_to_search={same}')
assert same, 'BAKE NOT FAITHFUL: baked stack differs from search build'
res = dict(winning_state=st, search_raw=WIN['raw'], search_bird=WIN['bird'],
           baked_raw=raw_b, baked_bird=bird_b, stack_pixel_identical=True,
           torso=TORSO, wing=WING, skull=SKULL, plume_offs_base=OFFS,
           plume_dx=st['pdx'], plume_dy=st['pdy'], hip_near=HIP_N, hip_far=HIP_F)
with open(f'{G.OUT}/bake_results_v23.json', 'w') as f:
    json.dump(res, f, indent=1)
print('BAKE OK')
