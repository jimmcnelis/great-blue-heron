#!/usr/bin/env python3
"""Motion test v2 measurements - SAME protocol as v1 (measure.py's
mask/fraction code verbatim), plus bill-centroid paths (the measure the
v1 report's motion-truth section used), probe-frame honesty checks and
a canvas-geometry lock check. Outputs work/metrics_v2.json."""
import json, os
import numpy as np
from PIL import Image

ROOT = os.path.expanduser('~/workspace/heron/art2')
MT = f'{ROOT}/finished-art-stills/motion-test'
V2 = f'{ROOT}/finished-art-stills/motion-test-v2'
FM = f'{ROOT}/finished-art-stills/finish-model'
ROSTER = f'{ROOT}/route2/roster/frames'
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

def canvas_mask(a):
    return a.mean(axis=2) < 200

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

out = {}
rest = load(f'{ROOT}/finished-art-stills/audubon_rest.png')
rest_mask = content_mask(rest)
rest_fracs = color_fracs(rest, rest_mask)
out['rest_fracs'] = {k: round(v, 4) for k, v in rest_fracs.items()}

# ---- checkpoint selection on probe frames (IoU vs gold + bill err) ----
sel = {}
for cand in ('ema', 'model'):
    ious, berr = [], []
    for i in PROBE:
        a = load(f'{V2}/frames/strike_{cand}/f{i:04d}.png'); m = content_mask(a)
        g = load(f'{MT}/frames/strike/f{i:04d}.png'); gm = content_mask(g)
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
hold = load(f'{V2}/frames/hold/hold_frame.png'); hm = content_mask(hold)
hf = color_fracs(hold, hm)
u = hm | rest_mask
out['gate1_hold'] = dict(fracs={k: round(v, 4) for k, v in hf.items()},
                         iou_vs_rest=round(iou(hm, rest_mask), 4),
                         mad_bird=round(float(np.abs(hold - rest)[u].mean()), 2),
                         mad_paper=round(float(np.abs(hold - rest)[~u].mean()), 2))
print('gate1 hold:', out['gate1_hold'], 'vs approved rest:', out['rest_fracs'])

# ---- gate 3 + 4 preparation: per-frame strike stats, gold vs model ----
def series(base):
    fr, bl, ioc = [], [], []
    for i in range(52):
        a = load(f'{base}/f{i:04d}.png'); m = content_mask(a)
        fr.append(color_fracs(a, m))
        bl.append(bill_centroid_y(a, m))
        ca = load(f'{ROSTER}/strike/f{i:04d}.png')
        ioc.append(iou(m, canvas_mask(ca)))
    return fr, bl, ioc
g_fr, g_bl, _ = series(f'{MT}/frames/strike')
n_fr, n_bl, n_ioc = series(f'{V2}/frames/strike_{WIN}')
out['gold_black'] = [round(f['black'], 4) for f in g_fr]
out['model_black'] = [round(f['black'], 4) for f in n_fr]
out['gold_bill_y'] = [round(v, 1) if v is not None else None for v in g_bl]
out['model_bill_y'] = [round(v, 1) if v is not None else None for v in n_bl]
out['model_iou_vs_canvas_median'] = round(float(np.median(n_ioc)), 4)

def release_profile(bl):
    seg = bl[23:28]  # f23..f27
    tot = seg[-1] - seg[0]
    inc = [seg[k + 1] - seg[k] for k in range(4)]
    return dict(path=[round(v, 1) for v in seg], increments=[round(v, 1) for v in inc],
                pct=[round(100 * v / tot, 1) if tot else None for v in inc])
def wrong_way(bl):
    seg = bl[28:42]  # f28..f41
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
print('model IoU vs canvas (median):', out['model_iou_vs_canvas_median'])

# ---- probe + train spot-check fidelity vs gold ----
def vs_gold(cand_base, i):
    a = load(f'{cand_base}/f{i:04d}.png'); m = content_mask(a)
    g = load(f'{MT}/frames/strike/f{i:04d}.png'); gm = content_mask(g)
    return dict(frame=i, iou=round(iou(m, gm), 4),
                black_model=round(color_fracs(a, m)['black'], 4), black_gold=round(color_fracs(g, gm)['black'], 4),
                bill_model=round(bill_centroid_y(a, m), 1), bill_gold=round(bill_centroid_y(g, gm), 1))
out['probe_vs_gold'] = [vs_gold(f'{V2}/frames/strike_{WIN}', i) for i in PROBE]
out['train_spot_vs_gold'] = [vs_gold(f'{V2}/frames/strike_{WIN}', i) for i in (10, 27, 40)]
print('probe vs gold:', out['probe_vs_gold'])
print('train spot vs gold:', out['train_spot_vs_gold'])

json.dump(out, open(f'{V2}/work/metrics_v2.json', 'w'), indent=1)
print('WROTE metrics_v2.json')
