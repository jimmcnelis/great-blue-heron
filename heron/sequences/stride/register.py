"""Register stride pose drawings onto the 2048x1152 flat canvas.
Anchor: feet on the home waterline (y=1097), bird ink height = home ink height,
x placed so each pose's ANCHOR foot lands on the home anchor x.
Reports each pose's foot clusters for schedule tuning."""
import numpy as np
from PIL import Image
import os

HOME = os.path.expanduser('~/workspace/heron/gate1-strike/fresh/K_coil_color_redo.png')
OUT = os.path.expanduser('~/workspace/heron/sequences/stride/registered')
os.makedirs(OUT, exist_ok=True)
PAPER = np.array([246, 235, 219], dtype=float)
CANVAS = (2048, 1152)
WATER_Y = 1097  # home waterline in 2048 space (95.2%)

def ink_mask(img):
    a = np.asarray(img.convert('RGB')).astype(int)
    return (np.abs(a - PAPER).sum(axis=2) > 60)

def analyze(img):
    m = ink_mask(img)
    ys, xs = np.nonzero(m)
    return m, xs.min(), xs.max(), ys.min(), ys.max()

def feet_clusters(m, ybot):
    band = m[ybot-40:ybot+1, :]
    xs = np.nonzero(band.any(axis=0))[0]
    if len(xs) == 0: return []
    clusters, cur = [], [xs[0]]
    for x in xs[1:]:
        if x - cur[-1] <= 25: cur.append(x)
        else: clusters.append(cur); cur = [x]
    clusters.append(cur)
    return [(int(np.mean(c)), len(c)) for c in clusters if len(c) >= 4]

home = Image.open(HOME)
hm, hx0, hx1, hy0, hy1 = analyze(home)
home_h = hy1 - hy0
print(f'home ink: x {hx0}-{hx1}, y {hy0}-{hy1}, h={home_h}, feet clusters={feet_clusters(hm, hy1)}')

POSES = ['d1_halfrise', 'd2_carriage', 'wa_swing', 'wb_pass', 'wc_swing',
         't1_turn', 't2_frontal', 't3_turn', 't4_left', 't5_sink']
for name in POSES:
    img = Image.open(f'{os.path.dirname(__file__)}/poses/{name}.png')
    m, x0, x1, y0, y1 = analyze(img)
    h = y1 - y0
    scale = home_h / h
    # paper-normalize: divide by own paper (corner sample), remap to home paper
    a = np.asarray(img.convert('RGB')).astype(np.float32)
    own_paper = a[:80, :80].reshape(-1, 3).mean(axis=0)
    a = np.clip(a / own_paper * PAPER, 0, 255)
    img_n = Image.fromarray(a.astype(np.uint8))
    bird = img_n.crop((x0, y0, x1 + 1, y1 + 1)).resize((round((x1 - x0 + 1) * scale), round(h * scale)), Image.LANCZOS)
    canvas = Image.new('RGB', CANVAS, tuple(PAPER.astype(int)))
    # anchor: feet-mid x of the ORIGINAL drawing maps to home feet-mid
    fc = feet_clusters(m, y1)
    if fc:
        anchor_raw = np.mean([c[0] for c in fc])
    else:
        anchor_raw = (x0 + x1) / 2
    anchor_home = 363  # home feet midpoint in 2048 space
    dx = round(anchor_home - (anchor_raw - x0) * scale)
    dy = WATER_Y - bird.height
    canvas.paste(bird, (dx, dy))
    canvas.save(f'{OUT}/{name}.png')
    fc_s = [(round((c[0] - x0) * scale) + dx, c[1]) for c in fc]
    print(f'{name}: ink h={h} scale={scale:.3f} placed dx={dx} dy={dy} feet_on_canvas={fc_s}')
print('registered ->', OUT)
