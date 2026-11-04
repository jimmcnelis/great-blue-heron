#!/usr/bin/env python3
"""Native-fps frame-diff within a time window (optionally a crop region).
Usage: window_motion.py <video> <t0> <t1> [x0 y0 x1 y1]  (region in 0-1000)
Writes work/wmotion_<stem>_<t0>-<t1>.csv and extracts full-res frames."""
import os, subprocess, sys
import numpy as np
from PIL import Image

SRC = os.path.expanduser('~/workspace/heron/reference-footage')
WORK = os.path.expanduser('~/workspace/heron/art2/real-bird-measure/work')
BASE = os.path.expanduser('~/workspace/heron/art2/real-bird-measure')

def probe_fps(path):
    out = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0',
                          '-show_entries', 'stream=avg_frame_rate,width,height',
                          '-of', 'csv=p=0', path], capture_output=True, text=True).stdout.strip()
    parts = out.split(',')
    w, h = int(parts[0]), int(parts[1])
    num, den = parts[2].split('/')
    return w, h, float(num) / float(den)

def main(name, t0, t1, region=None):
    path = os.path.join(SRC, name)
    stem = name.rsplit('.', 1)[0]
    W, H, fps = probe_fps(path)
    tag = f'{stem}_{t0}-{t1}'
    fdir = os.path.join(BASE, 'frames', tag)
    os.makedirs(fdir, exist_ok=True)
    lst = os.path.join(fdir, 'list.txt')
    if not os.path.exists(lst):
        subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(t0), '-i', path,
                        '-t', str(t1 - t0), '-q:v', '3',
                        os.path.join(fdir, 'f%04d.jpg')], check=True)
        with open(lst, 'w') as fh:
            for fn in sorted(os.listdir(fdir)):
                if fn.endswith('.jpg'):
                    fh.write(fn + '\n')
    files = [l.strip() for l in open(lst)]
    if region:
        x0, y0, x1, y1 = [int(v) for v in region]
        box = (x0 * W // 1000, y0 * H // 1000, x1 * W // 1000, y1 * H // 1000)
    else:
        box = (0, 0, W, H)
    prev = None
    rows = []
    for i, fn in enumerate(files):
        im = Image.open(os.path.join(fdir, fn)).convert('L').crop(box)
        a = np.asarray(im.resize((160, 90)), float)
        if prev is not None:
            rows.append((t0 + i / fps, float(np.abs(a - prev).mean())))
        prev = a
    rows = np.array(rows)
    np.savetxt(os.path.join(WORK, f'wmotion_{tag}.csv'), rows, delimiter=',',
               header='t,diff', comments='')
    med = np.median(rows[:, 1])
    print(f'{tag}: fps={fps:.2f} frames={len(files)} median={med:.3f}')
    # print the diff series compactly: mark local peaks > 2x median
    line = []
    for tt, dd in rows:
        mark = '*' if dd > 2 * med else ('+' if dd > 1.4 * med else '.')
        line.append(f'{tt:.2f}:{dd:.1f}{mark}')
    print(' '.join(line))

if __name__ == '__main__':
    reg = sys.argv[4:8] if len(sys.argv) > 7 else None
    main(sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), reg)
