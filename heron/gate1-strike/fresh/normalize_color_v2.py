#!/usr/bin/env python3
"""Chroma normalization of registered frames toward the APPROVED HOME register.
Distance-weighted chroma gain: paper pixels (near-zero chroma) are untouched;
bird chroma is scaled by a per-frame factor targeting the home frame's mean
bird saturation (46.5). One correction pass if the first lands >3 away."""
import os
import numpy as np
from PIL import Image

FRESH = os.path.dirname(os.path.abspath(__file__))
REG = os.path.join(FRESH, 'registered_v2')
TARGET = 46.5

def bird_sat(im):
    hsv = np.asarray(im.convert('HSV')).astype(float)
    lum = np.asarray(im.convert('L')).astype(float)
    return hsv[..., 1][lum < 210].mean()

def gain(im, k):
    a = np.asarray(im).astype(float)
    gray = (0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2])[..., None]
    d = a - gray
    dist = np.abs(d).mean(axis=2, keepdims=True)
    w = np.clip(dist / 25.0, 0, 1)
    g = 1 + (k - 1) * w
    return Image.fromarray(np.clip(gray + d * g, 0, 255).astype(np.uint8))

names = [f[:-4] for f in sorted(os.listdir(REG)) if f.endswith('.png') and f != 'HOME.png']
for n in names:
    p = os.path.join(REG, n + '.png')
    im = Image.open(p).convert('RGB')
    s0 = bird_sat(im)
    k = TARGET / s0
    im2 = gain(im, k)
    s1 = bird_sat(im2)
    if abs(s1 - TARGET) > 3:
        im2 = gain(im2, TARGET / s1)
        s1 = bird_sat(im2)
    im2.save(p)
    print(f'{n:10s} sat {s0:5.1f} -> {s1:5.1f}  (k={k:.2f})')
