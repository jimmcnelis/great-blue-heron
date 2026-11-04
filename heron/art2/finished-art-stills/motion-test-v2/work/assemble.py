#!/usr/bin/env python3
"""Assemble motion_test_v2.mp4: 48-frame hold (the single finished
hold frame tiled - a hold IS one frame; determinism proven separately)
+ the strike cycle twice. 152 frames, 24 fps, 1024x600.
Usage: assemble.py <winner: ema|model>"""
import os, shutil, subprocess, sys
ROOT = os.path.expanduser('~/workspace/heron/art2')
V2 = f'{ROOT}/finished-art-stills/motion-test-v2'
WIN = sys.argv[1]
seq = f'{V2}/work/seq'
shutil.rmtree(seq, ignore_errors=True); os.makedirs(seq)
n = 0
for _ in range(48):
    shutil.copy(f'{V2}/frames/hold/hold_frame.png', f'{seq}/{n:04d}.png'); n += 1
for _ in range(2):
    for i in range(52):
        shutil.copy(f'{V2}/frames/strike_{WIN}/f{i:04d}.png', f'{seq}/{n:04d}.png'); n += 1
print('sequence frames:', n)
subprocess.run(['ffmpeg', '-y', '-framerate', '24', '-i', f'{seq}/%04d.png',
                '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '17',
                f'{V2}/motion_test_v2.mp4'], check=True, capture_output=True)
print('wrote', f'{V2}/motion_test_v2.mp4')
