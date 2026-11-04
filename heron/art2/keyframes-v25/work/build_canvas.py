#!/usr/bin/env python3
"""Build pose-study canvases from rig v2.5 (iter2 build) + annotated
measurement references + mechanism values per pose. Also measures the
approved stills' ink fractions with the motion-test-v3 instrument
(content_mask + black = content px with mean RGB < 70)."""
import sys, json
import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, '/home/hatch/workspace/heron/art2/rig-v25-gate/iter2')
import rig_v25 as rig

KF = '/home/hatch/workspace/heron/art2/keyframes-v25'
STILLS = '/home/hatch/workspace/heron/art2/finished-art-stills'

# ---- ink instrument (verbatim protocol from motion-test-v3 measure_v3.py)
def load(p):
    return np.asarray(Image.open(p).convert('RGB'), dtype=np.float32)

def paper_color(a):
    patches = [a[:40, :40], a[:40, -40:], a[-40:, :40], a[-40:, -40:]]
    return np.median(np.concatenate([p.reshape(-1, 3) for p in patches]), axis=0)

def content_mask(a):
    pc = paper_color(a)
    d = np.abs(a - pc).sum(axis=2)
    return d > 55

def black_frac(a, mask):
    black = mask & (a.mean(axis=2) < 70)
    return float(black.sum() / max(mask.sum(), 1))

out = {}
for name in ('audubon_rest', 'audubon_strike'):
    a = load(f'{STILLS}/{name}.png')
    m = content_mask(a)
    out[name] = dict(black=round(black_frac(a, m), 4),
                     paper=[round(float(v), 1) for v in paper_color(a)],
                     content_px=int(m.sum()))
    print(f"{name}: black={out[name]['black']} paper={out[name]['paper']} content_px={out[name]['content_px']}")

# paper tone for canvases: rest still's paper
paper = np.array(out['audubon_rest']['paper'], dtype=np.uint8)
SLATE = (58, 64, 72)  # monochrome study tone

mech = {}
for pose in ('alert', 'deep_coil', 'strike_peak'):
    img, dv, eye = rig.render(pose)
    mask = np.array(img) < 128
    # study canvas: slate silhouette on the stills' paper
    canvas = np.zeros((600, 1024, 3), dtype=np.uint8)
    canvas[:] = paper
    canvas[mask] = SLATE
    Image.fromarray(canvas).save(f'{KF}/work/canvas_{pose}.png')
    # annotated reference: mask + chain centreline + stations + anchors
    ann = Image.new('RGB', (1024, 600), (255, 255, 255))
    ann.paste(Image.fromarray(np.where(mask, 0, 255).astype(np.uint8)).convert('RGB'))
    dr = ImageDraw.Draw(ann)
    vis, neckbase = rig.visible_chain(dv['pts'])
    dr.line([tuple(p) for p in vis], fill=(30, 100, 220), width=2)
    for f in (0.25, 0.5, 0.75):
        p = rig.pt_at_frac(vis[::-1], f)  # fractions from the skull end
        dr.ellipse([p[0] - 5, p[1] - 5, p[0] + 5, p[1] + 5], outline=(220, 30, 30), width=2)
    for p, c in ((neckbase, (220, 30, 30)), (dv['skull'], (30, 180, 30)), (eye, (230, 170, 0))):
        dr.ellipse([p[0] - 7, p[1] - 7, p[0] + 7, p[1] + 7], outline=c, width=3)
    ann.save(f'{KF}/work/annot_{pose}.png')
    mech[pose] = dict(
        torso_px=round(float(rig.T), 2),
        neckbase=[round(float(v), 1) for v in neckbase],
        skull=[round(float(v), 1) for v in dv['skull']],
        eye=[round(float(v), 1) for v in eye],
        design_chord_base=round(dv['chord_base'], 3),
        design_chord76=round(dv['chord76'], 3),
        design_arc=round(dv['arc_vis'], 3),
        design_arc_over_chord=round(dv['arc_vis'] / dv['chord_base'], 2),
        visible_stations_from_skull={str(f): [round(float(v), 1) for v in rig.pt_at_frac(vis[::-1], f)]
                                     for f in (0.25, 0.5, 0.75)})
    print(f"{pose}: {json.dumps(mech[pose])}")

json.dump(dict(stills=out, mechanism=mech), open(f'{KF}/work/canvas_meta.json', 'w'), indent=1)
print('WROTE canvas_meta.json + canvases + annotated refs')
