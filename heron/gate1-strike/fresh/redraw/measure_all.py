#!/usr/bin/env python3
"""Redraw gates: per-drawing bird_sat (raw poses) + registered feet positions.
Usage: python3 measure_all.py [poses|feet|all]"""
import os, sys
import numpy as np
from PIL import Image

REDRAW = os.path.dirname(os.path.abspath(__file__))
POSES = os.path.join(REDRAW, 'poses')
REG = os.path.join(REDRAW, 'registered')
HOME_SAT = 46.9
BAND = (42.9, 50.9)

def bird_sat(im):
    hsv = np.asarray(im.convert('HSV')).astype(float)
    lum = np.asarray(im.convert('L')).astype(float)
    return float(hsv[..., 1][lum < 210].mean())

def do_poses():
    print(f"{'drawing':10s} {'bird_sat':>8s}  gate")
    for f in sorted(os.listdir(POSES)):
        if not f.endswith('.png'):
            continue
        s = bird_sat(Image.open(os.path.join(POSES, f)).convert('RGB'))
        ok = BAND[0] <= s <= BAND[1]
        print(f"{f[:-4]:10s} {s:8.1f}  {'PASS' if ok else 'FAIL'}")

def feet_of(im):
    """Registered frame -> (front%, rear%) foot x-centres from the leg band."""
    a = np.asarray(im.convert('L')).astype(float)
    band = a[1020:1130, :]
    dark = band < 130
    cols = dark.sum(axis=0)
    xs = np.where(cols > 25)[0]
    if len(xs) == 0:
        return None
    groups, cur = [], [xs[0]]
    for x in xs[1:]:
        if x - cur[-1] <= 12:
            cur.append(x)
        else:
            groups.append(cur); cur = [x]
    groups.append(cur)
    cents = sorted(float(np.mean(g)) / a.shape[1] * 100 for g in groups if len(g) >= 3)
    return cents

def do_feet():
    print(f"{'drawing':10s} feet% (target front 15.2, rear 20.3, tol +/-0.8)")
    for f in sorted(os.listdir(REG)):
        if not f.endswith('.png'):
            continue
        c = feet_of(Image.open(os.path.join(REG, f)).convert('RGB'))
        print(f"{f[:-4]:10s} {c}")

if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'all'
    if mode in ('poses', 'all'):
        do_poses()
    if mode in ('feet', 'all'):
        do_feet()
