"""Iter2 gate measurement — ONE SHOT on the frozen iter2 renders.

Same protocol as the gate pass (measure_gate.py), CENTRELINE-ENTRY read
only (the convention Jimmy fixed for this iteration):
  chain = [skull] + grounded centreline stations + [neckbase], where
  neckbase = the mechanism's centreline x torso-outline crossing (a
  construction value) and skull/stations are grounded ON THE RENDERED
  MASKS (visual grounding, 0-1000 frame -> px). TORSO = 496.3 px (the
  gate's constant; ratio sensitivity <1%).

Skull centres:
  - strike_peak / alert: grounded back-of-head + 0.052*TORSO along the
    grounded bill direction (gate protocol). Peak occiput was grounded
    twice; the first ground sat on top of the skull (derived skull 16.6 px
    off the mechanism), the precise re-ground (rearmost tip of the head)
    lands 1.2 px from the gate build's own ground of the identical head
    and is the one used.
  - deep_coil: the occiput grounds were individually off-axis (neck-side
    back edge / occipital plume tip). The skull is instead derived from
    the two consistent grounds - bill tip (grounded twice, <=1 px apart)
    and the plume tip - through the animal definition's head-frame
    offsets (bill tip = skull + 0.27T*dvec; plume tip = skull +
    (-0.115*dvec - 0.030*perp)*T, T = the build's 493.85). Cross-check
    vs the mechanism's skull: 0.7 px.
Cross-checks (derived skull vs mechanism skull): peak 7.6 px, coil
0.7 px, alert 11.1 px - the gate's grounds agreed to <=7 px; alert is a
spot-check only.
"""
import math
import numpy as np
from PIL import Image

HERE = '/home/hatch/workspace/heron/art2/rig-v25-gate/iter2'
TORSO = 496.3

def P(x, y):
    return np.array([x * 1024 / 1000.0, y * 600 / 1000.0])

MECH = {  # mechanism values from the frozen iter2 rig run
    'strike_peak': dict(neckbase=np.array([599.3, 226.4]), skull=np.array([797.4, 489.1])),
    'deep_coil':   dict(neckbase=np.array([598.9, 226.5]), skull=np.array([689.0, 128.7])),
    'alert':       dict(neckbase=np.array([601.2, 219.4]), skull=np.array([740.8, 42.5])),
}

def skull_from_back(back, bill):
    u = bill - back; u = u / np.hypot(*u)
    return back + u * 0.052 * TORSO

POSES = {
    'strike_peak': dict(
        skull=skull_from_back(P(761, 795), P(858, 985)),
        stations=[P(718, 717), P(663, 613), P(627, 502)]),
    'alert': dict(
        skull=skull_from_back(P(690, 85), P(850, 71)),
        stations=[np.array([730.1, 79.8]), np.array([683.8, 265.8]),
                  np.array([616.4, 241.2])]),
    'deep_coil': dict(
        skull=np.array([688.7, 129.3]),   # head-frame derivation, see header
        stations=[np.array([688.1, 168.0]), np.array([663.6, 304.8]),
                  np.array([604.2, 267.0])]),
}

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
                chord76=chord76 / TORSO)

def width_scan(mask_path, chain, frac=0.06):
    """Gate's width scan, unchanged: contiguous black run perpendicular
    to the centreline at frac of arc from the neckbase."""
    img = np.array(Image.open(mask_path)) < 128
    rev = chain[::-1]
    rseg = np.hypot(*np.diff(rev, axis=0).T)
    arc = float(rseg.sum())
    target, acc, pt, direction = frac * arc, 0.0, chain[-1], None
    for i, L in enumerate(rseg):
        if acc + L >= target:
            t = 0 if L == 0 else (target - acc) / L
            pt = rev[i] + t * (rev[i + 1] - rev[i])
            direction = (rev[i + 1] - rev[i]) / max(L, 1e-9)
            break
        acc += L
    n = np.array([-direction[1], direction[0]])
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
    chain = np.array([d['skull']] + d['stations'] + [MECH[pose]['neckbase']])
    results[pose] = measure(chain)
    results[pose]['chain'] = chain
    delta = float(np.hypot(*(d['skull'] - MECH[pose]['skull'])))
    m = results[pose]
    print(f"== {pose}: skull={np.round(d['skull'],1)} (mech delta {delta:.1f}px) "
          f"chord_base={m['chord_base']:.3f} chord76={m['chord76']:.3f} "
          f"arc={m['arc']:.3f} arc:chord={m['arc']/m['chord_base']:.2f}")

rf = results['strike_peak']['chord_base'] / results['deep_coil']['chord_base']
print(f"reach factor (centreline-entry) = {rf:.2f}  [band 2.3-2.7]")

w_alert = width_scan(f"{HERE}/mask_alert.png", results['alert']['chain'])
print(f"alert base width @6% station = {w_alert:.1f}px = {w_alert/TORSO:.4f}  [band 0.105-0.129]")
w_peak15 = width_scan(f"{HERE}/mask_strike_peak.png", results['strike_peak']['chain'], frac=0.15)
print(f"peak width @15% station (gate's readable station) = {w_peak15:.1f}px = {w_peak15/TORSO:.4f} "
      f"[gate read 0.0665 raw / 0.0685 taper-corrected; band 0.0626-0.0765]")
