#!/usr/bin/env python3
"""REDRAW assembly: register all redraw poses under the locked transform,
write timing.json, device MJPEG, previews, proofs, delta table.
Run from fresh/. Expects redraw/poses/*.png (2048x1152) + redraw/work/tips.json."""
import os, io, json, subprocess, sys
import numpy as np
from PIL import Image

FRESH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REDRAW = os.path.join(FRESH, 'redraw')
POSES = os.path.join(REDRAW, 'poses')
REG = os.path.join(REDRAW, 'registered')
TS = sys.argv[1] if len(sys.argv) > 1 else 'redraw'
sys.path.insert(0, FRESH)
from build_v2 import register  # validated v2 registration (scale .80, +48/+204)

CHAIN = ['HOME', 'RX_1', 'RX_2', 'RK_EMID', 'RX_5', 'RX_4', 'RK_PEAK',
         'RK_EXIT', 'RW_A1', 'RW_A2', 'RW_A3', 'RW_A4', 'RW_A5',
         'RW_A7', 'RW_A9', 'RW_B1', 'RW_B2', 'RW_B3',
         'RW_B5', 'RW_B6', 'RW_B8', 'RW_B9', 'RW_C1',
         'RK_TUCK', 'RK_RISEA', 'RK_RISEB',
         'RW_E2', 'RW_E3', 'RW_E4', 'RW_E6', 'RW_E7', 'RW_E8',
         'RK_SETTLE']
IDX = {n: i for i, n in enumerate(CHAIN)}
# Re-timed map: slots whose poses failed after bounded attempts across
# multiple rounds (A6, A8, MIDW, B4, B7, D0, D1, E1, E5) are absorbed as
# holds on a neighbour; every absorbed step stays <= ~58 units.
COUNTS = {'RK_PEAK': 2, 'RW_A5': 2, 'RW_A7': 2, 'RW_A9': 2, 'RW_B1': 2,
          'RW_B3': 2, 'RW_B6': 2, 'RK_TUCK': 4, 'RK_RISEB': 2, 'RW_E2': 2,
          'RW_E8': 2}
tick_map = [0] * 10
for n in CHAIN[1:]:
    tick_map += [IDX[n]] * COUNTS.get(n, 1)
tick_map += [0] * 5
assert len(tick_map) == 60, len(tick_map)
assert len(CHAIN) == 33, len(CHAIN)

os.makedirs(REG, exist_ok=True)
for n in CHAIN[1:]:
    src = os.path.join(POSES, n + '.png')
    register(n, src).save(os.path.join(REG, n + '.png'))
    print('registered', n)
Image.open(os.path.join(FRESH, 'home_frame_approval.png')).convert('RGB').save(
    os.path.join(REG, 'HOME.png'))
print('home copied verbatim')

timing = {'fps': 12, 'duration_s': 5.0, 'ticks': 60,
          'unique_drawings': len(CHAIN),
          'home_frame': 'home_frame_approval.png (LOCKED, Jimmy-approved 2026-11-05 14:04; stream index 0, shown at t0-9 and t55-59)',
          'drawings': CHAIN, 'tick_map': tick_map,
          'phases': {'coil_freeze': 't0-9', 'extension': 't10-15 (t15=RK_PEAK)',
                     'peak_beat': 't15-16', 'withdrawal': 't17-43',
                     'settle': 't44-59 (t55-59=HOME)'},
          'build': 'FULL REDRAW 2026-11-05 (crew order 14:35-14:37): all drawings born in the home register; no post-hoc color normalization'}
with open(os.path.join(REDRAW, 'timing.json'), 'w') as f:
    json.dump(timing, f, indent=1)
print('timing.json written:', len(CHAIN), 'unique drawings')

paths = {n: os.path.join(REG, n + '.png') for n in CHAIN}
paper = Image.new('RGB', (1024, 600), (245, 233, 219))
stream = bytearray()
for n in CHAIN:
    im = Image.open(paths[n]).resize((1024, 576), Image.LANCZOS)
    frame = paper.copy(); frame.paste(im, (0, 12))
    buf = io.BytesIO(); frame.save(buf, 'JPEG', quality=82, subsampling=1)
    stream += buf.getvalue()
mjpeg_path = os.path.join(REDRAW, f'strike_device_1024x600_{TS}.mjpeg')
with open(mjpeg_path, 'wb') as f:
    f.write(stream)
i = stream.find(b'\xff\xc0')
print('device mjpeg bytes:', len(stream), 'SOF luma sampling byte:',
      hex(stream[i + 11]) if i > 0 else None,
      'UNDER CAP' if len(stream) < 2_500_000 else 'OVER 2.5MB CAP')

tmp = os.path.join(REDRAW, 'prev_tmp'); os.makedirs(tmp, exist_ok=True)
plate = Image.open(os.path.join(FRESH, '..', 'corrected', 'marsh_plate_pick.png')).convert('RGB').resize((2048, 1152), Image.LANCZOS)
for t, di in enumerate(tick_map):
    im = Image.open(paths[CHAIN[di]])
    im.resize((1280, 720), Image.LANCZOS).save(os.path.join(tmp, f'bird_{t:02d}.png'))
    a = np.asarray(im).astype(float); b = np.asarray(plate).astype(float)
    Image.fromarray((a * b / 255.0).astype(np.uint8)).resize((1280, 720), Image.LANCZOS).save(os.path.join(tmp, f'marsh_{t:02d}.png'))
for kind in ('bird', 'marsh'):
    out = os.path.join(REDRAW, f'heron_strike_{kind}_{TS}.mp4')
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-framerate', '12', '-i',
                    os.path.join(tmp, f'{kind}_%02d.png'), '-c:v', 'libx264',
                    '-pix_fmt', 'yuv420p', '-crf', '18', out, '-y'], check=True)
    print('preview:', out, os.path.getsize(out))

band_rows = [Image.open(paths[n]).crop((0, 830, 2048, 1152)).resize((1024, 161), Image.LANCZOS) for n in CHAIN]
band = Image.new('RGB', (1024, 161 * len(band_rows)), (245, 233, 219))
for i, r in enumerate(band_rows):
    band.paste(r, (0, i * 161))
band_path = os.path.join(REDRAW, f'proof_leg_band_{TS}.png'); band.save(band_path)
print('leg band:', band_path)
strip_names = ['RK_PEAK', 'RK_EXIT', 'RW_A2', 'RW_B2', 'RK_TUCK', 'RW_E2', 'HOME']
tiles = [Image.open(paths[n]).resize((512, 288), Image.LANCZOS) for n in strip_names]
strip = Image.new('RGB', (512 * len(tiles), 288), (245, 233, 219))
for i, t in enumerate(tiles):
    strip.paste(t, (i * 512, 0))
strip_path = os.path.join(REDRAW, f'proof_water_continuity_{TS}.png'); strip.save(strip_path)
print('water strip:', strip_path)

tips_path = os.path.join(REDRAW, 'work', 'tips.json')
if os.path.exists(tips_path):
    TIPS = {k: tuple(v) for k, v in json.load(open(tips_path)).items()}
    TIPS.setdefault('HOME', TIPS.get('K_coil'))
    seq = [CHAIN[di] for di in tick_map]
    steps = []
    for t in range(1, 60):
        a, b = TIPS[seq[t - 1]], TIPS[seq[t]]
        d = float(np.hypot(b[0] - a[0], b[1] - a[1]))
        if d > 0:
            steps.append((t, seq[t - 1], seq[t], round(d, 1)))
    deltas = [s[3] for s in steps]
    print('step deltas (per-tick):')
    for i, (t, a, b, d) in enumerate(steps):
        lo, hi = max(0, i - 2), min(len(deltas), i + 3)
        med = float(np.median(deltas[lo:hi]))
        flag = ' FLAG(>1.5x local median %.1f)' % med if d > 1.5 * med else ''
        print(f'  t{t:02d} {a:>9s} -> {b:<9s} {d:6.1f}{flag}')
else:
    print('no tips.json yet - delta table skipped')
