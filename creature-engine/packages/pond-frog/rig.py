"""Pond Frog rig — a NEW species rig written directly on engine/rigcore.

Deliberately trivial shapes (ellipses + lines): the plug test measures the
SEAM, not the art. Baseline: the frog sits with body centre at design
( root_x, 44 + root_y ), feet on the shore line (design y=52).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from engine.rigcore import Canvas  # noqa: E402

BASE_Y = 44.0

_DEFAULTS = dict(root_x=48.0, root_y=0.0, squash=1.0, throat=0.0, blink=0.0,
                 mouth_open=0.0, tongue=0.0, tongue_dx=14.0, tongue_dy=-5.0,
                 leg_stretch=0.0, eye_look=0.0)


def default_pose():
    return dict(_DEFAULTS)


def render(pose, ctx):
    p = {**_DEFAULTS, **pose}
    idx = ctx['palette_index']
    cv = Canvas(ctx['design_w'], ctx['design_h'], ctx['grid_w'], ctx['grid_h'],
                ctx['palette_size'], supersample=ctx['style'].supersample)
    bx, by = p['root_x'], BASE_Y + p['root_y']
    sq = p['squash']
    # hind legs: folded dark shapes at the sides; stretch swings them back-down
    st = p['leg_stretch']
    for sgn in (-1, 1):
        hx = bx + sgn * 9.5
        foot = (bx + sgn * (11.5 + 6.0 * st), 52.0 + 3.0 * st)
        knee = (bx + sgn * (13.0 + 2.0 * st), by + 3.0 + 2.0 * st)
        cv.poly([(bx + sgn * 6.0, by + 1.0), knee, foot,
                 (bx + sgn * 8.5, by + 6.5)], idx['dark'])
        cv.line([(knee[0], knee[1]), foot], idx['dark'], 1.8)
    # body + belly
    cv.ellipse(bx, by, 11.0, 7.0 * sq, idx['body'])
    cv.ellipse(bx + 1.5, by + 2.8, 8.0, 4.2 * sq, idx['belly'])
    # throat sac (in front of belly, under the mouth)
    tr = p['throat']
    if tr > 0.03:
        cv.ellipse(bx + 6.5, by + 3.4, 2.0 + 4.6 * tr, 1.8 + 3.8 * tr, idx['throat'])
    # head: merged bump at the front-top of the body
    cv.ellipse(bx + 5.5, by - 4.2 * sq, 7.2, 4.6 * sq, idx['body'])
    # eyes: two bumps; pupils ride eye_look; blink draws a lid line
    for ex in (bx + 2.6, bx + 8.6):
        cv.ellipse(ex, by - 8.2 * sq, 2.5, 2.3, idx['body'])
        if p['blink'] > 0.5:
            cv.line([(ex - 1.5, by - 8.2 * sq), (ex + 1.5, by - 8.2 * sq)], idx['ink'], 0.8)
        else:
            cv.ellipse(ex, by - 8.4 * sq, 1.5, 1.5, idx['white'])
            cv.ellipse(ex + p['eye_look'], by - 8.4 * sq, 0.85, 0.85, idx['ink'])
    # mouth: a smile line that opens into a small wedge
    mx, my = bx + 11.2, by - 2.2
    if p['mouth_open'] > 0.1:
        cv.poly([(mx - 2.6, my - 0.8), (mx + 0.8, my + 1.8 * p['mouth_open']),
                 (mx - 2.6, my + 1.2)], idx['ink'])
    else:
        cv.line([(mx - 3.2, my), (mx + 0.6, my + 0.7)], idx['ink'], 0.8)
    # tongue: a fast pink line to the target with a sticky tip
    if p['tongue'] > 0.02:
        tx, ty = mx + p['tongue_dx'] * p['tongue'], my + p['tongue_dy'] * p['tongue']
        cv.line([(mx, my), (tx, ty)], idx['tongue'], 1.5)
        cv.ellipse(tx, ty, 1.1, 1.1, idx['tongue'])
    # front legs: two small props
    for fx in (bx + 4.0, bx + 9.0):
        cv.line([(fx, by + 4.5), (fx + 0.5, 52.0)], idx['dark'], 1.4)
    grid = cv.finish(ctx.get('clip_planes', ()))
    return grid, {'mouth': cv.anchor(mx, my), 'body_center': cv.anchor(bx, by)}
