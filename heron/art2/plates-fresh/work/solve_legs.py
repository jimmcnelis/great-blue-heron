"""Solve corrected per-pose leg traces per LEG_CANON.md §2.2/§2.3 and
measure leg placement off mechanism mask PNGs (before/after method).

Construction (1024x600 canvas; fractions over torso loop x-extent 125-605,
span 480 px; segment targets upper = lower = 0.21 torso = 104.2 px at the
gate constant T = 496.3):
  - one waterline y_w = 382 (both intertarsal joints on it, canon)
  - one ground line y_g = 486 (both feet on it; feet stay planted)
  - joint x = foot x + sign(exit_x - foot_x) * sqrt(104.2^2 - (y_g-y_w)^2)
    -> lower segment length exact
  - exit y = y_w - sqrt(104.2^2 - (joint_x - exit_x)^2) -> upper exact;
    the exit sits at the torso belly edge + a small feather skirt
    (0-16 px; far legs read lower, as in the source traces)
  - hip = exit - 42 px * unit(joint - exit)  (buried in the body core)
"""
import sys, math, json
import numpy as np
sys.path.insert(0, '/home/hatch/workspace/heron/art2/plates-fresh/work/before')
from rig_scratch import TORSO_LOOP  # the verified iter2 torso trace

T = 496.3
SEG = 0.21 * T            # 104.2 px, LEG_CANON §2.3
Y_W, Y_G = 382.0, 486.0   # waterline (joints), ground (feet)

# pose -> list of (exit_x, foot_x), near leg first
CFG = {
    'alert':       [(408, 399), (380, 351)],
    'deep_coil':   [(413, 423), (365, 355)],
    'strike_peak': [(418, 411), (365, 325)],
}

loop = np.array(TORSO_LOOP, dtype=float)

def belly_y(x):
    """Bottom edge of the torso loop at x (max y of loop boundary there)."""
    ys = []
    n = len(loop)
    for i in range(n):
        x1, y1 = loop[i]; x2, y2 = loop[(i + 1) % n]
        if min(x1, x2) <= x <= max(x1, x2) and x1 != x2:
            ys.append(y1 + (y2 - y1) * (x - x1) / (x2 - x1))
    return max(ys)

def solve():
    out = {}
    for pose, legs in CFG.items():
        solved = []
        for xe, xf in legs:
            dxl = math.sqrt(max(SEG**2 - (Y_G - Y_W)**2, 0.0))
            jx = xf + math.copysign(dxl, xe - xf)
            dyu = math.sqrt(max(SEG**2 - (jx - xe)**2, 0.0))
            ye = Y_W - dyu
            skirt = ye - belly_y(xe)
            if skirt < 0:            # clamp exit to the belly edge
                ye = belly_y(xe)
                skirt = 0.0
            E = np.array([xe, ye]); J = np.array([jx, Y_W]); F = np.array([xf, Y_G])
            u = (J - E) / np.hypot(*(J - E))
            hip = E - 42 * u
            solved.append(dict(
                hip=tuple(np.round(hip, 1)), exit=tuple(np.round(E, 1)),
                joint=tuple(np.round(J, 1)), foot=tuple(np.round(F, 1)),
                skirt=round(float(skirt), 1),
                upper=round(float(np.hypot(*(J - E))), 1),
                lower=round(float(np.hypot(*(F - J))), 1)))
        out[pose] = solved
    return out

def frac(x):
    return (x - 125.0) / 480.0

def measure_mask(path):
    """Leg placement off a bare mask PNG. Window: x 180-480, y > 345
    (below the torso; only legs + toes are black there)."""
    from PIL import Image
    a = np.array(Image.open(path).convert('L')) < 128
    win = np.zeros_like(a); win[346:, 180:481] = a[346:, 180:481]
    ys, xs = np.nonzero(win)
    ymax = ys.max()
    # cluster the SHAFT pixels only (exclude the toe fan, bottom 40 rows)
    shaft = ys <= ymax - 40
    sx, sy = xs[shaft], ys[shaft]
    order = np.argsort(sx)
    sx_s, sy_s = sx[order], sy[order]
    clusters, cur = [], [0]
    for i in range(1, len(sx_s)):
        if sx_s[i] - sx_s[i - 1] > 25:
            clusters.append(cur); cur = []
        cur.append(i)
    clusters.append(cur)
    legs = []
    for c in clusters:
        cx, cy = sx_s[c], sy_s[c]
        if len(cx) < 40:
            continue
        # foot: fit the lower segment (rows ymax-65..ymax-35) and
        # extrapolate to the foot point (fan tips reach ~5.5 px below it)
        low = (cy >= ymax - 65) & (cy <= ymax - 35)
        k, b = np.polyfit(cy[low], cx[low], 1)
        foot_y = ymax - 5.5
        foot_x = float(k * foot_y + b)
        # emergence read: centroid x in the first rows of the window
        top = cy <= 356
        exit_x = float(cx[top].mean()) if top.any() else float(cx.mean())
        legs.append(dict(foot_x=round(foot_x, 1), foot_y=round(foot_y, 1),
                         exit_x=round(exit_x, 1)))
    legs.sort(key=lambda d: d['foot_x'])
    if len(legs) == 2:
        fc = frac((legs[0]['foot_x'] + legs[1]['foot_x']) / 2)
        stag = abs(legs[1]['foot_x'] - legs[0]['foot_x']) / 480.0
        em = sorted(frac(l['exit_x']) for l in legs)
        return dict(legs=legs, feet_centre=round(fc, 3), stagger=round(stag, 3),
                    emergence=sorted([round(frac(l['exit_x']), 3) for l in legs]))
    return dict(legs=legs, note='cluster count != 2')

if __name__ == '__main__':
    sol = solve()
    print(json.dumps(sol, indent=1))
    for pose, legs in sol.items():
        for L in legs:
            print(pose, 'exit f=%.3f foot f=%.3f upper=%.1f (%.3f) lower=%.1f (%.3f) skirt=%.1f'
                  % (frac(L['exit'][0]), frac(L['foot'][0]), L['upper'],
                     L['upper'] / T, L['lower'], L['lower'] / T, L['skirt']))
        fc = np.mean([frac(L['foot'][0]) for L in legs])
        print(pose, 'feet-centre f=%.3f' % fc)
    for name in ('alert', 'deep_coil', 'strike_peak'):
        p = f'/home/hatch/workspace/heron/art2/plates-fresh/work/before/mask_{name}.png'
        print('BEFORE mask', name, json.dumps(measure_mask(p)))
