#!/usr/bin/env python3
"""Strike correspondence test: fit gold target k against rig
silhouettes k-2..k+2 (extension window + one standing frame).
If k itself is not the best fit, the charts are phase-offset."""
import os, sys
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_corpus import bird_mask
from fit_test import fit, warp_mask, iou

HOME = os.path.expanduser('~')
FS = f'{HOME}/workspace/heron/art2/finished-art-stills'
V3 = f'{FS}/finish-model-v3'

def sil(k):
    return np.asarray(Image.open(f'{V3}/corpus/silhouette/strike_f{k:04d}.png')) > 0

for k in (6, 25, 27, 30, 34):
    tgt = np.asarray(Image.open(f'{FS}/finish-model/corpus/target/strike_f{k:04d}.png').convert('RGB'), dtype=np.float32)
    tm = bird_mask(tgt)
    res = {}
    for j in range(max(0, k - 2), min(52, k + 3)):
        v, s, th, dx, dy = fit(tm, sil(j))
        res[j] = round(v, 3)
    print(f'target f{k:02d}:', res, '-> best', max(res, key=res.get), flush=True)
