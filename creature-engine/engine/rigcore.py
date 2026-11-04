"""Design-space drawing core — the primitives the heron rig hand-rolled,
generalized: a Canvas maps DESIGN coordinates to a supersampled PIL image,
offers tube/line/poly/ellipse/bezier helpers, applies environment clip
planes, and majority-downsamples to a palette-index grid.

Species rigs draw with a Canvas; they never touch grid coordinates.
Anchors are returned in GRID coordinates (the engine's contract).
"""
import numpy as np
from PIL import Image, ImageDraw


def bezier(p0, p1, p2, p3, n=14):
    t = np.linspace(0, 1, n)[:, None]
    p0, p1, p2, p3 = [np.asarray(p, float) for p in (p0, p1, p2, p3)]
    return ((1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 +
            3 * (1 - t) * t ** 2 * t * p2 + t ** 3 * p3)


class Canvas:
    """One frame under construction.

    design_w/design_h: the stage's design space. grid_w/grid_h: output grid.
    scale = grid_h / design_h (the heron rule: character size follows frame
    height), stage centred horizontally — exactly the v1 mapping, now data.
    palette_size: number of LOCAL palette entries for this species.
    background: local index of the canvas color (always 0 by schema).
    """

    def __init__(self, design_w, design_h, grid_w, grid_h, palette_size,
                 background=0, supersample=4):
        self.dw, self.dh = float(design_w), float(design_h)
        self.W, self.H = int(grid_w), int(grid_h)
        self.SS = int(supersample)
        self.npal = int(palette_size)
        self.bg = int(background)
        self.S = self.H / self.dh
        self.img = Image.new('L', (self.W * self.SS, self.H * self.SS), self.bg)
        self.dr = ImageDraw.Draw(self.img)

    # design -> supersampled pixel coords
    def mx(self, x):
        return (x - self.dw / 2.0) * self.S + self.W / 2.0

    def my(self, y):
        return y * self.S

    def _pts(self, pts):
        return [(self.mx(float(p[0])) * self.SS, self.my(float(p[1])) * self.SS) for p in pts]

    def line(self, pts, color, width, joint='curve'):
        self.dr.line(self._pts(pts), fill=int(color),
                     width=max(1, int(width * self.SS * self.S)), joint=joint)

    def poly(self, pts, color, outline=None, outline_width=0.8):
        kw = {}
        if outline is not None:
            kw = dict(outline=int(outline),
                      width=max(1, int(outline_width * self.S * self.SS)))
        self.dr.polygon(self._pts(pts), fill=int(color), **kw)

    def ellipse(self, cx, cy, rx, ry, color, outline=None, outline_width=0.8):
        box = [(self.mx(cx) - rx * self.S) * self.SS, (self.my(cy) - ry * self.S) * self.SS,
               (self.mx(cx) + rx * self.S) * self.SS, (self.my(cy) + ry * self.S) * self.SS]
        kw = {}
        if outline is not None:
            kw = dict(outline=int(outline),
                      width=max(1, int(outline_width * self.S * self.SS)))
        self.dr.ellipse(box, fill=int(color), **kw)

    def tube(self, pts, w0, w1, color, outline=None, outline_width=0.8):
        """A tapered stroke along a point path (the heron neck primitive)."""
        pts = np.asarray(pts, float)
        d = np.gradient(pts, axis=0)
        n = np.hypot(d[:, 0], d[:, 1]); n[n == 0] = 1
        nrm = np.stack([-d[:, 1] / n, d[:, 0] / n], axis=1)
        w = np.linspace(w0, w1, len(pts))[:, None] / 2.0
        poly = np.concatenate([pts + nrm * w, (pts - nrm * w)[::-1]])
        self.poly(poly, color, outline=outline, outline_width=outline_width)

    def anchor(self, x, y):
        """Design coords -> grid coords (what rigs report)."""
        return (float(self.mx(x)), float(self.my(y)))

    def finish(self, clip_planes=()):
        """Apply clip planes (hide below/above a design-y line -> background),
        then majority-downsample to the index grid."""
        arr = np.array(self.img, dtype=np.uint8).reshape(self.H, self.SS, self.W, self.SS)
        for plane in clip_planes:
            row = int(round(self.my(plane['at'])))
            if plane.get('hide') == 'below':
                arr[row:, :, :, :] = self.bg
            elif plane.get('hide') == 'above':
                arr[:row, :, :, :] = self.bg
        blocks = arr.transpose(0, 2, 1, 3).reshape(self.H, self.W, self.SS * self.SS)
        counts = np.stack([(blocks == k).sum(-1) for k in range(self.npal)], axis=-1)
        return counts.argmax(-1).astype(np.uint8)
