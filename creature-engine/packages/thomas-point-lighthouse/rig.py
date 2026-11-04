"""Thomas Point Shoal Lighthouse — OBJECT rig (the object class's
reference rig).

Draws the landmark deterministically from state — no pose, no behavior,
no learned anything. State in: placement (root_x/root_y = waterline
centre), scale, lamp on/off, beam angle, glow. Geometry is authored in
design units relative to the root and multiplied by scale.

The real structure (model_sheet.md): a hexagonal white cottage on red
screwpiles, red roof, black lantern centred on the roof, gallery rail
around the lantern. Flat storybook treatment, per the shared style pack:
bold shapes, palette exact, no gradients.
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from engine.rigcore import Canvas  # noqa: E402

_DEFAULTS = dict(root_x=0.0, root_y=74.0, scale=1.0,
                 lamp=0.0, beam_angle=-12.0, glow=0.0)


def default_state():
    return dict(_DEFAULTS)


def render(state, ctx):
    p = {**_DEFAULTS, **state}
    idx = ctx['palette_index']
    cv = Canvas(ctx['design_w'], ctx['design_h'], ctx['grid_w'], ctx['grid_h'],
                ctx['palette_size'], supersample=ctx['style'].supersample)
    rx, ry, s = p['root_x'], p['root_y'], p['scale']

    def X(dx):
        return rx + dx * s

    def Y(dy):
        return ry + dy * s

    def P(dx, dy):
        return (X(dx), Y(dy))

    lit = p['lamp'] > 0.5
    lamp_c = (X(0), Y(-35.5))

    # beam first (behind everything): a flat wedge from the lantern
    if lit:
        a = math.radians(p['beam_angle'])
        tip = (lamp_c[0] + 36 * s * math.cos(a), lamp_c[1] + 36 * s * math.sin(a))
        perp = (-math.sin(a), math.cos(a))
        half = 3.2 * s
        cv.poly([lamp_c,
                 (tip[0] + perp[0] * half, tip[1] + perp[1] * half),
                 (tip[0] - perp[0] * half, tip[1] - perp[1] * half)],
                idx['beam'])
        if p['glow'] > 0.03:
            cv.ellipse(lamp_c[0], lamp_c[1], (3.5 + 4.5 * p['glow']) * s,
                       (3.5 + 4.5 * p['glow']) * s, idx['beam'])

    # screwpiles: five iron legs into the water + cross bracing
    for dx in (-15.0, -7.5, 0.0, 7.5, 15.0):
        cv.line([P(dx, 14), P(dx, -3)], idx['pile'], 1.7 * s)
    cv.line([P(-15, 8), P(15, -2)], idx['pile'], 1.1 * s)
    cv.line([P(15, 8), P(-15, -2)], idx['pile'], 1.1 * s)

    # platform deck the cottage stands on
    cv.poly([P(-18, -3), P(18, -3), P(15, -6.5), P(-15, -6.5)],
            idx['deck'], outline=idx['outline'], outline_width=0.7)
    cv.line([P(-15, -6.5), P(15, -6.5)], idx['roof'], 1.2 * s)

    # cottage: white hexagonal keeper's house (front face + edge lines)
    cv.poly([P(-12, -6.5), P(12, -6.5), P(12, -26), P(-12, -26)],
            idx['wall'], outline=idx['outline'], outline_width=0.8)
    cv.line([P(-12, -6.5), P(-12, -26)], idx['outline'], 0.7 * s)
    cv.line([P(12, -6.5), P(12, -26)], idx['outline'], 0.7 * s)
    # door (centre) and two shuttered windows
    cv.poly([P(-2.2, -6.5), P(2.2, -6.5), P(2.2, -15), P(-2.2, -15)],
            idx['shutter'], outline=idx['outline'], outline_width=0.6)
    for dx in (-8.0, 8.0):
        cv.poly([P(dx - 1.7, -21.5), P(dx + 1.7, -21.5),
                 P(dx + 1.7, -16.9), P(dx - 1.7, -16.9)],
                idx['ink'], outline=idx['outline'], outline_width=0.5)
        for sgn in (-1, 1):
            cv.poly([P(dx + sgn * 1.9, -21.5), P(dx + sgn * 3.1, -21.5),
                     P(dx + sgn * 3.1, -16.9), P(dx + sgn * 1.9, -16.9)],
                    idx['shutter'])

    # red mansard roof
    cv.poly([P(-13.5, -26), P(13.5, -26), P(7, -32.5), P(-7, -32.5)],
            idx['roof'], outline=idx['outline'], outline_width=0.8)

    # gallery rail around the lantern (the perch)
    cv.line([P(-6, -32.5), P(6, -32.5)], idx['ink'], 0.9 * s)
    for dx in (-6.0, -3.0, 0.0, 3.0, 6.0):
        cv.line([P(dx, -32.5), P(dx, -34.2)], idx['ink'], 0.55 * s)
    cv.line([P(-6, -34.2), P(6, -34.2)], idx['ink'], 0.55 * s)

    # lantern room: black frame, lamp cell lit or dark
    cv.poly([P(-2.6, -32.5), P(2.6, -32.5), P(2.6, -38.5), P(-2.6, -38.5)],
            idx['ink'], outline=idx['outline'], outline_width=0.6)
    cell = idx['lamp'] if lit else idx['outline']
    cv.poly([P(-1.4, -33.8), P(1.4, -33.8), P(1.4, -37.2), P(-1.4, -37.2)], cell)
    # lantern cap
    cv.poly([P(-3.4, -38.5), P(3.4, -38.5), P(0, -40.6)], idx['ink'])

    grid = cv.finish(ctx.get('clip_planes', ()))
    anchors = {
        'lantern': cv.anchor(*lamp_c),
        'gallery': cv.anchor(X(4.5), Y(-34.6)),
        'roof_peak': cv.anchor(X(-7), Y(-32.5)),
        'waterline': cv.anchor(X(0), Y(0)),
    }
    return grid, anchors
