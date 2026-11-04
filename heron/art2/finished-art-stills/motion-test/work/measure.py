#!/usr/bin/env python3
"""Motion-test measurements: fidelity + temporal consistency.
Masks: finished frames = color-distance from per-frame paper estimate
(corner median); study canvases = luminance < 200.
All frames 1024x600. Outputs work/metrics.json and prints summary tables.
"""
import json, os
import numpy as np
from PIL import Image

ROOT = os.path.expanduser('~/workspace/heron/art2')
MT = f'{ROOT}/finished-art-stills/motion-test'
ROSTER = f'{ROOT}/route2/roster/frames'

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

def hf_energy(a, mask):
    g = a.mean(axis=2)
    lap = np.abs(np.diff(g, axis=0)).mean() + np.abs(np.diff(g, axis=1)).mean()
    return float(lap)

def mask_stats(mask):
    ys, xs = np.nonzero(mask)
    if len(xs) == 0:
        return dict(area=0)
    return dict(area=int(mask.sum()), x0=int(xs.min()), x1=int(xs.max()),
                y0=int(ys.min()), y1=int(ys.max()),
                cx=float(xs.mean()), cy=float(ys.mean()),
                w=int(xs.max() - xs.min() + 1), h=int(ys.max() - ys.min() + 1))

def color_fracs(a, mask):
    r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    n = max(mask.sum(), 1)
    black = mask & (a.mean(axis=2) < 70)
    rust = mask & (r > 95) & (r - g > 22) & (r - b > 40)
    yellow = mask & (r > 150) & (g > 95) & (b < 120) & (r - b > 60)
    slate = mask & (b > r + 4) & (a.mean(axis=2) > 60) & (a.mean(axis=2) < 190)
    return dict(black=float(black.sum() / n), rust=float(rust.sum() / n),
                yellow=float(yellow.sum() / n), slate=float(slate.sum() / n))

def head_proxy(mask):
    """Mean y of mask pixels in the rightmost 12% of the mask's width."""
    st = mask_stats(mask)
    if st['area'] == 0:
        return None
    xthr = st['x1'] - 0.12 * st['w']
    ys, xs = np.nonzero(mask & (np.arange(mask.shape[1])[None, :] >= xthr))
    return float(ys.mean()) if len(ys) else None

out = {}

# ---------- reference stills ----------
rest = load(f'{ROOT}/finished-art-stills/audubon_rest.png')
rest_mask = content_mask(rest)
rest_stats = dict(mask=mask_stats(rest_mask), fracs=color_fracs(rest, rest_mask),
                  paper=paper_color(rest).tolist(), head=head_proxy(rest_mask))
strike_still = load(f'{ROOT}/finished-art-stills/audubon_strike.png')
strike_mask = content_mask(strike_still)
strike_stats = dict(mask=mask_stats(strike_mask), fracs=color_fracs(strike_still, strike_mask),
                    paper=paper_color(strike_still).tolist(), head=head_proxy(strike_mask))
out['reference'] = dict(rest=rest_stats, strike=strike_stats)

# ---------- idle ----------
idle_files = sorted(os.listdir(f'{MT}/frames/idle'))
idle = {}
prev = None
consec_mad = []
seq = []
for fn in idle_files:
    num = int(fn[1:5])
    a = load(f'{MT}/frames/idle/{fn}')
    m = content_mask(a)
    union = m | rest_mask
    inter = m & rest_mask
    iou = float(inter.sum() / union.sum())
    mad_bird = float(np.abs(a - rest)[union].mean())
    mad_paper = float(np.abs(a - rest)[~union].mean())
    rec = dict(file=fn, chart=num, iou_vs_rest=round(iou, 4), mad_vs_rest_bird=round(mad_bird, 2),
               mad_vs_rest_paper=round(mad_paper, 2), mask=mask_stats(m),
               fracs={k: round(v, 4) for k, v in color_fracs(a, m).items()},
               paper=np.round(paper_color(a), 1).tolist(), hf=round(hf_energy(a, m), 3),
               approved_original=(num == 30))
    idle[fn] = rec
    seq.append((num, a, m))
for (n0, a0, m0), (n1, a1, m1) in zip(seq, seq[1:]):
    u = m0 | m1
    consec_mad.append(dict(pair=f'{n0}->{n1}', chart_gap=n1 - n0,
                           mad_bird=round(float(np.abs(a0 - a1)[u].mean()), 2),
                           mad_paper=round(float(np.abs(a0 - a1)[~u].mean()), 2)))
out['idle'] = idle
out['idle_consec_mad'] = consec_mad

# ---------- strike ----------
strike = {}
for i in range(52):
    fn = f'f{i:04d}.png'
    a = load(f'{MT}/frames/strike/{fn}')
    m = content_mask(a)
    ca = load(f'{ROSTER}/strike/{fn}')
    cm = canvas_mask(ca)
    rec = dict(file=fn, mask=mask_stats(m), canvas_mask=mask_stats(cm),
               fracs={k: round(v, 4) for k, v in color_fracs(a, m).items()},
               head=head_proxy(m), canvas_head=head_proxy(cm),
               paper=np.round(paper_color(a), 1).tolist(), hf=round(hf_energy(a, m), 3),
               approved_original=(i == 27))
    strike[fn] = rec
out['strike'] = strike

with open(f'{MT}/work/metrics.json', 'w') as f:
    json.dump(out, f, indent=1)

# ---------- printed summaries ----------
def summ(vals):
    v = np.array(vals, dtype=float)
    return f'min {v.min():.3f} med {np.median(v):.3f} max {v.max():.3f} sd {v.std():.3f}'

gen = {k: v for k, v in idle.items() if not v['approved_original']}
print('REST reference:', rest_stats['mask'], {k: round(v, 4) for k, v in rest_stats['fracs'].items()},
      'paper', np.round(rest_stats['paper'], 1), 'head', rest_stats['head'])
print('STRIKE-STILL reference:', strike_stats['mask'], {k: round(v, 4) for k, v in strike_stats['fracs'].items()},
      'head', strike_stats['head'])
print()
print(f'IDLE generated n={len(gen)}')
print(' IoU vs rest      :', summ([v['iou_vs_rest'] for v in gen.values()]))
print(' MAD vs rest bird :', summ([v['mad_vs_rest_bird'] for v in gen.values()]))
print(' MAD vs rest paper:', summ([v['mad_vs_rest_paper'] for v in gen.values()]))
print(' mask area ratio  :', summ([v['mask']['area'] / rest_stats['mask']['area'] for v in gen.values()]))
print(' bbox w           :', summ([v['mask']['w'] for v in gen.values()]), 'rest w', rest_stats['mask']['w'])
print(' bbox h           :', summ([v['mask']['h'] for v in gen.values()]), 'rest h', rest_stats['mask']['h'])
print(' centroid x       :', summ([v['mask']['cx'] for v in gen.values()]), 'rest cx', round(rest_stats['mask']['cx'], 1))
print(' centroid y       :', summ([v['mask']['cy'] for v in gen.values()]), 'rest cy', round(rest_stats['mask']['cy'], 1))
print(' black frac       :', summ([v['fracs']['black'] for v in gen.values()]), 'rest', round(rest_stats['fracs']['black'], 4))
print(' rust frac        :', summ([v['fracs']['rust'] for v in gen.values()]), 'rest', round(rest_stats['fracs']['rust'], 4))
print(' yellow frac      :', summ([v['fracs']['yellow'] for v in gen.values()]), 'rest', round(rest_stats['fracs']['yellow'], 4))
print(' HF energy        :', summ([v['hf'] for v in gen.values()]))
print(' consec MAD bird  :', summ([c['mad_bird'] for c in consec_mad]))
print(' consec MAD paper :', summ([c['mad_paper'] for c in consec_mad]))
print()
print('STRIKE per-frame (frame area headY canvasHeadY blackFrac rustFrac yellowFrac):')
for i in range(52):
    r = strike[f'f{i:04d}.png']
    print(f" f{i:02d} area {r['mask']['area']:7d} head {r['head']:6.1f} chead {r['canvas_head'] if r['canvas_head'] is None else round(r['canvas_head'],1)} "
          f"black {r['fracs']['black']:.3f} rust {r['fracs']['rust']:.3f} yel {r['fracs']['yellow']:.3f}")
