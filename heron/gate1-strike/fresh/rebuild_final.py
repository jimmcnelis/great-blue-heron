#!/usr/bin/env python3
"""Final rebuild WITHOUT X6 (rejected at coordinator visual QA: saturated blue
crown in the source generation, amplified by the normalization lift).
W_g3_2 absorbs X6's tick (x3). Everything else reuses the normalized
registered_v2 frames as-is."""
import os, io, json, subprocess
import numpy as np
from PIL import Image

FRESH = os.path.dirname(os.path.abspath(__file__))
TS = '20261105-1920'
REG = os.path.join(FRESH, 'registered_v2')

CHAIN = ['HOME', 'E_125', 'E_250', 'E_500', 'E_750', 'E_875', 'K_peak',
         'W_125', 'W_250', 'X1', 'W_g2_1', 'W_g2_2', 'W_250_alt', 'W_g3_1',
         'W_g3_2', 'W_500', 'W_375', 'W_g5_1', 'W_g5_2', 'W_g5_3',
         'X11', 'W_625', 'W_750', 'W_875', 'W_g7_1', 'W_g7_2', 'W_g7_3',
         'W_g7_4', 'W_g7_5', 'W_g7_6']
IDX = {n: i for i, n in enumerate(CHAIN)}
COUNTS = {'W_125': 3, 'W_250': 2, 'X1': 1, 'W_g2_1': 1, 'W_g2_2': 2,
          'W_250_alt': 2, 'W_g3_1': 1, 'W_g3_2': 3, 'W_500': 2,
          'W_375': 1, 'W_g5_1': 1, 'W_g5_2': 2, 'W_g5_3': 1, 'X11': 1,
          'W_625': 2, 'W_750': 2, 'W_875': 1, 'W_g7_1': 2, 'W_g7_2': 2,
          'W_g7_3': 2, 'W_g7_4': 2, 'W_g7_5': 2, 'W_g7_6': 3}
tick_map = [0] * 10 + [IDX[n] for n in ['E_125', 'E_250', 'E_500', 'E_750', 'E_875', 'K_peak']] + [IDX['K_peak']]
for n in CHAIN[7:]:
    tick_map += [IDX[n]] * COUNTS[n]
tick_map += [0] * 2
assert len(tick_map) == 60, len(tick_map)

timing = {'fps': 12, 'duration_s': 5.0, 'ticks': 60,
          'unique_drawings': len(CHAIN),
          'home_frame': 'home_frame_approval.png (LOCKED, Jimmy-approved 2026-11-05 14:04; stream index 0, shown at t0-9 and t58-59)',
          'drawings': CHAIN, 'tick_map': tick_map,
          'phases': {'coil_freeze': 't0-9', 'extension': 't10-15 (t15=K_peak)',
                     'peak_beat': 't15-16', 'withdrawal': 't17-43', 'settle': 't44-59 (t58-59=HOME)'}}
with open(os.path.join(FRESH, 'timing.json'), 'w') as f:
    json.dump(timing, f, indent=1)
print('timing.json rewritten:', len(CHAIN), 'unique drawings')
paths = {n: os.path.join(REG, n + '.png') for n in CHAIN}

paper = Image.new('RGB', (1024, 600), (245, 233, 219))
stream = bytearray()
for n in CHAIN:
    im = Image.open(paths[n]).resize((1024, 576), Image.LANCZOS)
    frame = paper.copy(); frame.paste(im, (0, 12))
    buf = io.BytesIO(); frame.save(buf, 'JPEG', quality=82, subsampling=1)
    stream += buf.getvalue()
mjpeg_path = os.path.join(FRESH, f'strike_device_1024x600_{TS}.mjpeg')
with open(mjpeg_path, 'wb') as f:
    f.write(stream)
i = stream.find(b'\xff\xc0')
print('device mjpeg bytes:', len(stream), 'SOF luma sampling byte:', hex(stream[i + 11]) if i > 0 else None)

tmp = os.path.join(FRESH, 'prev_tmp'); os.makedirs(tmp, exist_ok=True)
plate = Image.open('/home/hatch/workspace/heron/gate1-strike/corrected/marsh_plate_pick.png').convert('RGB').resize((2048, 1152), Image.LANCZOS)
for t, di in enumerate(tick_map):
    im = Image.open(paths[CHAIN[di]])
    im.resize((1280, 720), Image.LANCZOS).save(os.path.join(tmp, f'bird_{t:02d}.png'))
    a = np.asarray(im).astype(float); b = np.asarray(plate).astype(float)
    Image.fromarray((a * b / 255.0).astype(np.uint8)).resize((1280, 720), Image.LANCZOS).save(os.path.join(tmp, f'marsh_{t:02d}.png'))
for kind in ('bird', 'marsh'):
    out = os.path.join(FRESH, f'heron_strike_{kind}_{TS}.mp4')
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-framerate', '12', '-i',
                    os.path.join(tmp, f'{kind}_%02d.png'), '-c:v', 'libx264',
                    '-pix_fmt', 'yuv420p', '-crf', '18', out, '-y'], check=True)
    print('preview:', out, os.path.getsize(out))

band_rows = [Image.open(paths[n]).crop((0, 830, 2048, 1152)).resize((1024, 161), Image.LANCZOS) for n in CHAIN]
band = Image.new('RGB', (1024, 161 * len(band_rows)), (245, 233, 219))
for i, r in enumerate(band_rows):
    band.paste(r, (0, i * 161))
band_path = os.path.join(FRESH, f'proof_leg_band_{TS}.png'); band.save(band_path)
print('leg band:', band_path)
strip_names = ['K_peak', 'W_125', 'X1', 'W_500', 'W_875', 'HOME']
tiles = [Image.open(paths[n]).resize((512, 288), Image.LANCZOS) for n in strip_names]
strip = Image.new('RGB', (512 * len(tiles), 288), (245, 233, 219))
for i, t in enumerate(tiles):
    strip.paste(t, (i * 512, 0))
strip_path = os.path.join(FRESH, f'proof_water_continuity_{TS}.png'); strip.save(strip_path)
print('water strip:', strip_path)

TIPS = {'HOME': (472, 848), 'E_125': (537, 817), 'E_250': (577, 814),
        'E_500': (643, 840), 'E_750': (607, 922), 'E_875': (614, 957),
        'K_peak': (596, 954), 'W_125': (602, 810), 'W_250': (598, 823),
        'X1': (592, 809), 'W_g2_1': (603, 797), 'W_g2_2': (601, 761),
        'W_250_alt': (602, 760), 'W_g3_1': (600, 715), 'W_g3_2': (595, 716),
        'W_500': (596, 734), 'W_375': (604, 672),
        'W_g5_1': (587, 766), 'W_g5_2': (571, 784), 'W_g5_3': (554, 830),
        'X11': (489, 805), 'W_625': (449, 823), 'W_750': (447, 820),
        'W_875': (562, 696), 'W_g7_1': (555, 775), 'W_g7_2': (556, 807),
        'W_g7_3': (553, 796), 'W_g7_4': (551, 822), 'W_g7_5': (550, 824),
        'W_g7_6': (550, 823)}
seq = [CHAIN[di] for di in tick_map]
steps = []
for t in range(1, 60):
    a, b = TIPS[seq[t - 1]], TIPS[seq[t]]
    d = float(np.hypot(b[0] - a[0], b[1] - a[1]))
    if d > 0:
        steps.append((t, seq[t - 1], seq[t], round(d, 1)))
deltas = [s[3] for s in steps]
print('step deltas:')
for i, (t, a, b, d) in enumerate(steps):
    lo, hi = max(0, i - 2), min(len(deltas), i + 3)
    med = float(np.median(deltas[lo:hi]))
    flag = ' FLAG(>1.5x local median %.1f)' % med if d > 1.5 * med else ''
    print(f'  t{t:02d} {a:>9s} -> {b:<9s} {d:6.1f}{flag}')
