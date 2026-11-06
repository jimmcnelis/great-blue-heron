"""Flight composite: paper-normalize -> register (0.80, +48/+204) -> multiply over marsh plate.
Same recipe as strike/idle/stretch/preen. Usage: composite(raw_path) -> PIL Image 2048x1152."""
import numpy as np
from PIL import Image
import os

HOME_PAPER = np.array([246.0, 235.0, 219.0])
FLAT = (244, 233, 215)
PLATE = os.path.expanduser('~/workspace/heron/gate1-strike/corrected/marsh_plate_pick.png')
_plate = None

def plate():
    global _plate
    if _plate is None:
        _plate = np.asarray(Image.open(PLATE).convert('RGB').resize((2048, 1152))).astype(np.float32)
    return _plate

def measure_paper(img):
    a = np.asarray(img).astype(np.float32)
    patches = [a[10:80, 10:80], a[10:80, -80:-10], a[-80:-10, 10:80], a[-80:-10, -80:-10]]
    return np.stack([p.reshape(-1, 3).mean(axis=0) for p in patches]).mean(axis=0)

def composite(raw_path, dx=0, dy=0):
    img = Image.open(raw_path).convert('RGB').resize((2048, 1152))
    paper = measure_paper(img)
    a = np.asarray(img).astype(np.float32) / paper * HOME_PAPER
    layer = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).resize((1638, 922))
    canvas = Image.new('RGB', (2048, 1152), FLAT)
    canvas.paste(layer, (48 + dx, 204 + dy))
    out = np.clip(np.asarray(canvas).astype(np.float32) * plate() / 255.0, 0, 255).astype(np.uint8)
    return Image.fromarray(out)
