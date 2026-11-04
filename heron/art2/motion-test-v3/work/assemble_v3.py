#!/usr/bin/env python3
"""Assemble motion_test_v3.mp4 - same protocol as v2: 48-frame hold
(the single finished hold frame tiled; determinism proven separately)
+ the strike cycle twice. 152 frames, 24 fps, 1024x600.
Usage: assemble_v3.py <winner: ema|model>"""
import os, shutil, subprocess, sys
ROOT = os.path.expanduser('~/workspace/heron/art2')
V3 = f'{ROOT}/motion-test-v3'
WIN = sys.argv[1]
seq = f'{V3}/work/seq'
shutil.rmtree(seq, ignore_errors=True); os.makedirs(seq)
n = 0
for _ in range(48):
    shutil.copy(f'{V3}/frames/hold/hold_frame.png', f'{seq}/{n:04d}.png'); n += 1
for _ in range(2):
    for i in range(52):
        shutil.copy(f'{V3}/frames/strike_{WIN}/f{i:04d}.png', f'{seq}/{n:04d}.png'); n += 1
print('sequence frames:', n)
subprocess.run(['ffmpeg', '-y', '-framerate', '24', '-i', f'{seq}/%04d.png',
                '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '17',
                f'{V3}/motion_test_v3.mp4'], check=True, capture_output=True)
print('wrote', f'{V3}/motion_test_v3.mp4')
