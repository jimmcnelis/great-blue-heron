"""Wrapper around the shared build_sample.py: monkeypatches
maskrender.xform_points to pass underscore scalar keys (_px_per_unit,
_neck_w) through untouched — the stock version crashes on float scalars
(IndexError in tf), which makes the KEYPOINTS.md-documented kp format
unusable. Point/polygon handling is byte-identical to stock.
Usage: build_one.py --image I --alpha A --kp K --pose P --out O"""
import os, sys
ART2 = os.path.expanduser('~/workspace/heron/art2')
sys.path.insert(0, ART2)
import numpy as np
import maskrender as M

_orig = M.xform_points
def xform_points_fixed(kp, fn):
    out = {}
    for k, v in kp.items():
        if k.startswith('_'):
            out[k] = v
        elif k in ('torso_poly', 'spine', 'bill_poly', 'wing_poly', 'tail_poly', 'plume_poly'):
            out[k] = [list(fn(np.asarray(p, float))) for p in v]
        else:
            out[k] = list(fn(np.asarray(v, float)))
    return out
M.xform_points = xform_points_fixed

import build_sample
build_sample.main()
