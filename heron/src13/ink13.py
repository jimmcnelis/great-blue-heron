"""Ink v1.3 — the world's caused water marks. Procedural, palette INK only,
fired by events; at rest there is nothing. Shared by both style packs:
the style layer never touches ink; the creature never draws it.
Events: (birth_frame, kind, x, y, scale) in design coords.
Kinds: ripple (step plant), splash (strike contact / dip), drip (falling
drop from bill/fish during withdrawal), ring (landing/takeoff residue).
"""
import numpy as np
import rig13 as R

INK = R.INK

def _ellipse(cv, cx, cy, rx, ry, w=0.35):
    cv.dr.ellipse([R.X(cx - rx), R.Y(cy - ry), R.X(cx + rx), R.Y(cy + ry)],
                  outline=INK, width=max(1, int(w * R.U * R.SS)))

def _arc(cv, cx, cy, rx, ry, a0, a1, w=0.3):
    cv.dr.arc([R.X(cx - rx), R.Y(cy - ry), R.X(cx + rx), R.Y(cy + ry)],
              start=a0, end=a1, fill=INK, width=max(1, int(w * R.U * R.SS)))

def _dot(cv, x, y, r=0.42):
    cv.dr.ellipse([R.X(x - r), R.Y(y - r * 0.75), R.X(x + r), R.Y(y + r * 0.75)], fill=INK)

def _tick(cv, x, y, dx, dy, ln, w=0.3):
    cv.line([(x, y), (x + dx * ln, y + dy * ln)], INK, w=w)

LIVES = dict(ripple=24, splash=18, drip=10, ring=30)

def frame_ink(events, frame):
    """Return draw callbacks for all live events at `frame`."""
    out = []
    for (birth, kind, x, y, s) in events:
        age = frame - birth
        life = LIVES[kind]
        if age < 0 or age >= life:
            continue
        a = age / life
        if kind == 'ripple':
            def dr(cv, x=x, y=y, s=s, a=a, age=age):
                for k in range(3):
                    aa = a - k * 0.16
                    if aa < 0:
                        continue
                    r = (0.8 + 6.4 * aa) * s
                    if aa < 0.75:
                        _ellipse(cv, x, y, r, r * 0.30, w=0.34 * (1 - aa * 0.6))
                    else:  # oldest ring breaks into dashes as it dies
                        for a0 in range(0, 360, 72):
                            _arc(cv, x, y, r, r * 0.30, a0 + age * 3, a0 + 34, w=0.26)
            out.append(dr)
        elif kind == 'splash':
            def dr(cv, x=x, y=y, s=s, a=a):
                r = (0.7 + 4.6 * a) * s
                _ellipse(cv, x, y, r, r * 0.30, w=0.4 * (1 - a * 0.5))
                n = 9
                for i in range(n):
                    ang = np.pi * (0.08 + 0.84 * i / (n - 1))  # upward fan
                    dx, dy = np.cos(ang), -np.sin(ang)
                    ln = (2.6 * (1 - a) + 0.4) * s
                    bx, by = x + dx * r * 0.5, y - 0.3
                    _tick(cv, bx, by, dx, dy, ln, w=0.3)
                    if a > 0.25:
                        gx = x + dx * (r * 0.5 + ln * 0.9)
                        gy = y - 0.3 + dy * ln * 0.9 + (a - 0.25) ** 2 * 9 * s
                        _dot(cv, gx, gy, r=0.34)
            out.append(dr)
        elif kind == 'drip':
            def dr(cv, x=x, y=y, s=s, a=a):
                yy = y + (R.WATER_Y - y) * (a ** 1.6)
                _dot(cv, x, yy, r=0.36 * s)
                if a > 0.8:
                    _ellipse(cv, x, R.WATER_Y, 1.1 * s, 0.33 * s, w=0.25)
            out.append(dr)
        elif kind == 'ring':
            def dr(cv, x=x, y=y, s=s, a=a):
                r = (1.0 + 8.5 * a) * s
                if a < 0.7:
                    _ellipse(cv, x, y, r, r * 0.30, w=0.3 * (1 - a))
                else:
                    for a0 in range(0, 360, 90):
                        _arc(cv, x, y, r, r * 0.30, a0, a0 + 40, w=0.22)
            out.append(dr)
    return out
