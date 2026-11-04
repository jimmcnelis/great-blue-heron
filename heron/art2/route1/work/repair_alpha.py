"""Matte repair for samples where rembg missed the head (and day_38's
neck): the head IS present in the source RGB — rembg failed to matte
the pale head against bright jetski/sky. Where a sample's mean alpha
inside the head channel is < 60, take alpha = max(clean_alpha,
feathered hand-annotated head-union). Same for the neck channel when
its mean is < 60. Rebuilds those samples with build_one.py."""
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
        IMG[f[:-5]] = os.path.join(ART2, 'frames', f[:-5] + '.jpg')
IMG['still_a'] = os.path.expanduser('~/workspace/heron/reference/real-heron-a.jpg')
IMG['still_b'] = os.path.expanduser('~/workspace/heron/reference/real-heron-b.jpg')

for name in sorted(IMG):
    sp = os.path.join(R1, 'samples', name + '.npz')
    if not os.path.exists(sp): continue
    z = np.load(sp)
    m, a = z['mask'], z['alpha'].astype(float)
    means = {}
    for ch in (1, 2):
        sel = m[ch] > 0
        means[ch] = float(a[sel].mean()) if sel.sum() > 50 else 999
    bad = [ch for ch in (1, 2) if means[ch] < 60]
    if not bad:
        continue
    ann = json.load(open(os.path.join(R1, 'ann', name + '.json')))
    pose = ann['_pose']
    img = Image.open(IMG[name]).convert('RGB')
    W, H = img.size
    scalars = dict(neck_w=float(ann.get('_neck_w', 1.0)), bulge_pos=0.0,
                   bulge_amp=0.0, px_per_unit=float(ann['_px_per_unit']))
    stack = M.build_mask_stack(ann, scalars, (W, H))
    add = np.zeros((H, W), np.float32)
    for ch in bad:
        add = np.maximum(add, (stack[ch] > 0).astype(np.float32))
    add = cv2.GaussianBlur(add, (0, 0), 1.5) * 255.0
    clean = np.asarray(Image.open(os.path.join(R1, 'alpha_clean', name + '.png'))).astype(np.float32)
    rep = np.maximum(clean, np.minimum(add, 255.0))
    apath = os.path.join(R1, 'alpha_clean', name + '.png')
    Image.fromarray(rep.astype(np.uint8)).save(apath)
    r = subprocess.run([sys.executable, os.path.join(R1, 'work', 'build_one.py'),
                        '--image', IMG[name], '--alpha', apath,
                        '--kp', os.path.join(R1, 'work', f'kp_{name}.json'),
                        '--pose', os.path.join(R1, 'work', f'pose_{name}.json'),
                        '--out', os.path.join(R1, 'samples', name + '.npz')],
                       capture_output=True, text=True)
    print(name, 'repaired channels', bad, 'means', {k: round(v) for k, v in means.items()},
          'rc', r.returncode)
print('REPAIR DONE')
