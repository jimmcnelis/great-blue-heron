"""Flight assembly: anchor-aligned composites.

Each raw drawing is paper-normalized, optionally wash-faded (water band),
measured for ink anchor + scale, then placed so its anchor follows the
flight path. Preview scale: final 1024x576 working space (half of 2048).
Anchor modes: 'feet' (bottom ink centroid, lower third) for ground frames,
'centroid' (ink centroid) for airborne frames.
Scale: bbox width vs reference drawing in the same family, clamped.
"""
import os
import numpy as np
from PIL import Image

H = os.path.expanduser('~/workspace/heron')
PLATE = Image.open(f'{H}/gate1-strike/corrected/marsh_plate_pick.png').convert('RGB').resize((1024, 576))
HOME_PAPER = np.array([246, 235, 219], dtype=np.float32)
FLAT = np.array([244, 233, 215], dtype=np.float32)
LAYER_SCALE = 0.80  # of the 1024-wide working frame -> layer is 819x461


def prep(raw_path, wash_fade=False):
    im = Image.open(raw_path).convert('RGB').resize((1024, 576))
    a = np.asarray(im).astype(np.float32)
    patches = np.concatenate([a[:40, :40].reshape(-1, 3), a[:40, -40:].reshape(-1, 3),
                              a[-40:, :40].reshape(-1, 3), a[-40:, -40:].reshape(-1, 3)])
    paper = np.median(patches, axis=0)
    a = np.clip(a / np.maximum(paper, 1) * HOME_PAPER, 0, 255)
    if wash_fade:
        # push low-contrast pixels (water wash) toward paper, keep dark ink
        gray = a.mean(axis=2)
        dark = HOME_PAPER.mean() - gray          # 0 on paper
        k = np.clip(1.0 - np.clip((dark - 8) / 40.0, 0, 1) * 0.0, 0, 1)  # placeholder
        low = dark < 55                            # wash zone
        blend = np.clip(dark / 55.0, 0, 1) * 0.35 + 0.65   # wash keeps 65% of its depth min
        f = np.where(low, blend, 1.0)[..., None]
        a = HOME_PAPER - (HOME_PAPER - a) * f
    return a


def ink_mask(a):
    gray = a.mean(axis=2)
    return gray < (HOME_PAPER.mean() - 22)


def measure(a, mode):
    m = ink_mask(a)
    ys, xs = np.nonzero(m)
    if mode == 'feet':
        low = ys > (a.shape[0] * 0.62)
        xs2, ys2 = xs[low], ys[low]
        anchor = np.array([xs2.mean(), ys2.max()])
    else:
        anchor = np.array([xs.mean(), ys.mean()])
    width = xs.max() - xs.min()
    return anchor, width


SCALE_OVERRIDE = {'lr': 1.00, 'td': 1.00, 's0': 1.00, 's1': 1.00, 'st': 1.00}

def place(a, anchor, width, ref_width, target, out_size=(1024, 576), f_override=None):
    f = float(f_override) if f_override is not None else float(np.clip(ref_width / max(width, 1), 0.86, 1.10))
    lw, lh = int(1024 * LAYER_SCALE * f), int(576 * LAYER_SCALE * f)
    layer = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).resize((lw, lh))
    ax, ay = anchor * LAYER_SCALE * f
    ox, oy = int(round(target[0] - ax)), int(round(target[1] - ay))
    canvas = Image.new('RGB', out_size, tuple(FLAT.astype(int)))
    canvas.paste(layer, (ox, oy))
    out = np.asarray(canvas).astype(np.float32) * np.asarray(PLATE).astype(np.float32) / 255.0
    return Image.fromarray(np.clip(deyellow(out), 0, 255).astype(np.uint8))

_plate_a = np.asarray(PLATE).astype(np.float32)
PAPER_TARGET = np.median(_plate_a[:50, 410:614].reshape(-1, 3), axis=0)

def deyellow(out):
    patch = np.median(out[:50, 410:614].reshape(-1, 3), axis=0)
    gains = PAPER_TARGET / np.maximum(patch, 1)
    lum = out.mean(axis=2)
    sat = out.max(axis=2) - out.min(axis=2)
    paperiness = np.clip((lum - 160) / 50.0, 0, 1) * np.clip((75 - sat) / 40.0, 0, 1)
    strength = (paperiness * 1.0)[..., None]
    balanced = np.clip(out * gains, 0, 255)
    return out * (1 - strength) + balanced * strength


POSES = {
    'home':   (f'{H}/gate1-strike/fresh/K_coil_color_redo.png', 'feet', False),
    'c0':     (f'{H}/sequences/flight/poses/c0.png', 'feet', False),
    'c1':     (f'{H}/sequences/flight/poses/c1.png', 'feet', False),
    'crouch': (f'{H}/sequences/flight/keys/crouch.png', 'feet', False),
    'r1':     (f'{H}/sequences/flight/poses/r1.png', 'feet', False),
    'raised': (f'{H}/sequences/flight/keys/raised.png', 'feet', False),
    'l1':     (f'{H}/sequences/flight/poses/l1.png', 'feet', True),
    'd1':     (f'{H}/sequences/flight/poses/d1.png', 'centroid', True),
    't1':     (f'{H}/sequences/flight/poses/t1.png', 'centroid', False),
    'down':   (f'{H}/sequences/flight/keys/downstroke.png', 'centroid', False),
    'mup':    (f'{H}/sequences/flight/poses/mup.png', 'centroid', False),
    'up':     (f'{H}/sequences/flight/keys/upstroke.png', 'centroid', False),
    'mdown':  (f'{H}/sequences/flight/poses/mdown.png', 'centroid', False),
    'glide':  (f'{H}/sequences/flight/keys/glide.png', 'centroid', False),
    'bank':   (f'{H}/sequences/flight/keys/approach_bank.png', 'centroid', False),
    'flare':  (f'{H}/sequences/flight/keys/flare.png', 'centroid', False),
    'lr':     (f'{H}/sequences/flight/redo_batch3/reach.png', 'feet', False),
    'td':     (f'{H}/sequences/flight/redo_batch3/touchdown.png', 'feet', False),
    's0':     (f'{H}/sequences/flight/redo_batch3/step.png', 'feet', False),
    's1':     (f'{H}/sequences/flight/redo_batch3/settle.png', 'feet', False),
    'st':     (f'{H}/sequences/flight/redo_batch3/settle.png', 'feet', False),
}

# Home-derived ground poses share the home frame's true feet anchor
# (resized-raw coords): chained edits kept the feet at home's raw position,
# while the generic lower-third centroid is dragged right by the ripple rings.
ANCHOR_OVERRIDE = {name: (196.0, 557.0) for name in ('home', 'c0', 'c1', 'crouch', 'r1', 'raised', 'l1')}
ANCHOR_OVERRIDE.update({
    'lr': (452.0, 545.0),    # redo reach: feet midpoint
    'td': (460.0, 531.0),    # redo touchdown: feet midpoint
    's0': (437.0, 545.0),    # redo step: planted foot only
    's1': (247.0, 541.0),    # redo settle: feet midpoint
    'st': (247.0, 541.0),
})

_cache = {}

def get_pose(name):
    if name not in _cache:
        path, mode, wash = POSES[name]
        a = prep(path, wash_fade=wash)
        anchor, width = measure(a, mode)
        if name in ANCHOR_OVERRIDE:
            anchor = np.array(ANCHOR_OVERRIDE[name])
        _cache[name] = (a, anchor, width, mode)
    return _cache[name]


def frame(name, target, mirror=False):
    a, anchor, width, mode = get_pose(name)
    ref_name = 'home' if mode == 'feet' else 'down'
    ref_width = get_pose(ref_name)[2]
    if mirror:
        a = a[:, ::-1].copy()
        anchor = np.array([1024.0 - anchor[0], anchor[1]])
    return place(a, anchor, width, ref_width, target, f_override=SCALE_OVERRIDE.get(name))
