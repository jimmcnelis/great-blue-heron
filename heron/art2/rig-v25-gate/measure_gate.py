"""Gate measurement pass — INDEPENDENT of the design integrals.

Landmarks were placed by visual grounding ON THE RENDERED MASKS (the motion
study's own method), converted here from the grounding frame (0-1000) to
pixels on the 1024x600 canvas. Torso = hull diameter (max pairwise distance
over tail/chest/backtop/belly, the study's definition).

The torso is ONE rigid outline shared by all three masks, so a single torso
constant is used: the two uncontaminated per-mask reads are 498.2 (peak) and
494.3 (alert); the coil's chest read landed on the protruding throat and was
rejected. TORSO = 496.3 px (their mean; ratio sensitivity <1%).

Neckbase is reported under two grounded reads because a bare silhouette
under-determines it where the tube merges with the body:
  - "notch": where the neck's upper outline meets the body outline (the
    project's established convention — cf. the approved-still instrument).
  - "blend": where the tube's flank visually merges into the body mass.
Plus "design": the mechanism's centreline x torso-outline crossing, for
reference (a construction value, not an artifact read).

station-1 = point at 76% of arc FROM SKULL; chord76 = |skull - station-1|;
chord_base = |skull - neckbase|; arc = centreline polyline length.
"""
import math
import numpy as np
from PIL import Image

HERE = '/home/hatch/workspace/heron/art2/rig-v25-gate'
TORSO = 496.3

def P(x, y):  # grounding frame (0-1000) -> px
    return np.array([x * 1024 / 1000.0, y * 600 / 1000.0])

# skull centre = grounded back-of-head + skull semi-major (0.052 T) along the
# grounded bill direction (back-of-head -> bill tip). Design cross-check in
# the report: all three agree with the mechanism to <=7 px.
POSES = {
    'strike_peak': dict(
        back=P(761, 793), bill=P(855, 994),
        stations=[P(774, 783), P(686, 602), P(631, 435)],   # skull -> base
        notch=P(600, 356), blend=P(579, 462),
        design_neckbase=np.array([599.8, 229.5])),
    'alert': dict(
        back=P(698, 66), bill=P(853, 70),
        stations=[np.array([731.7, 70.8]), np.array([733.7, 159.0]),
                  np.array([681.9, 263.4])],                # edge midpoints
        notch=P(589, 348), blend=P(592, 420),
        design_neckbase=np.array([601.2, 219.4])),
    'deep_coil': dict(
        back=P(671, 196), bill=P(793, 350),
        stations=[np.array([699.9, 142.8]), np.array([717.8, 219.0]),
                  np.array([670.7, 304.5])],                # edge midpoints
        notch=P(613, 352), blend=P(570, 480),
        design_neckbase=np.array([599.5, 232.7])),
}

def skull_centre(d):
    u = d['bill'] - d['back']
    u = u / np.hypot(*u)
    return d['back'] + u * 0.052 * TORSO

def measure(chain):
    seg = np.hypot(*np.diff(chain, axis=0).T)
    arc = float(seg.sum())
    skull, base = chain[0], chain[-1]
    chord_base = float(np.hypot(*(skull - base)))
    target, acc, s1 = 0.76 * arc, 0.0, chain[-1]
    for i, L in enumerate(seg):
        if acc + L >= target:
            t = 0 if L == 0 else (target - acc) / L
            s1 = chain[i] + t * (chain[i + 1] - chain[i])
            break
        acc += L
    chord76 = float(np.hypot(*(skull - s1)))
    return dict(arc=arc / TORSO, chord_base=chord_base / TORSO,
                chord76=chord76 / TORSO, arc_px=arc)

def width_scan(mask_path, chain, frac=0.06):
    """Mask width perpendicular to the centreline at frac of arc from the
    neckbase (the study's base-width station)."""
    img = np.array(Image.open(mask_path)) < 128
    seg = np.hypot(*np.diff(chain, axis=0).T)
    arc = float(seg.sum())
    target, acc, pt, direction = frac * arc, 0.0, chain[-1], None
    rev = chain[::-1]                       # walk from the base skull-ward
    rseg = np.hypot(*np.diff(rev, axis=0).T)
    for i, L in enumerate(rseg):
        if acc + L >= target:
            t = 0 if L == 0 else (target - acc) / L
            pt = rev[i] + t * (rev[i + 1] - rev[i])
            direction = (rev[i + 1] - rev[i]) / max(L, 1e-9)
            break
        acc += L
    n = np.array([-direction[1], direction[0]])
    # contiguous black run containing the scan point (a max-min span over
    # the whole line inflates the read wherever the line re-enters the body)
    def black(s):
        q = pt + n * s
        xi, yi = int(round(q[0])), int(round(q[1]))
        return 0 <= xi < 1024 and 0 <= yi < 600 and img[yi, xi]
    if not black(0.0):
        return float('nan')
    hi, lo = 0.0, 0.0
    while black(hi + 0.5) and hi < 120:
        hi += 0.5
    while black(lo - 0.5) and lo > -120:
        lo -= 0.5
    return hi - lo

results = {}
for pose, d in POSES.items():
    skull = skull_centre(d)
    results[pose] = dict(skull=skull)
    for read in ('notch', 'blend', 'design'):
        nb = d['design_neckbase'] if read == 'design' else d[read]
        chain = np.array([skull] + d['stations'] + [nb])
        results[pose][read] = measure(chain)
        if read == 'design':
            results[pose]['chain_design'] = chain
    # width station rides the centreline (stations + centreline-entry base);
    # the scan itself reads mask pixels only.
    w = width_scan(f"{HERE}/mask_{pose}.png", results[pose]['chain_design'])
    results[pose]['base_width'] = w / TORSO
    print(f"== {pose}: skull={np.round(skull,1)} base_width={results[pose]['base_width']:.4f} ({w:.1f}px)")
    for read in ('notch', 'design', 'blend'):
        m = results[pose][read]
        print(f"   {read:7s} chord_base={m['chord_base']:.3f} chord76={m['chord76']:.3f} "
              f"arc={m['arc']:.3f} arc:chord={m['arc']/m['chord_base']:.2f}")

for read in ('notch', 'design', 'blend'):
    rf = results['strike_peak'][read]['chord_base'] / results['deep_coil'][read]['chord_base']
    print(f"reach factor ({read}) = {rf:.2f}")
