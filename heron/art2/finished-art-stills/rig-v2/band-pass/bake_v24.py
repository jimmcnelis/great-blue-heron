#!/usr/bin/env python3
"""Bake the band-pass winning delta state into the v2.4 files.

Only TORSO / WING change (the pass's whole vocabulary); skull, plume,
hips and the pose carry over from v2.3 untouched. Canonical positions
mirror prior rounds (src13/rig13_r4_v24.py, art2/roster_render_v24.py),
with record copies + pose_tracks_v24.json in the band-pass folder.

Bake-faithfulness proof: a fresh import of the baked v2.4 modules
must reproduce the band_core.apply(winning state) mask stack
pixel-identically and the winning scores exactly.
"""
import copy, json, os, re, shutil, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import band_core as B
import geo_common as G
import roster_render_v23 as RR23
import rig13_r4_v23 as R23

WIN = json.load(open(f'{HERE}/winning_params_v24.json'))
st = dict(B.INIT_STATE); st.update(WIN['state'])
print('winning delta:', json.dumps(WIN['delta']))
print(f"search scores: raw={WIN['metrics']['raw']:.4f} bird={WIN['metrics']['bird']:.4f} "
      f"band_err={WIN['metrics']['band_err']:.4f}")

# ---- replicate band_core.apply()'s torso/wing delta computation
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
    for k, v in st.items():
        if k.startswith('tp'):
            idx = int(k[2:-1]); d = td.setdefault(idx, [0.0, 0.0])
            d[0 if k[-1] == 'x' else 1] += v
        elif k.startswith('wp'):
            idx = int(k[2:-1]); d = wd.setdefault(idx, [0.0, 0.0])
            d[0 if k[-1] == 'x' else 1] += v
    torso = [(x + td.get(i, [0, 0])[0], y + td.get(i, [0, 0])[1])
             for i, (x, y) in enumerate(B.BASE_TORSO)]
    wing = [(x + wd.get(i, [0, 0])[0], y + wd.get(i, [0, 0])[1])
            for i, (x, y) in enumerate(B.BASE_WING)]
    return torso, wing

TORSO, WING = compute(st)

# ---- reference build via band_core.apply (the search build itself)
raw_ref, bird_ref, m_ref, sil_ref, stack_ref = B.evaluate(st)
print(f'search-apply build: raw={raw_ref:.4f} bird={bird_ref:.4f} band_err={m_ref["band_err"]:.4f}')
assert abs(raw_ref - WIN['metrics']['raw']) < 0.0011 and abs(bird_ref - WIN['metrics']['bird']) < 0.0011, \
    'apply replication does not reproduce the search scores'

def fmt(pts, per=4):
    parts = [f"({x:.4g}, {y:.4g})" for (x, y) in pts]
    lines = []
    for i in range(0, len(parts), per):
        lines.append(', '.join(parts[i:i + per]))
    return lines

def sub_block(src, start_marker, new_lines, indent='         '):
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

SRC13 = os.path.expanduser('~/workspace/heron/src13')
ART2 = os.path.expanduser('~/workspace/heron/art2')

# ---- rig file: v23 source with TORSO / WING replaced
src = open(f'{SRC13}/rig13_r4_v23.py').read()
src = sub_block(src, 'TORSO = ', fmt(TORSO))
src = sub_block(src, 'WING = ', fmt(WING))
src = src.replace('# rig-v2.3', '# rig-v2.4 (band pass: TORSO/WING only)')
open(f'{SRC13}/rig13_r4_v24.py', 'w').write(src)
print('rig written: src13/rig13_r4_v24.py')

# ---- renderer file: v23 source, rig import bumped to v24
src = open(f'{ART2}/roster_render_v23.py').read()
assert 'import rig13_r4_v23 as R' in src
src = src.replace('import rig13_r4_v23 as R', 'import rig13_r4_v24 as R')
open(f'{ART2}/roster_render_v24.py', 'w').write(src)
print('renderer written: art2/roster_render_v24.py')

# ---- pose file: unchanged from v2.3 (pose frozen in this pass)
tracks = json.load(open(f'{B.GEO}/pose_tracks_v23.json'))
with open(f'{HERE}/pose_tracks_v24.json', 'w') as f:
    json.dump(tracks, f, indent=1)
print('pose written: band-pass/pose_tracks_v24.json (identical to v2.3)')

# ---- record copies in the band-pass folder
shutil.copy(f'{SRC13}/rig13_r4_v24.py', f'{HERE}/rig13_r4_v24.py')
shutil.copy(f'{ART2}/roster_render_v24.py', f'{HERE}/roster_render_v24.py')

# ---- faithfulness: fresh import of the baked files
for m in ('roster_render_v24', 'rig13_r4_v24'):
    sys.modules.pop(m, None)
import importlib
RR24 = importlib.import_module('roster_render_v24')
pose_b = tracks['idle'][0]
sil_b, stack_b, kpm_b = G.sil_stack(RR24, copy.deepcopy(pose_b))
same = bool(np.array_equal(stack_b, stack_ref))
raw_b, _, bird_b, _ = G.score(sil_b)
print(f'baked build: raw={raw_b:.4f} bird={bird_b:.4f} stack_pixel_identical_to_search={same}')
assert same, 'BAKE NOT FAITHFUL: baked stack differs from search build'
res = dict(winning_delta=WIN['delta'], search_metrics=WIN['metrics'],
           baked_raw=raw_b, baked_bird=bird_b, stack_pixel_identical=True,
           torso=TORSO, wing=WING)
with open(f'{HERE}/bake_results_v24.json', 'w') as f:
    json.dump(res, f, indent=1)
print('BAKE OK')
