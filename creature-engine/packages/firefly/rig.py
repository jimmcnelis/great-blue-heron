"""Firefly rig — a glow dot with a halo. Small on purpose: species #2 exists
to prove a second animal plugs into the same stage with no engine changes."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from engine.rigcore import Canvas  # noqa: E402

_DEFAULTS = dict(root_x=20.0, root_y=30.0, glow=0.5, wing=0.0)


def default_pose():
    return dict(_DEFAULTS)


def render(pose, ctx):
    p = {**_DEFAULTS, **pose}
    idx = ctx['palette_index']
    cv = Canvas(ctx['design_w'], ctx['design_h'], ctx['grid_w'], ctx['grid_h'],
                ctx['palette_size'], supersample=ctx['style'].supersample)
    x, y, glow = p['root_x'], p['root_y'], max(0.0, min(1.0, p['glow']))
    if glow > 0.05:
        cv.ellipse(x, y, 1.8 + 3.2 * glow, 1.6 + 2.8 * glow, idx['halo'])
    cv.ellipse(x, y, 1.5, 1.2, idx['glow'] if glow > 0.25 else idx['bodydark'])
    cv.ellipse(x, y, 0.7, 0.6, idx['bodydark'])
    if p['wing'] > 0.5:
        cv.line([(x - 0.5, y - 1.0), (x - 2.6, y - 2.6)], idx['wing'], 0.7)
        cv.line([(x + 0.5, y - 1.0), (x + 2.4, y - 2.8)], idx['wing'], 0.7)
    grid = cv.finish(ctx.get('clip_planes', ()))
    return grid, {'body': cv.anchor(x, y)}
