#!/usr/bin/env python3
"""Build QA montages: idle sample sheet, strike contact strips, flicker-diff sheet."""
import os
from PIL import Image, ImageDraw

ROOT = os.path.expanduser('~/workspace/heron/art2')
MT = f'{ROOT}/finished-art-stills/motion-test'

def sheet(paths, cols, tw, th, labels, out):
    rows = (len(paths) + cols - 1) // cols
    s = Image.new('RGB', (cols * tw, rows * (th + 16)), 'white')
    d = ImageDraw.Draw(s)
    for i, (p, lab) in enumerate(zip(paths, labels)):
        im = Image.open(p).convert('RGB').resize((tw, th))
        x, y = (i % cols) * tw, (i // cols) * (th + 16)
        s.paste(im, (x, y))
        d.text((x + 4, y + th + 3), lab, fill='black')
    s.save(out)
    print('wrote', out, s.size)

idle_files = sorted(os.listdir(f'{MT}/frames/idle'))
sel = ['f0008.png', 'f0013.png', 'f0018.png', 'f0023.png', 'f0029.png', 'f0030.png',
       'f0034.png', 'f0037.png', 'f0040.png', 'f0045.png', 'f0047.png', 'f0049.png']
sel = [f for f in sel if f in idle_files]
sheet([f'{MT}/frames/idle/{f}' for f in sel], 3, 341, 200,
      [f'idle {f[1:5]}' + (' (APPROVED)' if f == 'f0030.png' else '') for f in sel],
      f'{MT}/work/qa_idle_sheet.png')

strike_all = [f'{MT}/frames/strike/f{i:04d}.png' for i in range(52)]
sheet(strike_all, 6, 341, 200, [f'f{i:02d}' + (' APPROVED' if i == 27 else '') for i in range(52)],
      f'{MT}/work/qa_strike_sheet.png')

# flicker sheet: |frame - approved rest| amplified x4 for three idle frames
import numpy as np
rest = np.asarray(Image.open(f'{ROOT}/finished-art-stills/audubon_rest.png').convert('RGB'), dtype=np.int16)
diffs = []
for f in ['f0029.png', 'f0034.png', 'f0045.png']:
    a = np.asarray(Image.open(f'{MT}/frames/idle/{f}').convert('RGB'), dtype=np.int16)
    d = np.clip(np.abs(a - rest) * 4, 0, 255).astype(np.uint8)
    Image.fromarray(d).save(f'{MT}/work/diff_{f}')
    diffs.append(f)
print('diffs', diffs)
