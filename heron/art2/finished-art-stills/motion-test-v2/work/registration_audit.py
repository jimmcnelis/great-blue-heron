#!/usr/bin/env python3
"""Registration audit: for every corpus pair, compare the canvas bird's
geometry (bbox, centroid, area) with the target bird's. A pose-conditioned
translator can only learn geometry lock if these agree pair by pair."""
import csv, os
import numpy as np
from PIL import Image

FM = os.path.expanduser('~/workspace/heron/art2/finished-art-stills/finish-model')
COR = os.path.join(FM, 'corpus')

def load(p):
    return np.asarray(Image.open(p).convert('RGB'), dtype=np.float32)

def paper_color(a):
    patches = [a[:40, :40], a[:40, -40:], a[-40:, :40], a[-40:, -40:]]
    return np.median(np.concatenate([p.reshape(-1, 3) for p in patches]), axis=0)

def content_mask(a):
    pc = paper_color(a)
    return np.abs(a - pc).sum(axis=2) > 55

def canvas_mask(a):
    return a.mean(axis=2) < 200

def stats(m):
    ys, xs = np.nonzero(m)
    if len(xs) == 0:
        return None
    return dict(x0=int(xs.min()), x1=int(xs.max()), y0=int(ys.min()), y1=int(ys.max()),
                cx=float(xs.mean()), cy=float(ys.mean()), area=int(m.sum()))

rows = list(csv.DictReader(open(os.path.join(FM, 'corpus_manifest.csv'))))
out = []
for r in rows:
    c = load(os.path.join(COR, r['canvas'])); t = load(os.path.join(COR, r['target']))
    cm, tm = canvas_mask(c), content_mask(t)
    cs, ts = stats(cm), stats(tm)
    if not cs or not ts:
        continue
    inter = (cm & tm).sum(); union = (cm | tm).sum()
    out.append(dict(pair=r['pair_id'],
                    d_cx=ts['cx'] - cs['cx'], d_cy=ts['cy'] - cs['cy'],
                    h_ratio=(ts['y1'] - ts['y0']) / max(cs['y1'] - cs['y0'], 1),
                    w_ratio=(ts['x1'] - ts['x0']) / max(cs['x1'] - cs['x0'], 1),
                    area_ratio=ts['area'] / max(cs['area'], 1),
                    iou=float(inter / union)))

import json
def summ(key):
    v = np.array([o[key] for o in out], dtype=float)
    return dict(median=round(float(np.median(v)), 3), p10=round(float(np.percentile(v, 10)), 3),
                p90=round(float(np.percentile(v, 90)), 3), min=round(float(v.min()), 3), max=round(float(v.max()), 3))
res = {k: summ(k) for k in ('d_cx', 'd_cy', 'h_ratio', 'w_ratio', 'area_ratio', 'iou')}
res['n_pairs'] = len(out)
print(json.dumps(res, indent=1))
idle = [o for o in out if o['pair'].startswith('idle')]
strike = [o for o in out if o['pair'].startswith('strike')]
for name, grp in (('idle', idle), ('strike', strike)):
    if grp:
        print(name, 'n=', len(grp),
              'd_cx med', round(float(np.median([o['d_cx'] for o in grp])), 1),
              'd_cy med', round(float(np.median([o['d_cy'] for o in grp])), 1),
              'h_ratio med', round(float(np.median([o['h_ratio'] for o in grp])), 3),
              'iou med', round(float(np.median([o['iou'] for o in grp])), 3))
with open(os.path.join(FM, 'registration_audit.csv'), 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
print('wrote registration_audit.csv')
