#!/usr/bin/env python3
"""Extract small gray frames at fixed fps to disk, compute frame-diff series,
build a contact sheet. Usage: extract_scan.py <video.mp4> <fps>"""
import os, subprocess, sys, glob
import numpy as np
from PIL import Image, ImageDraw

SRC = os.path.expanduser('~/workspace/heron/reference-footage')
WORK = os.path.expanduser('~/workspace/heron/art2/real-bird-measure/work')

def main(name, fps):
    stem = name.rsplit('.', 1)[0]
    d = os.path.join(WORK, 'scan_' + stem)
    os.makedirs(d, exist_ok=True)
    if not glob.glob(os.path.join(d, 'f*.jpg')):
        subprocess.run(['ffmpeg', '-v', 'error', '-i', os.path.join(SRC, name),
                        '-vf', f'fps={fps},scale=320:-2', '-q:v', '5',
                        os.path.join(d, 'f%04d.jpg')], check=True)
    files = sorted(glob.glob(os.path.join(d, 'f*.jpg')))
    arrs = [np.asarray(Image.open(f).convert('L'), float) for f in files]
    rows = []
    for i in range(1, len(arrs)):
        if arrs[i].shape == arrs[i - 1].shape:
            rows.append(((i) / fps, float(np.abs(arrs[i] - arrs[i - 1]).mean())))
    rows = np.array(rows)
    np.savetxt(os.path.join(WORK, f'motion_{stem}.csv'), rows, delimiter=',',
               header='t,diff', comments='')
    med = np.median(rows[:, 1])
    # stillness: fraction of steps with diff < 1.6x the 10th percentile noise floor
    floor = np.percentile(rows[:, 1], 10)
    still = float((rows[:, 1] < max(1.6 * floor, floor + 0.35)).mean())
    print(f'{name}: {len(files)} frames @ {fps}fps, median diff {med:.3f}, '
          f'noise floor {floor:.3f}, still-fraction(global) {still:.2f}')
    peaks = []
    d = rows[:, 1]
    for i in range(1, len(d) - 1):
        if d[i] > 2.5 * med and d[i] >= d[i - 1] and d[i] >= d[i + 1]:
            if not peaks or rows[i, 0] - peaks[-1][0] > 1.5:
                peaks.append([rows[i, 0], d[i]])
            elif d[i] > peaks[-1][1]:
                peaks[-1] = [rows[i, 0], d[i]]
    for tt, dd in sorted(peaks, key=lambda x: -x[1])[:16]:
        print(f'   burst t={tt:7.2f}s diff={dd:.2f}')
    # contact sheet: every Nth frame to make ~48 thumbs
    step = max(1, len(files) // 48)
    thumbs = []
    for i in range(0, len(files), step):
        im = Image.open(files[i]).convert('RGB')
        dr = ImageDraw.Draw(im)
        dr.rectangle([0, 0, 62, 14], fill=(0, 0, 0))
        dr.text((2, 2), f'{i/fps:.0f}s', fill=(255, 255, 0))
        thumbs.append(im)
    cols = 8
    rws = (len(thumbs) + cols - 1) // cols
    tw, th = thumbs[0].size
    sheet = Image.new('RGB', (cols * tw, rws * th))
    for i, im in enumerate(thumbs):
        sheet.paste(im, ((i % cols) * tw, (i // cols) * th))
    sheet.save(os.path.join(WORK, f'sheet_{stem}.jpg'), quality=80)
    print(f'   sheet: sheet_{stem}.jpg ({len(thumbs)} thumbs, every {step/fps:.1f}s)')

if __name__ == '__main__':
    main(sys.argv[1], float(sys.argv[2]))
