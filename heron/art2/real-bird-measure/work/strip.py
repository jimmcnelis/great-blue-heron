#!/usr/bin/env python3
"""Montage selected frames from an extracted window dir into a labeled strip.
Usage: strip.py <frames_dir> <f0> <f1> <step> <t0> <fps> <out.jpg> [cols] [thumbw]"""
import os, sys
from PIL import Image, ImageDraw

d, f0, f1, step = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
t0, fps, out = float(sys.argv[5]), float(sys.argv[6]), sys.argv[7]
cols = int(sys.argv[8]) if len(sys.argv) > 8 else 8
tw = int(sys.argv[9]) if len(sys.argv) > 9 else 320
files = sorted(f for f in os.listdir(d) if f.endswith('.jpg'))
sel = []
for i in range(f0, f1 + 1, step):
    if 1 <= i <= len(files):
        sel.append((i, files[i - 1]))
thumbs = []
for i, fn in sel:
    im = Image.open(os.path.join(d, fn)).convert('RGB')
    r = tw / im.width
    im = im.resize((tw, int(im.height * r)))
    dr = ImageDraw.Draw(im)
    t = t0 + (i - 1) / fps
    dr.rectangle([0, 0, 118, 16], fill=(0, 0, 0))
    dr.text((3, 3), f'f{i} t={t:.2f}s', fill=(255, 255, 0))
    thumbs.append(im)
rows = (len(thumbs) + cols - 1) // cols
th = max(t.height for t in thumbs)
sheet = Image.new('RGB', (cols * tw, rows * th))
for i, im in enumerate(thumbs):
    sheet.paste(im, ((i % cols) * tw, (i // cols) * th))
sheet.save(out, quality=85)
print('strip ->', out, f'({len(thumbs)} frames)')
