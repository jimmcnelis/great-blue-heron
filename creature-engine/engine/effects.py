"""Procedural caused-mark runtime — the heron InkSim, generalized.

The engine owns effect PRIMITIVES (ripple, splash, drips, ring, puff). Which
clip events cause which effects, and with what parameters, is the
ENVIRONMENT package's effect_map — causality is a property of the world,
not of the animal and not of the engine.

Marks obey the founding law: they are only ever painted onto cells that are
still background. Stillness is the default; every mark is caused.
"""
import numpy as np


class Effects:
    def __init__(self, effect_map, ink_index, bg_index=0, surface_row=None,
                 effect_region=None):
        self.map = effect_map
        self.ink = int(ink_index)
        self.bg = int(bg_index)
        self.surface_row = surface_row          # grid row of the surface band centre
        self.region_half = (effect_region or {}).get('half_height', 5)
        self.ripples = []   # (x, t0, rmax, dur)
        self.splashes = []  # (x, t0, scale, seed)
        self.drips = []     # (x, y, vy, t_spawn)
        self.rings = []     # (x, y, t0, rmax, dur) free-position rings

    # -- spawners ------------------------------------------------------
    def ripple(self, x, t, rmax=7.0, dur=1.1):
        self.ripples.append((x, t, rmax, dur))

    def splash(self, x, t, scale=1.0, seed=0):
        self.splashes.append((x, t, scale, seed))
        self.ripple(x, t, 11 * scale, 1.4)
        self.ripple(x, t + 0.25, 7 * scale, 1.1)

    def ring(self, x, y, t, rmax=6.0, dur=0.9):
        self.rings.append((x, y, t, rmax, dur))

    def start_drips(self, x, y, t):
        self.drips.append((x, y, 2.0, t))

    # -- event intake --------------------------------------------------
    def fire(self, event, t, seed=0):
        """Resolve a clip event through the environment's causality table."""
        for inv in self.map.get(event.get('type'), []):
            fn = getattr(self, inv['effect'])
            scale = inv.get('scale', 1.0)
            params = inv.get('params', {})
            x = event.get('x', 0.0)
            if inv['effect'] == 'ripple':
                fn(x, t, rmax=params.get('rmax', 7.0 * scale),
                   dur=params.get('dur', 1.1))
            elif inv['effect'] == 'splash':
                fn(x, t, scale=scale, seed=seed)
            elif inv['effect'] == 'ring':
                fn(x, event.get('y', self.surface_row or 0), t, rmax=6.0 * scale)
            elif inv['effect'] == 'drips':
                fn(x, event.get('y', (self.surface_row or 10) - 6), t)

    # -- drawing ---------------------------------------------------------
    def draw(self, grid, t):
        g = grid
        H, W = g.shape
        cy = self.surface_row if self.surface_row is not None else H // 2
        for (x, t0, rmax, dur) in self.ripples:
            age = t - t0
            if age < 0 or age > dur:
                continue
            r = rmax * (1 - (1 - age / dur) ** 2)
            if r < 0.8:
                continue
            xs = np.arange(max(0, int(x - rmax - 2)), min(W, int(x + rmax + 3)))
            for xx in xs:
                for yy in range(cy - self.region_half, cy + self.region_half + 1):
                    if 0 <= yy < H:
                        d = np.hypot(xx - x, (yy - cy) * 3.1)
                        if abs(d - r) < 0.8 and g[yy, xx] == self.bg:
                            g[yy, xx] = self.ink
        for (x, y, t0, rmax, dur) in self.rings:
            age = t - t0
            if age < 0 or age > dur:
                continue
            r = rmax * (age / dur)
            if r < 0.6:
                continue
            for yy in range(max(0, int(y - rmax - 1)), min(H, int(y + rmax + 2))):
                for xx in range(max(0, int(x - rmax - 1)), min(W, int(x + rmax + 2))):
                    if abs(np.hypot(xx - x, yy - y) - r) < 0.8 and g[yy, xx] == self.bg:
                        g[yy, xx] = self.ink
        for (x, t0, scale, seed) in self.splashes:
            age = t - t0
            if age < 0 or age > 0.5:
                continue
            rng = np.random.default_rng(seed)
            for _ in range(9):
                vx = rng.uniform(-9, 9) * scale
                vy = rng.uniform(-26, -13) * scale
                px = x + vx * age
                py = cy - 1 + vy * age + 60 * age * age
                if 0 <= int(px) < W and 0 <= int(py) < H and g[int(py), int(px)] == self.bg:
                    g[int(py), int(px)] = self.ink
        alive = []
        for (x, y, vy, ts) in self.drips:
            yy = y + vy * (t - ts) + 30 * (t - ts) ** 2
            if self.surface_row is not None and yy >= self.surface_row:
                self.ripple(x, t, 3.2, 0.7)
                continue
            alive.append((x, y, vy, ts))
            if 0 <= int(yy) < H and 0 <= int(x) < W and g[int(yy), int(x)] == self.bg:
                g[int(yy), int(x)] = self.ink
        self.drips = alive
        return g
