#!/usr/bin/env python3
"""Motion test v3 measurements - SAME protocol as v2 (measure_v2.py
mask/fraction/bill code verbatim), with the gold references repointed
at the v3 REGISTERED corpus targets (the same drawings in rig
geometry - the geometry the v3 model was trained to produce), plus:
  - gate 1 also reported raw vs the original approved still
    (continuity with v2's number; capped by the still's own 0.684
    fit to rig geometry)
  - model IoU vs its own input silhouette (geometry lock)
  - torso-extent read (the carried v2.4 flag): bird bbox width /
    standing height in hold output vs approved still vs rig.
Frames layout (mirrors v2): ../frames/hold/hold_frame.png,
../frames/strike_ema|strike_model/fXXXX.png, determinism.json.
"""
import json, os
import numpy as np
from PIL import Image

ROOT = os.path.expanduser('~/workspace/heron/art2')
V3 = f'{ROOT}/motion-test-v3'
FM3 = f'{ROOT}/finished-art-stills/finish-model-v3'
PROBE = [6, 25, 34, 45]

def load(p):
    return np.asarray(Image.open(p).convert('RGB'), dtype=np.float32)

def paper_color(a):
    patches = [a[:40, :40], a[:40, -40:], a[-40:, :40], a[-40:, -40:]]
    return np.median(np.concatenate([p.reshape(-1, 3) for p in patches]), axis=0)

def content_mask(a):
    pc = paper_color(a)
    d = np.abs(a - pc).sum(axis=2)
    return d > 55

def color_fracs(a, mask):
    r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    n = max(mask.sum(), 1)
    black = mask & (a.mean(axis=2) < 70)
    rust = mask & (r > 95) & (r - g > 22) & (r - b > 40)
    yellow = mask & (r > 150) & (g > 95) & (b < 120) & (r - b > 60)
    slate = mask & (b > r + 4) & (a.mean(axis=2) > 60) & (a.mean(axis=2) < 190)
    return dict(black=float(black.sum() / n), rust=float(rust.sum() / n),
                yellow=float(yellow.sum() / n), slate=float(slate.sum() / n))

def bill_centroid_y(a, mask):
    r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    yel = mask & (r > 150) & (g > 95) & (b < 120) & (r - b > 60)
    ys, _ = np.nonzero(yel)
    return float(ys.mean()) if len(ys) else None

def iou(m0, m1):
    u = (m0 | m1).sum()
    return float((m0 & m1).sum() / u) if u else 1.0

def gold(i):
    return load(f'{FM3}/corpus/target/strike_f{i:04d}.png')

out = {}
rest = load(f'{ROOT}/finished-art-stills/audubon_rest.png')
rest_mask = content_mask(rest)
out['rest_fracs'] = {k: round(v, 4) for k, v in color_fracs(rest, rest_mask).items()}
rest_reg = load(f'{FM3}/corpus/target/idle_f0030.png')  # approved still, registered
rest_reg_mask = content_mask(rest_reg)

# ---- checkpoint selection on probe frames (IoU vs registered gold) ----
sel = {}
for cand in ('ema', 'model'):
    ious, berr = [], []
    for i in PROBE:
        a = load(f'{V3}/frames/strike_{cand}/f{i:04d}.png'); m = content_mask(a)
        g = gold(i); gm = content_mask(g)
        ious.append(iou(m, gm))
        b0, b1 = bill_centroid_y(a, m), bill_centroid_y(g, gm)
        berr.append(abs(b0 - b1) if (b0 is not None and b1 is not None) else None)
    sel[cand] = dict(probe_iou_mean=round(float(np.mean(ious)), 4),
                     probe_bill_err_mean=round(float(np.mean([e for e in berr if e is not None])), 2))
out['checkpoint_selection'] = sel
WIN = 'ema' if sel['ema']['probe_iou_mean'] >= sel['model']['probe_iou_mean'] else 'model'
out['winner'] = WIN
print('checkpoint selection:', sel, '-> winner:', WIN)

# ---- gate 1: fidelity at rest ----
hold = load(f'{V3}/frames/hold/hold_frame.png'); hm = content_mask(hold)
hf = color_fracs(hold, hm)
u = hm | rest_reg_mask
out['gate1_hold'] = dict(fracs={k: round(v, 4) for k, v in hf.items()},
                         iou_vs_registered_rest=round(iou(hm, rest_reg_mask), 4),
                         mad_bird_vs_registered=round(float(np.abs(hold - rest_reg)[u].mean()), 2),
                         iou_vs_original_rest=round(iou(hm, rest_mask), 4),
                         mad_bird_vs_original=round(float(np.abs(hold - rest)[hm | rest_mask].mean()), 2),
                         mad_paper=round(float(np.abs(hold - rest_reg)[~u].mean()), 2))
print('gate1 hold:', out['gate1_hold'], 'vs approved rest fracs:', out['rest_fracs'])

# ---- torso extent read (carried flag: rig torso 0.849 H vs spec 0.80) ----
def extent(a, m):
    ys, xs = np.nonzero(m)
    return dict(w=int(xs.max() - xs.min() + 1), h=int(ys.max() - ys.min() + 1),
                w_over_h=round(float((xs.max() - xs.min() + 1) / (ys.max() - ys.min() + 1)), 3))
sil_idle = np.asarray(Image.open(f'{FM3}/corpus/silhouette/idle_hold.png')) > 0
out['extent'] = dict(approved_original=extent(rest, rest_mask),
                     approved_registered=extent(rest_reg, rest_reg_mask),
                     rig_silhouette=extent(None, sil_idle),
                     model_hold=extent(hold, hm))
print('extent:', out['extent'])

# ---- gates 3+4: per-frame strike stats, registered gold vs model ----
def series_model():
    fr, bl, ios = [], [], []
    for i in range(52):
        a = load(f'{V3}/frames/strike_{WIN}/f{i:04d}.png'); m = content_mask(a)
        fr.append(color_fracs(a, m)); bl.append(bill_centroid_y(a, m))
        sil = np.asarray(Image.open(f'{FM3}/corpus/silhouette/strike_f{i:04d}.png')) > 0
        ios.append(iou(m, sil))
    return fr, bl, ios
def series_gold():
    fr, bl = [], []
    for i in range(52):
        a = gold(i); m = content_mask(a)
        fr.append(color_fracs(a, m)); bl.append(bill_centroid_y(a, m))
    return fr, bl
g_fr, g_bl = series_gold()
n_fr, n_bl, n_ios = series_model()
out['gold_black'] = [round(f['black'], 4) for f in g_fr]
out['model_black'] = [round(f['black'], 4) for f in n_fr]
out['gold_bill_y'] = [round(v, 1) if v is not None else None for v in g_bl]
out['model_bill_y'] = [round(v, 1) if v is not None else None for v in n_bl]
out['model_iou_vs_silhouette_median'] = round(float(np.median(n_ios)), 4)
out['model_iou_vs_silhouette'] = [round(v, 3) for v in n_ios]

def release_profile(bl):
    seg = bl[23:28]
    if any(v is None for v in seg):
        return dict(path=seg, increments=None, pct=None)
    tot = seg[-1] - seg[0]
    inc = [seg[k + 1] - seg[k] for k in range(4)]
    return dict(path=[round(v, 1) for v in seg], increments=[round(v, 1) for v in inc],
                pct=[round(100 * v / tot, 1) if tot else None for v in inc])
def wrong_way(bl):
    seg = bl[28:42]
    if any(v is None for v in seg):
        return dict(path=seg, wrong_way=None, steps=len(seg) - 1)
    return dict(path=[round(v, 1) for v in seg],
                wrong_way=sum(1 for k in range(len(seg) - 1) if seg[k + 1] > seg[k]),
                steps=len(seg) - 1)
out['gate3'] = dict(gold_release=release_profile(g_bl), model_release=release_profile(n_bl),
                    gold_withdrawal=wrong_way(g_bl), model_withdrawal=wrong_way(n_bl),
                    chart_pct=[25, 35, 40, 0])
print('gate3 gold release :', out['gate3']['gold_release'])
print('gate3 model release:', out['gate3']['model_release'])
print('gate3 gold withdrawal :', out['gate3']['gold_withdrawal'])
print('gate3 model withdrawal:', out['gate3']['model_withdrawal'])

gb = [v for i, v in enumerate(out['gold_black']) if i != 27]
nb = [v for i, v in enumerate(out['model_black']) if i != 27]
out['gate4'] = dict(gold_band_excl_f27=[min(gb), max(gb)], gold_f27=out['gold_black'][27],
                    model_band_excl_f27=[min(nb), max(nb)], model_f27=out['model_black'][27])
print('gate4:', out['gate4'])
print('model IoU vs silhouette (median):', out['model_iou_vs_silhouette_median'])

def vs_gold(i):
    a = load(f'{V3}/frames/strike_{WIN}/f{i:04d}.png'); m = content_mask(a)
    g = gold(i); gm = content_mask(g)
    return dict(frame=i, iou=round(iou(m, gm), 4),
                black_model=round(color_fracs(a, m)['black'], 4), black_gold=round(color_fracs(g, gm)['black'], 4),
                bill_model=(round(bill_centroid_y(a, m), 1) if bill_centroid_y(a, m) is not None else None),
                bill_gold=(round(bill_centroid_y(g, gm), 1) if bill_centroid_y(g, gm) is not None else None))
out['probe_vs_gold'] = [vs_gold(i) for i in PROBE]
out['train_spot_vs_gold'] = [vs_gold(i) for i in (10, 27, 40)]
print('probe vs gold:', out['probe_vs_gold'])
print('train spot vs gold:', out['train_spot_vs_gold'])

json.dump(out, open(f'{V3}/work/metrics_v3.json', 'w'), indent=1)
print('WROTE metrics_v3.json')
