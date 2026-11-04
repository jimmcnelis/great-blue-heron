#!/usr/bin/env python3
"""Strike locator: frame-difference burst scan at 6 fps on small gray frames.
Outputs work/motion_<name>.csv (t, meandiff) and prints top bursts."""
import os, subprocess, sys
import numpy as np
from PIL import Image
import io

SRC = os.path.expanduser('~/workspace/heron/reference-footage')
OUT = os.path.expanduser('~/workspace/heron/art2/real-bird-measure/work')
FPS = 6
W = 256

def frames(path):
    cmd = ['ffmpeg', '-v', 'error', '-i', path, '-vf', f'fps={FPS},scale={W}:-2,format=gray',
           '-f', 'image2pipe', '-vcodec', 'png', '-']
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    buf = b''
    while True:
        chunk = p.stdout.read(65536)
        if not chunk:
            break
        buf += chunk
        # PNG boundaries: split on IEND
        while True:
            i = buf.find(b'IEND')
            if i < 0:
                break
            end = i + 8
            img = Image.open(io.BytesIO(buf[:end]))
            yield np.asarray(img, float)
            buf = buf[end:]
    p.wait()

def main(name):
    path = os.path.join(SRC, name)
    prev = None
    rows = []
    t = 0.0
    for f in frames(path):
        if prev is not None and f.shape == prev.shape:
            rows.append((t, float(np.abs(f - prev).mean())))
        prev = f
        t += 1.0 / FPS
    rows = np.array(rows)
    np.savetxt(os.path.join(OUT, f'motion_{name}.csv'), rows, delimiter=',',
               header='t,diff', comments='')
    # burst summary: local maxima above 2.5x median, min separation 1.5 s
    d = rows[:, 1]
    med = np.median(d)
    peaks = []
    for i in range(1, len(d) - 1):
        if d[i] > 2.5 * med and d[i] >= d[i - 1] and d[i] >= d[i + 1]:
            if not peaks or rows[i, 0] - peaks[-1][0] > 1.5:
                peaks.append((rows[i, 0], d[i]))
            elif d[i] > peaks[-1][1]:
                peaks[-1] = (rows[i, 0], d[i])
    print(f'{name}: median diff {med:.3f}; {len(peaks)} bursts')
    for tt, dd in sorted(peaks, key=lambda x: -x[1])[:14]:
        print(f'   t={tt:7.2f}s  diff={dd:.2f}')

if __name__ == '__main__':
    main(sys.argv[1])
