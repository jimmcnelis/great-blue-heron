"""Route-1 sample builder: clean each frame's raw rembg alpha by
restricting it to the dilated union of the hand-annotated part masks
(kills kayak-seat/paddle contamination; keeps only bird geometry),
report mask coverage, then build samples with the shared build_sample.py.
Frames whose raw alpha covers <45% of the annotated mask union are
dropped as segmentation failures."""
import json, os, subprocess, sys
import numpy as np
import cv2
from PIL import Image

ART2 = os.path.expanduser('~/workspace/heron/art2')
R1 = os.path.join(ART2, 'route1')
sys.path.insert(0, ART2)
import maskrender as M

IMG = {}
for f in os.listdir(os.path.join(R1, 'ann')):
    if f.endswith('.json'):
        IMG[f[:-5]] = None
for name in list(IMG):
    p = os.path.join(ART2, 'frames', name + '.jpg')
    IMG[name] = p if os.path.exists(p) else None
IMG['still_a'] = os.path.expanduser('~/workspace/heron/reference/real-heron-a.jpg')
IMG['still_b'] = os.path.expanduser('~/workspace/heron/reference/real-heron-b.jpg')

os.makedirs(os.path.join(R1, 'alpha_clean'), exist_ok=True)
os.makedirs(os.path.join(R1, 'samples'), exist_ok=True)
kept, dropped = [], []
for name in sorted(IMG):
    ann = json.load(open(os.path.join(R1, 'ann', name + '.json')))
    pose = ann.pop('_pose')
    img = Image.open(IMG[name]).convert('RGB')
    W, H = img.size
    raw = np.asarray(Image.open(os.path.join(R1, 'alpha_raw', name + '.png')))
    scalars = dict(neck_w=float(ann.get('_neck_w', 1.0)), bulge_pos=0.0,
                   bulge_amp=0.0, px_per_unit=float(ann['_px_per_unit']))
    stack = M.build_mask_stack(ann, scalars, (W, H))
    union = (stack.max(axis=0) > 0).astype(np.uint8)
    dil = max(3, int(round(2.5 * float(ann['_px_per_unit']))))
    ker = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * dil + 1, 2 * dil + 1))
    union_d = cv2.dilate(union, ker)
    cov = float(((raw > 40) & (union > 0)).sum()) / max(1, int((union > 0).sum()))
    clean = np.where(union_d > 0, raw, 0).astype(np.uint8)
    print(f'{name}: coverage {cov:.2f} dilate {dil}')
    if cov < 0.45:
        dropped.append((name, round(cov, 2)))
        continue
    apath = os.path.join(R1, 'alpha_clean', name + '.png')
    Image.fromarray(clean).save(apath)
    kpp = os.path.join(R1, 'work', f'kp_{name}.json')
    pop = os.path.join(R1, 'work', f'pose_{name}.json')
    json.dump(ann, open(kpp, 'w'))
    json.dump(pose, open(pop, 'w'))
    r = subprocess.run([sys.executable, os.path.join(R1, 'work', 'build_one.py'),
                        '--image', IMG[name], '--alpha', apath,
                        '--kp', kpp, '--pose', pop,
                        '--out', os.path.join(R1, 'samples', name + '.npz')],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(name, 'BUILD FAIL', r.stderr[-300:])
        dropped.append((name, 'build-fail'))
    else:
        kept.append(name)
print('KEPT', len(kept), kept)
print('DROPPED', dropped)
