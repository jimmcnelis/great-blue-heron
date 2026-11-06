#!/usr/bin/env python3
"""Rebuild device stream, previews and proofs from registered_v2/ (post color
normalization). Timing already written by assemble_v2.py."""
import os, io, json, subprocess
import numpy as np
from PIL import Image

FRESH = os.path.dirname(os.path.abspath(__file__))
TS = '20261105-1920'
REG = os.path.join(FRESH, 'registered_v2')
timing = json.load(open(os.path.join(FRESH, 'timing.json')))
CHAIN = timing['drawings']; tick_map = timing['tick_map']
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
