"""Heron prey fish, standalone on engine/rigcore — the shape transcribed
from v1 rig._draw_fish. In v1 the fish still RENDERS inside the heron's
clips (pose state 'fish' on the predator); this package is the extraction
target (refactor Phase 5) — it exists so scenes can already NAME the fish
as a participant and interactions can be written against it."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from engine.rigcore import Canvas  # noqa: E402

_DEFAULTS = dict(root_x=60.0, root_y=70.0, length=5.5, ang=-65.0, flip=1.0)


def default_pose():
    return dict(_DEFAULTS)


def render(pose, ctx):
    p = {**_DEFAULTS, **pose}
    idx = ctx['palette_index']
    cv = Canvas(ctx['design_w'], ctx['design_h'], ctx['grid_w'], ctx['grid_h'],
                ctx['palette_size'], supersample=ctx['style'].supersample)
    cx, cy, L = p['root_x'], p['root_y'], p['length']
    a = np.deg2rad(p['ang'])
    R = np.array([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]])
    flip = p['flip']
    h = L * 0.42

    def xf(pts):
        return [tuple(np.array([cx, cy]) + R @ (q * np.array([flip, 1]))) for q in pts]

    body = [[L * 0.5, 0], [L * 0.18, -h * 0.5], [-L * 0.28, -h * 0.46],
            [-L * 0.5, 0], [-L * 0.28, h * 0.46], [L * 0.18, h * 0.5]]
    tail = [[-L * 0.42, 0], [-L * 0.72, -h * 0.55], [-L * 0.72, h * 0.55]]
    back = [[L * 0.5, 0], [L * 0.18, -h * 0.5], [-L * 0.28, -h * 0.46],
            [-L * 0.2, -h * 0.1], [L * 0.2, -h * 0.08]]
    cv.poly(xf(tail), idx['fishback'])
    cv.poly(xf(body), idx['fish'])
    cv.poly(xf(back), idx['fishback'])
    eye = np.array([cx, cy]) + R @ (np.array([L * 0.32, -h * 0.08]) * np.array([flip, 1]))
    cv.ellipse(eye[0], eye[1], 0.55, 0.55, idx['ink'])
    return cv.finish(ctx.get('clip_planes', ())), {}
