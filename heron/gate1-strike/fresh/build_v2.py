#!/usr/bin/env python3
"""Densified strike — registration + assembly pipeline (v2, home-anchored).

Registration LOCKED to the approved home frame's build placement:
  scale 0.80, offset (+48, +204) on the 2048x1152 canvas
  (validated: bbox-restricted ink IoU 0.959-0.963 vs home_frame_approval.png;
   landmark fit exact on bill tip + both feet at this transform).
Paper target = approved home frame paper (245, 233, 219).
Canvas texture = mirror-tiled blank paper patch from the home frame itself,
so sequence frames sit on the same paper as the locked home frame.
The registered HOME is home_frame_approval.png VERBATIM (never re-derived).
"""
from PIL import Image
import numpy as np, os, json, sys

FRESH = os.path.dirname(os.path.abspath(__file__))
W, H = 2048, 1152
SCALE, DX, DY = 0.80, 48, 204
TARGET_PAPER = np.array([245.0, 233.0, 219.0])

def measure_paper(im):
    a = np.asarray(im.convert('RGB')).astype(float)
    h, w, _ = a.shape
    pts = []
    for y0, y1, x0, x1 in [(0, 40, 0, 40), (0, 40, w - 40, w), (0, 40, w // 2 - 20, w // 2 + 20)]:
        pts.append(a[y0:y1, x0:x1].reshape(-1, 3))
    return np.median(np.concatenate(pts), axis=0)

def paper_canvas():
    home = Image.open(os.path.join(FRESH, 'home_frame_approval.png')).convert('RGB')
    patch = home.crop((1250, 30, 2000, 530))  # pure paper, top-right
    pw, ph = patch.size
    canvas = Image.new('RGB', (W, H))
    flipx = patch.transpose(Image.FLIP_LEFT_RIGHT)
    flipy = patch.transpose(Image.FLIP_TOP_BOTTOM)
    flipxy = patch.transpose(Image.ROTATE_180)
    tiles = [[patch, flipx], [flipy, flipxy]]
    for ty in range(0, H, ph):
        for tx in range(0, W, pw):
            t = tiles[(ty // ph) % 2][(tx // pw) % 2]
            canvas.paste(t, (tx, ty))
    return canvas

CANVAS = paper_canvas()

def register(name, src_path):
    """Normalize paper -> target, scale/place with the locked transform,
    feather-paste onto the textured paper canvas."""
    im = Image.open(src_path).convert('RGB')
    p = measure_paper(im)
    gain = TARGET_PAPER / np.maximum(p, 1.0)
    a = np.asarray(im).astype(float) * gain[None, None, :]
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    sw, sh = round(W * SCALE), round(H * SCALE)
    small = im.resize((sw, sh), Image.LANCZOS)
    # feather mask: solid inside, cosine ramp on the outer 60 px
    m = np.ones((sh, sw), dtype=float)
    r = 60
    ramp = 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, r))
    m[:r, :] *= ramp[:, None]; m[-r:, :] *= ramp[::-1][:, None]
    m[:, :r] *= ramp[None, :]; m[:, -r:] *= ramp[::-1][None, :]
    mask = Image.fromarray((m * 255).astype(np.uint8))
    out = CANVAS.copy()
    out.paste(small, (DX, DY), mask)
    return out

if __name__ == '__main__':
    outdir = os.path.join(FRESH, 'registered_v2')
    os.makedirs(outdir, exist_ok=True)
    names = sys.argv[1:]
    for n in names:
        src = os.path.join(FRESH, 'poses', n + '.png')
        register(n, src).save(os.path.join(outdir, n + '.png'))
        print('registered', n)
    # home: verbatim copy
    Image.open(os.path.join(FRESH, 'home_frame_approval.png')).convert('RGB').save(
        os.path.join(outdir, 'HOME.png'))
    print('home copied verbatim')
